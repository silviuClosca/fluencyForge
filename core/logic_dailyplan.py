from __future__ import annotations

from typing import Dict, Any

from .models import DailyPlan
from .storage import load_json, save_json


_FILENAME = "dailyplan.json"


def _default() -> Dict[str, Any]:
    return {
        "tasks": ["", "", "", ""],
        "show_on_startup": False,
    }


def load_daily_plan() -> DailyPlan:
    data = load_json(_FILENAME, _default())
    if not isinstance(data, dict):
        data = _default()
    # Backward compatibility: if legacy morning/afternoon/evening exist,
    # use them to seed the first three tasks.
    tasks_raw = data.get("tasks")
    if isinstance(tasks_raw, list):
        tasks = [str(t) for t in tasks_raw]
    else:
        tasks = []

    if not tasks:
        legacy = [
            str(data.get("morning", "")),
            str(data.get("afternoon", "")),
            str(data.get("evening", "")),
        ]
        tasks = legacy

    # Ensure exactly four task slots.
    while len(tasks) < 4:
        tasks.append("")
    if len(tasks) > 4:
        tasks = tasks[:4]

    return DailyPlan(
        tasks=tasks,
        show_on_startup=bool(data.get("show_on_startup", False)),
    )


def save_daily_plan(plan: DailyPlan) -> None:
    save_json(_FILENAME, plan.to_dict())
