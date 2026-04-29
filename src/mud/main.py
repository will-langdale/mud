"""Mud's Pygame entrypoint."""

from __future__ import annotations

import asyncio

from mud.ui import main


def run() -> None:
    """Run Mud's Pygame UI."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
