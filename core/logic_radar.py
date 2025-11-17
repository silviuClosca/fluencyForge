from __future__ import annotations

from datetime import datetime, date
from typing import Dict, Optional

from .models import RadarSnapshot
from .storage import load_json, save_json


_FILENAME = "radar.json"


def _default() -> Dict[str, Dict]:
    return {}


def load_radar_snapshots() -> Dict[str, Dict]:
    data = load_json(_FILENAME, _default())
    if not isinstance(data, dict):
        return _default()
    return data


def save_radar_snapshot(snapshot: RadarSnapshot) -> None:
    data = load_radar_snapshots()
    data[snapshot.month] = snapshot.to_dict()
    save_json(_FILENAME, data)


def compute_balance_index(snapshot: Dict) -> Optional[int]:
    """Compute a 0–100 balance score for a single snapshot.

    The idea: the closer all skills are to each other, the higher the score.
    We compute the average absolute deviation from the mean and map it so that
    0 deviation -> 100, and a deviation of 2 (roughly the maximum for 1–5
    ratings) maps to 0.
    """

    values = [
        float(snapshot.get("reading", 0)),
        float(snapshot.get("listening", 0)),
        float(snapshot.get("speaking", 0)),
        float(snapshot.get("writing", 0)),
    ]
    if not any(values):
        return None

    avg = sum(values) / len(values)
    deviations = sum(abs(v - avg) for v in values) / len(values)
    max_deviation = 2.0
    score = 100.0 * (1.0 - min(deviations, max_deviation) / max_deviation)
    return max(0, min(100, int(round(score))))


def compute_trends(current: Dict, previous: Dict) -> Dict[str, str]:
    """Return per-skill trend between two snapshots: 'up', 'down', or 'same'."""

    trends: Dict[str, str] = {}
    for key in ("reading", "listening", "speaking", "writing"):
        cur = int(current.get(key, 0))
        prev = int(previous.get(key, 0))
        if cur > prev:
            trends[key] = "up"
        elif cur < prev:
            trends[key] = "down"
        else:
            trends[key] = "same"
    return trends


def get_days_since_last_snapshot() -> Optional[int]:
    """Return days since the most recent snapshot, or None if no data."""

    snapshots = load_radar_snapshots()
    if not snapshots:
        return None

    last_month = max(snapshots.keys())
    try:
        last_date = datetime.strptime(f"{last_month}-01", "%Y-%m-%d").date()
    except Exception:
        return None

    today = date.today()
    return (today - last_date).days
