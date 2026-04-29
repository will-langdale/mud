"""Typed model objects for Mud's engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Direction = Literal["north", "east", "south", "west"]


@dataclass(slots=True)
class Item:
    """Declarative item metadata and mutable description state."""

    id: str
    aliases: list[str]
    name: str
    first: str
    look: str
    search: str
    actions: dict[str, list[str]] = field(default_factory=dict)
    hidden: bool = False


@dataclass(slots=True)
class Location:
    """Declarative location metadata and mutable room state."""

    id: str
    name: str
    first: str
    look: str
    search: str
    exits: dict[Direction, str] = field(default_factory=dict)
    restricted: bool = False
    restriction: str = ""
    items: list[str] = field(default_factory=list)


@dataclass(slots=True)
class World:
    """Declarative world data."""

    locations: dict[str, Location] = field(default_factory=dict)
    items: dict[str, Item] = field(default_factory=dict)
    condition_items: dict[str, str] = field(default_factory=dict)
    start: str = "plane"
    obstacles: list[list[str]] = field(default_factory=list)
    commands: dict[str, list[str]] = field(default_factory=dict)

    @property
    def start_location(self) -> str:
        """Backward-compatible start location name."""
        return self.start


@dataclass(slots=True)
class Condition:
    """Mutable player condition state."""

    id: str
    active: bool = False
    started_turn: float = 0
    count: float = 0
    cleared: bool = False


def default_conditions() -> dict[str, Condition]:
    """Return fresh traversal conditions."""
    return {
        "leeches": Condition("leeches"),
        "poison": Condition("poison"),
        "sinking": Condition("sinking", started_turn=-1),
    }


@dataclass(slots=True)
class GameState:
    """Mutable state for a traversal."""

    current: str = "plane"
    previous: str = "plane"
    turns: float = 0
    artifacts: list[bool] = field(default_factory=lambda: [False, False, False])
    holding: set[str] = field(default_factory=set)
    searched: set[str] = field(default_factory=set)
    visited: set[str] = field(default_factory=set)
    textrecord: list[str] = field(default_factory=list)
    conditions: dict[str, Condition] = field(default_factory=default_conditions)
    time_progress: int = 0
    time_seen: list[int] = field(default_factory=list)
    music_location: str = ""
    cave_room: str = "small"
    cave_hint: int = 0
    cave_ghosts: bool = False
    cave_ghost_turn: float = 0
    cave_dir: str = "west"

    @property
    def current_location(self) -> str:
        """Backward-compatible current location name."""
        return self.current

    @property
    def previous_location(self) -> str:
        """Backward-compatible previous location name."""
        return self.previous

    def condition(self, condition_id: str) -> Condition:
        """Return mutable state for a player condition."""
        return self.conditions[condition_id]

    def activate_condition(
        self,
        condition_id: str,
        *,
        started_turn: float | None = None,
        count: float | None = None,
    ) -> Condition:
        """Activate and return a player condition."""
        condition = self.condition(condition_id)
        condition.active = True
        if started_turn is not None:
            condition.started_turn = started_turn
        if count is not None:
            condition.count = count
        return condition

    def clear_condition(
        self,
        condition_id: str,
        *,
        mark_cleared: bool = False,
    ) -> Condition:
        """Clear and return a player condition."""
        condition = self.condition(condition_id)
        condition.active = False
        condition.count = 0
        if mark_cleared:
            condition.cleared = True
        return condition
