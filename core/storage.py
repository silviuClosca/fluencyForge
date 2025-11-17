from __future__ import annotations

from pathlib import Path
from typing import Any

from aqt import mw


def get_addon_dir() -> Path:
    return Path(mw.addonManager.addonsFolder()) / "fluencyforge"


def get_data_dir() -> Path:
    data_dir = get_addon_dir() / "fluencyforge_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def load_json(filename: str, default: Any) -> Any:
    path = get_data_dir() / filename
    if not path.exists():
        return default
    try:
        import json

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(filename: str, data: Any) -> None:
    path = get_data_dir() / filename
    try:
        import json

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
