"""Engine exception types."""

from __future__ import annotations


class Death(Exception):
    """Raised internally when a traversal dies."""

    def __init__(self, text: str, artifacts: list[bool]) -> None:
        """Store the death text and artifact metadata."""
        super().__init__(text)
        self.text = text
        self.artifacts = artifacts


class Quit(Exception):
    """Raised internally when the traversal quits."""


class InputExhausted(Exception):
    """Raised by scripted sessions when no more input is available."""


class MissingTextError(KeyError):
    """Raised when engine code references an unknown text asset key."""

    def __init__(self, key: str) -> None:
        """Store the missing text key."""
        super().__init__(key)
        self.key = key

    def __str__(self) -> str:
        """Return a readable error message without KeyError repr noise."""
        return f"Missing text asset key: {self.key}"


class TextAssetError(ValueError):
    """Raised when bundled text assets are malformed."""
