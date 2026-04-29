"""Helpers for loading packaged Mud resources."""

from __future__ import annotations

from contextlib import ExitStack
from importlib import resources
from pathlib import Path
from typing import Final

PACKAGE: Final = "mud"
ASSETS: Final = "assets"

_RESOURCE_FILES = ExitStack()


def resource_path(*parts: str) -> str:
    """Return a filesystem path for a packaged resource."""
    resource = resources.files(PACKAGE).joinpath(ASSETS, *parts)
    return str(_RESOURCE_FILES.enter_context(resources.as_file(resource)))


def audio_path(name: str) -> str:
    """Return a filesystem path for a bundled audio file."""
    return resource_path("audio", name)


def font_path(name: str) -> str:
    """Return a filesystem path for a bundled font file."""
    return resource_path("fonts", name)


def image_path(name: str) -> str:
    """Return a filesystem path for a bundled image file."""
    return resource_path("images", name)


def text_path(*parts: str) -> Path:
    """Return a filesystem path for a bundled text asset."""
    return Path(resource_path("text", *parts))
