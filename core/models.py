from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any


@dataclass
class RadarSnapshot:
    month: str
    reading: int
    listening: int
    speaking: int
    writing: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DailyActivity = Dict[str, Dict[str, bool]]


@dataclass
class MonthlyGoals:
    month: str
    goals: List[str]
    completed: List[bool]
    notes: str = ""
    archived: bool = False
    # Per-goal metadata (all lists kept at length 3)
    categories: List[str] = field(default_factory=list)
    reflections: List[str] = field(default_factory=list)
    subtasks: List[List[str]] = field(default_factory=list)
    subtasks_done: List[List[bool]] = field(default_factory=list)
    created_at: List[str] = field(default_factory=list)
    completed_at: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResourceItem:
    id: str
    type: str
    name: str
    link: str
    notes: str
    deck_name: Optional[str]
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DailyPlan:
    # Four generic daily tasks stored in order; UI can label them as it likes.
    tasks: List[str]
    show_on_startup: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
