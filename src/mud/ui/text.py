"""Font setup and text rendering helpers."""

from __future__ import annotations

import pygame

from mud.ui.constants import GREY

TITLE: pygame.font.Font | None = None
BODY: pygame.font.Font | None = None


def configure_fonts(title: pygame.font.Font, body: pygame.font.Font) -> None:
    """Store the Pygame font objects used by UI widgets."""
    global TITLE
    global BODY

    TITLE = title
    BODY = body


def title_font() -> pygame.font.Font:
    """Return the configured title font."""
    if TITLE is None:
        msg = "UI title font has not been configured"
        raise RuntimeError(msg)
    return TITLE


def body_font() -> pygame.font.Font:
    """Return the configured body font."""
    if BODY is None:
        msg = "UI body font has not been configured"
        raise RuntimeError(msg)
    return BODY


class Bodytext:
    """Body font text."""

    def __init__(self, text: str, location: tuple[float, float]) -> None:
        """Render body text at a top-left location."""
        self.font = body_font()
        self.colour = GREY
        self.text = self.font.render(text, False, self.colour)
        self.rect = self.text.get_rect(topleft=location)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the text on a surface."""
        surface.blit(self.text, self.rect)


class Bodycredits(Bodytext):
    """Centered body font text for credits."""

    def __init__(self, text: str, location: tuple[float, float]) -> None:
        """Render body text centered on a location."""
        self.font = body_font()
        self.colour = GREY
        self.text = self.font.render(text, False, self.colour)
        self.rect = self.text.get_rect(center=location)


class TitleText:
    """Rendered title text."""

    def __init__(self, location: tuple[float, float]) -> None:
        """Render the title centered on a location."""
        self.font = title_font()
        self.colour = GREY
        self.text = self.font.render("MUD", False, self.colour)
        self.rect = self.text.get_rect(center=location)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title on a surface."""
        surface.blit(self.text, self.rect)
