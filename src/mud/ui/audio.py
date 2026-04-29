"""Music and sound effect cue handling."""

from __future__ import annotations

import pygame

from mud.resources import audio_path


class SFXPlay:
    """Handles sound cues."""

    def __init__(self, sounds: dict[str, pygame.mixer.Sound]) -> None:
        """Create a sound cue handler."""
        self.cues: dict[pygame.mixer.Sound, str] = {}
        self.sounds = sounds

    def play(self, sound: pygame.mixer.Sound) -> None:
        """Play a sound effect."""
        sound.play()

    def cuecheck(self, topline: list[str]) -> None:
        """Play sound effects queued for the current line."""
        played = None
        for sound in list(self.cues.keys()):
            if self.cues[sound] == topline[0][:10]:
                self.play(sound)
                played = sound
        if played is not None:
            del self.cues[played]

    def addsound(self, sound: str, cue: str) -> None:
        """Queue a sound effect by engine sound name."""
        self.cues[self.sounds[sound]] = cue


class Music:
    """Music track cue handling."""

    def __init__(self) -> None:
        """Create the music cue handler."""
        self.menu = audio_path("menu.ogg")
        self.credits = audio_path("credits.ogg")
        self.main = audio_path("main.ogg")
        self.cave = audio_path("cave.ogg")
        self.musiclib = {
            self.menu: "menu",
            self.credits: "credits",
            self.cave: "cave",
            self.main: "main",
        }

        self.cues: dict[tuple[str, int], str] = {}

    def change(self, music: str, rep: int) -> None:
        """Change the active music track."""
        pygame.mixer.music.stop()
        for path in list(self.musiclib.keys()):
            if music == self.musiclib[path]:
                pygame.mixer.music.load(path)
        if rep == 0:
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.play(rep)

    def cuecheck(self, topline: list[str]) -> None:
        """Apply queued music changes."""
        played = None
        for i in list(self.cues.keys()):
            if self.cues[i] == topline[0][:10]:
                self.change(*i)
                played = i
        if played is not None:
            del self.cues[played]

    def addmusic(self, name: tuple[str, int], cue: str) -> None:
        """Queue a music change."""
        music = name[0]

        for i in list(self.musiclib.keys()):
            if music == self.musiclib[i]:
                self.cues[name] = cue
