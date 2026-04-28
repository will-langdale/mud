"""Regression tests for the ported Mud engine."""

from __future__ import annotations

import importlib
from collections.abc import Iterable

from mud import legacy
from mud.engine import run_script
from mud.events import Artifacts, MediaEvent


def text_events(events: Iterable[object]) -> list[str]:
    """Return only text events from a scripted run."""
    return [event for event in events if isinstance(event, str)]


def test_parser_matches_commands_directions_and_ignores_digits() -> None:
    """The parser keeps the original broad word-matching behavior."""
    engine = importlib.reload(legacy)
    parsed = engine.parser(
        "go north 123",
        engine.dictmerge(engine.directions, engine.commands),
    )

    assert engine.move in parsed
    assert any(
        subject in engine.directions and engine.directions[subject][0] == "north"
        for subject in parsed
    )


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
