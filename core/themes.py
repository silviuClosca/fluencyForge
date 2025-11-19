from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ThemeColors:
    """Color palette for a FluencyForge theme.
    
    All colors are hex strings (e.g., "#FFFFFF").
    """
    
    # Primary UI colors
    background: str
    text: str
    text_secondary: str  # Muted text for labels, hints
    accent: str
    
    # Tab bar
    tab_bg: str
    tab_text: str
    tab_selected_border: str
    tab_hover_bg: str
    
    # Dashboard/Cards
    card_bg: str
    card_border: str
    divider: str
    
    # Buttons
    button_bg: str
    button_text: str
    button_border: str
    button_hover_bg: str
    button_hover_border: str
    
    # Input fields (QLineEdit, QTextEdit, QComboBox)
    input_bg: str
    input_text: str
    input_border: str
    input_focus_border: str
    
    # Widgets
    circle_empty: str
    circle_complete: str
    circle_hover_bg: str
    
    # Radar chart
    radar_axes: str
    radar_axes_hover: str
    radar_polygon: str
    radar_ghost: str
    radar_dots: str
    radar_dots_hover: str
    
    # Tracker
    tracker_today_bg: str
    tracker_header_text: str
    tracker_week_card_bg: str
    tracker_week_card_border: str
    tracker_stats_bg: str
    tracker_stats_border: str
    
    # Goals
    goals_card_bg: str
    goals_card_border: str
    goals_archived_banner_bg: str
    goals_archived_banner_text: str
    
    # Resources
    resource_link_color: str
    resource_table_header_bg: str
    
    # Progress bars
    progress_bg: str
    progress_fill: str


# Theme definitions
_THEMES: Dict[str, ThemeColors] = {
    "light": ThemeColors(
        # Light Mode - Clean, modern light theme
        background="#FFFFFF",
        text="#1F2937",
        text_secondary="#6B7280",
        accent="#3B82F6",
        tab_bg="#FFFFFF",
        tab_text="#1F2937",
        tab_selected_border="#3B82F6",
        tab_hover_bg="rgba(59, 130, 246, 0.08)",
        card_bg="#F9FAFB",
        card_border="#E5E7EB",
        divider="#E5E7EB",
        button_bg="#FFFFFF",
        button_text="#1F2937",
        button_border="#D1D5DB",
        button_hover_bg="#F3F4F6",
        button_hover_border="#3B82F6",
        input_bg="#FFFFFF",
        input_text="#1F2937",
        input_border="#D1D5DB",
        input_focus_border="#3B82F6",
        circle_empty="#DBEAFE",
        circle_complete="#3B82F6",
        circle_hover_bg="#DBEAFE",
        radar_axes="#9CA3AF",
        radar_axes_hover="#D1D5DB",
        radar_polygon="#60A5FA",
        radar_ghost="#BFDBFE",
        radar_dots="#6B7280",
        radar_dots_hover="#D1D5DB",
        tracker_today_bg="#EFF6FF",
        tracker_header_text="#1F2937",
        tracker_week_card_bg="rgba(148, 163, 184, 0.1)",
        tracker_week_card_border="rgba(148, 163, 184, 0.3)",
        tracker_stats_bg="rgba(148, 163, 184, 0.12)",
        tracker_stats_border="rgba(15, 23, 42, 0.15)",
        goals_card_bg="#F9FAFB",
        goals_card_border="#E5E7EB",
        goals_archived_banner_bg="#FEF3C7",
        goals_archived_banner_text="#92400E",
        resource_link_color="#3B82F6",
        resource_table_header_bg="transparent",
        progress_bg="#E5E7EB",
        progress_fill="#3B82F6",
    ),
    
    "zen": ThemeColors(
        # Zen Mode - Soft neutral colors, calming earth tones
        background="#F5F5F0",
        text="#4A4A3A",
        text_secondary="#6B6B5A",
        accent="#8B9A7A",
        tab_bg="#F5F5F0",
        tab_text="#4A4A3A",
        tab_selected_border="#8B9A7A",
        tab_hover_bg="rgba(139, 154, 122, 0.1)",
        card_bg="#FAFAF8",
        card_border="#D0D5CA",
        divider="#D0D5CA",
        button_bg="#FAFAF8",
        button_text="#4A4A3A",
        button_border="#C8CFC0",
        button_hover_bg="#F0F2ED",
        button_hover_border="#8B9A7A",
        input_bg="#FAFAF8",
        input_text="#4A4A3A",
        input_border="#C8CFC0",
        input_focus_border="#8B9A7A",
        circle_empty="#D4D9CD",
        circle_complete="#8B9A7A",
        circle_hover_bg="#E8EBE3",
        radar_axes="#B8BDB0",
        radar_axes_hover="#D0D5CA",
        radar_polygon="#A8B89A",
        radar_ghost="#C8D3BC",
        radar_dots="#9BA88E",
        radar_dots_hover="#C0C9B5",
        tracker_today_bg="#E8EBE3",
        tracker_header_text="#4A4A3A",
        tracker_week_card_bg="rgba(139, 154, 122, 0.08)",
        tracker_week_card_border="rgba(139, 154, 122, 0.25)",
        tracker_stats_bg="rgba(139, 154, 122, 0.12)",
        tracker_stats_border="rgba(74, 74, 58, 0.15)",
        goals_card_bg="#FAFAF8",
        goals_card_border="#D0D5CA",
        goals_archived_banner_bg="#F3F4E8",
        goals_archived_banner_text="#5A5A3A",
        resource_link_color="#7A8A6A",
        resource_table_header_bg="transparent",
        progress_bg="#D0D5CA",
        progress_fill="#8B9A7A",
    ),
    
    "high_contrast": ThemeColors(
        # High Contrast Mode - Maximum readability
        background="#FFFFFF",
        text="#000000",
        text_secondary="#333333",
        accent="#0066CC",
        tab_bg="#F0F0F0",
        tab_text="#000000",
        tab_selected_border="#0066CC",
        tab_hover_bg="rgba(0, 102, 204, 0.1)",
        card_bg="#FFFFFF",
        card_border="#000000",
        divider="#000000",
        button_bg="#FFFFFF",
        button_text="#000000",
        button_border="#000000",
        button_hover_bg="#F0F0F0",
        button_hover_border="#0066CC",
        input_bg="#FFFFFF",
        input_text="#000000",
        input_border="#000000",
        input_focus_border="#0066CC",
        circle_empty="#CCCCCC",
        circle_complete="#0066CC",
        circle_hover_bg="#E6F2FF",
        radar_axes="#666666",
        radar_axes_hover="#999999",
        radar_polygon="#0066CC",
        radar_ghost="#99CCFF",
        radar_dots="#333333",
        radar_dots_hover="#666666",
        tracker_today_bg="#E6F2FF",
        tracker_header_text="#000000",
        tracker_week_card_bg="#FAFAFA",
        tracker_week_card_border="#000000",
        tracker_stats_bg="#F5F5F5",
        tracker_stats_border="#000000",
        goals_card_bg="#FFFFFF",
        goals_card_border="#000000",
        goals_archived_banner_bg="#FFFFCC",
        goals_archived_banner_text="#000000",
        resource_link_color="#0066CC",
        resource_table_header_bg="transparent",
        progress_bg="#CCCCCC",
        progress_fill="#0066CC",
    ),
    
    "japanese_pastel": ThemeColors(
        # Japanese-style pastel theme - Soft, harmonious colors
        background="#FFF8F8",
        text="#4A4A4A",
        text_secondary="#8A7A7A",
        accent="#FFB7C5",
        tab_bg="#FFF8F8",
        tab_text="#4A4A4A",
        tab_selected_border="#FFB7C5",
        tab_hover_bg="rgba(255, 183, 197, 0.1)",
        card_bg="#FFFBFB",
        card_border="#FFE4E9",
        divider="#FFE4E9",
        button_bg="#FFFBFB",
        button_text="#4A4A4A",
        button_border="#FFD4DC",
        button_hover_bg="#FFF5F7",
        button_hover_border="#FFB7C5",
        input_bg="#FFFBFB",
        input_text="#4A4A4A",
        input_border="#FFD4DC",
        input_focus_border="#FFB7C5",
        circle_empty="#FFE4E9",
        circle_complete="#FFB7C5",
        circle_hover_bg="#FFF0F3",
        radar_axes="#D4C5D0",
        radar_axes_hover="#E8DDE5",
        radar_polygon="#B4D7E8",
        radar_ghost="#E0EEF5",
        radar_dots="#C0B5BD",
        radar_dots_hover="#D8CFD5",
        tracker_today_bg="#FFF0F5",
        tracker_header_text="#4A4A4A",
        tracker_week_card_bg="rgba(255, 183, 197, 0.08)",
        tracker_week_card_border="rgba(255, 183, 197, 0.25)",
        tracker_stats_bg="rgba(255, 183, 197, 0.12)",
        tracker_stats_border="rgba(74, 74, 74, 0.12)",
        goals_card_bg="#FFFBFB",
        goals_card_border="#FFE4E9",
        goals_archived_banner_bg="#FFF5E6",
        goals_archived_banner_text="#8B5A3C",
        resource_link_color="#A8C8D8",
        resource_table_header_bg="transparent",
        progress_bg="#FFE4E9",
        progress_fill="#FFB7C5",
    ),
    
    "dark": ThemeColors(
        # Dark Mode - Modern dark theme with blue accents
        background="#1E1E1E",
        text="#E0E0E0",
        text_secondary="#A0A0A0",
        accent="#4A9EFF",
        tab_bg="#252525",
        tab_text="#E0E0E0",
        tab_selected_border="#4A9EFF",
        tab_hover_bg="rgba(74, 158, 255, 0.1)",
        card_bg="#252525",
        card_border="#3A3A3A",
        divider="#3A3A3A",
        button_bg="#2A2A2A",
        button_text="#E0E0E0",
        button_border="#404040",
        button_hover_bg="#353535",
        button_hover_border="#4A9EFF",
        input_bg="#2A2A2A",
        input_text="#E0E0E0",
        input_border="#404040",
        input_focus_border="#4A9EFF",
        circle_empty="#3A5A7A",
        circle_complete="#4A9EFF",
        circle_hover_bg="#2A4A6A",
        radar_axes="#707070",
        radar_axes_hover="#909090",
        radar_polygon="#4A9EFF",
        radar_ghost="#2A4A6A",
        radar_dots="#606060",
        radar_dots_hover="#808080",
        tracker_today_bg="#2A3A4A",
        tracker_header_text="#E0E0E0",
        tracker_week_card_bg="rgba(74, 158, 255, 0.08)",
        tracker_week_card_border="rgba(74, 158, 255, 0.25)",
        tracker_stats_bg="rgba(74, 158, 255, 0.12)",
        tracker_stats_border="rgba(224, 224, 224, 0.15)",
        goals_card_bg="#252525",
        goals_card_border="#3A3A3A",
        goals_archived_banner_bg="#3A3A2A",
        goals_archived_banner_text="#FFD699",
        resource_link_color="#4A9EFF",
        resource_table_header_bg="transparent",
        progress_bg="#3A3A3A",
        progress_fill="#4A9EFF",
    ),
}


def get_theme_colors(theme_name: str, is_anki_dark: bool = False) -> ThemeColors:
    """Get theme colors for the specified theme.
    
    Args:
        theme_name: One of "anki_auto", "light", "dark", "zen", "high_contrast", "japanese_pastel"
        is_anki_dark: Whether Anki is currently in dark mode (only used for "anki_auto")
    
    Returns:
        ThemeColors object with the color palette
    """
    
    if theme_name == "anki_auto":
        # Follow Anki's theme: use a dark variant for dark mode, light for light mode
        if is_anki_dark:
            return _get_anki_dark_theme()
        else:
            return _THEMES.get("light", _THEMES["light"])
    
    return _THEMES.get(theme_name, _THEMES["light"])


def _get_anki_dark_theme() -> ThemeColors:
    """Generate a dark theme that matches Anki's dark mode."""
    
    return ThemeColors(
        background="#2B2B2B",
        text="#FFFFFF",
        text_secondary="#B0B0B0",
        accent="#58A6FF",
        tab_bg="#333333",
        tab_text="#FFFFFF",
        tab_selected_border="#58A6FF",
        tab_hover_bg="rgba(255, 255, 255, 0.08)",
        card_bg="#333333",
        card_border="#404040",
        divider="#404040",
        button_bg="#333333",
        button_text="#FFFFFF",
        button_border="#505050",
        button_hover_bg="#3A3A3A",
        button_hover_border="#58A6FF",
        input_bg="#2B2B2B",
        input_text="#FFFFFF",
        input_border="#505050",
        input_focus_border="#58A6FF",
        circle_empty="#3A5A6A",
        circle_complete="#58A6FF",
        circle_hover_bg="#3A4A5A",
        radar_axes="#808080",
        radar_axes_hover="#A0A0A0",
        radar_polygon="#58A6FF",
        radar_ghost="#3A5A7A",
        radar_dots="#707070",
        radar_dots_hover="#909090",
        tracker_today_bg="#3A4A5A",
        tracker_header_text="#FFFFFF",
        tracker_week_card_bg="rgba(88, 166, 255, 0.08)",
        tracker_week_card_border="rgba(88, 166, 255, 0.25)",
        tracker_stats_bg="rgba(88, 166, 255, 0.12)",
        tracker_stats_border="rgba(255, 255, 255, 0.15)",
        goals_card_bg="#333333",
        goals_card_border="#404040",
        goals_archived_banner_bg="#4A4A2A",
        goals_archived_banner_text="#FFEB99",
        resource_link_color="#58A6FF",
        resource_table_header_bg="transparent",
        progress_bg="#404040",
        progress_fill="#58A6FF",
    )


def get_theme_display_name(theme_name: str) -> str:
    """Get the user-friendly display name for a theme."""
    
    display_names = {
        "anki_auto": "Auto (Follow Anki)",
        "light": "Light Mode",
        "dark": "Dark Mode",
        "zen": "Zen Mode",
        "high_contrast": "High Contrast",
        "japanese_pastel": "Japanese Pastel",
    }
    
    return display_names.get(theme_name, theme_name)


def get_all_theme_names() -> list[str]:
    """Get list of all available theme names."""
    
    return ["anki_auto", "light", "dark", "zen", "high_contrast", "japanese_pastel"]
