"""Regression tests for Pygame UI helpers."""

from __future__ import annotations

import os

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from mud import ui
from mud.events import Artifacts, MediaEvent


def test_title_time_filter_uses_integer_colour_steps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The title menu colour cycle must not index colours with floats."""
    pygame.init()
    try:
        time_filter = ui.TimeFilter()
        time_filter.ticks2 = 0
        time_filter.colour = pygame.Color(*ui.AFTERNOON)
        time_filter.colourtgt = pygame.Color(*ui.AFTERNOON)
        monkeypatch.setattr(pygame.time, "get_ticks", lambda: 10001)

        time_filter.menu()
    finally:
        pygame.quit()


def test_key_text_prefers_event_unicode_for_web_key_events() -> None:
    """Browser key events should use unicode text, not key name text."""
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UNKNOWN, unicode="h")

    assert ui.key_text(event) == "h"


def test_text_input_filters_to_supported_prompt_characters() -> None:
    """Text input events are the primary printable text path in browser builds."""
    event = pygame.event.Event(pygame.TEXTINPUT, text="he l!0")

    assert ui.text_input(event) == "hel0"


def test_recieve_does_not_rebuild_old_output_without_new_events() -> None:
    """Old output should not force the UI back from prompt to display."""
    control = object.__new__(ui.Control)
    control.status = "prompt"
    control.pending_events = []
    control.listin = ["A line that was already displayed."]
    control.listtrunc = []

    ui.Control.recieve(control)

    assert control.status == "prompt"
    assert control.listtrunc == []


def test_recieve_handles_death_restart_event_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Death emits text, artifacts, and restart media in one UI batch."""
    control = object.__new__(ui.Control)
    control.status = "display"
    control.artifacts = []
    control.listin = []
    control.listtrunc = []
    control.pending_events = [
        "Death text.",
        Artifacts([True, False, False]),
        MediaEvent("bg", 255),
        " ",
        MediaEvent("reset", ""),
        "Restart text.",
    ]

    class DummySfx:
        def addsound(self, name: str, cue: str) -> None:
            del name, cue

    class DummyBg:
        blackalphatgt = 0

        def alpha(self, value: int, cue: str) -> None:
            del value, cue

    class DummyMusic:
        def addmusic(self, music: tuple[str, int], cue: str) -> None:
            del music, cue

        def change(self, name: str, loops: int) -> None:
            del name, loops

    class DummyReset:
        def addcue(self, cue: str) -> None:
            del cue

    def linetrunc(self: object, text: list[object]) -> list[list[str]]:
        del self
        assert text == ["Death text.", " ", "Restart text."]
        return [["Death text."]]

    control.sfx = DummySfx()
    control.bg = DummyBg()
    control.music = DummyMusic()
    control.reset = DummyReset()
    monkeypatch.setattr(ui.Control, "linetrunc", linetrunc)

    ui.Control.recieve(control)

    assert control.artifacts == [True, False, False]
    assert control.listtrunc == [["Death text."]]
    assert control.status == "display"
