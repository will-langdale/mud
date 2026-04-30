"""Narrative text asset loading."""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from string import Formatter
from types import MappingProxyType
from typing import Self

from mud.engine.exceptions import MissingTextError, TextAssetError


class CaseConfigParser(configparser.ConfigParser):
    """Config parser that preserves text asset key case."""

    def optionxform(self, optionstr: str) -> str:
        """Return option keys unchanged."""
        return optionstr


@dataclass(frozen=True, slots=True)
class IntroText:
    """Intro and restart text."""

    help_prompt: str
    first_run: str
    restart_early: str
    restart_mid: str
    restart_late: str
    final_ending: str
    final_credit: str


@dataclass(frozen=True, slots=True)
class CreditsText:
    """Credits screen text."""

    none: str
    earth: str
    stone: str
    default: str
    full: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SystemText:
    """General engine and UI text."""

    help: str
    invalid: str
    confused: str
    blocked: str
    unreachable: str
    alone_wait: str
    where_go: str
    no_pages: str
    medkit_hint: str
    no_options: str
    exit_confirm: str
    title_prompt: str
    space_prompt: str


@dataclass(frozen=True, slots=True)
class ArtifactText:
    """Artifact hint and discovery text."""

    intrusion: str
    earth: str
    stone: str
    smoke: str
    smoke_found: str


@dataclass(frozen=True, slots=True)
class TemplateText:
    """Renderable text templates."""

    movement: str
    look_direction: str
    room_return: str
    forest_tracks: str
    think_single: str
    think_many: str


@dataclass(frozen=True, slots=True)
class ItemText:
    """Narrative text attached to one item."""

    first: str
    look: str
    search: str


@dataclass(frozen=True, slots=True)
class LocationText:
    """Narrative text attached to one location."""

    name: str
    first: str
    look: str
    search: str
    restriction: str


@dataclass(frozen=True, slots=True)
class StumpActionText:
    """Text for stump actions."""

    climb: str
    climb_item_first: str
    climb_location_first: str
    climb_search: str
    smash: str
    smash_item_first: str
    smash_location_first: str
    smash_search: str
    broken_name: str
    wade: str
    through: str


@dataclass(frozen=True, slots=True)
class ForestActionText:
    """Text for dense forest actions."""

    wood_climb: str
    search_empty: str
    edge: str
    captivity_death: str


@dataclass(frozen=True, slots=True)
class SwampActionText:
    """Text for swamp actions."""

    tree_climb: str
    leeches_begin: str


@dataclass(frozen=True, slots=True)
class LeechActionText:
    """Text for leech actions."""

    remove: str


@dataclass(frozen=True, slots=True)
class LighterActionText:
    """Text for lighter actions."""

    spark: str


@dataclass(frozen=True, slots=True)
class SearchActionText:
    """Text for special search actions."""

    fighter_searched: str
    fighter_found: str
    pages_search: str
    pages_found: str


@dataclass(frozen=True, slots=True)
class SandActionText:
    """Text for sand actions."""

    escape: str
    death: str


@dataclass(frozen=True, slots=True)
class TroopActionText:
    """Text for troop actions."""

    approach_death: str
    fall_back: str
    voices: str


@dataclass(frozen=True, slots=True)
class StoneActionText:
    """Text for stone actions."""

    listen: str
    troops_close: str
    climb: str


@dataclass(frozen=True, slots=True)
class CaveActionText:
    """Text for cave actions."""

    enter: str
    fall: str
    landing: str
    sense_small: str
    sense_medium: str
    sense_large: str
    sense_unknown: str
    return_: str


@dataclass(frozen=True, slots=True)
class FlareActionText:
    """Text for flare actions."""

    after_look: str
    after_search: str
    fire: str


@dataclass(frozen=True, slots=True)
class BoxActionText:
    """Text for box actions."""

    box3_empty: str
    box3_found: str
    box4_empty: str
    box4_found: str


@dataclass(frozen=True, slots=True)
class MedkitActionText:
    """Text for medkit actions."""

    use_poisoned: str
    use_unneeded: str


@dataclass(frozen=True, slots=True)
class BoatActionText:
    """Text for boat actions."""

    enter: str
    death: str
    swept_right: str
    nightmares: str
    restart: str


@dataclass(frozen=True, slots=True)
class WaterActionText:
    """Text for water actions."""

    enter: str
    death: str
    escape: str


@dataclass(frozen=True, slots=True)
class FogActionText:
    """Text for fog actions."""

    inside_first: str
    escape: str
    return_first: str


@dataclass(frozen=True, slots=True)
class ActionText:
    """Text grouped by action subsystem."""

    stump: StumpActionText
    forest: ForestActionText
    swamp: SwampActionText
    leeches: LeechActionText
    lighter: LighterActionText
    search: SearchActionText
    sand: SandActionText
    troops: TroopActionText
    stones: StoneActionText
    cave: CaveActionText
    flare: FlareActionText
    boxes: BoxActionText
    medkit: MedkitActionText
    boat: BoatActionText
    water: WaterActionText
    fog: FogActionText


@dataclass(frozen=True, slots=True)
class SinkingStatusText:
    """Sinking status text."""

    trouble: str
    warning: str
    stuck: str
    death: str
    face_cave: str
    face_open: str
    chest: str
    legs: str


@dataclass(frozen=True, slots=True)
class PoisonStatusText:
    """Poison status text."""

    death: str
    severe: str
    early: str


@dataclass(frozen=True, slots=True)
class LeechesStatusText:
    """Leech status text."""

    poisoned: str


@dataclass(frozen=True, slots=True)
class TimeStatusText:
    """Time status text."""

    death: str


@dataclass(frozen=True, slots=True)
class StatusText:
    """Recurring status rule text."""

    sinking: SinkingStatusText
    poison: PoisonStatusText
    leeches: LeechesStatusText
    time: TimeStatusText


@dataclass(frozen=True, slots=True)
class RandomText:
    """Named banks for legacy random text."""

    movement: tuple[str, ...]
    mud: tuple[str, ...]
    time: tuple[str, ...]
    exhaustion: tuple[str, ...]
    waiting: tuple[str, ...]
    shouting: tuple[str, ...]
    fog: tuple[str, ...]
    leeches: tuple[str, ...]
    woods_lost: tuple[str, ...]
    woods_correct: tuple[str, ...]
    woods_escape: tuple[str, ...]
    woods: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _TextValue:
    value: str
    source: str


class _AssetBuilder:
    """Track semantic asset consumption while building typed text assets."""

    def __init__(self, values: dict[str, _TextValue]) -> None:
        self._values = values
        self._used: set[str] = set()

    def text(self, section: str, key: str) -> str:
        """Return one required text value."""
        asset_key = f"{section}.{key}"
        try:
            entry = self._values[asset_key]
        except KeyError as exc:
            raise MissingTextError(asset_key) from exc
        self._used.add(asset_key)
        return entry.value

    def section(self, section: str) -> tuple[str, ...]:
        """Return a numeric section as a tuple sorted by index."""
        prefix = f"{section}."
        pairs: list[tuple[int, str, str]] = []
        for key, entry in self._values.items():
            if not key.startswith(prefix):
                continue
            index_key = key.removeprefix(prefix)
            try:
                index = int(index_key)
            except ValueError as exc:
                msg = f"Text sequence key must be numeric: {key} ({entry.source})"
                raise TextAssetError(msg) from exc
            pairs.append((index, key, entry.value))
        if not pairs:
            raise MissingTextError(section)
        ordered = sorted(pairs, key=lambda pair: pair[0])
        expected = list(range(1, len(ordered) + 1))
        actual = [index for index, _, _ in ordered]
        if actual != expected:
            msg = f"Text sequence keys must be contiguous for {section}: {actual}"
            raise TextAssetError(msg)
        self._used.update(key for _, key, _ in ordered)
        return tuple(value for _, _, value in ordered)

    def assert_all_used(self) -> None:
        """Reject asset keys that are not part of the typed catalog."""
        unused = sorted(set(self._values) - self._used)
        if unused:
            key = unused[0]
            entry = self._values[key]
            msg = f"Unused text asset key: {key} ({entry.source})"
            raise TextAssetError(msg)


@dataclass(frozen=True, slots=True)
class TextAssets:
    """Typed catalog of all narrative text assets."""

    intro: IntroText
    credits: CreditsText
    system: SystemText
    artifacts: ArtifactText
    templates: TemplateText
    items: MappingProxyType[str, ItemText]
    locations: MappingProxyType[str, LocationText]
    actions: ActionText
    status: StatusText
    random: RandomText

    @classmethod
    def load(cls, root: Traversable | Path | None = None) -> Self:
        """Load and validate all bundled ``assets/text/**/*.txt`` files."""
        if root is None:
            root = resources.files("mud").joinpath("assets", "text")
        return cls._from_values(_load_text_values(root))

    @classmethod
    def from_values(cls, values: dict[str, str]) -> Self:
        """Build text assets from raw values for validation tests."""
        return cls._from_values(
            {key: _TextValue(value, "<memory>") for key, value in values.items()}
        )

    @classmethod
    def _from_values(cls, values: dict[str, _TextValue]) -> Self:
        _reject_legacy_keys(values)
        builder = _AssetBuilder(values)

        item_ids = [
            "lighter",
            "fighter",
            "stump",
            "route",
            "pages",
            "swamptrees",
            "woodtrees",
            "leeches",
            "sandtrap",
            "trooptrap",
            "stones",
            "cavetrap",
            "box1",
            "box2",
            "flare",
            "box3",
            "medkit",
            "box4",
            "bodies",
            "boat",
            "water",
            "aagun",
        ]
        location_ids = [
            "plane",
            "snake",
            "sand",
            "sand_in",
            "debris",
            "fog",
            "blanksw",
            "log",
            "swamp",
            "gun",
            "cave",
            "cave_in",
            "wood",
            "wood_in",
            "river",
            "troops",
            "troops_in",
            "blankse",
            "blanknw",
            "blankne",
        ]

        assets = cls(
            intro=IntroText(
                help_prompt=builder.text("intro", "help_prompt"),
                first_run=builder.text("intro", "first_run"),
                restart_early=builder.text("intro", "restart_early"),
                restart_mid=builder.text("intro", "restart_mid"),
                restart_late=builder.text("intro", "restart_late"),
                final_ending=builder.text("intro", "final_ending"),
                final_credit=builder.text("intro", "final_credit"),
            ),
            credits=CreditsText(
                none=builder.text("credits", "none"),
                earth=builder.text("credits", "earth"),
                stone=builder.text("credits", "stone"),
                default=builder.text("credits", "default"),
                full=builder.section("credits.full"),
            ),
            system=SystemText(
                help=builder.text("system", "help"),
                invalid=builder.text("system", "invalid"),
                confused=builder.text("system", "confused"),
                blocked=builder.text("system", "blocked"),
                unreachable=builder.text("system", "unreachable"),
                alone_wait=builder.text("system", "alone_wait"),
                where_go=builder.text("system", "where_go"),
                no_pages=builder.text("system", "no_pages"),
                medkit_hint=builder.text("system", "medkit_hint"),
                no_options=builder.text("system", "no_options"),
                exit_confirm=builder.text("system", "exit_confirm"),
                title_prompt=builder.text("system", "title_prompt"),
                space_prompt=builder.text("system", "space_prompt"),
            ),
            artifacts=ArtifactText(
                intrusion=builder.text("artifacts", "intrusion"),
                earth=builder.text("artifacts", "earth"),
                stone=builder.text("artifacts", "stone"),
                smoke=builder.text("artifacts", "smoke"),
                smoke_found=builder.text("artifacts", "smoke_found"),
            ),
            templates=TemplateText(
                movement=builder.text("templates", "movement"),
                look_direction=builder.text("templates", "look_direction"),
                room_return=builder.text("templates", "room_return"),
                forest_tracks=builder.text("templates", "forest_tracks"),
                think_single=builder.text("templates", "think_single"),
                think_many=builder.text("templates", "think_many"),
            ),
            items=MappingProxyType(
                {
                    item_id: ItemText(
                        first=builder.text(f"items.{item_id}", "first"),
                        look=builder.text(f"items.{item_id}", "look"),
                        search=builder.text(f"items.{item_id}", "search"),
                    )
                    for item_id in item_ids
                }
            ),
            locations=MappingProxyType(
                {
                    location_id: LocationText(
                        name=builder.text(f"locations.{location_id}", "name"),
                        first=builder.text(f"locations.{location_id}", "first"),
                        look=builder.text(f"locations.{location_id}", "look"),
                        search=builder.text(f"locations.{location_id}", "search"),
                        restriction=builder.text(
                            f"locations.{location_id}", "restriction"
                        ),
                    )
                    for location_id in location_ids
                }
            ),
            actions=ActionText(
                stump=StumpActionText(
                    climb=builder.text("actions.stump", "climb"),
                    climb_item_first=builder.text("actions.stump", "climb_item_first"),
                    climb_location_first=builder.text(
                        "actions.stump", "climb_location_first"
                    ),
                    climb_search=builder.text("actions.stump", "climb_search"),
                    smash=builder.text("actions.stump", "smash"),
                    smash_item_first=builder.text("actions.stump", "smash_item_first"),
                    smash_location_first=builder.text(
                        "actions.stump", "smash_location_first"
                    ),
                    smash_search=builder.text("actions.stump", "smash_search"),
                    broken_name=builder.text("actions.stump", "broken_name"),
                    wade=builder.text("actions.stump", "wade"),
                    through=builder.text("actions.stump", "through"),
                ),
                forest=ForestActionText(
                    wood_climb=builder.text("actions.forest", "wood_climb"),
                    search_empty=builder.text("actions.forest", "search_empty"),
                    edge=builder.text("actions.forest", "edge"),
                    captivity_death=builder.text("actions.forest", "captivity_death"),
                ),
                swamp=SwampActionText(
                    tree_climb=builder.text("actions.swamp", "tree_climb"),
                    leeches_begin=builder.text("actions.swamp", "leeches_begin"),
                ),
                leeches=LeechActionText(
                    remove=builder.text("actions.leeches", "remove"),
                ),
                lighter=LighterActionText(
                    spark=builder.text("actions.lighter", "spark"),
                ),
                search=SearchActionText(
                    fighter_searched=builder.text("actions.search", "fighter_searched"),
                    fighter_found=builder.text("actions.search", "fighter_found"),
                    pages_search=builder.text("actions.search", "pages_search"),
                    pages_found=builder.text("actions.search", "pages_found"),
                ),
                sand=SandActionText(
                    escape=builder.text("actions.sand", "escape"),
                    death=builder.text("actions.sand", "death"),
                ),
                troops=TroopActionText(
                    approach_death=builder.text("actions.troops", "approach_death"),
                    fall_back=builder.text("actions.troops", "fall_back"),
                    voices=builder.text("actions.troops", "voices"),
                ),
                stones=StoneActionText(
                    listen=builder.text("actions.stones", "listen"),
                    troops_close=builder.text("actions.stones", "troops_close"),
                    climb=builder.text("actions.stones", "climb"),
                ),
                cave=CaveActionText(
                    enter=builder.text("actions.cave", "enter"),
                    fall=builder.text("actions.cave", "fall"),
                    landing=builder.text("actions.cave", "landing"),
                    sense_small=builder.text("actions.cave", "sense_small"),
                    sense_medium=builder.text("actions.cave", "sense_medium"),
                    sense_large=builder.text("actions.cave", "sense_large"),
                    sense_unknown=builder.text("actions.cave", "sense_unknown"),
                    return_=builder.text("actions.cave", "return"),
                ),
                flare=FlareActionText(
                    after_look=builder.text("actions.flare", "after_look"),
                    after_search=builder.text("actions.flare", "after_search"),
                    fire=builder.text("actions.flare", "fire"),
                ),
                boxes=BoxActionText(
                    box3_empty=builder.text("actions.boxes", "box3_empty"),
                    box3_found=builder.text("actions.boxes", "box3_found"),
                    box4_empty=builder.text("actions.boxes", "box4_empty"),
                    box4_found=builder.text("actions.boxes", "box4_found"),
                ),
                medkit=MedkitActionText(
                    use_poisoned=builder.text("actions.medkit", "use_poisoned"),
                    use_unneeded=builder.text("actions.medkit", "use_unneeded"),
                ),
                boat=BoatActionText(
                    enter=builder.text("actions.boat", "enter"),
                    death=builder.text("actions.boat", "death"),
                    swept_right=builder.text("actions.boat", "swept_right"),
                    nightmares=builder.text("actions.boat", "nightmares"),
                    restart=builder.text("actions.boat", "restart"),
                ),
                water=WaterActionText(
                    enter=builder.text("actions.water", "enter"),
                    death=builder.text("actions.water", "death"),
                    escape=builder.text("actions.water", "escape"),
                ),
                fog=FogActionText(
                    inside_first=builder.text("actions.fog", "inside_first"),
                    escape=builder.text("actions.fog", "escape"),
                    return_first=builder.text("actions.fog", "return_first"),
                ),
            ),
            status=StatusText(
                sinking=SinkingStatusText(
                    trouble=builder.text("status.sinking", "trouble"),
                    warning=builder.text("status.sinking", "warning"),
                    stuck=builder.text("status.sinking", "stuck"),
                    death=builder.text("status.sinking", "death"),
                    face_cave=builder.text("status.sinking", "face_cave"),
                    face_open=builder.text("status.sinking", "face_open"),
                    chest=builder.text("status.sinking", "chest"),
                    legs=builder.text("status.sinking", "legs"),
                ),
                poison=PoisonStatusText(
                    death=builder.text("status.poison", "death"),
                    severe=builder.text("status.poison", "severe"),
                    early=builder.text("status.poison", "early"),
                ),
                leeches=LeechesStatusText(
                    poisoned=builder.text("status.leeches", "poisoned"),
                ),
                time=TimeStatusText(
                    death=builder.text("status.time", "death"),
                ),
            ),
            random=RandomText(
                movement=builder.section("random.movement"),
                mud=builder.section("random.mud"),
                time=builder.section("random.time"),
                exhaustion=builder.section("random.exhaustion"),
                waiting=builder.section("random.waiting"),
                shouting=builder.section("random.shouting"),
                fog=builder.section("random.fog"),
                leeches=builder.section("random.leeches"),
                woods_lost=builder.section("random.woods_lost"),
                woods_correct=builder.section("random.woods_correct"),
                woods_escape=builder.section("random.woods_escape"),
                woods=builder.section("random.woods"),
            ),
        )
        builder.assert_all_used()
        return assets

    def render(self, template: str, **values: object) -> str:
        """Render a text template with named placeholders."""
        return template.format(**values)

    def placeholders(self, template: str) -> set[str]:
        """Return placeholder names used by a text template."""
        return {
            name for _, name, _, _ in Formatter().parse(template) if name is not None
        }


def _load_text_values(root: Traversable | Path) -> dict[str, _TextValue]:
    """Load all text asset values under a resources tree."""
    values: dict[str, _TextValue] = {}
    for asset in sorted(_text_assets(root), key=lambda item: str(item)):
        parser = CaseConfigParser(interpolation=None)
        source = str(asset)
        try:
            parser.read_string(asset.read_text(encoding="utf-8"), source=source)
        except configparser.Error as exc:
            raise TextAssetError(str(exc)) from exc
        for section in parser.sections():
            for key, value in parser.items(section):
                asset_key = f"{section}.{key}"
                new_value = _TextValue(value.strip(), f"{source}:{section}.{key}")
                if asset_key in values:
                    old = values[asset_key]
                    msg = (
                        f"Duplicate text asset key: {asset_key} "
                        f"({old.source}, {new_value.source})"
                    )
                    raise TextAssetError(msg)
                values[asset_key] = new_value
    return values


def _reject_legacy_keys(values: dict[str, _TextValue]) -> None:
    """Reject line-numbered legacy asset names."""
    for key, entry in values.items():
        if key.startswith("legacy."):
            msg = f"Legacy text asset key is not allowed: {key} ({entry.source})"
            raise TextAssetError(msg)


def _text_assets(root: Traversable | Path) -> list[Traversable | Path]:
    """Return text assets under a resources tree."""
    assets: list[Traversable | Path] = []
    for child in root.iterdir():
        if child.is_dir():
            assets.extend(_text_assets(child))
        elif child.is_file() and child.name.endswith(".txt"):
            assets.append(child)
    return assets
