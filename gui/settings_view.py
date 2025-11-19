from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.themes import ThemeColors

from aqt.qt import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QCheckBox,
    Qt,
    QSpinBox,
    QComboBox,
)

from ..core.logic_settings import load_settings, save_settings, Settings
from ..core.themes import get_all_theme_names, get_theme_display_name


class SettingsView(QWidget):
    """Settings tab for LanguageForge.

    Exposes theme, visual, and startup/behavior options.
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        apply_theme_callback: Optional[Callable[[Settings], None]] = None,
    ) -> None:
        super().__init__(parent)

        self._apply_theme_callback = apply_theme_callback
        self._settings: Settings = load_settings()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Visual section -----------------------------------------------
        visual_group = QGroupBox("Visual", self)
        visual_layout = QVBoxLayout(visual_group)

        # Theme selector dropdown
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme", visual_group))
        self.theme_combo = QComboBox(visual_group)
        # Prevent Anki's global stylesheet from affecting this combo box
        self.theme_combo.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        for theme_name in get_all_theme_names():
            self.theme_combo.addItem(get_theme_display_name(theme_name))
        theme_row.addWidget(self.theme_combo, 1)
        visual_layout.addLayout(theme_row)

        # Font size spin box: user can type an exact point size within a range.
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font size (pt)", visual_group))
        self.font_spin = QSpinBox(visual_group)
        self.font_spin.setRange(8, 24)
        self.font_spin.setSingleStep(1)
        font_row.addWidget(self.font_spin, 0)

        visual_layout.addLayout(font_row)

        layout.addWidget(visual_group)

        # Startup / Behavior section -----------------------------------
        startup_group = QGroupBox("Startup / Behavior", self)
        startup_layout = QVBoxLayout(startup_group)

        self.open_on_startup_checkbox = QCheckBox(
            "Open LanguageForge automatically when Anki starts", startup_group
        )
        startup_layout.addWidget(self.open_on_startup_checkbox)

        layout.addWidget(startup_group)
        layout.addStretch(1)

        # Wire up initial values & signals
        self._load_into_widgets()
        self._connect_signals()

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------
    def _load_into_widgets(self) -> None:
        # Theme
        theme_names = get_all_theme_names()
        current_theme = self._settings.theme
        if current_theme in theme_names:
            self.theme_combo.setCurrentIndex(theme_names.index(current_theme))
        else:
            self.theme_combo.setCurrentIndex(0)  # Default to anki_auto

        # Font size
        # New representation: a point size stored as a string (e.g. "11").
        raw = self._settings.font_size
        size = 11
        if isinstance(raw, str) and raw.isdigit():
            size = int(raw)
        elif isinstance(raw, str) and raw.startswith("scale_"):
            # Backward compatibility with slider-based scale values.
            try:
                scale = int(raw.split("_", 1)[1])
            except ValueError:
                scale = 0
            size = 11 + scale
        else:
            # Backward compatibility with old small/medium/large values.
            legacy_map = {"small": 10, "medium": 11, "large": 13}
            size = legacy_map.get(str(raw), 11)

        size = max(8, min(24, size))
        self.font_spin.setValue(size)

        # Startup
        self.open_on_startup_checkbox.setChecked(self._settings.open_on_startup)

    def _connect_signals(self) -> None:
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.font_spin.valueChanged.connect(self._on_font_size_changed)
        self.open_on_startup_checkbox.toggled.connect(self._on_open_on_startup_toggled)

    def _on_theme_changed(self, index: int) -> None:
        theme_names = get_all_theme_names()
        if 0 <= index < len(theme_names):
            self._settings.theme = theme_names[index]
            save_settings(self._settings)
            self._apply_theme()

    def _on_font_size_changed(self, value: int) -> None:
        self._settings.font_size = str(int(value))
        save_settings(self._settings)
        self._apply_theme()

    def _on_open_on_startup_toggled(self, checked: bool) -> None:
        self._settings.open_on_startup = checked
        save_settings(self._settings)

    def _apply_theme(self) -> None:
        if self._apply_theme_callback is not None:
            self._apply_theme_callback(self._settings)
    
    def apply_theme(self, colors: 'ThemeColors') -> None:
        """Apply theme colors to settings view components."""
        # Update theme combo styling
        if hasattr(self, 'theme_combo'):
            self.theme_combo.setStyleSheet(
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
                f"QComboBox QAbstractItemView {{"
                f"  background-color: {colors.input_bg};"
                f"  color: {colors.input_text};"
                f"  border: 1px solid {colors.input_border};"
                f"  selection-background-color: {colors.accent};"
                f"  selection-color: {colors.background};"
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
            )
        
        # Update font size spinbox styling
        if hasattr(self, 'font_spin'):
            self.font_spin.setStyleSheet(
                f"QSpinBox {{"
                f"  border: 1px solid {colors.input_border};"
                f"  border-radius: 4px;"
                f"  padding: 4px 8px;"
                f"  background-color: {colors.input_bg};"
                f"  color: {colors.input_text};"
                f"}}"
                f"QSpinBox:focus {{"
                f"  border-color: {colors.input_focus_border};"
                f"}}"
            )
        
        # Update checkboxes
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setStyleSheet(
                f"QCheckBox {{"
                f"  color: {colors.text};"
                f"}}"
                f"QCheckBox::indicator {{"
                f"  width: 16px;"
                f"  height: 16px;"
                f"  border: 1px solid {colors.input_border};"
                f"  border-radius: 3px;"
                f"  background-color: {colors.input_bg};"
                f"}}"
                f"QCheckBox::indicator:checked {{"
                f"  background-color: {colors.accent};"
                f"  border-color: {colors.accent};"
                f"}}"
            )
        
        # Update group boxes
        for groupbox in self.findChildren(QGroupBox):
            groupbox.setStyleSheet(
                f"QGroupBox {{"
                f"  border: 1px solid {colors.card_border};"
                f"  border-radius: 6px;"
                f"  margin-top: 12px;"
                f"  padding-top: 12px;"
                f"  font-weight: bold;"
                f"  color: {colors.text};"
                f"}}"
                f"QGroupBox::title {{"
                f"  subcontrol-origin: margin;"
                f"  subcontrol-position: top left;"
                f"  padding: 0 6px;"
                f"  background-color: {colors.background};"
                f"}}"
            )
