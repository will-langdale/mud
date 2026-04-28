"""Pygbag entrypoint for Mud."""

from __future__ import annotations

import asyncio

import pygame

WINDOW = (800, 600)
BLACK = (0, 0, 0)


async def prime_canvas() -> None:
    """Open one browser frame before importing the game UI."""
    pygame.init()
    pygame.display.set_caption("Mud")
    screen = pygame.display.set_mode(WINDOW)
    screen.fill(BLACK)
    pygame.display.flip()
    await asyncio.sleep(0)


async def main() -> None:
    """Prime pygbag's canvas, then start the game."""
    await prime_canvas()

    # Pygbag needs this import after the browser canvas has opened.
    from mud.ui import main as ui_main  # noqa: PLC0415

    await ui_main()


asyncio.run(main())
