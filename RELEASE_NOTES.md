# LanguageForge Release Notes

## 1.1.0 – Theme Mode & UI Polish

- **Theme engine refactor**
  - Introduced centralized `ThemeColors` palette (`core/themes.py`) and wired it through all major views.
  - Added `apply_theme` methods to Dashboard, Tracker, Goals, Resources, Settings, and Radar views to keep styling consistent.
  - Updated `main.py` to react to Anki theme changes when using the `anki_auto` theme mode, reapplying colors automatically.

- **CircleIndicator theming**
  - Updated `CircleIndicator` to accept `theme_colors` and use theme-driven colors for empty state, completed state, hover background, and checkmark.
  - Ensured all CircleIndicators across Dashboard, Tracker, Goals, and other views receive the active theme.

- **Combo box / selector styling**
  - Themed month selectors and other dropdowns across Tracker, Goals, Radar (Fluency Snapshot), Settings, and Resources dialogs.
  - Applied consistent borders, background, text, focus, and selection colors via stylesheets.

- **Dashboard improvements**
  - Themed the "This Week's Activity" current-day circle using the accent color.
  - Styled embedded RadarView to match the overall dashboard theme.
  - Added themed, hoverable **Open** buttons in the Resources preview section.
  - Styled the "This Month's Goals" pencil buttons with borders and hover feedback matching theme buttons.

- **Goals view improvements**
  - Themed goal cards, inputs, and category combos using the centralized palette.
  - Updated subtask `CircleIndicator`s to use theme colors, including when loaded from storage.
  - Replaced trash-can icons for subtasks with `✕` buttons and styled them as red-ish delete actions with a clear hover state.
  - Themed the "Show archived months" checkbox and archived banner for consistency.

- **Resources view improvements**
  - Themed the Resources dialog (add/edit) including combo boxes, inputs, labels, and buttons.
  - Kept the Resources table visually integrated with Anki while applying theme-aware link colors.

- **Settings view improvements**
  - Themed the theme selector, font size spinbox, and checkboxes.
  - Centralized logic for applying theme changes across all views from the Settings tab.

- **Tracker view improvements**
  - Added `apply_theme` to style the month selector, stats card, week cards, and all CircleIndicators.

---

## 1.0.0 – Initial Release

- Initial public release of LanguageForge with Dashboard, Tracker, Goals, and Resources features.
