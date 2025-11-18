from __future__ import annotations

from datetime import datetime
from typing import Optional

from aqt.qt import Qt, QVBoxLayout, QLabel, QTabWidget, QHBoxLayout, QWidget, QScrollArea

from .dashboard_view import DashboardView
from .radar_view import RadarView
from .tracker_view import TrackerView
from .goals_view import GoalsView
from .resources_view import ResourcesView
from ..core.storage import load_json, save_json


class FluencyForgeWindow(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.resize(900, 600)

        main_layout = QVBoxLayout(self)

        # Start directly with the tab bar inside a scroll area so tall
        # content (like the dashboard radar) doesn't push controls
        # off-screen.
        self.tabs = QTabWidget(self)
        self.dashboard_view = DashboardView(self)
        # Keep a RadarView instance for reuse, but do not expose it as a tab.
        self.radar_view = RadarView(self)
        self.tracker_view = TrackerView(self)
        self.goals_view = GoalsView(self)
        self.resources_view = ResourcesView(self)

        self.tabs.addTab(self.dashboard_view, "Dashboard")
        self.tabs.addTab(self.tracker_view, "Daily Tracker")
        self.tabs.addTab(self.goals_view, "Goals")
        self.tabs.addTab(self.resources_view, "Resources")

        # React to tab changes so we can refresh dashboard/goals views.
        self.tabs.currentChanged.connect(self._on_tab_changed)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        # Only vertical scrolling; keep width fixed to the dock.
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self.tabs)
        main_layout.addWidget(scroll)

        bottom = QHBoxLayout()
        self.status_label = QLabel("Ready")
        bottom.addWidget(self.status_label)
        main_layout.addLayout(bottom)

        # Always start on Dashboard tab (index 0)
        self.tabs.setCurrentIndex(0)

    def set_status(self, text: str) -> None:
        now = datetime.now().strftime("%H:%M")
        self.status_label.setText(f"{text} – {now}")

    def _restore_last_tab(self) -> None:
        # Behavior changed: we now always start on Dashboard, so this is a no-op.
        return

    def _on_tab_changed(self, index: int) -> None:
        # When switching tabs, refresh any views that cache data from disk.
        widget = self.tabs.widget(index)
        if widget is self.dashboard_view:
            if hasattr(self.dashboard_view, "refresh_goals_from_storage"):
                self.dashboard_view.refresh_goals_from_storage()
            if hasattr(self.dashboard_view, "refresh_resources_from_storage"):
                self.dashboard_view.refresh_resources_from_storage()
        elif widget is self.goals_view and hasattr(self.goals_view, "refresh_current_month"):
            self.goals_view.refresh_current_month()
        elif widget is self.tracker_view and hasattr(self.tracker_view, "refresh_from_storage"):
            self.tracker_view.refresh_from_storage()

    def show_radar_tab(self) -> None:
        index = self.tabs.indexOf(self.radar_view)
        if index != -1:
            self.tabs.setCurrentIndex(index)

    def show_tracker_tab(self) -> None:
        index = self.tabs.indexOf(self.tracker_view)
        if index != -1:
            self.tabs.setCurrentIndex(index)

    def show_goals_tab(self) -> None:
        index = self.tabs.indexOf(self.goals_view)
        if index != -1:
            self.tabs.setCurrentIndex(index)

    def show_resources_tab(self) -> None:
        index = self.tabs.indexOf(self.resources_view)
        if index != -1:
            self.tabs.setCurrentIndex(index)

    def show_resources_tab_and_select(self, index_row: int) -> None:
        self.show_resources_tab()
        if hasattr(self.resources_view, "select_row"):
            self.resources_view.select_row(index_row)
