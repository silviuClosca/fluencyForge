from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict

from .storage import load_json, save_json


_SETTINGS_FILENAME = "settings.json"


@dataclass
class Settings:
    """User settings for FluencyForge.

    Includes theme selection, font sizing, and startup behavior.
    """

    font_size: str = "medium"  # small, medium, large, or numeric point size
    open_on_startup: bool = False
    theme: str = "anki_auto"  # anki_auto, light, zen, high_contrast, japanese_pastel

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _default_settings() -> Settings:
    return Settings()


def load_settings() -> Settings:
    """Load settings from JSON, falling back to sensible defaults.

    Any missing keys are filled with default values so new fields are
    backward-compatible with older settings.json versions.
    """

    raw = load_json(_SETTINGS_FILENAME, default=_default_settings().to_dict())
    if not isinstance(raw, dict):
        return _default_settings()

    base = _default_settings().to_dict()
    base.update({k: v for k, v in raw.items() if k in base})

    return Settings(**base)


def save_settings(settings: Settings) -> None:
    """Persist settings to JSON."""

    save_json(_SETTINGS_FILENAME, settings.to_dict())
