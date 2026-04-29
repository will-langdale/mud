"""Narrative text asset loading."""

from __future__ import annotations

import configparser
from importlib import resources
from importlib.resources.abc import Traversable
from string import Formatter

from mud.engine.exceptions import MissingTextError


class CaseConfigParser(configparser.ConfigParser):
    """Config parser that preserves text asset key case."""

    def optionxform(self, optionstr: str) -> str:
        """Return option keys unchanged."""
        return optionstr


class TextStore:
    """Load and render INI-style text assets."""

    def __init__(self) -> None:
        """Create an empty text store."""
        self._values: dict[str, str] = {}

    @classmethod
    def load(cls) -> TextStore:
        """Load all bundled ``assets/text/**/*.txt`` files."""
        store = cls()
        root = resources.files("mud").joinpath("assets", "text")
        for asset in sorted(_text_assets(root), key=lambda item: str(item)):
            parser = CaseConfigParser(interpolation=None)
            parser.read_string(asset.read_text(encoding="utf-8"))
            for section in parser.sections():
                for key, value in parser.items(section):
                    store.add(f"{section}.{key}", value.strip())
        return store

    def add(self, key: str, value: str) -> None:
        """Add a text value."""
        if key in self._values:
            msg = f"Duplicate text asset key: {key}"
            raise ValueError(msg)
        self._values[key] = value

    def get(self, key: str) -> str:
        """Return a raw text value."""
        try:
            return self._values[key]
        except KeyError as exc:
            raise MissingTextError(key) from exc

    def render(self, key: str, **values: object) -> str:
        """Render a text value with named placeholders."""
        return self.get(key).format(**values)

    def keys(self) -> set[str]:
        """Return all loaded text keys."""
        return set(self._values)

    def placeholders(self, key: str) -> set[str]:
        """Return placeholder names used by a text value."""
        return {
            name
            for _, name, _, _ in Formatter().parse(self.get(key))
            if name is not None
        }


def _text_assets(root: Traversable) -> list[Traversable]:
    """Return text assets under a resources tree."""
    assets: list[Traversable] = []
    for child in root.iterdir():
        if child.is_dir():
            assets.extend(_text_assets(child))
        elif child.is_file() and child.name.endswith(".txt"):
            assets.append(child)
    return assets
