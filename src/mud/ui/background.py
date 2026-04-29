"""Animated background and lighting effects."""

from __future__ import annotations

import random
from typing import Any

import pygame

from mud.ui.constants import (
    ABBLACK,
    AFTERNOON,
    BGGREY,
    BLACK,
    BLUE,
    DARKBLUE,
    GREY,
    MOON,
    ORANGE,
    SUNK,
)


class BgImage:
    """The scrolling background and black alpha for light effects."""

    def __init__(self, bg: pygame.Surface, figure: pygame.Surface) -> None:
        """Create the scrolling background from loaded image surfaces."""
        self.bgcomp = pygame.Surface((800, 600))
        self.bg = bg
        self.blackalpha = 255
        self.blackalphatgt = 255
        self.blackground = pygame.Surface((800, 600))

        self.ticks = pygame.time.get_ticks()
        self.ticks2 = pygame.time.get_ticks()
        self.xpos = 100
        self.ypos = 0
        self.timecol = TimeFilter()

        self.stars: list[tuple[int, int]] = []
        self.starstick = pygame.time.get_ticks()
        self.sunpos = (400, -200)
        self.sun = (MOON, self.sunpos, 100)
        self.suntick = pygame.time.get_ticks()
        self.figure = figure

        self.cues: dict[str, int] = {}

    def draw(self, surface: pygame.Surface, end: bool) -> None:
        """Draw the background frame."""
        if end is False:
            self.move()
        else:
            self.movedown()
        self.blackfade()
        self.combine(end)
        surface.blit(self.bgcomp, (0, 0))

    def combine(self, end: bool) -> None:
        """Composite the background layers."""
        if end is True:
            self.blackground.fill(ABBLACK)
            self.blackground.set_alpha(255)
            self.stardraw(self.blackground)
            self.sundraw(self.blackground)
            self.blackground.blit(self.figure, (397, (0 - self.ypos) - 14))
            self.bgcomp.blit(self.blackground, (0, 0))
            self.bgcomp.blit(self.bg, (0, 0), (self.xpos, self.ypos, 800, 600))
        else:
            self.blackground.fill(BLACK)
            self.blackground.set_alpha(self.blackalpha)
            self.bgcomp.blit(self.bg, (0, 0), (self.xpos, self.ypos, 800, 600))
            self.bgcomp.blit(self.blackground, (0, 0))

    def movedown(self) -> None:
        """Scroll the ending background downward."""
        time = pygame.time.get_ticks() - self.ticks
        if time >= 30 and self.ypos > -450:
            self.ypos -= 0.5
            self.ticks = pygame.time.get_ticks()

    def sundraw(self, surface: pygame.Surface) -> None:
        """Draw the ending sun."""
        time = pygame.time.get_ticks()

        if time - self.suntick >= 40:
            if self.ypos < -100 and self.sunpos[1] < 390:
                x = self.sunpos[0]
                y = self.sunpos[1] + 1
                self.sunpos = (x, y)
                self.sun = (MOON, self.sunpos, 100)
            self.suntick = pygame.time.get_ticks()

        pygame.draw.circle(surface, *self.sun)

    def stardraw(self, surface: pygame.Surface) -> None:
        """Draw ending stars."""
        time = pygame.time.get_ticks()

        if len(self.stars) < 50 and time - self.starstick >= 500:
            x = random.randint(5, 800)
            y = random.randint(5, 600)
            self.stars.append((x, y))
            self.starstick = pygame.time.get_ticks()

        if len(self.stars) > 0:
            for i in self.stars:
                rec = (i[0], i[1], 3, 3)
                pygame.draw.rect(surface, GREY, rec)

    def move(self) -> None:
        """Scroll the normal background."""
        if self.xpos <= 0:
            self.xpos = 1594
        time = pygame.time.get_ticks() - self.ticks
        if time >= 30:
            self.xpos -= 0.5
            self.ticks = pygame.time.get_ticks()

    def blackfade(self) -> None:
        """Move background darkness toward its target alpha."""
        time = pygame.time.get_ticks() - self.ticks2
        if time >= 10:
            if self.blackalpha != self.blackalphatgt:
                if self.blackalpha > self.blackalphatgt:
                    if self.blackalpha > self.blackalphatgt + 16:
                        self.blackalpha -= 15
                    else:
                        self.blackalpha -= 1
                elif self.blackalpha < self.blackalphatgt:
                    if self.blackalpha < self.blackalphatgt - 16:
                        self.blackalpha += 15
                    else:
                        self.blackalpha += 1
            self.ticks2 = pygame.time.get_ticks()

    def cuecheck(self, topline: list[str]) -> None:
        """Apply queued lighting cues."""
        played = ""
        for i in list(self.cues.keys()):
            if i == topline[0][:10]:
                self.blackalphatgt = self.cues[i]
                played = i
        if played != "":
            del self.cues[played]

    def alpha(self, alpha: int, cue: str) -> None:
        """Queue a lighting cue."""
        self.cues[cue] = alpha


class Reset:
    """Queued display reset cue."""

    def __init__(self) -> None:
        """Create an empty reset cue queue."""
        self.cues: dict[str, str] = {}

    def cuecheck(self, topline: list[str]) -> str | None:
        """Return reset when a queued cue is reached."""
        for i in list(self.cues.keys()):
            if i == topline[0][:10]:
                del self.cues[i]
                return "reset"
        return None

    def addcue(self, cue: str) -> None:
        """Queue a reset cue."""
        self.cues[cue] = "reset"


class TimeFilter:
    """The filter for time colour effects. Now only used on title menu."""

    def __init__(self) -> None:
        """Create the title-menu time filter."""
        self.sky = pygame.Surface((800, 600))
        self.colourlist = [BLUE, AFTERNOON, SUNK, ORANGE, DARKBLUE, ABBLACK, BLACK]
        self.colour = pygame.Color(*BLUE)
        self.colourtgt = pygame.Color(*AFTERNOON)
        self.ticks = pygame.time.get_ticks()
        self.ticks2 = pygame.time.get_ticks()
        self.ticks2index = 0
        self.sunstart = (1000, -100)
        self.sunpos = (400, 300)
        self.sun = (GREY, self.sunpos, 100)
        self.stars: list[tuple[int, int]] = []
        self.starstick = pygame.time.get_ticks()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the filter overlay."""
        self.colchange()
        self.sky.fill(self.colour)
        pygame.draw.circle(self.sky, *self.sun)
        self.stardraw(surface)
        self.sky.set_alpha(40)
        surface.blit(self.sky, (0, 0))

    def menu(self) -> None:
        """Advance title-menu time and colour state."""
        t = pygame.time.get_ticks() - self.ticks2
        i = t // 10000
        self.sunmove(t)
        if t >= 65000:
            self.ticks2 = pygame.time.get_ticks()
        elif self.colour == self.colourtgt and i != self.ticks2index:
            if i >= len(self.colourlist) - 1:
                self.colmove()
            else:
                self.colmove(self.colourlist[i])
                self.ticks2index = i

    def stardraw(self, surface: pygame.Surface) -> None:
        """Draw stars when the menu is dark enough."""
        time = pygame.time.get_ticks()

        if (
            self.colourtgt == DARKBLUE
            or self.colourtgt == ABBLACK
            or self.colourtgt == BLACK
        ):
            if len(self.stars) < 20 and time - self.starstick >= 500:
                x = random.randint(5, 800)
                y = random.randint(5, 200)
                self.stars.append((x, y))
                self.starstick = pygame.time.get_ticks()

            if len(self.stars) > 0:
                for i in self.stars:
                    rec = (i[0], i[1], 3, 3)
                    pygame.draw.rect(surface, GREY, rec)
        else:
            del self.stars[:]

    def sunmove(self, tick: int) -> None:
        """Move the title-menu sun."""
        i = int((tick / 12000.0) * 100)
        sunx = self.sunstart[0] - (3 * i)
        suny = self.sunstart[1] + i
        self.sunpos = (sunx, suny)
        self.sun = (GREY, self.sunpos, 100)

    def colmove(self, *col: Any) -> None:
        """Move the filter toward a new target colour."""
        if len(col) != 0:
            if col[0] in self.colourlist:
                self.colourtgt = pygame.Color(*col[0])
        else:
            for i, v in enumerate(self.colourlist):
                if self.colour == pygame.Color(*v):
                    if i == len(self.colourlist) - 1:
                        self.colourtgt = pygame.Color(*self.colourlist[0])
                    else:
                        self.colourtgt = pygame.Color(*self.colourlist[i + 1])

    def colchange(self) -> None:
        """Step the filter colour toward its target."""
        if (
            self.colour != self.colourtgt
            and (pygame.time.get_ticks() - self.ticks) >= 10
        ):
            a = self.colour.normalize()
            b = self.colourtgt.normalize()
            newcol = [0, 0, 0, 0]
            for rgb, value in enumerate(a):
                nval = int(value * 255)
                if nval > int(b[rgb] * 255):
                    nval -= 1
                    newcol[rgb] = nval
                elif nval < int(b[rgb] * 255):
                    nval += 1
                    newcol[rgb] = nval
                else:
                    newcol[rgb] = nval
            x = tuple(newcol)
            self.colour = pygame.Color(*x)
            self.ticks = pygame.time.get_ticks()


class Smoke:
    """The smoke on the title menu."""

    def __init__(self, pos: tuple[int, int]) -> None:
        """Create a smoke particle."""
        self.pos = pos
        self.size = (2, 2)
        self.alpha = 240
        self.smokesurface = pygame.Surface(self.size)
        self.collist = [GREY, BGGREY, BLACK, ABBLACK]
        self.smokecol = self.collist[random.randint(0, 3)]
        self.maxx = self.pos[0] + 5 + random.randint(0, 3)
        self.ticks = pygame.time.get_ticks()
        self.done = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the smoke particle."""
        if self.done is False:
            self.move()
            self.smokesurface.fill(self.smokecol)
            self.smokesurface.set_alpha(self.alpha)
            surface.blit(self.smokesurface, self.pos)

    def move(self) -> None:
        """Move the smoke particle."""
        time = pygame.time.get_ticks()
        if time - self.ticks >= 50:
            if self.size[0] < 7:
                x = self.size[0] + 1
                y = self.size[1] + 1
                self.size = (x, y)
                self.smokesurface = pygame.Surface(self.size)

            if self.pos[0] < self.maxx:
                x1 = self.pos[0] + 1
                y1 = self.pos[1] - 3
                self.pos = (x1, y1)
            else:
                if self.done is False:
                    x1 = self.pos[0]
                    y1 = self.pos[1] - 2
                    self.pos = (x1, y1)
                    self.alpha -= 10
                    if self.alpha == 0:
                        self.done = True

            self.ticks = pygame.time.get_ticks()
