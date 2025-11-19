# LanguageForge

## Install from AnkiWeb

Add-on code: **275563061**  
https://ankiweb.net/shared/info/275563061

**LanguageForge** is an Anki add-on that helps you track and balance your language-learning practice across the four core skills:

- **Reading**
- **Listening**
- **Speaking**
- **Writing**

It provides a compact dashboard inside Anki with a **weekly tracker**, **monthly calendar**, and a **fluency snapshot radar chart** for quickly visualizing consistency and balance.

---

## Features

### Dashboard Overview
- Fluency Snapshot **radar chart** with monthly snapshots and a balance index  
- Weekly activity tracker (Mon–Sun) with **one-click skill toggles**  
- Integrated **Daily Plan** tasks for the current week  

### Tracker Tab
- Monthly **calendar-style** view  
- Emoji + label row for each skill  
- Clickable daily completion circles  
- Today’s date highlighted  
- Monthly summary card showing:  
  - active days  
  - longest streak  
  - per-skill percentages  

### Goals Tab
- Three goal cards with circular completion indicators  
- Overall progress bar summarizing goal completion  

### Resources Tab
- Scrollable list of external resources  
- Quick-open buttons for links, notes, and materials  

### Settings
- Numeric base font-size control  
- Option to auto-open LanguageForge when Anki starts  

---

## Installation

1. Clone or download this repository.
2. Copy the folder into your Anki add-ons directory. Example path:

   ```
   %APPDATA%\Anki2\addons21\fluencyforge
   ```

3. Restart Anki.
4. Open **Tools → Add-ons**, ensure **LanguageForge** is enabled.
5. Open LanguageForge from the main Anki window (it appears as a dockable panel).

---

## Data & Privacy

LanguageForge stores all of its user data locally in JSON files under:

```
fluencyforge_data/
```

These files contain:
- tracker history  
- radar snapshots  
- goals  
- settings  
- resources  

Notes:
- These files are **specific to your machine and Anki profile**.  
- The repository includes a `.gitignore` entry so `fluencyforge_data/` is **not tracked in Git**.  
- On first run, LanguageForge will automatically create any missing JSON files with sensible defaults.

If distributing this add-on:
- Keep `fluencyforge_data/` empty (or omit it).  
- Let each user generate their own data locally.

---

## Development

### Requirements
- **Anki 2.15+** (or any version using Qt6)
- Python (bundled with Anki)

### Project Structure
Key modules:

- `main.py` — Entry point; integrates LanguageForge into Anki  
- `gui/main_window.py` — Main LanguageForge dockable window  
- `gui/dashboard_view.py` — Weekly tracker, radar chart, goals view  
- `gui/tracker_view.py` — Monthly calendar tracker  
- `gui/radar_view.py` — Radar chart + balance index  
- `gui/widgets/` — Shared widgets (circle indicators, layouts, etc.)  
- `core/logic.py` — Logic + persistence for tracker, goals, radar, settings, resources  

### Running From Source
1. With Anki closed, place this repo under your `addons21` directory.
2. Start Anki — it will load the add-on automatically.
3. Open the Anki Console (**Tools → Add-ons → View Console**) to inspect logs while developing.

### Contributing
- Please keep UI changes consistent with the existing compact and clean aesthetic.
- PRs are welcome for improvements and bug fixes.

---

## License

**MIT License + Non-Commercial Addendum**  
You may not use this software for commercial purposes without obtaining a separate commercial license.  
See the full `LICENSE` file for details.


