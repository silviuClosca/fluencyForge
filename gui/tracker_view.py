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

        self.mode_label = QLabel("Daily Tracker – Monthly View", self)
        layout.addWidget(self.mode_label)

        # Monthly view only
        monthly_container = QWidget(self)
        monthly_layout = QVBoxLayout(monthly_container)

        top = QHBoxLayout()
        top.addWidget(QLabel("Month"))
        self.month_combo = QComboBox(self)
        top.addWidget(self.month_combo)
        monthly_layout.addLayout(top)

        # Monthly grid: layout-based (no table), similar to weekly dashboard preview.
        self.grid_container = QWidget(self)
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        # Slightly tighter horizontal spacing so emoji column sits closer to circles.
        self.grid_layout.setHorizontalSpacing(4)
        self.grid_layout.setVerticalSpacing(6)
        # Column 0 (emoji) should stay narrow; remaining columns get the space.
        self.grid_layout.setColumnStretch(0, 0)
        monthly_layout.addWidget(self.grid_container)

        # Legend under the table
        legend_layout = QHBoxLayout()
        for skill in self.skills:
            emoji = get_skill_emoji(skill)
            label = get_skill_label(skill)
            item = QLabel(f"{emoji} {label}", self)
            legend_layout.addWidget(item)
        legend_layout.addStretch(1)
        monthly_layout.addLayout(legend_layout)

        self.month_stats_label = QLabel("", self)
        monthly_layout.addWidget(self.month_stats_label)

        layout.addWidget(monthly_container)

        # Init data
        self._populate_months()
        self.month_combo.currentTextChanged.connect(self._on_month_changed)

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

        # Clear previous grid contents
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        # Helper to add a band of consecutive days starting at start_day.
        # Returns the next free row index after the band.
        def add_band(start_day: int, count: int, base_row: int) -> int:
            if count <= 0:
                return base_row

            # Empty corner for this band
            self.grid_layout.addWidget(QLabel("", self.grid_container), base_row, 0)

            # Day headers
            for col in range(count):
                day_num = start_day + col
                header = QLabel(str(day_num), self.grid_container)
                header.setAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                self.grid_layout.addWidget(header, base_row, col + 1)

            # Skill icons and circles
            for offset_row, skill in enumerate(self.skills, start=1):
                row = base_row + offset_row
                emoji_label = QLabel(get_skill_emoji(skill), self.grid_container)
                emoji_label.setAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                )
                emoji_label.setFixedWidth(18)
                self.grid_layout.addWidget(emoji_label, row, 0)

                for col in range(count):
                    day_num = start_day + col
                    day_str = date(year, month_num, day_num).strftime("%Y-%m-%d")
                    day_data = self.activity.get(day_str, {})
                    done = bool(day_data.get(skill, False))
                    indicator = CircleIndicator(
                        done, size=18, parent=self.grid_container
                    )

                    def make_handler(d_str: str, s: str, w: CircleIndicator) -> None:
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
                    self.grid_layout.addWidget(indicator, row, col + 1)

            return base_row + 1 + len(self.skills)

        # First band: days 1–16 (or fewer if month shorter)
        first_band_days = min(16, days_in_month)
        next_row = add_band(1, first_band_days, 0)

        # Second band: remaining days 17–end
        remaining = days_in_month - 16
        if remaining > 0:
            # Add a small gap row between bands for visual separation
            next_row += 1
            add_band(17, remaining, next_row)

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

        text = (
            f"Active days: {active_days} / {days_in_month} | "
            f"Longest streak: {longest_streak} days | "
            + ", ".join(f"{s.capitalize()}: {per_skill_pct[s]}%" for s in self.skills)
        )
        self.month_stats_label.setText(text)

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
