"""Regression tests for the ported Mud engine."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Iterable
from contextlib import suppress
from pathlib import Path

import pytest

from mud.engine import GameEngine, GameSession, InputExhausted, build_world, run_script
from mud.engine.actions import ACTION_HANDLERS
from mud.engine.parser import dictmerge, parser
from mud.events import Artifacts, MediaEvent

GOLDEN_EVENTS = json.loads(
    Path("test/fixtures/golden_events.json").read_text(encoding="utf-8")
)
GOLDEN_INPUTS = {
    "startup": [],
    "help": ["help"],
    "look": ["look"],
    "movement": ["north"],
    "invalid": ["xyzzy"],
    "death_restart": ["wait", "wait", "wait", "wait"],
    "search_pickup": ["search fighter"],
    "restricted_movement": ["east", "north"],
    "random_sand": ["north", "yes", "north", "north", "north"],
}
DEATH_INPUTS = {
    "sinking": ["wait", "wait", "wait", "wait"],
    "sand": ["north", "yes", "look"],
    "troops": ["west", "west", "west", "west", "yes"],
    "poison": ["east", "climb", "east", "west", "east", "west", "east", "west"],
    "time": ["north", "south"] * 16,
}


def text_events(events: Iterable[object]) -> list[str]:
    """Return only text events from a scripted run."""
    return [event for event in events if isinstance(event, str)]


def event_name(value: object) -> object:
    """Normalize event payloads for JSON comparison."""
    if isinstance(value, tuple):
        return list(value)
    return value


def normalized_events(events: Iterable[object]) -> list[dict[str, object]]:
    """Return JSON-compatible engine events."""
    normalized: list[dict[str, object]] = []
    for event in events:
        if isinstance(event, str):
            normalized.append({"kind": "text", "value": event})
        elif isinstance(event, MediaEvent):
            normalized.append(
                {"kind": "media", "type": event.type, "name": event_name(event.name)}
            )
        elif isinstance(event, Artifacts):
            normalized.append({"kind": "artifacts", "artifacts": event.artifacts})
        else:
            msg = f"Unknown event type: {type(event)}"
            raise TypeError(msg)
    return normalized


async def run_session(
    inputs: Iterable[str],
    *,
    artifacts: list[bool] | None = None,
    seed: int = 7,
) -> list[object]:
    """Run a session with optional preloaded artifact state."""
    events: list[object] = []
    iterator = iter(inputs)

    def next_input() -> str:
        try:
            return next(iterator)
        except StopIteration as exc:
            raise InputExhausted from exc

    session = GameSession(next_input, events.append, seed=seed)
    if artifacts is not None:
        session.artifacts = artifacts
    with suppress(InputExhausted):
        await session.run()
    return events


async def run_engine_from(
    location: str,
    inputs: Iterable[str],
    *,
    seed: int = 7,
) -> tuple[GameEngine, list[object]]:
    """Run a partial engine loop from a chosen location."""
    events: list[object] = []
    iterator = iter(inputs)

    def next_input() -> str:
        try:
            return next(iterator)
        except StopIteration as exc:
            raise InputExhausted from exc

    engine = GameEngine(next_input, events.append, seed=seed)
    engine.state.current = location
    engine.state.previous = location
    with suppress(InputExhausted):
        while True:
            await engine.status()
            await engine.room()
            await engine.whatnow()
    return engine, events


def test_parser_matches_commands_directions_and_ignores_digits() -> None:
    """The parser keeps the original broad word-matching behavior."""
    move = object()
    north = object()
    parsed = parser(
        "go north 123",
        dictmerge({move: ["move", "go"]}, {north: ["north", "n"]}),
    )

    assert parsed == [move, north]


@pytest.mark.parametrize("scenario", GOLDEN_INPUTS)
def test_scripted_runs_match_golden_events(scenario: str) -> None:
    """Representative command scripts preserve player-facing event streams."""
    events = run_script(GOLDEN_INPUTS[scenario], seed=7)

    assert normalized_events(events) == GOLDEN_EVENTS[scenario]


def test_artifact_carryover_matches_golden_events() -> None:
    """Artifact state carries into a restarted traversal."""
    events = asyncio.run(
        run_session(
            ["wait", "wait", "wait", "wait"],
            artifacts=[True, False, False],
        )
    )

    assert normalized_events(events) == GOLDEN_EVENTS["artifact_carryover_death"]


def test_final_ending_matches_golden_events_without_system_exit() -> None:
    """The final ending returns through session control flow, not sys.exit."""
    events = asyncio.run(run_session([], artifacts=[True, True, True]))

    assert normalized_events(events) == GOLDEN_EVENTS["final_ending"]


def test_world_view_uses_stable_ids() -> None:
    """The typed world boundary exposes stable location and item IDs."""
    world = build_world(seed=7)

    assert world.start_location == "plane"
    assert {"plane", "snake", "cave", "river"} <= set(world.locations)
    assert {"fighter", "stump", "boat", "water"} <= set(world.items)
    assert world.locations["plane"].items == ["fighter"]


def test_world_actions_have_registered_handlers() -> None:
    """Declarative world actions must be executable by the engine."""
    world = build_world(seed=7)
    action_ids = {action for item in world.items.values() for action in item.actions}

    assert action_ids <= set(ACTION_HANDLERS)


def test_engine_exposes_typed_state_snapshot() -> None:
    """Mutable traversal state is visible through a typed snapshot."""
    engine = GameEngine(lambda: "", lambda event: None, seed=7)

    assert engine.state.current_location == "plane"
    assert engine.state.previous_location == "plane"
    assert engine.state.artifacts == [False, False, False]
    assert {"leeches", "poison", "sinking"} <= set(engine.state.conditions)


def test_startup_emits_music_background_and_intro() -> None:
    """A fresh game emits the original startup sequence before prompting."""
    events = run_script([])

    assert events[0] == MediaEvent("music", ("main", -1))
    assert MediaEvent("bg", 0) in events
    assert any(event == "Type HELP at the prompt for commands." for event in events)
    assert any(
        "Endless blue. The open sky is an endless blue." in event
        for event in text_events(events)
    )


def test_representative_commands_emit_expected_text() -> None:
    """Common commands still travel through the old interpreter."""
    help_text = text_events(run_script(["help"]))
    look_text = text_events(run_script(["look"]))
    move_text = text_events(run_script(["north"]))
    invalid_text = text_events(run_script(["xyzzy"]))

    assert any("You can GO NORTH, SOUTH, EAST or WEST." in event for event in help_text)
    assert any(
        "The hot, twisted metal of your aircraft" in event for event in look_text
    )
    assert any(
        "The one-person aircraft is damaged beyond repair." in event
        for event in look_text
    )
    assert any(
        "The bleak mud ahead appears less viscous" in event for event in move_text
    )
    assert any("You stand still, exhausted" in event for event in invalid_text)


def test_death_resets_and_emits_artifacts() -> None:
    """Death restarts the traversal and carries artifact state forward."""
    events = run_script(["wait", "wait", "wait", "wait"])

    assert any(isinstance(event, Artifacts) for event in events)
    assert any(
        "The mire closes over your face" in event for event in text_events(events)
    )
    assert any(
        "You feel for the sides of the cockpit and awkwardly stand up." in event
        for event in text_events(events)
    )


@pytest.mark.parametrize("scenario", DEATH_INPUTS)
def test_death_paths_do_not_surface_engine_errors(scenario: str) -> None:
    """Death outcomes should not escape as generic session errors."""
    events = run_script(DEATH_INPUTS[scenario], seed=7)

    assert any(isinstance(event, Artifacts) for event in events)
    assert not any(
        isinstance(event, str) and ("[[Error]]" in event or "Traceback" in event)
        for event in events
    )


def test_active_leeches_can_be_pulled_off_before_they_are_held() -> None:
    """The worm-removal action is available whenever leeches are attached."""
    events: list[object] = []
    engine = GameEngine(lambda: "", events.append, seed=7)
    engine.state.current = "swamp"
    engine.state.previous = "sand"
    engine.state.activate_condition("leeches", count=3)

    assert engine.active_condition_item_ids() == ["leeches"]
    assert "leeches" not in engine.state.holding
    asyncio.run(engine.interpret(engine.parse("pull off worms")))

    leeches = engine.state.condition("leeches")
    assert engine.text.actions.leeches.remove in events
    assert leeches.active is False
    assert leeches.cleared is True
    assert leeches.count == 0
    assert "leeches" not in engine.state.holding


def test_removed_leeches_do_not_reattach_on_swamp_room_load() -> None:
    """Clearing leeches disables the swamp load trap for this traversal."""
    events: list[object] = []
    engine = GameEngine(lambda: "", events.append, seed=7)
    engine.state.current = "swamp"
    engine.state.previous = "sand"
    engine.state.activate_condition("leeches")

    asyncio.run(engine.run_action("leeches_rid", None))
    events.clear()
    asyncio.run(engine.room())

    assert engine.state.condition("leeches").active is False
    assert "leeches" not in engine.state.holding
    assert "You can feel movement beneath the water." not in events


def test_medkit_clears_poison_condition() -> None:
    """Poison is a player condition, not an inventory or room item."""
    events: list[object] = []
    engine = GameEngine(lambda: "", events.append, seed=7)
    engine.state.activate_condition("poison", started_turn=engine.state.turns)

    asyncio.run(engine.run_action("medkit_use", None))

    assert engine.text.actions.medkit.use_poisoned in events
    assert engine.state.condition("poison").active is False


def test_repeated_east_from_waterway_stays_in_valid_forest_scene() -> None:
    """The waterway-to-forest route should not move into raw direction IDs."""
    engine, events = asyncio.run(run_engine_from("river", ["e"] * 8))

    assert engine.state.current in engine.world.locations
    assert engine.state.current != "east"
    assert not any(
        isinstance(event, str) and ("[[Error]]" in event or "Traceback" in event)
        for event in events
    )
