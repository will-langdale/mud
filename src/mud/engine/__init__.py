"""Public engine API for Mud."""

from __future__ import annotations

from mud.engine.engine import EngineOutcome, GameEngine, TraversalResult, build_world
from mud.engine.exceptions import InputExhausted, MissingTextError, TextAssetError
from mud.engine.session import (
    GameSession,
    InputProvider,
    OutputHandler,
    QuitHandler,
    run_script,
    run_script_async,
)

__all__ = [
    "EngineOutcome",
    "GameEngine",
    "GameSession",
    "InputExhausted",
    "InputProvider",
    "MissingTextError",
    "OutputHandler",
    "QuitHandler",
    "TextAssetError",
    "TraversalResult",
    "build_world",
    "run_script",
    "run_script_async",
]
