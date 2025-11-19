from __future__ import annotations

from datetime import datetime
from typing import Optional

from aqt import mw
from aqt.qt import (
    Qt,
    QVBoxLayout,
    QLabel,
    QTabWidget,
    QHBoxLayout,
    QWidget,
    QScrollArea,
    QToolButton,
    QStyle,
    QDockWidget,
)

from .dashboard_view import DashboardView
from .radar_view import RadarView
from .tracker_view import TrackerView
from .goals_view import GoalsView
from .resources_view import ResourcesView
from .settings_view import SettingsView
from ..core.logic_settings import load_settings, Settings
from ..core.themes import get_theme_colors, ThemeColors


class LanguageForgeWindow(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("LanguageForge")
        self.resize(900, 700)

        # Set object name for styling
        self.setObjectName("languageforge_main")
        
        # Prevent Anki's stylesheet from affecting our widgets
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.resize(900, 600)

        main_layout = QVBoxLayout(self)
        # Remove outer margins so the tab bar sits flush with the top edge of
        # the dock, matching Anki's own top button row.
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Settings/state
        self._settings: Settings = load_settings()
        # Remember the initial base font size so Small/Medium/Large can be
        # applied symmetrically regardless of how many times the user toggles.
        initial_font = self.font()
        self._base_font_size = initial_font.pointSize() or 10
        
        # Theme colors
        self._current_theme_colors: ThemeColors = self._get_current_theme_colors()

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
        self.settings_view = SettingsView(
            self, apply_theme_callback=self._on_settings_changed
        )

        self.tabs.addTab(self.dashboard_view, "Dashboard")
        self.tabs.addTab(self.tracker_view, "Tracker")
        self.tabs.addTab(self.goals_view, "Goals")
        self.tabs.addTab(self.resources_view, "Resources")
        self.tabs.addTab(self.settings_view, "Settings")

        # Initial tab styling and theme based on current Anki theme.
        self._apply_tab_styles()
        self._apply_font_size()
        self._apply_theme_to_all_views()

        # Inline window controls aligned with the tab bar: pop-out and close.
        controls = QWidget(self)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(4)

        self.popout_button = QToolButton(controls)
        self.popout_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
        )
        self.popout_button.setToolTip("Pop out FluencyForge window")
        self.popout_button.clicked.connect(self._on_popout_clicked)
        controls_layout.addWidget(self.popout_button)

        self.close_button = QToolButton(controls)
        self.close_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        )
        self.close_button.setToolTip("Close FluencyForge")
        self.close_button.clicked.connect(self._on_close_clicked)
        controls_layout.addWidget(self.close_button)

        self.tabs.setCornerWidget(controls, Qt.Corner.TopRightCorner)

        # React to tab changes so we can refresh dashboard/goals views.
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self._scroll = QScrollArea(self)
        scroll = self._scroll
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setObjectName("languageforge_scroll")
        # Allow horizontal scrolling when needed so larger font sizes don't
        # cause the right edge of the UI to be clipped.
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Anchor content to the top-right inside the scroll area. When the
        # content becomes wider than the dock, the extra space is placed on
        # the left so the right edge (buttons, etc.) stays visible.
        scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
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
        # When switching tabs, refresh any views that cache data from disk and
        # re-apply tab styles in case the Anki theme changed.
        self._apply_tab_styles()
        widget = self.tabs.widget(index)
        if widget is self.dashboard_view:
            if hasattr(self.dashboard_view, "refresh_goals_from_storage"):
                self.dashboard_view.refresh_goals_from_storage()
            if hasattr(self.dashboard_view, "refresh_resources_from_storage"):
                self.dashboard_view.refresh_resources_from_storage()
            if hasattr(self.dashboard_view, "refresh_week_from_storage"):
                self.dashboard_view.refresh_week_from_storage()
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

    def _apply_font_size(self) -> None:
        """Apply the configured font size to the LanguageForge UI.

        We adjust the base font on the main window and propagate it to all
        children so that Dashboard/Tracker/Goals/Resources/Settings update
        immediately when the user changes the size in Settings.
        """

        font = self.font()
        base = self._base_font_size

        # New representation: a point size stored as a string (e.g. "11").
        # Fallback to legacy "scale_N" or small/medium/large values.
        raw = getattr(self._settings, "font_size", str(base))

        if isinstance(raw, str) and raw.isdigit():
            new_size = int(raw)
        elif isinstance(raw, str) and raw.startswith("scale_"):
            try:
                scale = int(raw.split("_", 1)[1])
            except ValueError:
                scale = 0
            new_size = base + scale
        else:
            legacy_map = {"small": base - 1, "medium": base, "large": base + 2}
            new_size = legacy_map.get(str(raw), base)

        new_size = max(6, min(24, new_size))
        font.setPointSize(new_size)

        self.setFont(font)
        for child in self.findChildren(QWidget):
            child.setFont(font)

        # After resizing fonts, keep the right edge of the content visible by
        # scrolling horizontally to the maximum extent if needed.
        scroll = getattr(self, "_scroll", None)
        if scroll is not None:
            hbar = scroll.horizontalScrollBar()
            if hbar is not None:
                hbar.setValue(hbar.maximum())

    def _get_current_theme_colors(self) -> ThemeColors:
        """Get the current theme colors based on settings and Anki state."""
        is_anki_dark = self._is_anki_dark_mode()
        return get_theme_colors(self._settings.theme, is_anki_dark)

    def _is_anki_dark_mode(self) -> bool:
        """Detect if Anki is currently in dark mode."""
        is_dark = False
        try:
            if hasattr(mw, "pm"):
                # night_mode() exists on older Anki; theme attribute on newer.
                if hasattr(mw.pm, "night_mode"):
                    is_dark = bool(mw.pm.night_mode())
                elif hasattr(mw.pm, "theme"):
                    theme = str(getattr(mw.pm, "theme", "")).lower()
                    is_dark = "dark" in theme or "night" in theme
        except Exception:
            is_dark = False
        return is_dark

    def _apply_tab_styles(self) -> None:
        """Style the tab bar and main window using current theme colors."""
        colors = self._current_theme_colors

        # Apply background color to the entire main window and all child widgets
        main_stylesheet = (
            f"QWidget#fluencyforge_main {{"
            f"  background-color: {colors.background};"
            f"  color: {colors.text};"
            f"}}"
            f"QWidget {{"
            f"  background-color: {colors.background};"
            f"  color: {colors.text};"
            f"}}"
            f"QLabel {{"
            f"  color: {colors.text};"
            f"  background-color: transparent;"
            f"}}"
            f"QScrollArea#fluencyforge_scroll {{"
            f"  background-color: {colors.background};"
            f"  border: none;"
            f"}}"
            f"QScrollBar:vertical {{"
            f"  background-color: {colors.background};"
            f"  width: 12px;"
            f"  border: none;"
            f"}}"
            f"QScrollBar::handle:vertical {{"
            f"  background-color: {colors.input_border};"
            f"  border-radius: 6px;"
            f"  min-height: 20px;"
            f"}}"
            f"QScrollBar::handle:vertical:hover {{"
            f"  background-color: {colors.accent};"
            f"}}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{"
            f"  height: 0px;"
            f"}}"
            f"QScrollBar:horizontal {{"
            f"  background-color: {colors.background};"
            f"  height: 12px;"
            f"  border: none;"
            f"}}"
            f"QScrollBar::handle:horizontal {{"
            f"  background-color: {colors.input_border};"
            f"  border-radius: 6px;"
            f"  min-width: 20px;"
            f"}}"
            f"QScrollBar::handle:horizontal:hover {{"
            f"  background-color: {colors.accent};"
            f"}}"
            f"QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{"
            f"  width: 0px;"
            f"}}"
            f"QComboBox {{"
            f"  border: 1px solid {colors.input_border};"
            f"  border-radius: 4px;"
            f"  padding: 4px 8px;"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"}}"
            f"QComboBox:hover {{"
            f"  border-color: {colors.input_focus_border};"
            f"}}"
            f"QComboBox:focus {{"
            f"  border-color: {colors.input_focus_border};"
            f"}}"
            f"QComboBox::drop-down {{"
            f"  border: none;"
            f"  width: 20px;"
            f"}}"
            f"QComboBox::down-arrow {{"
            f"  image: none;"
            f"  border-left: 4px solid transparent;"
            f"  border-right: 4px solid transparent;"
            f"  border-top: 5px solid {colors.text};"
            f"  width: 0px;"
            f"  height: 0px;"
            f"}}"
            f"QComboBox QAbstractItemView {{"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"  border: 1px solid {colors.input_border};"
            f"  selection-background-color: {colors.accent};"
            f"  selection-color: {colors.background};"
            f"  outline: none;"
            f"}}"
            f"QComboBox QAbstractItemView::item {{"
            f"  background-color: {colors.input_bg};"
            f"  color: {colors.input_text};"
            f"  padding: 4px;"
            f"}}"
            f"QComboBox QAbstractItemView::item:selected {{"
            f"  background-color: {colors.accent};"
            f"  color: {colors.background};"
            f"}}"
            f"QComboBox QAbstractItemView::item:hover {{"
            f"  background-color: {colors.button_hover_bg};"
            f"}}"
        )
        self.setStyleSheet(main_stylesheet)

        tabs_stylesheet = (
            "QTabWidget::pane {"
            f" background-color: {colors.background};"
            " border: none;"
            " padding: 8px;"
            " }"
            "QTabBar::tab {"
            f" background: {colors.tab_bg};"
            f" color: {colors.tab_text};"
            " border: none;"
            " padding: 6px 12px;"
            " margin-right: 4px;"
            " border-radius: 0px;"
            " }"
            "QTabBar::tab:selected {"
            f" border-bottom: 2px solid {colors.tab_selected_border};"
            " font-weight: 600;"
            f" color: {colors.tab_text};"
            " border-radius: 0px;"
            " }"
            "QTabBar::tab:hover {"
            f" background: {colors.tab_hover_bg};"
            " border-radius: 0px;"
            " }"
        )
        self.tabs.setStyleSheet(tabs_stylesheet)

    def _apply_theme_to_all_views(self) -> None:
        """Apply current theme colors to all child views."""
        colors = self._current_theme_colors
        
        # Update dashboard
        if hasattr(self.dashboard_view, 'apply_theme'):
            self.dashboard_view.apply_theme(colors)
        
        # Update radar
        if hasattr(self.radar_view, 'apply_theme'):
            self.radar_view.apply_theme(colors)
        
        # Update tracker
        if hasattr(self.tracker_view, 'apply_theme'):
            self.tracker_view.apply_theme(colors)
        
        # Update goals
        if hasattr(self.goals_view, 'apply_theme'):
            self.goals_view.apply_theme(colors)
        
        # Update resources
        if hasattr(self.resources_view, 'apply_theme'):
            self.resources_view.apply_theme(colors)
        
        # Update settings
        if hasattr(self.settings_view, 'apply_theme'):
            self.settings_view.apply_theme(colors)

    def _on_settings_changed(self, settings: Settings) -> None:
        """Callback from SettingsView when settings are updated."""

        self._settings = settings
        
        # Update theme colors
        self._current_theme_colors = self._get_current_theme_colors()
        
        # Re-apply tab bar style (for text/background).
        self._apply_tab_styles()
        
        # First rebuild dashboard previews that create widgets dynamically so
        # that newly created widgets are present when we apply theme & font.
        if hasattr(self.dashboard_view, "refresh_resources_from_storage"):
            self.dashboard_view.refresh_resources_from_storage()

        # Apply theme to all views, including the rebuilt dashboard.
        self._apply_theme_to_all_views()

        # Now apply the font size to the entire LanguageForge UI, including the
        # freshly rebuilt dashboard resources preview.
        self._apply_font_size()

    # dock helpers -----------------------------------------------------

    def _find_dock(self) -> Optional[QDockWidget]:
        """Locate the LanguageForge QDockWidget in Anki's main window."""

        if mw is None:
            return None
        return mw.findChild(QDockWidget, "LanguageForgeDock")

    def _on_popout_clicked(self) -> None:
        """Pop out the LanguageForge dock as a floating window."""

        dock = self._find_dock()
        if dock is None:
            return
        dock.setFloating(True)
        dock.raise_()

    def _on_close_clicked(self) -> None:
        """Close (hide) the LanguageForge dock."""

        dock = self._find_dock()
        if dock is None:
            return
        dock.hide()
