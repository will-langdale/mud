"""Pygame application loop for Mud."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import cast

import pygame
from pygame.locals import (
    K_BACKSPACE,
    K_KP_ENTER,
    K_RETURN,
    K_SPACE,
    KEYDOWN,
    QUIT,
    TEXTINPUT,
)

from mud.engine import GameSession
from mud.events import Artifacts, MediaEvent
from mud.resources import audio_path, font_path, image_path
from mud.ui import text as ui_text
from mud.ui.audio import Music, SFXPlay
from mud.ui.background import BgImage, Reset
from mud.ui.constants import BLACK, BLUE, BROWN, CAPTION, LINES, WINDOW
from mud.ui.input import key_text, text_input
from mud.ui.screens import EndCredits, EndMenu, TextBox, TitleMenu
from mud.ui.text import Bodytext


@dataclass(slots=True)
class LoadedMedia:
    """Pygame media objects loaded during startup."""

    images: dict[str, pygame.Surface]
    sounds: dict[str, pygame.mixer.Sound]


async def yield_browser_frame() -> None:
    """Let the browser runtime process a frame during startup."""
    surface = pygame.display.get_surface()
    if surface is not None:
        pygame.event.pump()
        pygame.display.flip()
    await asyncio.sleep(0)


class Control:
    """Runs the game."""

    def __init__(self, media: LoadedMedia) -> None:
        """Create the game controller with loaded media."""
        self.media = media
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.done = False
        self.keys = pygame.key.get_pressed()
        self.textline = ""
        self.lineh = ui_text.body_font().get_linesize()
        self.text = Bodytext(self.textline, (55, 50 + (self.lineh // 2)))
        self.status = "menu"  # prompt / display / menu / credits / end
        self.complete = False
        self.listin: list[object] = []
        self.listtrunc: list[list[str]] = []
        self.listdisplay: list[list[str]] = []
        self.displaytick = pygame.time.get_ticks()
        self.pending_events: list[object] = []
        self.submitted_text = None
        self.input_queue: asyncio.Queue[str] = asyncio.Queue()
        self.start_requested = False
        self.session_task: asyncio.Task[None] | None = None
        self.textbox = TextBox()
        self.titlemenu = TitleMenu(
            self.media.images["BGTOP"],
            self.media.images["BGPLANE"],
        )
        self.artifacts: list[bool] = []
        self.credits: EndCredits | None = None
        self.bg = BgImage(self.media.images["BG"], self.media.images["FIGURE"])
        self.sfx = SFXPlay(self.media.sounds)
        self.reset = Reset()
        self.end = EndMenu()
        self.music = Music()
        self.music.change("menu", -1)
        self.session = GameSession(self.wait_for_input, self.emit, self.show_credits)

    def emit(self, event: object) -> None:
        """Collect an event from the game engine."""
        self.pending_events.append(event)

    def show_credits(self) -> None:
        """Switch to the credits screen when the game requests a quit."""
        self.status = "credits"

    def start_game(self) -> None:
        """Start the game from the title menu."""
        self.media.sounds["PLANE"].play()
        self.status = "display"
        self.start_requested = True

    def add_prompt_text(self, text: str) -> bool:
        """Append typed prompt text while preserving the input box width."""
        changed = False
        body = ui_text.body_font()
        for char in text:
            if body.size(self.textline + char)[0] < 680:
                self.textline += char
                changed = True
        return changed

    def refresh_text(self) -> None:
        """Refresh the rendered prompt text."""
        self.text = Bodytext(self.textline.lstrip(), (55, 50 + (self.lineh // 2)))

    def events(self) -> None:
        """Handle keyboard input."""
        events = pygame.event.get()
        has_text_input = any(e.type == TEXTINPUT for e in events)
        text_changed = False

        for e in events:
            if e.type == QUIT:
                self.done = True
            if e.type == TEXTINPUT:
                typed = text_input(e)
                if typed != "":
                    if self.status == "prompt":
                        text_changed = self.add_prompt_text(typed) or text_changed
                    elif self.status == "menu":
                        self.start_game()
            if e.type == KEYDOWN:
                typed = "" if has_text_input else key_text(e)
                if typed != "":
                    if self.status == "prompt":
                        text_changed = self.add_prompt_text(typed) or text_changed
                    elif self.status == "menu":
                        self.start_game()
                elif e.key == K_BACKSPACE:
                    if self.status == "prompt":
                        self.textline = self.textline[:-1]
                        text_changed = True
                    elif self.status == "menu":
                        self.start_game()
                elif e.key == K_SPACE:
                    if self.status == "display":
                        if self.listtrunc != []:
                            self.scroll(self.listtrunc.pop(0))
                        self.displaytick = pygame.time.get_ticks()
                        if len(self.listtrunc) == 0:
                            self.status = "prompt"
                    elif self.status == "prompt":
                        if ui_text.body_font().size(self.textline + " ")[0] < 680:
                            self.textline += " "
                            text_changed = True
                    elif self.status == "menu":
                        self.start_game()
                    elif self.status == "credits":
                        self.done = True
                    elif self.status == "end":
                        if self.listtrunc != []:
                            self.scroll(self.listtrunc.pop(0))
                        self.displaytick = pygame.time.get_ticks()
                        if len(self.listtrunc) == 0:
                            self.status = "credits"
                elif e.key in (K_RETURN, K_KP_ENTER):
                    if self.status == "prompt":
                        del self.listin[:]
                        del self.listtrunc[:]
                        self.scroll([self.textline.upper().lstrip()])
                        self.displaytick = pygame.time.get_ticks()
                        self.input_queue.put_nowait(self.textline)
                        self.textline = ""
                        text_changed = True
                    elif self.status == "menu":
                        self.start_game()

        if text_changed:
            self.refresh_text()

    def draw(self) -> None:
        """Draw everything."""
        if self.status == "menu":
            self.titlemenu.draw(self.screen)
        elif self.status == "credits":
            if self.credits is None:
                self.credits = EndCredits(self.artifacts)
            self.credits.draw(self.screen)
        elif self.status == "end":
            self.screen.fill(BLUE)
            self.end.draw(self.screen)
            self.bg.draw(self.screen, True)
            self.focus()
            self.printtext2()
            self.text.draw(self.screen)
        else:
            self.screen.fill(BROWN)
            self.bg.draw(self.screen, False)
            self.focus()
            self.printtext2()
            if self.listdisplay != []:
                self.sfx.cuecheck(self.listdisplay[0])
                self.bg.cuecheck(self.listdisplay[0])
                self.music.cuecheck(self.listdisplay[0])
                reset = self.reset.cuecheck(self.listdisplay[0])
                if reset == "reset":
                    del self.listdisplay[:]
            self.text.draw(self.screen)

    def focus(self) -> None:
        """Change text entry box based on prompt status."""
        if self.status == "prompt":
            self.textbox.draw(self.screen, 120, False)
        elif self.status == "display":
            self.textbox.draw(self.screen, 50, True)

    def recieve(self) -> None:
        """Get info from the game engine."""
        if self.status == "display" or self.status == "prompt":
            received_events = len(self.pending_events) > 0
            while self.pending_events:
                self.listin.append(self.pending_events.pop(0))
            if not received_events:
                return
            listintest = list(self.listin)
            for value in listintest:
                if isinstance(value, MediaEvent):
                    index = self.listin.index(value)
                    cue = self.previous_text_cue(index)
                    self.listin.pop(index)
                    if value.type == "sound":
                        if cue != "":
                            self.sfx.addsound(cast(str, value.name), cue)
                    elif value.type == "bg":
                        alpha = cast(int, value.name)
                        if cue != "":
                            self.bg.alpha(alpha, cue)
                        else:
                            self.bg.blackalphatgt = alpha
                    elif value.type == "music":
                        music = cast(tuple[str, int], value.name)
                        if cue != "":
                            self.music.addmusic(music, cue)
                        else:
                            self.music.change(*music)
                    elif value.type == "reset":
                        if cue != "":
                            self.reset.addcue(cue)
                    elif value.type == "end":
                        self.complete = True
                elif isinstance(value, Artifacts):
                    index = self.listin.index(value)
                    self.listin.pop(index)
                    self.artifacts = value.artifacts
            self.listtrunc = self.linetrunc(self.listin)
            if self.listtrunc != []:
                self.status = "display"

    def previous_text_cue(self, index: int) -> str:
        """Return the cue text before an engine media event."""
        for value in reversed(self.listin[:index]):
            if isinstance(value, str):
                return value[:10]
        return ""

    def linetrunc(self, text: list[object]) -> list[list[str]]:
        """Break text into manageable lines."""
        toreturn = []
        body = ui_text.body_font()
        for i in text:
            phrase = []
            line = ""
            word = ""
            for x in cast(str, i):
                if body.size(line + word)[0] < 700:
                    if x != " ":
                        word += x
                    else:
                        word += x
                        line += word
                        word = ""
                    if x == "." or x == "?" or x == "~":
                        line += word
                        phrase.append(line.lstrip())
                        toreturn.append(phrase)
                        phrase = []
                        line = ""
                        word = ""
                else:
                    word += x
                    phrase.append(line.lstrip())
                    line = ""
                    if x == "." or x == "?" or x == "~":
                        line += word
                        phrase.append(line.lstrip())
                        toreturn.append(phrase)
                        phrase = []
                        line = ""
                        word = ""
            else:
                if line == " ":
                    phrase.append(" ")
            toreturn.append(phrase)

        toreturnclean = []
        for i in toreturn:
            if i != []:
                toreturnclean.append(i)
        return toreturnclean

    def scroll(self, newline: list[str]) -> None:
        """Move the entered text by a line, entering a new one."""
        self.listdisplay.insert(0, newline)
        linestest = self.listdisplay
        linesa = 0
        for i, v in enumerate(linestest):
            for w in v:
                linesa += 1
                if linesa > LINES:
                    self.listdisplay[i].remove(w)
        self.listdisplay = [x for x in self.listdisplay if x != []]

    def printtext2(self) -> None:
        """Print the lines to be displayed."""
        time = int((pygame.time.get_ticks() - self.displaytick) / 10)
        count = 0
        for index, text in enumerate(self.listdisplay):
            if count < LINES:
                if len(text) == 1:
                    if index == 0:
                        Bodytext(
                            text[0][:time],
                            (50, (50 + (2.5 * self.lineh) + (self.lineh * count))),
                        ).draw(self.screen)
                    else:
                        Bodytext(
                            text[0],
                            (50, (50 + (2.5 * self.lineh) + (self.lineh * count))),
                        ).draw(self.screen)
                    count += 1
                else:
                    if index == 0:
                        for i, item in enumerate(text):
                            if i > 0:
                                previt = 0
                                for p in text[i - 1 :: -1]:
                                    previt += len(p)
                                if time > previt:
                                    Bodytext(
                                        item[: time - previt],
                                        (
                                            50,
                                            (
                                                50
                                                + (2.5 * self.lineh)
                                                + (self.lineh * count)
                                            ),
                                        ),
                                    ).draw(self.screen)
                                count += 1
                            else:
                                Bodytext(
                                    item[:time],
                                    (
                                        50,
                                        (
                                            50
                                            + (2.5 * self.lineh)
                                            + (self.lineh * count)
                                        ),
                                    ),
                                ).draw(self.screen)
                                count += 1
                    else:
                        for item in text:
                            Bodytext(
                                item,
                                (50, (50 + (2.5 * self.lineh) + (self.lineh * count))),
                            ).draw(self.screen)
                            count += 1

    def gamequit(self) -> None:
        """Check whether the script has quit."""
        if self.done is True:
            self.status = "credits"

    async def wait_for_input(self) -> str:
        """Return the next submitted text command."""
        return await self.input_queue.get()

    def update_end_state(self) -> None:
        """Switch to the end screen when the final text is reached."""
        if (
            self.complete is True
            and len(self.listdisplay) > 0
            and self.listdisplay[0] == ["Endless filth."]
        ):
            self.status = "end"

    async def loop(self) -> None:
        """Run the game loop."""
        while not self.done:
            self.clock.tick(60)
            self.events()
            self.recieve()
            self.draw()
            self.gamequit()
            self.update_end_state()
            pygame.display.update()
            if self.start_requested is True:
                self.start_requested = False
                if self.session_task is None:
                    self.session_task = asyncio.create_task(self.session.run())
            if self.session_task is not None and self.session_task.done():
                self.session_task.result()
                self.session_task = None
            await asyncio.sleep(0)


async def load_media() -> LoadedMedia:
    """Load fonts, images, and sounds after Pygame is initialized."""
    ui_text.configure_fonts(
        pygame.font.Font(font_path("basica.ttf"), 200),
        pygame.font.Font(font_path("vcr.ttf"), 20),
    )
    await yield_browser_frame()

    images = {
        "BG": pygame.image.load(image_path("bg1.png")),
        "BGTOP": pygame.image.load(image_path("top6.png")).convert_alpha(),
        "BGPLANE": pygame.image.load(image_path("plane5050.png")).convert_alpha(),
        "FIGURE": pygame.image.load(image_path("figure.png")).convert_alpha(),
    }
    await yield_browser_frame()

    sounds = {
        "PLANE": pygame.mixer.Sound(audio_path("plane.ogg")),
        "RIVER": pygame.mixer.Sound(audio_path("river.ogg")),
        "WHISPERS": pygame.mixer.Sound(audio_path("whispers.ogg")),
        "BIRDS": pygame.mixer.Sound(audio_path("birds.ogg")),
        "DARK": pygame.mixer.Sound(audio_path("dark.ogg")),
        "BELLS": pygame.mixer.Sound(audio_path("bells.ogg")),
    }
    await yield_browser_frame()

    return LoadedMedia(images=images, sounds=sounds)


async def main() -> None:
    """Start Pygame and run the game loop."""
    pygame.init()

    pygame.display.set_caption(CAPTION)
    screen = pygame.display.set_mode(WINDOW)
    screen.fill(BLACK)
    await yield_browser_frame()

    pygame.key.start_text_input()
    pygame.key.set_repeat(500, 50)
    await yield_browser_frame()

    control = Control(await load_media())
    await yield_browser_frame()
    await control.loop()

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
