"""Resource and text asset tests."""

from __future__ import annotations

import ast
import shutil
import tomllib
from pathlib import Path

import pytest

from mud.engine.exceptions import MissingTextError, TextAssetError
from mud.engine.text import TextAssets
from mud.resources import audio_path, font_path, image_path, text_path


def test_runtime_resources_resolve_from_package_assets() -> None:
    """Fonts, images, audio, and text resolve through mud.resources."""
    assert Path(font_path("vcr.ttf")).is_file()
    assert Path(image_path("bg1.png")).is_file()
    assert Path(audio_path("plane.ogg")).is_file()
    assert text_path("intro.txt").is_file()


def test_text_assets_load_typed_catalog_and_placeholders() -> None:
    """Grouped text files expose stable typed fields."""
    text = TextAssets.load()

    assert text.intro.help_prompt == "Type HELP at the prompt for commands."
    assert "You can GO NORTH, SOUTH, EAST or WEST." in text.system.help
    assert text.items["lighter"].look.startswith("Beneath caked mud")
    assert text.locations["plane"].first.startswith("The hot, twisted metal")
    assert text.random.movement[2] == "You manage to go %s."
    assert text.placeholders(text.templates.movement) == {"direction"}
    assert text.render(text.templates.movement, direction="north") == (
        "You manage to go north."
    )


def test_text_assets_report_missing_keys_clearly() -> None:
    """Missing text keys should not surface as raw KeyError reprs."""
    with pytest.raises(
        MissingTextError, match="Missing text asset key: intro.help_prompt"
    ):
        TextAssets.from_values({})


def test_text_assets_reject_legacy_keys() -> None:
    """Line-numbered legacy keys should not come back."""
    with pytest.raises(
        TextAssetError,
        match="Legacy text asset key is not allowed: legacy.line_0001",
    ):
        TextAssets.from_values({"legacy.line_0001": "Nope."})


def test_text_assets_reject_unused_asset_keys(tmp_path: Path) -> None:
    """Unexpected asset keys should fail at load time."""
    asset_root = tmp_path / "text"
    shutil.copytree(Path("src/mud/assets/text"), asset_root)
    (asset_root / "extra.txt").write_text(
        "[unexpected]\nvalue = This key is not mapped.\n",
        encoding="utf-8",
    )

    with pytest.raises(
        TextAssetError,
        match=r"Unused text asset key: unexpected.value .*extra.txt",
    ):
        TextAssets.load(asset_root)


def test_text_assets_report_duplicate_asset_sources(tmp_path: Path) -> None:
    """Duplicate semantic keys should identify the colliding key."""
    asset_root = tmp_path / "text"
    shutil.copytree(Path("src/mud/assets/text"), asset_root)
    (asset_root / "duplicate.txt").write_text(
        "[intro]\nhelp_prompt = Duplicate.\n",
        encoding="utf-8",
    )

    with pytest.raises(
        TextAssetError,
        match="Duplicate text asset key: intro.help_prompt",
    ):
        TextAssets.load(asset_root)


def test_runtime_code_avoids_legacy_text_keys_and_raw_text_gets() -> None:
    """Runtime code should use TextAssets fields, not raw asset keys."""
    violations: list[str] = []

    for path in Path("src/mud").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and "legacy.line_" in node.value
            ):
                violations.append(f"{path}:{node.lineno}: {node.value}")
            if is_text_get_call(node):
                violations.append(
                    f"{path}:{getattr(node, 'lineno', '?')}: raw text.get call"
                )

    assert violations == []


def test_package_data_patterns_include_assets() -> None:
    """Package metadata configuration includes bundled asset patterns."""
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_data = pyproject["tool"]["setuptools"]["package-data"]["mud"]

    assert "assets/audio/*.ogg" in package_data
    assert "assets/fonts/*.ttf" in package_data
    assert "assets/images/*.png" in package_data
    assert "assets/text/**/*.txt" in package_data


def is_text_get_call(node: ast.AST) -> bool:
    """Return whether a node calls a runtime text catalog ``get`` method."""
    if not isinstance(node, ast.Call):
        return False
    if not isinstance(node.func, ast.Attribute) or node.func.attr != "get":
        return False
    return dotted_name(node.func.value) in {"engine.text", "self.text", "TEXT"}


def dotted_name(node: ast.AST) -> str:
    """Return a dotted name for simple attribute chains."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""
