"""Shared event objects for the Mud engine and Pygame UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

type MediaEventType = Literal["sound", "reset", "music", "end", "bg"]


@dataclass(slots=True)
class MediaEvent:
    """A non-text event emitted by the game engine."""

    type: MediaEventType
    name: object


@dataclass(slots=True)
class Artifacts:
    """The artifact state carried between game traversals."""

    artifacts: list[bool]


type EngineEvent = str | MediaEvent | Artifacts
