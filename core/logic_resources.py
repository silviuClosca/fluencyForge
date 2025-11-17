from __future__ import annotations

from typing import List, Dict, Any

from .models import ResourceItem
from .storage import load_json, save_json


_FILENAME = "resources.json"


def _default() -> List[Dict[str, Any]]:
    return []


def load_resources() -> List[Dict[str, Any]]:
    data = load_json(_FILENAME, _default())
    if not isinstance(data, list):
        return _default()
    return data


def save_resources(items: List[ResourceItem]) -> None:
    data = [item.to_dict() for item in items]
    save_json(_FILENAME, data)
