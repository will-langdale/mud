"""Screen and overlay widgets."""

from __future__ import annotations

import pygame

from mud.engine.text import TextAssets
from mud.resources import audio_path
from mud.ui import text as ui_text
from mud.ui.background import Smoke, TimeFilter
from mud.ui.constants import BGGREY, BLACK, BLUE
from mud.ui.text import Bodycredits, Bodytext, TitleText

TEXT = TextAssets.load()


class EndMenu:
    """The very final winning screen of the game."""

    def __init__(self) -> None:
        """Create the end screen."""
        self.started = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen and start credits music."""
        self.music()

    def music(self) -> None:
        """Start the credits music once."""
        if self.started is False:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_path("credits.ogg"))
            pygame.mixer.music.play()
        self.started = True


class TitleMenu:
    """The title menu."""

    def __init__(self, top: pygame.Surface, plane: pygame.Surface) -> None:
        """Create the title menu from loaded image surfaces."""
        self.top = top
        self.skyboxcol = BLUE
        self.skyboxrec = pygame.Surface((800, 500))
        self.titletext = TitleText((400, 200))
        self.light = TimeFilter()
        self.plane = plane
        self.smokes: list[Smoke] = []
        self.ticks = pygame.time.get_ticks()
        self.text = TEXT.system.title_prompt
        self.textprint = Bodycredits(self.text, (400, 560))
        self.ticks2 = pygame.time.get_ticks()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title menu."""
        self.skyboxrec.fill(self.skyboxcol)
        self.skyboxrec.set_alpha(30)
        surface.blit(self.skyboxrec, (0, 0))
        surface.blit(self.top, (0, 230))
        surface.blit(self.plane, (300, 480))
        self.smokedraw(surface)
        self.titletext.draw(surface)
        if pygame.time.get_ticks() - self.ticks2 > 15000:
            self.textprint.draw(surface)
        self.light.draw(surface)
        self.light.menu()

    def smokedraw(self, surface: pygame.Surface) -> None:
        """Draw and update smoke particles."""
        time = pygame.time.get_ticks()
        smokes = self.smokes

        for i, v in enumerate(smokes):
            if v.done is True:
                del self.smokes[i]

        if len(smokes) < 15 and time - self.ticks >= 100:
            x = Smoke((340, 500))
            self.smokes.append(x)
            self.ticks = pygame.time.get_ticks()

        for i in self.smokes:
            i.draw(surface)


class EndCredits:
    """Final credits."""

    def __init__(self, artifacts: list[bool]) -> None:
        """Create the credits screen for an artifact state."""
        self.bgcol = BLACK
        self.bgrec = (0, 0, 800, 600)
        self.credtext: str | list[str] = "MUD. By Will Langdale."
        self.credprint = Bodycredits(str(self.credtext), (400, 200))
        self.artifacts = artifacts

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the credits for the collected artifact state."""
        pygame.draw.rect(surface, self.bgcol, self.bgrec)
        if self.artifacts == [False, False, False]:
            self.credtext = TEXT.credits.none
            self.credprint = Bodycredits(self.credtext, (400, 200))
            self.credprint.draw(surface)
        elif self.artifacts == [True, False, False]:
            self.credtext = TEXT.credits.earth
            self.credprint = Bodycredits(self.credtext, (400, 200))
            self.credprint.draw(surface)
        elif self.artifacts == [True, True, False]:
            self.credtext = TEXT.credits.stone
            self.credprint = Bodycredits(self.credtext, (400, 200))
            self.credprint.draw(surface)
        elif self.artifacts == [True, True, True]:
            self.credtext = list(TEXT.credits.full)
            lineh = ui_text.body_font().get_linesize()
            for i, v in enumerate(self.credtext):
                line = Bodycredits(v, (400, 100 + lineh * i))
                line.draw(surface)
        else:
            self.credtext = TEXT.credits.default
            self.credprint = Bodycredits(self.credtext, (400, 200))
            self.credprint.draw(surface)


class TextBox:
    """Text box at top of input."""

    def __init__(self) -> None:
        """Create the prompt/status textbox."""
        self.lineh = ui_text.body_font().get_linesize()
        self.boxheight = self.lineh * 2
        self.box = pygame.Surface((700, self.boxheight))
        self.currentalpha = 0
        self.ticks = pygame.time.get_ticks()

    def draw(self, surface: pygame.Surface, alpha: int, display: bool) -> None:
        """Draw the input/status box."""
        self.box.fill(BGGREY)

        if alpha != self.currentalpha:
            if alpha > self.currentalpha:
                if (pygame.time.get_ticks() - self.ticks) >= 10:
                    self.currentalpha += 5
                    self.ticks = pygame.time.get_ticks()
                    self.box.set_alpha(self.currentalpha)
            elif (
                alpha < self.currentalpha
                and (pygame.time.get_ticks() - self.ticks) >= 10
            ):
                self.currentalpha -= 5
                self.ticks = pygame.time.get_ticks()
                self.box.set_alpha(self.currentalpha)
        else:
            self.box.set_alpha(self.currentalpha)

        if display is True:
            space = Bodytext(TEXT.system.space_prompt, (5, self.lineh // 2))
            space.draw(self.box)

        surface.blit(self.box, (50, 50))
