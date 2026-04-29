"""Resource and text asset tests."""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest

from mud.engine.exceptions import MissingTextError
from mud.engine.text import TextStore
from mud.resources import audio_path, font_path, image_path, text_path


def test_runtime_resources_resolve_from_package_assets() -> None:
    """Fonts, images, audio, and text resolve through mud.resources."""
    assert Path(font_path("vcr.ttf")).is_file()
    assert Path(image_path("bg1.png")).is_file()
    assert Path(audio_path("plane.ogg")).is_file()
    assert text_path("intro.txt").is_file()


def test_text_store_loads_grouped_assets_and_placeholders() -> None:
    """Grouped text files expose stable renderable keys."""
    text = TextStore.load()
    keys = text.keys()

    assert text.get("intro.help_prompt") == "Type HELP at the prompt for commands."
    assert "system.help" in keys
    assert text.placeholders("placeholders.movement") == {"direction"}
    assert text.render("placeholders.movement", direction="north") == (
        "You manage to go north."
    )


def test_text_store_reports_missing_keys_clearly() -> None:
    """Missing text keys should not surface as raw KeyError reprs."""
    text = TextStore.load()

    with pytest.raises(MissingTextError, match="Missing text asset key: missing.key"):
        text.get("missing.key")


def test_literal_text_asset_references_exist() -> None:
    """Literal text keys referenced in source must exist in bundled assets."""
    text = TextStore.load()
    keys = text.keys()
    missing = []

    for path in Path("src/mud").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            key = literal_text_key(node)
            if key is not None and key not in keys:
                if isinstance(node, ast.expr):
                    missing.append(f"{path}:{node.lineno}: {key}")
                else:
                    missing.append(f"{path}:?: {key}")

    assert missing == []


def test_package_data_patterns_include_assets() -> None:
    """Package metadata configuration includes bundled asset patterns."""
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_data = pyproject["tool"]["setuptools"]["package-data"]["mud"]

    assert "assets/audio/*.ogg" in package_data
    assert "assets/fonts/*.ttf" in package_data
    assert "assets/images/*.png" in package_data
    assert "assets/text/**/*.txt" in package_data


def literal_text_key(node: ast.AST) -> str | None:
    """Return a literal text asset key referenced by a call node."""
    if not isinstance(node, ast.Call) or not node.args:
        return None
    first = node.args[0]
    if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
        return None

    if isinstance(node.func, ast.Name) and node.func.id == "t":
        return first.value
    if not isinstance(node.func, ast.Attribute):
        return None
    if node.func.attr not in {"get", "render", "placeholders"}:
        return None
    if "." not in first.value:
        return None
    return first.value
