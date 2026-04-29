"""Resource and text asset tests."""

from __future__ import annotations

import tomllib
from pathlib import Path

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


def test_package_data_patterns_include_assets() -> None:
    """Package metadata configuration includes bundled asset patterns."""
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_data = pyproject["tool"]["setuptools"]["package-data"]["mud"]

    assert "assets/audio/*.ogg" in package_data
    assert "assets/fonts/*.ttf" in package_data
    assert "assets/images/*.png" in package_data
    assert "assets/text/**/*.txt" in package_data
