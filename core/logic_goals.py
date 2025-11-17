from __future__ import annotations

from typing import Dict, List
from datetime import datetime

from .models import MonthlyGoals
from .storage import load_json, save_json, get_data_dir


# New storage filename for goals to avoid interference with any legacy
# writers that still touch the old goals.json.
_FILENAME = "goals_v2.json"
_LEGACY_FILENAME = "goals.json"


def _default() -> Dict[str, Dict]:
    return {}


def load_goals() -> Dict[str, Dict]:
    """Load all goals from the new storage file.

    On first run, if the new file does not exist but a legacy goals.json
    does, migrate its contents into the new file and continue from there.
    """

    data_dir = get_data_dir()
    new_path = data_dir / _FILENAME
    legacy_path = data_dir / _LEGACY_FILENAME

    # If the new file doesn't exist yet but the legacy one does, migrate.
    if not new_path.exists() and legacy_path.exists():
        legacy = load_json(_LEGACY_FILENAME, _default())
        if isinstance(legacy, dict):
            save_json(_FILENAME, legacy)

    data = load_json(_FILENAME, _default())
    if not isinstance(data, dict):
        return _default()
    return data


def get_current_month_id() -> str:
    """Return the current month as YYYY-MM."""

    return datetime.now().strftime("%Y-%m")


def load_goals_for_month(month: str) -> MonthlyGoals:
    """Load goals for a specific month, filling defaults and archived flag.

    Backwards compatible with older JSON that may not have the archived field.
    """

    data = load_goals()
    raw = data.get(month)
    if not isinstance(raw, dict):
        # Completely new month: return blank goals with default metadata.
        return MonthlyGoals(
            month=month,
            goals=["", "", ""],
            completed=[False, False, False],
            notes="",
            archived=False,
            categories=["General", "General", "General"],
            reflections=["", "", ""],
            subtasks=[[], [], []],
            subtasks_done=[[], [], []],
            created_at=["", "", ""],
            completed_at=["", "", ""],
        )

    goals = raw.get("goals") or ["", "", ""]
    completed = raw.get("completed") or [False, False, False]
    notes = raw.get("notes") or ""
    archived = bool(raw.get("archived", False))

    categories = raw.get("categories") or []
    reflections = raw.get("reflections") or []
    subtasks = raw.get("subtasks") or []
    subtasks_done = raw.get("subtasks_done") or []
    created_at = raw.get("created_at") or []
    completed_at = raw.get("completed_at") or []

    # Normalise lengths to exactly three goals.
    def _pad_list(lst, default, target_len: int = 3):
        lst = list(lst)
        while len(lst) < target_len:
            lst.append(default)
        return lst[:target_len]

    goals = _pad_list(goals, "")
    completed = _pad_list(completed, False)
    categories = _pad_list(categories, "General")
    reflections = _pad_list(reflections, "")
    created_at = _pad_list(created_at, "")
    completed_at = _pad_list(completed_at, "")

    # Subtasks are lists-of-lists; ensure outer list has 3 entries and
    # each inner list has matching length for done flags.
    subtasks = list(subtasks) if isinstance(subtasks, list) else []
    subtasks_done = list(subtasks_done) if isinstance(subtasks_done, list) else []
    while len(subtasks) < 3:
        subtasks.append([])
    while len(subtasks_done) < 3:
        subtasks_done.append([])

    norm_subtasks: List[List[str]] = []
    norm_subtasks_done: List[List[bool]] = []
    for i in range(3):
        st_list = subtasks[i] if isinstance(subtasks[i], list) else []
        done_list = subtasks_done[i] if isinstance(subtasks_done[i], list) else []
        # Pad done_list to length of st_list.
        done_list = list(done_list)
        while len(done_list) < len(st_list):
            done_list.append(False)
        norm_subtasks.append([str(s) for s in st_list])
        norm_subtasks_done.append([bool(d) for d in done_list[: len(st_list)]])

    return MonthlyGoals(
        month=month,
        goals=goals,
        completed=completed,
        notes=notes,
        archived=archived,
        categories=categories,
        reflections=reflections,
        subtasks=norm_subtasks,
        subtasks_done=norm_subtasks_done,
        created_at=created_at,
        completed_at=completed_at,
    )


# Backwards-compatible aliases
def load_month_goals(month: str) -> MonthlyGoals:
    return load_goals_for_month(month)


def save_goals_for_month(goals: MonthlyGoals, source: str | None = None) -> None:
    """Persist a MonthlyGoals object back to goals.json.

    To avoid accidental data loss on startup or from default objects, we do
    not overwrite existing month data with an "effectively blank" object
    (no titles, completions, reflections, subtasks, or notes). This guards
    against code paths that construct a fresh MonthlyGoals for the current
    month and save it immediately, which would otherwise wipe subtasks.
    """

    data = load_goals()
    new_obj = goals.to_dict()

    if source:
        # Lightweight debug metadata to track who last wrote this month.
        new_obj["last_saved_by"] = source

    # If there is existing data for this month and the new object is
    # effectively empty, keep the existing data instead of overwriting it.
    existing = data.get(goals.month)
    if isinstance(existing, dict):
        goals_list = new_obj.get("goals") or []
        completed_list = new_obj.get("completed") or []
        reflections_list = new_obj.get("reflections") or []
        subtasks_list = new_obj.get("subtasks") or []
        notes_val = new_obj.get("notes") or ""

        def _all_blank_str(items):
            return all(not str(x).strip() for x in items)

        def _all_false(items):
            return all(not bool(x) for x in items)

        # Flatten subtasks to see if there is any text at all.
        flat_subtasks = []
        for lst in subtasks_list:
            if isinstance(lst, list):
                flat_subtasks.extend(lst)

        is_effectively_blank = (
            _all_blank_str(goals_list)
            and _all_false(completed_list)
            and _all_blank_str(reflections_list)
            and _all_blank_str(flat_subtasks)
            and not str(notes_val).strip()
        )

        if is_effectively_blank:
            # Skip overwriting richer existing data.
            return

    data[goals.month] = new_obj
    save_json(_FILENAME, data)


def save_month_goals(goals: MonthlyGoals, source: str | None = None) -> None:
    # Backwards-compatible name
    save_goals_for_month(goals, source=source)


def get_all_goals() -> List[MonthlyGoals]:
    """Return a list of all MonthlyGoals objects in goals.json."""

    data = load_goals()
    items: List[MonthlyGoals] = []
    for month in sorted(data.keys()):
        items.append(load_goals_for_month(month))
    return items


def auto_archive_past_goals(current_month_id: str) -> None:
    """Mark goals from months before current_month_id as archived.

    Does not modify current or future months.
    """

    data = load_goals()
    changed = False
    for month, raw in list(data.items()):
        if not isinstance(raw, dict):
            continue
        if month < current_month_id:
            if not raw.get("archived", False):
                raw["archived"] = True
                data[month] = raw
                changed = True
    if changed:
        save_json(_FILENAME, data)
