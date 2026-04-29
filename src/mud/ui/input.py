"""Keyboard and text input helpers."""

from __future__ import annotations

import string

import pygame

SUPPORTED_PROMPT_TEXT = string.ascii_letters + string.digits


def key_text(event: pygame.event.Event) -> str:
    """Return the typed letter or digit for a keydown event."""
    text = getattr(event, "unicode", "")
    if len(text) == 1 and text in SUPPORTED_PROMPT_TEXT:
        return text

    name = pygame.key.name(event.key)
    if len(name) == 1 and name in SUPPORTED_PROMPT_TEXT:
        return name

    return ""


def text_input(event: pygame.event.Event) -> str:
    """Return supported text from a text input event."""
    return "".join(
        char for char in getattr(event, "text", "") if char in SUPPORTED_PROMPT_TEXT
    )
