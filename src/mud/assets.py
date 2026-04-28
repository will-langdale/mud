"""Asset path helpers."""

from __future__ import annotations

from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"


def asset_path(name: str) -> str:
    """Return the filesystem path for a bundled asset."""
    return str(ASSET_DIR / name)
