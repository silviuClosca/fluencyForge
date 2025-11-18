from __future__ import annotations

from datetime import date, datetime
from calendar import monthrange
from typing import Optional

from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    Qt,
    QGridLayout,
    QSizePolicy,
    QFrame,
)

from ..core.logic_tracker import load_daily_activity, save_daily_activity
from ..core.models import DailyActivity
from .widgets import CircleIndicator, get_skill_emoji, get_skill_label


class TrackerView(QWidget):
    skills = ["reading", "listening", "speaking", "writing"]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.activity: DailyActivity = load_daily_activity()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # We no longer show a separate heading text; the Month selector row
        # acts as the visual header for this view.
        self.mode_label = QLabel("", self)
        self.mode_label.setVisible(False)

        # Monthly view only
        monthly_container = QWidget(self)
        monthly_layout = QVBoxLayout(monthly_container)

        # Header row: "Month" label and a compact combo box, packed together
        # and anchored to the left.
        header = QWidget(self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        header_layout.addWidget(QLabel("Month", header))
        self.month_combo = QComboBox(header)
        # Keep the month selector compact: size to its text + arrow only.
        self.month_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
        self.month_combo.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        header_layout.addWidget(self.month_combo)

        monthly_layout.addWidget(header)
        monthly_layout.setAlignment(header, Qt.AlignmentFlag.AlignLeft)

        # Main content row: monthly grid on the left, analytics summary card on
        # the right.
        content_row = QHBoxLayout()

        # Monthly grid container: a vertical stack of week "cards", each with
        # its own compact inner grid.
        self.grid_container = QWidget(self)
        self.grid_container.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.grid_layout = QVBoxLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(6)
        content_row.addWidget(self.grid_container)

        # Right column: analytics summary card (multi-line text) with a soft
        # background and rounded corners. The meaning of each emoji is shown
        # directly in the grid's left column, so we only need this single
        # summary card on the side.
        side_column = QVBoxLayout()

        stats_card = QFrame(self)
        stats_card.setFrameShape(QFrame.Shape.NoFrame)
        stats_card.setFrameShadow(QFrame.Shadow.Plain)
        stats_card.setStyleSheet(
            "QFrame {"
            "  background-color: rgba(148, 163, 184, 30);"  # soft slate tint
            "  border-radius: 8px;"
            "  border: 1px solid rgba(15, 23, 42, 40);"      # subtle border/shadow
            "}"
        )
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(2, 2, 2, 2)
        stats_layout.setSpacing(2)

        self.month_stats_label = QLabel("", stats_card)
        stats_layout.addWidget(self.month_stats_label)

        side_column.addWidget(stats_card)
        side_column.addStretch(1)

        content_row.addLayout(side_column)
        monthly_layout.addLayout(content_row)

        layout.addWidget(monthly_container)

        # Init data
        self._populate_months()
        self.month_combo.currentTextChanged.connect(self._on_month_changed)

        self._load_month()

    def refresh_from_storage(self) -> None:
        """Reload daily activity from storage and refresh the current month view."""

        self.activity = load_daily_activity()
        # Rebuild the month list (in case new months were added) and keep
        # the currently selected month when possible.
        current = self.month_combo.currentText() or self._current_month_str()
        self._populate_months()
        idx = self.month_combo.findText(current)
        if idx >= 0:
            self.month_combo.setCurrentIndex(idx)
        self._load_month()

    # --------------------
    # Monthly helpers
    # --------------------
    def _current_month_str(self) -> str:
        return datetime.now().strftime("%Y-%m")

    def _populate_months(self) -> None:
        current = self._current_month_str()
        current_year = current.split("-")[0]

        # Start with all months of the current year.
        months = {f"{current_year}-{m:02d}" for m in range(1, 13)}

        # Add any additional months that exist in the activity data.
        for d in self.activity.keys():
            months.add(d[:7])

        self.month_combo.clear()
        for m in sorted(months):
            self.month_combo.addItem(m)

        index = self.month_combo.findText(current)
        if index >= 0:
            self.month_combo.setCurrentIndex(index)

    def _on_month_changed(self, _text: str) -> None:
        self._load_month()

    def _load_month(self) -> None:
        month = self.month_combo.currentText() or self._current_month_str()
        year, month_num = map(int, month.split("-"))
        days_in_month = monthrange(year, month_num)[1]
        today = date.today()

        # Clear previous grid contents
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        # Calendar-style layout by weeks: columns = Mon–Sun, rows = weeks.
        # Compute weekday of the first of the month (0=Monday .. 6=Sunday).
        first_weekday, _ = monthrange(year, month_num)

        # Build a vertical stack of week cards. Each card has its own compact
        # grid: header row of day numbers + one row per skill.
        week_index = 0
        while True:
            # Determine if this week has any days in the current month. If not,
            # we stop creating further week cards.
            has_days = False
            for col in range(7):
                calendar_index = week_index * 7 + col
                day_num = calendar_index - first_weekday + 1
                if 1 <= day_num <= days_in_month:
                    has_days = True
                    break
            if not has_days:
                break

            week_card = QFrame(self.grid_container)
            week_card.setFrameShape(QFrame.Shape.NoFrame)
            week_card.setFrameShadow(QFrame.Shadow.Plain)
            week_card.setStyleSheet(
                "QFrame {"
                "  background-color: rgba(148, 163, 184, 10);"
                "  border-radius: 6px;"
                "  border: 1px solid rgba(148, 163, 184, 80);"
                "}"
            )
            week_layout = QGridLayout(week_card)
            week_layout.setContentsMargins(8, 1, 8, 1)
            week_layout.setHorizontalSpacing(12)
            # Tighter vertical spacing so skill rows sit closer together while
            # remaining readable.
            week_layout.setVerticalSpacing(0)

            # Header row for this week: compact day numbers above each column.
            for col in range(7):
                calendar_index = week_index * 7 + col
                day_num = calendar_index - first_weekday + 1

                header = QLabel("", week_card)
                header.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header.setContentsMargins(0, 0, 0, 0)
                # Slightly taller so the highlight border around today's day
                # number is not clipped vertically.
                header.setFixedHeight(18)
                if 1 <= day_num <= days_in_month:
                    header.setText(str(day_num))

                    # Highlight today's date in the monthly tracker so it is
                    # easy to spot at a glance.
                    if (
                        year == today.year
                        and month_num == today.month
                        and day_num == today.day
                    ):
                        header.setStyleSheet(
                            "QLabel {"
                            " border: 1px solid #7CC9A3;"
                            " border-radius: 8px;"
                            " padding: 1px 4px;"
                            " background-color: rgba(190, 234, 211, 80);"
                            " }"
                        )
                    else:
                        # All other days stay clean text-only.
                        header.setStyleSheet(
                            "QLabel { background: transparent; border: none; }"
                        )
                else:
                    # Empty cells have no styling.
                    header.setStyleSheet(
                        "QLabel { background: transparent; border: none; }"
                    )
                week_layout.addWidget(header, 0, col + 1)

            # Skill rows for this week.
            for offset_row, skill in enumerate(self.skills, start=1):
                row = offset_row

                # Emoji + label in column 0 for this skill/week, so users can
                # read the meaning without a separate legend.
                emoji = get_skill_emoji(skill)
                skill_name = get_skill_label(skill)
                emoji_label = QLabel(f"{emoji} {skill_name}", week_card)
                emoji_label.setAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                )
                emoji_label.setMinimumWidth(80)
                # Strip any inherited background/border so labels stay clean
                # and text-only inside the week card.
                emoji_label.setStyleSheet(
                    "QLabel { background: transparent; border: none; }"
                )
                week_layout.addWidget(emoji_label, row, 0)

                # Circles for each day of this week.
                for col in range(7):
                    calendar_index = week_index * 7 + col
                    day_num = calendar_index - first_weekday + 1

                    if day_num < 1 or day_num > days_in_month:
                        continue

                    day_str = date(year, month_num, day_num).strftime("%Y-%m-%d")
                    day_data = self.activity.get(day_str, {})
                    done = bool(day_data.get(skill, False))
                    # Slightly smaller circles so the monthly rows sit tighter
                    # together vertically.
                    indicator = CircleIndicator(
                        done, size=16, parent=week_card
                    )

                    def make_handler(
                        d_str: str, s: str, w: CircleIndicator
                    ) -> None:
                        def _on_clicked() -> None:
                            day_data_inner = self.activity.setdefault(
                                d_str, {sk: False for sk in self.skills}
                            )
                            new_val = not bool(day_data_inner.get(s, False))
                            day_data_inner[s] = new_val
                            save_daily_activity(self.activity)
                            w.set_completed(new_val)
                            self._update_month_stats()

                        return _on_clicked

                    indicator.clicked.connect(make_handler(day_str, skill, indicator))
                    week_layout.addWidget(indicator, row, col + 1)

            self.grid_layout.addWidget(week_card)
            week_index += 1

        self._update_month_stats()

    def _update_month_stats(self) -> None:
        month = self.month_combo.currentText() or self._current_month_str()
        year, month_num = map(int, month.split("-"))
        days_in_month = monthrange(year, month_num)[1]

        active_days = 0
        longest_streak = 0
        current_streak = 0
        per_skill_counts = {s: 0 for s in self.skills}

        for day in range(1, days_in_month + 1):
            day_str = date(year, month_num, day).strftime("%Y-%m-%d")
            day_data = self.activity.get(day_str, {})
            any_active = any(bool(day_data.get(s, False)) for s in self.skills)
            if any_active:
                active_days += 1
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0
            for s in self.skills:
                if bool(day_data.get(s, False)):
                    per_skill_counts[s] += 1

        if days_in_month == 0:
            days_in_month = 1
        per_skill_pct = {
            s: int(100 * per_skill_counts[s] / days_in_month) for s in self.skills
        }

        lines = [
            f"Active days: {active_days} / {days_in_month}",
            f"Longest streak: {longest_streak} days",
        ]
        lines.extend(
            f"{s.capitalize()}: {per_skill_pct[s]}%" for s in self.skills
        )
        self.month_stats_label.setText("\n".join(lines))

    # --------------------
    # View toggle
    # --------------------
    def _on_toggle_view(self) -> None:
        if self.stack.currentIndex() == 0:
            # switch to monthly
            self.stack.setCurrentIndex(1)
            self.mode_label.setText("Daily Tracker – Monthly View")
            self.toggle_view_btn.setText("Switch to Weekly View")
        else:
            # switch to weekly
            self.stack.setCurrentIndex(0)
            self.mode_label.setText("Daily Tracker – Weekly View")
            self.toggle_view_btn.setText("Switch to Monthly View")
