"""Recurring traversal rules for Mud."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mud.events import MediaEvent

if TYPE_CHECKING:
    from mud.engine.engine import GameEngine


def status(engine: GameEngine) -> None:
    """Apply recurring status rules."""
    poison(engine)
    leeched(engine)
    time(engine)
    music(engine)


async def sink(engine: GameEngine, amount: float = 1) -> None:
    """Apply sinking pressure for stationary actions."""
    state = engine.state
    sinking = state.condition("sinking")
    if sinking.started_turn == -1:
        sinking.started_turn = state.turns
    if state.turns - sinking.count != sinking.started_turn and not sinking.active:
        sinking.started_turn = -1
        sinking.count = 0
        return
    sinking.count += amount
    if sinking.count >= 2:
        sinking.active = True
        await sink_death(engine)
    elif sinking.count > 1:
        engine.emit("You're having trouble shifting your weight.")
    elif sinking.count >= 0.75:
        engine.emit(engine.text.get("legacy.line_2602_229"))


async def sink_death(engine: GameEngine) -> None:
    """Run the sinking death prompt loop."""
    sinking = engine.state.condition("sinking")
    engine.place().restricted = True
    engine.state.previous = ""
    while sinking.active:
        if sinking.count >= 5:
            sinking.active = False
            engine.dead(engine.text.get("legacy.line_2620_230"))
        if sinking.count >= 4:
            key = (
                "legacy.line_2625_231"
                if engine.state.current == "cave_in"
                else "legacy.line_2629_232"
            )
            engine.emit(engine.text.get(key))
        elif sinking.count >= 3:
            engine.emit(engine.text.get("legacy.line_2638_233"))
        elif sinking.count >= 2:
            engine.emit(engine.text.get("legacy.line_2647_234"))
        else:
            engine.emit("You flounder deep in the mud, utterly stuck.")
        engine.state.turns += 1
        sinking.count += 0.5
        await engine.whatnow()
        status(engine)


def poison(engine: GameEngine) -> None:
    """Apply poison progression."""
    state = engine.state
    poisoned = state.condition("poison")
    if not poisoned.active:
        return
    if poisoned.started_turn <= state.turns - 10:
        engine.dead(engine.text.get("legacy.line_2284_213"))
    if poisoned.started_turn <= state.turns - 6 and poisoned.count == 2:
        engine.emit(engine.text.get("legacy.line_2288_214"))
        poisoned.count = 3
    elif poisoned.started_turn <= state.turns - 2 and poisoned.count == 1:
        engine.emit(engine.text.get("legacy.line_2293_215"))
        poisoned.count = 2
    elif poisoned.started_turn <= state.turns and poisoned.count == 0:
        poisoned.count = 1


def leeched(engine: GameEngine) -> None:
    """Apply leech progression."""
    state = engine.state
    leeches = state.condition("leeches")
    if leeches.active and state.current != "swamp":
        engine.emit(engine.rnd(engine.world.obstacles[9]))
        leeches.count += 1
    if leeches.count == 5:
        engine.emit(engine.text.get("legacy.line_2687_235"))
        state.activate_condition("poison", started_turn=state.turns)


def time(engine: GameEngine) -> None:
    """Apply time progression."""
    thresholds = [
        (3, 0, 20),
        (10, 1, 40),
        (15, 2, None),
        (17, 3, 90),
        (23, 4, 130),
        (24, 5, None),
        (28, 6, 170),
    ]
    for turn, index, bg in thresholds:
        if (
            engine.state.turns >= turn
            and engine.state.time_progress == index
            and index not in engine.state.time_seen
        ):
            if engine.state.current != "cave_in":
                engine.emit(engine.world.obstacles[3][index])
                if bg is not None:
                    engine.emit(MediaEvent("bg", bg))
                engine.state.time_seen.append(index)
            engine.state.time_progress = index + 1
    if engine.state.turns >= 30:
        engine.dead(engine.text.get("legacy.line_2750_236"))


def music(engine: GameEngine) -> None:
    """Emit location sound cues."""
    if engine.state.music_location != engine.state.current:
        sounds = {"river": "RIVER", "troops": "WHISPERS", "wood": "BIRDS"}
        if engine.state.current in sounds:
            engine.emit(MediaEvent("sound", sounds[engine.state.current]))
    engine.state.music_location = engine.state.current
