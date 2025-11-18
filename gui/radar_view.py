from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict

from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QCheckBox,
    Qt,
    pyqtSignal,
    QFont,
)
from aqt.qt import QPainter, QPen, QColor, QPointF

from ..core.logic_radar import (
    load_radar_snapshots,
    save_radar_snapshot,
    compute_balance_index,
    compute_trends,
    get_days_since_last_snapshot,
)
from ..core.models import RadarSnapshot


class RadarChartWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.values = [0, 0, 0, 0]
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(policy)

    def set_values(self, values: list[int]) -> None:
        self.values = values
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        if not self.values:
            return

        painter = QPainter(self)
        try:
            hint = QPainter.RenderHint.Antialiasing  # Qt6 style
        except AttributeError:
            # Fallback for older Qt bindings, though Anki 25.x uses Qt6
            hint = QPainter.Antialiasing  # type: ignore[attr-defined]
        painter.setRenderHint(hint)

        width = self.width()
        height = self.height()
        center = QPointF(width / 2.0, height / 2.0)
        radius = min(width, height) * 0.35

        max_value = 5.0
        axes = 4

        painter.setPen(QPen(QColor(180, 180, 180)))
        for i in range(axes):
            angle = 2.0 * 3.14159 * i / axes - 3.14159 / 2.0
            end_x = center.x() + radius * float((1.0)) * float((__import__("math").cos(angle)))
            end_y = center.y() + radius * float((1.0)) * float((__import__("math").sin(angle)))
            painter.drawLine(center, QPointF(end_x, end_y))

        points = []
        painter.setPen(QPen(QColor(80, 120, 200), 2))
        for i, val in enumerate(self.values):
            angle = 2.0 * 3.14159 * i / axes - 3.14159 / 2.0
            r = radius * max(0.0, min(float(val) / max_value, 1.0))
            x = center.x() + r * float((__import__("math").cos(angle)))
            y = center.y() + r * float((__import__("math").sin(angle)))
            points.append(QPointF(x, y))

        if len(points) >= 2:
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                painter.drawLine(p1, p2)


class InteractiveRadarWidget(QWidget):
    """Interactive radar control for setting skill values by click/drag."""

    valueChanged = pyqtSignal(str, int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(policy)

        self.skills = ["reading", "listening", "speaking", "writing"]
        self.skill_values: Dict[str, int] = {s: 1 for s in self.skills}
        # per-skill trend: "up", "down", or "same"
        self.skill_trends: Dict[str, str] = {s: "same" for s in self.skills}
        # optional previous-month values for ghost comparison polygon
        self.prev_skill_values: Dict[str, int] = {s: 0 for s in self.skills}

        self._center = QPointF(0, 0)
        self._radius = 0.0
        self._hover_axis: Optional[int] = None
        self._hover_value: Optional[float] = None

        self.setMouseTracking(True)

    # public helpers -------------------------------------------------
    def set_values_dict(self, values: Dict[str, int]) -> None:
        for s in self.skills:
            v = int(values.get(s, 1))
            self.skill_values[s] = max(1, min(5, v))
        self.update()

    def get_values_dict(self) -> Dict[str, int]:
        return dict(self.skill_values)

    def set_trends(self, trends: Dict[str, str]) -> None:
        """Update per-skill trend directions used for axis labels."""
        for s in self.skills:
            t = trends.get(s, "same")
            if t not in {"up", "down", "same"}:
                t = "same"
            self.skill_trends[s] = t
        self.update()

    def set_previous_values(self, values: Optional[Dict[str, int]]) -> None:
        """Set previous-month values for ghost comparison polygon.

        Pass None or an empty dict to hide the ghost polygon.
        """

        if not values:
            self.prev_skill_values = {s: 0 for s in self.skills}
        else:
            new_prev: Dict[str, int] = {}
            for s in self.skills:
                v = int(values.get(s, 0))
                new_prev[s] = max(0, min(5, v))
            self.prev_skill_values = new_prev
        self.update()

    # drawing --------------------------------------------------------
    def paintEvent(self, event) -> None:  # type: ignore[override]
        from math import cos, sin, pi

        if not self.skill_values:
            return

        painter = QPainter(self)
        try:
            hint = QPainter.RenderHint.Antialiasing
        except AttributeError:
            hint = QPainter.Antialiasing  # type: ignore[attr-defined]
        painter.setRenderHint(hint)

        width = self.width()
        height = self.height()
        self._center = QPointF(width / 2.0, height / 2.0)
        # Slightly reduced radius so labels on vertical axes remain visible.
        self._radius = min(width, height) * 0.40

        max_value = 5.0
        axes = len(self.skills)

        # axes
        base_pen = QPen(QColor(180, 180, 180))
        hover_pen = QPen(QColor(220, 220, 220))
        # Emojis for the four skills (same order as self.skills)
        axis_emojis = ["📖", "🎧", "🗣️", "✍️"]
        arrow_map = {"up": "↑", "down": "↓", "same": "="}

        font = painter.font()
        font.setPointSize(max(8, font.pointSize() - 2))
        painter.setFont(font)

        for i in range(axes):
            angle = 2.0 * pi * i / axes - pi / 2.0
            end_x = self._center.x() + self._radius * cos(angle)
            end_y = self._center.y() + self._radius * sin(angle)
            painter.setPen(hover_pen if i == self._hover_axis else base_pen)
            painter.drawLine(self._center, QPointF(end_x, end_y))

            # Small dots for each discrete step (1–5) along the axis
            # Highlight only the closest dot on the hovered axis.
            hovered_step = None
            if self._hover_axis == i and self._hover_value is not None:
                hovered_step = max(1, min(5, int(round(self._hover_value))))

            for step in range(1, int(max_value) + 1):
                r_step = self._radius * (step / max_value)
                sx = self._center.x() + r_step * cos(angle)
                sy = self._center.y() + r_step * sin(angle)

                if hovered_step is not None and step == hovered_step:
                    # Highlighted dot
                    dot_pen = QPen(QColor(220, 220, 220))
                    painter.setPen(dot_pen)
                    painter.drawEllipse(QPointF(sx, sy), 3, 3)
                else:
                    dot_pen = QPen(QColor(140, 140, 140))
                    painter.setPen(dot_pen)
                    painter.drawEllipse(QPointF(sx, sy), 2, 2)

            # Emoji + numeric value + trend arrow label slightly outside the circle
            painter.setPen(hover_pen if i == self._hover_axis else base_pen)
            if i < len(axis_emojis):
                # Give horizontal axes (right/left) a bit more spacing so
                # labels don't overlap the line endpoints.
                if i in (1, 3):  # right and left axes
                    label_r = self._radius + 22
                else:
                    label_r = self._radius + 12
                label_x = self._center.x() + label_r * cos(angle)
                label_y = self._center.y() + label_r * sin(angle)
                skill = self.skills[i]
                value = self.skill_values.get(skill, 1)
                trend = self.skill_trends.get(skill, "same")
                arrow = arrow_map.get(trend, "=")
                text = f"{axis_emojis[i]} {value} {arrow}"
                painter.drawText(
                    QPointF(label_x - 14, label_y + 4),
                    text,
                )

        # polygon (ghost previous-month outline + filled current area)
        points_prev = []
        points = []
        for i, skill in enumerate(self.skills):
            # previous values (may be 0 to indicate "no data")
            prev_val = float(self.prev_skill_values.get(skill, 0))
            angle = 2.0 * pi * i / axes - pi / 2.0
            if prev_val > 0:
                r_prev = self._radius * max(0.0, min(prev_val / max_value, 1.0))
                x_prev = self._center.x() + r_prev * cos(angle)
                y_prev = self._center.y() + r_prev * sin(angle)
                points_prev.append(QPointF(x_prev, y_prev))

            # current values
            val = float(self.skill_values.get(skill, 1))
            r = self._radius * max(0.0, min(val / max_value, 1.0))
            x = self._center.x() + r * cos(angle)
            y = self._center.y() + r * sin(angle)
            points.append(QPointF(x, y))

        # Ghost polygon for previous month
        if len(points_prev) >= 3:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            ghost_pen = QPen(QColor(120, 120, 120, 160), 1)
            ghost_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(ghost_pen)
            for i in range(len(points_prev)):
                p1 = points_prev[i]
                p2 = points_prev[(i + 1) % len(points_prev)]
                painter.drawLine(p1, p2)

        # Filled polygon for current month
        if len(points) >= 3:
            fill_color = QColor(80, 120, 200, 80)
            painter.setBrush(fill_color)
            painter.setPen(QPen(QColor(80, 120, 200, 160), 1))
            painter.drawPolygon(points)

            # Stronger outline on top
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(80, 120, 200), 2))
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                painter.drawLine(p1, p2)

        # No hover guide circle: keep interaction but avoid extra visual clutter

    # interaction ----------------------------------------------------
    def _axis_and_value_from_pos(self, pos) -> Optional[tuple[int, int, float]]:
        from math import atan2, hypot, pi

        if self._radius <= 0:
            return None

        dx = pos.x() - self._center.x()
        dy = pos.y() - self._center.y()
        angle = atan2(dy, dx)

        axes = len(self.skills)
        best_axis = 0
        best_diff = None
        for i in range(axes):
            axis_angle = 2.0 * pi * i / axes - pi / 2.0
            diff = (angle - axis_angle + pi) % (2 * pi) - pi
            ad = abs(diff)
            if best_diff is None or ad < best_diff:
                best_diff = ad
                best_axis = i

        dist = hypot(dx, dy)
        raw = (dist / self._radius) * 5.0
        value = max(1, min(5, int(round(raw))))
        return best_axis, value, raw

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        info = self._axis_and_value_from_pos(event.position())  # type: ignore[attr-defined]
        if info is None:
            return
        axis, value, raw = info
        self._hover_axis = axis
        self._hover_value = raw

        if event.buttons() & Qt.MouseButton.LeftButton:
            self._apply_value(axis, value)

        self.update()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.MouseButton.LeftButton:
            return
        info = self._axis_and_value_from_pos(event.position())  # type: ignore[attr-defined]
        if info is None:
            return
        axis, value, raw = info
        self._hover_axis = axis
        self._hover_value = raw
        self._apply_value(axis, value)
        self.update()

    def _apply_value(self, axis: int, value: int) -> None:
        skill = self.skills[axis]
        old = self.skill_values.get(skill, 1)
        value = max(1, min(5, value))
        if value == old:
            return
        self.skill_values[skill] = value
        self.update()
        self.valueChanged.emit(skill, value)


class RadarView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.snapshots = load_radar_snapshots()
        # current in-memory values for the selected month
        self.values: Dict[str, int] = {
            "reading": 1,
            "listening": 1,
            "speaking": 1,
            "writing": 1,
        }

        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Single-column layout: header row (month selector + save + balance),
        # interactive chart, values + trends + reminder banner.
        right_layout = QVBoxLayout()
        # Extremely tight vertical spacing so the chart and text feel connected
        right_layout.setSpacing(0)
        # Keep contents top-aligned; we'll center the chart itself explicitly so
        # the header row can span the full card width.
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        month_row = QHBoxLayout()
        month_row.setContentsMargins(0, 0, 0, 0)
        # Label shows the current month as a 3-letter abbreviation with a dot
        # (e.g. "Nov.") instead of the generic "Month" text.
        self.month_label = QLabel("", self)
        month_row.addWidget(self.month_label)
        self.month_combo = QComboBox(self)
        # Let the combo size itself to its contents instead of stretching.
        self.month_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
        # Give the month selector a light border and subtle hover/focus
        # background so it visually aligns with the dashboard buttons.
        self.month_combo.setStyleSheet(
            "QComboBox { border: 1px solid #d0d7de; border-radius: 4px; padding: 2px 6px; }"
            "QComboBox:hover { background-color: rgba(255, 255, 255, 40); }"
            "QComboBox:focus { border-color: #4a90e2; }"
        )
        self._populate_months()
        self._update_month_label_prefix()
        month_row.addWidget(self.month_combo)

        self.save_button = QPushButton("Save", self)
        self.save_button.setStyleSheet(
            "QPushButton { border: 1px solid #d0d7de; border-radius: 4px; padding: 4px 10px; }"
            "QPushButton:hover { background-color: rgba(255, 255, 255, 40); }"
        )
        month_row.addWidget(self.save_button)

        # Balance index text on the same header row, right-aligned so the row
        # spans the full width of the Fluency Snapshot card.
        month_row.addStretch(1)
        self.balance_label = QLabel("Balance Index: -", self)
        self.balance_label.setContentsMargins(0, 0, 0, 0)
        self.balance_label.setMargin(0)
        month_row.addWidget(self.balance_label, 0, Qt.AlignmentFlag.AlignRight)
        right_layout.addLayout(month_row)
        self.chart = InteractiveRadarWidget(self)
        # Slightly smaller fixed height so the text sits closer to the chart.
        self.chart.setFixedHeight(220)
        # Limit the chart's width so it doesn't expand to fill the entire
        # dashboard card, but give it enough horizontal space for axis labels
        # on the left/right to be fully visible.
        self.chart.setMinimumWidth(250)
        self.chart.setMaximumWidth(420)

        # Place the chart on its own row and center it horizontally.
        chart_row = QHBoxLayout()
        chart_row.setContentsMargins(0, 0, 0, 0)
        chart_row.addWidget(self.chart, 0, Qt.AlignmentFlag.AlignHCenter)
        right_layout.addLayout(chart_row)

        # Metrics widgets (value labels, trend text, reminder) are still
        # created for internal analysis, but no longer added under the chart in
        # this compact dashboard view.
        self.reading_label = QLabel("", self)
        self.listening_label = QLabel("", self)
        self.speaking_label = QLabel("", self)
        self.writing_label = QLabel("", self)

        self.trend_label = QLabel("No trend data yet", self)
        self.trend_label.setContentsMargins(0, 0, 0, 0)
        self.trend_label.setMargin(0)

        self.reminder_label = QLabel("", self)
        self.reminder_label.setContentsMargins(0, 0, 0, 0)
        self.reminder_label.setMargin(0)

        main_layout.addLayout(right_layout, 1)

        # The wheel now shows per-skill values and trends directly,
        # so keep the detailed value row and trend summary hidden.
        self.reading_label.hide()
        self.listening_label.hide()
        self.speaking_label.hide()
        self.writing_label.hide()
        self.trend_label.hide()

        self.month_combo.currentTextChanged.connect(self._on_month_changed)
        self.save_button.clicked.connect(self._on_save)
        self.chart.valueChanged.connect(self._on_chart_value_changed)

        self._load_current_month_values()
        self._update_banner()

    def _current_month_str(self) -> str:
        return datetime.now().strftime("%Y-%m")

    def _update_month_label_prefix(self) -> None:
        """Update the header label to show the current month as 'Mon.'"""

        text = self.month_combo.currentText() or self._current_month_str()
        try:
            dt = datetime.strptime(text, "%Y-%m")
            prefix = dt.strftime("%b")
        except ValueError:
            prefix = "Month"
        self.month_label.setText(prefix)

    def _populate_months(self) -> None:
        current = self._current_month_str()
        current_year = current.split("-")[0]

        # Start with all months of the current year.
        months = {f"{current_year}-{m:02d}" for m in range(1, 13)}

        # Add any months that exist in the snapshots (may include other years).
        for key in self.snapshots.keys():
            months.add(key)

        self.month_combo.clear()
        for m in sorted(months):
            self.month_combo.addItem(m)

        index = self.month_combo.findText(current)
        if index >= 0:
            self.month_combo.setCurrentIndex(index)

    def _load_current_month_values(self) -> None:
        month = self.month_combo.currentText() or self._current_month_str()
        data = self.snapshots.get(month)
        if isinstance(data, dict):
            self.values = {
                "reading": int(data.get("reading", 1)),
                "listening": int(data.get("listening", 1)),
                "speaking": int(data.get("speaking", 1)),
                "writing": int(data.get("writing", 1)),
            }
        else:
            self.values = {s: 1 for s in self.values.keys()}
        self._update_chart()
        self.save_button.setEnabled(False)

    def _update_chart(self) -> None:
        # Push current dict values into the interactive chart
        self.chart.set_values_dict(self.values)
        self._refresh_value_labels()
        self._update_analysis()

    def _on_month_changed(self, _text: str) -> None:
        self._update_month_label_prefix()
        self._load_current_month_values()

    def _on_save(self) -> None:
        month = self.month_combo.currentText() or self._current_month_str()
        snapshot = RadarSnapshot(
            month=month,
            reading=self.values["reading"],
            listening=self.values["listening"],
            speaking=self.values["speaking"],
            writing=self.values["writing"],
        )
        save_radar_snapshot(snapshot)
        self.snapshots = load_radar_snapshots()
        self._populate_months()
        self._update_chart()
        self._update_banner()
        self.save_button.setEnabled(False)

    def _on_chart_value_changed(self, skill: str, value: int) -> None:
        # Update in-memory values and UI when the user interacts with the radar.
        self.values[skill] = max(1, min(5, int(value)))
        self._update_chart()
        self.save_button.setEnabled(True)

    def _refresh_value_labels(self) -> None:
        self.reading_label.setText(f"Reading: {self.values['reading']}")
        self.listening_label.setText(f"Listening: {self.values['listening']}")
        self.speaking_label.setText(f"Speaking: {self.values['speaking']}")
        self.writing_label.setText(f"Writing: {self.values['writing']}")

    def _update_analysis(self) -> None:
        """Update balance index and trend labels based on snapshots."""

        if not self.snapshots:
            self.balance_label.setText("Balance Index: -")
            self.trend_label.setText("No trend data yet")
            self.chart.set_previous_values(None)
            return

        month = self.month_combo.currentText() or self._current_month_str()
        current = self.snapshots.get(month)
        if not isinstance(current, dict):
            self.balance_label.setText("Balance Index: -")
            self.trend_label.setText("No trend data yet")
            self.chart.set_previous_values(None)
            return

        score = compute_balance_index(current)
        if score is None:
            self.balance_label.setText("Balance Index: -")
        else:
            self.balance_label.setText(f"Balance Index: {score}%")

        # Trends compared to previous month, if any
        months_sorted = sorted(self.snapshots.keys())
        try:
            idx = months_sorted.index(month)
        except ValueError:
            idx = -1

        if idx <= 0:
            self.trend_label.setText("No trend data yet")
            # No previous month: reset trends on the chart to neutral
            self.chart.set_trends({})
            self.chart.set_previous_values(None)
            return

        prev_month = months_sorted[idx - 1]
        previous = self.snapshots.get(prev_month, {})
        trends = compute_trends(current, previous)
        # Feed trends into the interactive chart so axis arrows match
        self.chart.set_trends(trends)

        # Feed previous-month values into the chart for ghost polygon
        if isinstance(previous, dict):
            prev_values = {
                "reading": int(previous.get("reading", 0)),
                "listening": int(previous.get("listening", 0)),
                "speaking": int(previous.get("speaking", 0)),
                "writing": int(previous.get("writing", 0)),
            }
            self.chart.set_previous_values(prev_values)
        else:
            self.chart.set_previous_values(None)
        arrows = {"up": "↑", "down": "↓", "same": "="}
        parts = []
        for label, key in [
            ("Reading", "reading"),
            ("Listening", "listening"),
            ("Speaking", "speaking"),
            ("Writing", "writing"),
        ]:
            t = trends.get(key, "same")
            arrow = arrows.get(t, "=")
            parts.append(f"{label} {arrow}")
        self.trend_label.setText(" | ".join(parts))

    def _update_banner(self) -> None:
        days = get_days_since_last_snapshot()
        # Show the reminder inline with the Balance Index text so it
        # appears on the same row in the dashboard.
        base = self.balance_label.text()

        if days is None or days <= 30:
            # Keep only the balance text, clear any previous reminder.
            self.balance_label.setText(base)
            self.reminder_label.setText("")
        else:
            self.balance_label.setText(
                f"{base} — Your last snapshot is {days} days old. Update now?"
            )
            # No separate reminder row for now.
            self.reminder_label.setText("")
