from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
import webbrowser

from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    Qt,
    QCheckBox,
    QFont,
    QLineEdit,
    QProgressBar,
    QToolButton,
    QScrollArea,
)

from .radar_view import RadarView
from ..core.logic_tracker import load_daily_activity, save_daily_activity
from ..core.logic_dailyplan import load_daily_plan, save_daily_plan
from ..core.logic_goals import (
    load_goals_for_month,
    save_goals_for_month,
    get_current_month_id,
    auto_archive_past_goals,
)
from ..core.logic_resources import load_resources
from ..core.models import DailyPlan, MonthlyGoals
from .widgets import CircleIndicator, get_skill_emoji, get_skill_label


class DashboardView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Slightly larger base font for better readability, similar to decks view.
        base_font: QFont = self.font()
        if base_font.pointSize() > 0:
            base_font.setPointSize(base_font.pointSize() + 4)
            self.setFont(base_font)

        # Archive past goals once per session when the dashboard is created.
        auto_archive_past_goals(get_current_month_id())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        # Reduce spacing between section boxes so they appear closer together.
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self._create_radar_section())
        layout.addWidget(self._create_tracker_section())
        layout.addWidget(self._create_goals_section())
        layout.addWidget(self._create_resources_section())
        layout.addStretch(1)

        # Auto-start checkbox at the bottom of the dashboard
        footer = QHBoxLayout()
        footer.addStretch(1)
        self.auto_start_checkbox = QCheckBox(
            "Open FluencyForge automatically when Anki starts", self
        )
        # Initialize from DailyPlan
        plan: DailyPlan = load_daily_plan()
        self.auto_start_checkbox.setChecked(plan.show_on_startup)
        self.auto_start_checkbox.toggled.connect(self._on_auto_start_toggled)
        footer.addWidget(self.auto_start_checkbox)
        layout.addLayout(footer)

    # helpers to reach main window and tabs
    def _main_window(self):
        w = self.parent()
        # Walk up the parents until we find the FluencyForge main window,
        # identified by its tab navigation helpers (e.g. show_goals_tab).
        while w is not None and not hasattr(w, "show_goals_tab"):
            w = w.parent()
        return w

    def _create_section_frame(self, title: str) -> QFrame:
        frame = QFrame(self)
        try:
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setFrameShadow(QFrame.Shadow.Raised)
        except AttributeError:
            frame.setFrameShape(QFrame.StyledPanel)  # type: ignore[attr-defined]
            frame.setFrameShadow(QFrame.Raised)  # type: ignore[attr-defined]
        v = QVBoxLayout(frame)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)
        header = QLabel(f"<b>{title}</b>")
        v.addWidget(header)
        return frame

    # RADAR PREVIEW (Fluency Snapshot)
    def _create_radar_section(self) -> QFrame:
        """Show the full interactive RadarView directly on the dashboard."""

        frame = self._create_section_frame("Fluency Snapshot")
        layout = frame.layout()  # type: ignore[assignment]

        radar = RadarView(self)
        layout.addWidget(radar)

        return frame

    # WEEKLY TRACKER PREVIEW + DAILY PLAN
    def _create_tracker_section(self) -> QFrame:
        frame = self._create_section_frame("This Week's Activity")
        layout = frame.layout()  # type: ignore[assignment]

        activity = load_daily_activity()
        skills = ["reading", "listening", "speaking", "writing"]

        # Load current daily plan (4 generic tasks) to show alongside tracker.
        plan: DailyPlan = load_daily_plan()

        today = date.today()
        start = today - timedelta(days=today.weekday())  # Monday

        # Grid: row 0 = headers, rows 1-4 = skills
        grid_container = QWidget(self)
        grid = QGridLayout(grid_container)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        # Empty corner cell
        corner = QLabel("")
        grid.addWidget(corner, 0, 0)

        # Day headers, highlight today's weekday by drawing a circle around it.
        weekday_index = today.weekday()  # Monday=0 .. Sunday=6
        for idx, label in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            col = idx + 1
            day_label = QLabel(label)
            day_label.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
            )
            if idx == weekday_index:
                day_label.setStyleSheet(
                    "QLabel {"
                    " border: 1px solid #7CC9A3;"
                    " border-radius: 10px;"
                    " padding: 1px 4px;"
                    " }"
                )
            grid.addWidget(day_label, 0, col)

        # Daily Plan header + today's date aligned with day headers (same row, right side).
        daily_plan_header = QLabel("<b>Daily Plan</b>")
        today_label = QLabel(today.strftime("%A, %d %B %Y"))
        today_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        dp_header_widget = QWidget(self)
        dp_header_layout = QHBoxLayout(dp_header_widget)
        dp_header_layout.setContentsMargins(0, 0, 0, 0)
        dp_header_layout.setSpacing(6)
        dp_header_layout.addWidget(daily_plan_header)
        dp_header_layout.addStretch(1)
        dp_header_layout.addWidget(today_label)
        grid.addWidget(dp_header_widget, 0, 8)

        active_days = 0
        total_days = 7

        # Prepare inline Daily Plan edits aligned with skill rows.
        self._daily_plan_edits: list[QLineEdit] = []

        # Helper to recompute weekly consistency label based on current activity.
        def update_consistency_label() -> None:
            # Count how many days in the current week have at least one skill done.
            active = 0
            for offset in range(7):
                day = start + timedelta(days=offset)
                day_str = day.strftime("%Y-%m-%d")
                day_data = activity.get(day_str, {})
                if any(bool(day_data.get(sk, False)) for sk in skills):
                    active += 1
            percent = int(100 * active / total_days) if total_days else 0
            consistency_label.setText(
                f"This Week: {percent}% consistency — {active} active days"
            )

        for row, skill in enumerate(skills, start=1):
            emoji = get_skill_emoji(skill)
            skill_label = QLabel(emoji)
            skill_label.setAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            skill_label.setToolTip(get_skill_label(skill))
            skill_label.setMinimumWidth(40)
            grid.addWidget(skill_label, row, 0)

            any_active_row = False
            for col in range(7):
                day = start + timedelta(days=col)
                day_str = day.strftime("%Y-%m-%d")
                day_data = activity.get(day_str, {})
                done = bool(day_data.get(skill, False))
                indicator = CircleIndicator(done, size=16, parent=grid_container)

                def make_handler(d, s, w):
                    def _on_clicked():
                        day_s = d.strftime("%Y-%m-%d")
                        day_data_inner = activity.setdefault(
                            day_s, {sk: False for sk in skills}
                        )
                        new_val = not bool(day_data_inner.get(s, False))
                        day_data_inner[s] = new_val
                        save_daily_activity(activity)
                        w.set_completed(new_val)
                        status_label.setText(
                            f"Updated: {get_skill_label(s)} on {d.strftime('%a %d %b')}"
                        )
                        update_consistency_label()

                    return _on_clicked

                indicator.clicked.connect(make_handler(day, skill, indicator))
                grid.addWidget(indicator, row, col + 1)
                if done:
                    any_active_row = True

            # Daily Plan task for this skill row (Task 1-4)
            if row - 1 < 4:
                edit = QLineEdit(self)
                edit.setStyleSheet(
                    "QLineEdit {"
                    " border: none;"
                    " background-color: rgba(0, 0, 0, 0);"
                    " padding: 2px 4px;"
                    " }"
                )
                edit.setPlaceholderText(f"Task {row}")
                text = plan.tasks[row - 1] if row - 1 < len(plan.tasks) else ""
                edit.setText(text)
                grid.addWidget(edit, row, 8)
                self._daily_plan_edits.append(edit)
            if any_active_row:
                active_days += 1

        # Add the combined tracker + daily plan grid directly.
        layout.addWidget(grid_container)

        # Consistency label that will be updated dynamically.
        consistency_label = QLabel("", self)
        layout.addWidget(consistency_label)
        update_consistency_label()

        status_label = QLabel("", self)
        layout.addWidget(status_label)

        # Buttons row: tracker button on the left, daily plan save on the right.
        button_row = QHBoxLayout()
        tracker_btn = QPushButton("View Full Tracker", self)
        tracker_btn.clicked.connect(self._go_tracker)
        button_row.addWidget(tracker_btn)
        button_row.addStretch(1)
        save_btn = QPushButton("Save Daily Plan", self)
        save_btn.clicked.connect(self._on_save_daily_plan)
        button_row.addWidget(save_btn)
        layout.addLayout(button_row)

        return frame

    def _on_save_daily_plan(self) -> None:
        """Persist the four inline Daily Plan tasks to storage."""

        plan = load_daily_plan()
        tasks: list[str] = [e.text() for e in getattr(self, "_daily_plan_edits", [])]
        # Ensure exactly four entries
        while len(tasks) < 4:
            tasks.append("")
        if len(tasks) > 4:
            tasks = tasks[:4]

        updated = DailyPlan(tasks=tasks, show_on_startup=plan.show_on_startup)
        save_daily_plan(updated)

    # GOALS PREVIEW
    def _create_goals_section(self) -> QFrame:
        frame = self._create_section_frame("This Month's Goals")
        layout = frame.layout()  # type: ignore[assignment]

        # Store current month and goals for dashboard interactions.
        self._goals_month_id: str = get_current_month_id()
        self._dashboard_goals: MonthlyGoals = load_goals_for_month(self._goals_month_id)

        # Mini goal cards
        cards_layout = QVBoxLayout()
        # Make the goals stack more compact vertically.
        cards_layout.setSpacing(2)
        self._goal_edits_dash: list[QLineEdit] = []
        self._goal_checks_dash: list[QCheckBox] = []
        # CircleIndicators used as the visual completion control; we still
        # keep a QCheckBox per goal for logic and persistence.
        self._goal_state_indicators: list[CircleIndicator] = []

        for idx in range(3):
            card = QFrame(self)
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card.setFrameShadow(QFrame.Shadow.Plain)
            # Slightly tighter padding so the goals box is more compact, and
            # a subtle background to host the inline goal controls.
            card.setStyleSheet(
                "QFrame { border-radius: 4px; padding: 1px; "
                "background-color: rgba(0, 0, 0, 0); }"
            )

            row = QHBoxLayout(card)
            # Reduce internal margins and spacing further to save vertical space.
            row.setContentsMargins(1, 0, 1, 0)
            row.setSpacing(1)

            # CircleIndicator for visual completion (same widget as weekly
            # tracker), plus a hidden checkbox for existing logic.
            state_indicator = CircleIndicator(False, size=16, parent=card)
            row.addWidget(state_indicator)

            check = QCheckBox(card)
            check.setTristate(False)
            # Hide the built-in checkbox indicator; CircleIndicator is the
            # visible control.
            check.setStyleSheet(
                "QCheckBox::indicator { width: 0px; height: 0px; "
                "border: none; background-color: transparent; }"
            )
            row.addWidget(check)

            edit = QLineEdit(card)
            edit.setPlaceholderText("Set your goal…")
            edit.setClearButtonEnabled(False)
            # Borderless text, sitting directly on the card background.
            edit.setStyleSheet(
                "QLineEdit {"
                " border: none;"
                " background-color: rgba(0, 0, 0, 0);"
                " padding: 2px 4px;"
                " }"
            )
            row.addWidget(edit, 1)

            # Pencil button to jump to Goals tab and focus this goal
            pencil = QToolButton(card)
            pencil.setText("✎")
            pencil.setToolTip("Open full Goals view for this goal")
            pencil.clicked.connect(lambda _=False, i=idx: self._open_goal_in_goals_tab(i))
            row.addWidget(pencil)

            cards_layout.addWidget(card)

            self._goal_state_indicators.append(state_indicator)
            self._goal_checks_dash.append(check)
            self._goal_edits_dash.append(edit)

            # Populate initial values
            text = (
                self._dashboard_goals.goals[idx]
                if idx < len(self._dashboard_goals.goals)
                else ""
            )
            completed = (
                self._dashboard_goals.completed[idx]
                if idx < len(self._dashboard_goals.completed)
                else False
            )
            edit.setText(text)
            check.setChecked(completed)
            state_indicator.set_completed(completed)

            # Wire interactions: clicking the circle toggles the hidden
            # checkbox, which then drives the save logic.
            check.toggled.connect(
                lambda checked, i=idx: self._on_dashboard_goal_checked(i, checked)
            )
            state_indicator.clicked.connect(lambda _=False, c=check: c.toggle())
            edit.editingFinished.connect(
                lambda i=idx: self._on_dashboard_goal_edited(i)
            )

        layout.addLayout(cards_layout)

        # Progress bar and label
        self._goals_progress_label = QLabel("", self)
        layout.addWidget(self._goals_progress_label)

        self._goals_progress_bar = QProgressBar(self)
        self._goals_progress_bar.setRange(0, 3)
        self._goals_progress_bar.setTextVisible(False)
        self._goals_progress_bar.setFixedHeight(10)
        # Neutral style by default; color updated in
        # _refresh_dashboard_goals_progress.
        self._goals_progress_bar.setStyleSheet("")
        layout.addWidget(self._goals_progress_bar)

        self._refresh_dashboard_goals_progress()
        self._refresh_dashboard_goal_colors()

        return frame

    # RESOURCES PREVIEW
    def _create_resources_section(self) -> QFrame:
        frame = self._create_section_frame("Resources")
        layout = frame.layout()  # type: ignore[assignment]

        # Container widget + scroll area so only ~2 resources are visible and
        # the rest can be scrolled.
        resources_container = QWidget(self)
        self._resources_rows_layout = QVBoxLayout(resources_container)
        self._resources_rows_layout.setContentsMargins(0, 0, 0, 0)
        self._resources_rows_layout.setSpacing(4)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        # Transparent background so the scroll area blends with the addon.
        scroll.setStyleSheet(
            "QScrollArea { background-color: transparent; border: none; }"
            "QScrollArea > QWidget > QWidget { background-color: transparent; }"
        )
        # Fixed height so that roughly two resource rows are visible.
        scroll.setFixedHeight(70)
        scroll.setWidget(resources_container)

        layout.addWidget(scroll)

        self._populate_resources_preview()

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        btn = QPushButton("View All Resources", self)
        btn.clicked.connect(self._go_resources)
        button_row.addWidget(btn)
        layout.addLayout(button_row)

        return frame

    def _populate_resources_preview(self) -> None:
        """Populate the dashboard's mini resources list from storage."""

        rows_layout = getattr(self, "_resources_rows_layout", None)
        if rows_layout is None:
            return

        # Clear existing row layouts/widgets.
        while rows_layout.count():
            item = rows_layout.takeAt(0)
            inner = item.layout()
            w = item.widget()
            if inner is not None:
                while inner.count():
                    child_item = inner.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget is not None:
                        child_widget.deleteLater()
            if w is not None:
                w.deleteLater()

        raw = load_resources()
        items: List[Dict] = raw

        if not items:
            rows_layout.addWidget(QLabel("No resources added yet"))
            return

        for idx, obj in enumerate(items):
            row = QHBoxLayout()
            type_label = QLabel(str(obj.get("type", "")))
            name_label = QLabel(str(obj.get("name", "")))
            name_label.setWordWrap(True)
            row.addWidget(type_label)
            row.addWidget(name_label, 1)

            btn = QPushButton("Open", self)
            btn.clicked.connect(lambda _=False, i=idx: self._go_resource(i))
            row.addWidget(btn)

            rows_layout.addLayout(row)

    def refresh_resources_from_storage(self) -> None:
        """Public hook: refresh the dashboard Resources preview from disk."""

        self._populate_resources_preview()

    # navigation helpers
    def _go_tracker(self) -> None:
        mw = self._main_window()
        if mw is not None and hasattr(mw, "show_tracker_tab"):
            mw.show_tracker_tab()

    def _go_daily_plan(self) -> None:
        mw = self._main_window()
        if mw is not None and hasattr(mw, "show_daily_plan_tab"):
            mw.show_daily_plan_tab()

    def _go_goals(self) -> None:
        mw = self._main_window()
        if mw is not None and hasattr(mw, "show_goals_tab"):
            mw.show_goals_tab()

    def _go_resources(self) -> None:
        mw = self._main_window()
        if mw is not None and hasattr(mw, "show_resources_tab"):
            mw.show_resources_tab()

    def _go_resource(self, index: int) -> None:
        """Open the Resources tab, select the resource, and open its link."""

        # Try to open the link in the system browser first.
        try:
            raw = load_resources()
            if 0 <= index < len(raw):
                link = str(raw[index].get("link", "") or "").strip()
                if link:
                    webbrowser.open(link)
        except Exception:
            # Fail silently if anything goes wrong with loading or opening.
            pass

        # Also navigate to the Resources tab and select the item, as before.
        mw = self._main_window()
        if mw is not None and hasattr(mw, "show_resources_tab_and_select"):
            mw.show_resources_tab_and_select(index)

    # dashboard goals helpers

    def _refresh_dashboard_goals_progress(self) -> None:
        goals = self._dashboard_goals.goals
        completed_flags = self._dashboard_goals.completed

        total_defined = sum(1 for g in goals if g.strip())
        total_defined = max(total_defined, 1)

        done = 0
        for idx, g in enumerate(goals):
            if g.strip() and idx < len(completed_flags) and completed_flags[idx]:
                done += 1

        percent = round(done / total_defined * 100)
        self._goals_progress_label.setText(
            f"{done} / 3 goals completed — {percent}%"
        )
        self._goals_progress_bar.setValue(done)

        # Match progress bar color to the green state indicator while keeping
        # the background transparent and corners rounded so it blends with the
        # addon UI.
        base_style = (
            "QProgressBar {"
            " background-color: transparent;"
            " border: 0px;"
            " border-radius: 5px;"
            " }"
            "QProgressBar::chunk {"
            " background-color: #7CC9A3;"
            " border-radius: 5px;"
            " }"
        )
        self._goals_progress_bar.setStyleSheet(base_style)

    def _refresh_dashboard_goal_colors(self) -> None:
        """Sync CircleIndicators used as completion controls with goal state."""

        goals = self._dashboard_goals
        for i in range(3):
            done = goals.completed[i] if i < len(goals.completed) else False
            if i < len(self._goal_state_indicators):
                self._goal_state_indicators[i].set_completed(done)

    def _update_dashboard_goals_from_widgets(self) -> None:
        texts: list[str] = [e.text() for e in self._goal_edits_dash]
        checks: list[bool] = [c.isChecked() for c in self._goal_checks_dash]

        # Ensure lists have exactly 3 entries
        while len(texts) < 3:
            texts.append("")
        while len(checks) < 3:
            checks.append(False)

        self._dashboard_goals.goals = texts[:3]
        self._dashboard_goals.completed = checks[:3]

        save_goals_for_month(self._dashboard_goals, source="dashboard_view")
        self._refresh_dashboard_goals_progress()
        self._refresh_dashboard_goal_colors()

    def _open_goal_in_goals_tab(self, goal_index: int) -> None:
        """Switch to the Goals tab and expand the selected goal card."""

        mw = self._main_window()
        if mw is None or not hasattr(mw, "show_goals_tab"):
            return

        # Switch to Goals tab
        mw.show_goals_tab()

        # Ask the GoalsView to refresh and expand the given goal index
        if hasattr(mw, "goals_view") and hasattr(mw.goals_view, "focus_goal_index"):
            mw.goals_view.focus_goal_index(goal_index)

    def refresh_goals_from_storage(self) -> None:
        """Reload current month's goals from storage into mini-cards."""

        self._goals_month_id = get_current_month_id()
        self._dashboard_goals = load_goals_for_month(self._goals_month_id)

        for idx in range(3):
            text = (
                self._dashboard_goals.goals[idx]
                if idx < len(self._dashboard_goals.goals)
                else ""
            )
            completed = (
                self._dashboard_goals.completed[idx]
                if idx < len(self._dashboard_goals.completed)
                else False
            )
            if idx < len(self._goal_edits_dash):
                self._goal_edits_dash[idx].setText(text)
            if idx < len(self._goal_checks_dash):
                self._goal_checks_dash[idx].setChecked(completed)

        self._refresh_dashboard_goals_progress()
        self._refresh_dashboard_goal_colors()

    def _on_dashboard_goal_checked(self, index: int, checked: bool) -> None:
        if index < len(self._goal_checks_dash):
            self._goal_checks_dash[index].setChecked(checked)
        self._update_dashboard_goals_from_widgets()

    def _on_dashboard_goal_edited(self, index: int) -> None:
        # Editing finished on a card; update and persist.
        self._update_dashboard_goals_from_widgets()

    def _on_auto_start_toggled(self, checked: bool) -> None:
        """Persist the auto-start setting in the DailyPlan model."""

        current = load_daily_plan()
        plan = DailyPlan(tasks=list(current.tasks), show_on_startup=checked)
        save_daily_plan(plan)
