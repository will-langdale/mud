"""Typed model objects for Mud's engine boundary."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

EngineAction = Callable[..., object | Awaitable[object]]


@dataclass(slots=True)
class Action:
    """A command action and its accepted aliases."""

    handler: EngineAction
    aliases: list[str]


@dataclass(slots=True)
class Item:
    """Declarative item metadata."""

    id: str
    aliases: list[str]
    name: str
    first_sight_key: str
    look_key: str
    search_key: str
    actions: list[Action] = field(default_factory=list)
    hidden: bool = False


@dataclass(slots=True)
class Location:
    """Declarative location metadata."""

    id: str
    name: str
    first_sight_key: str
    look_key: str
    search_key: str
    exits: dict[str, str] = field(default_factory=dict)
    restricted: bool = False
    restriction_key: str = ""
    items: list[str] = field(default_factory=list)


@dataclass(slots=True)
class World:
    """Declarative world data."""

    locations: dict[str, Location] = field(default_factory=dict)
    items: dict[str, Item] = field(default_factory=dict)
    start_location: str = "plane"


@dataclass(slots=True)
class GameState:
    """Mutable state for a traversal."""

    current_location: str = "plane"
    previous_location: str = "plane"
    turns: float = 0
    deaths: int = 0
    artifacts: list[bool] = field(default_factory=lambda: [False, False, False])
    holding: set[str] = field(default_factory=set)
    searched: set[str] = field(default_factory=set)
    visited: set[str] = field(default_factory=set)
