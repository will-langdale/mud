"""Runtime engine for Mud."""

from __future__ import annotations

import inspect
import random
from collections.abc import Awaitable, Callable, Iterable, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import cast

from mud.engine import rules
from mud.engine.actions import ACTION_HANDLERS, describe_cave
from mud.engine.exceptions import Death, Quit
from mud.engine.model import GameState, Item, Location, World
from mud.engine.parser import dictmerge, parser
from mud.engine.text import TextAssets
from mud.engine.world import build_world as make_world
from mud.events import EngineEvent, MediaEvent

InputProvider = Callable[[], str | Awaitable[str]]
OutputHandler = Callable[[EngineEvent], None]
Token = tuple[str, str]


class EngineOutcome(Enum):
    """High-level result from a traversal."""

    DEATH = auto()
    QUIT = auto()
    FINAL_ENDING = auto()


@dataclass(slots=True)
class TraversalResult:
    """Result returned when a traversal stops internally."""

    outcome: EngineOutcome
    death_text: str = ""
    artifacts: list[bool] | None = None


class GameEngine:
    """Run one Mud traversal with explicit world and state objects."""

    directions = {
        "north": ["north", "n", "up", "u"],
        "east": ["east", "e", "right", "r"],
        "south": ["south", "s", "down", "d"],
        "west": ["west", "w", "left", "l"],
    }

    def __init__(
        self,
        input_provider: InputProvider,
        output_handler: OutputHandler,
        *,
        seed: int | None = None,
        rng: random.Random | None = None,
    ) -> None:
        """Create an engine traversal with deterministic optional RNG."""
        self.input_provider = input_provider
        self.output_handler = output_handler
        self.rng = rng if rng is not None else random.Random(seed)
        self.text = TextAssets.load()
        self.world = make_world(self.text)
        self.state = self._new_state()

    async def run(self, deaths: int, artifacts: list[bool]) -> TraversalResult:
        """Run this traversal until death, quit, final ending, or input exhaustion."""
        self.state.artifacts = artifacts
        try:
            await self.start(deaths)
            await self.loop()
        except Death as why:
            return TraversalResult(
                EngineOutcome.DEATH,
                why.text,
                list(why.artifacts),
            )
        except Quit:
            return TraversalResult(EngineOutcome.QUIT)
        return TraversalResult(EngineOutcome.FINAL_ENDING)

    def reset_traversal(self) -> None:
        """Reset traversal state while preserving RNG and callbacks."""
        artifacts = list(self.state.artifacts)
        cave_room = self.state.cave_room
        self.world = make_world(self.text)
        self.state = self._new_state(cave_room)
        self.state.artifacts = artifacts

    async def start(self, deaths: int) -> None:
        """Emit the traversal opening or the final ending."""
        if False not in self.state.artifacts:
            self.emit(MediaEvent("bg", 255))
            self.emit(" ")
            self.emit(MediaEvent("reset", ""))
            self.emit(self.text.intro.final_ending)
            self.emit(MediaEvent("bg", 0))
            self.emit(MediaEvent("end", 0))
            self.emit(" ")
            self.emit(self.text.intro.final_credit)
            raise Quit

        if deaths == 0:
            self.emit(MediaEvent("music", ("main", -1)))
            self.emit(self.text.intro.help_prompt)
            self.emit(MediaEvent("bg", 0))
            self.emit(" ")
            self.emit(self.text.intro.first_run)
        elif deaths <= 2:
            self.emit_restart(self.text.intro.restart_early)
        elif deaths <= 4:
            self.emit_restart(self.text.intro.restart_mid)
        else:
            self.emit_restart(self.text.intro.restart_late)

    async def loop(self) -> None:
        """Run the room/status/input loop."""
        while True:
            await self.status()
            await self.room()
            await self.whatnow()

    def emit_restart(self, restart_text: str) -> None:
        """Emit the standard restart sequence."""
        self.emit(MediaEvent("bg", 255))
        self.emit(" ")
        self.emit(MediaEvent("reset", ""))
        self.emit(restart_text)
        self.emit(MediaEvent("bg", 0))
        self.emit(MediaEvent("sound", "PLANE"))

    def emit(self, event: EngineEvent) -> None:
        """Emit an engine event."""
        self.output_handler(event)

    def rnd(self, values: Sequence[str]) -> str:
        """Return a legacy-style random list element."""
        return values[self.rng.randint(0, len(values) - 1)]

    async def prompt(self) -> str:
        """Return the next input command."""
        value = self.input_provider()
        if inspect.isawaitable(value):
            value = await value
        command = cast(str, value)
        self.state.textrecord.append(command)
        return command

    async def whatnow(self) -> None:
        """Parse and interpret one input command."""
        await self.interpret(self.parse(await self.prompt()))

    def parse(self, raw: object) -> list[Token]:
        """Parse input against commands, directions, subjects, and actions."""
        return parser(
            raw,
            dictmerge(
                self.direction_tokens(),
                self.command_tokens(),
                self.subject_tokens(),
                self.action_tokens(),
            ),
        )

    async def interpret(self, parsed: list[Token]) -> None:
        """Interpret parsed command tokens."""
        commands = self.extract(parsed, "command")
        dirs = self.extract(parsed, "direction")
        actions = self.extract(parsed, "action")
        subjects = self.extract(parsed, "subject")

        for group in (commands, dirs, actions, subjects):
            if len(group) > 1:
                self.emit(self.text.system.confused)
                await self.sink(0.25)
                self.state.turns += 0.25
                return
        if not commands and not dirs and not actions and not subjects:
            self.emit(self.text.system.invalid)
            await self.sink(0.25)
            self.state.turns += 0.25
            return

        if dirs and self.blocked(dirs[0], commands):
            await self.sink(0.25)
            self.state.turns += 0.25
            self.emit(self.text.system.blocked)
            return

        if self.state.condition("sinking").active:
            if actions or subjects:
                self.emit(self.text.system.unreachable)
                await self.sink(0.25)
                self.state.turns += 0.25
                return
            if "wait" in commands:
                self.emit(self.text.system.alone_wait)
                await self.sink(1)
                self.state.turns += 1
                return

        if commands and dirs:
            await self.run_command(commands[0], dirs[0])
        elif dirs:
            self.move(dirs[0])
        elif commands and subjects:
            await self.run_command(commands[0], subjects[0])
        elif commands:
            await self.run_command(commands[0], None)
        elif actions and subjects:
            await self.run_action(actions[0], subjects[0])
        elif actions:
            await self.run_action(actions[0], None)
        elif subjects:
            await self.look(subjects[0])

    async def run_command(self, command: str, target: str | None) -> None:
        """Run a general command."""
        if command == "look":
            await self.look(target)
        elif command == "move":
            if target is None:
                self.emit(self.text.system.where_go)
            else:
                self.move(target)
        elif command == "help":
            self.emit(self.text.system.help)
            await self.sink(0.25)
            self.state.turns += 0.25
        elif command == "think":
            await self.think()
        elif command == "search":
            await self.search(target)
        elif command == "wait":
            await self.wait()
        elif command == "shout":
            self.emit(self.rnd(self.world.random.shouting))
        elif command == "exit":
            await self.exit()

    async def run_action(self, action: str, target: str | None) -> None:
        """Run a world-specific action."""
        del target
        handler = ACTION_HANDLERS.get(action)
        if handler is None:
            self.emit(self.text.system.invalid)
            await self.sink(0.25)
            self.state.turns += 0.25
            return
        await handler(self)

    def blocked(self, destination: str, commands: list[str]) -> bool:
        """Return whether movement to a destination is blocked."""
        place = self.place()
        move_command = not commands or "move" in commands
        return move_command and (
            (place.restricted and destination != self.state.previous)
            or destination == self.state.current
        )

    def move(self, destination: str) -> None:
        """Move to a neighboring place."""
        if destination == "":
            self.emit(self.text.system.where_go)
            return
        self.state.turns += 2
        self.emit(self.rnd(self.world.random.mud))
        self.emit(
            self.rnd(self.world.random.movement) % self.direction_name(destination)
        )
        if not self.place().restricted:
            self.state.previous = self.state.current
        self.state.current = destination

    async def look(self, target: str | None) -> None:
        """Look at a room, direction, or item."""
        if target is None:
            if self.state.current == "cave_in":
                self.cave_think()
            else:
                self.emit(self.place().first)
                for item in self.visible_items():
                    self.emit(item.first)
        elif target in self.place().exits.values():
            self.emit(
                self.text.render(
                    self.text.templates.look_direction,
                    look=self.world.locations[target].look,
                )
            )
        else:
            item = self.world.items[target]
            if not item.hidden:
                self.emit(item.look)
        await self.sink(0.25)
        self.state.turns += 0.25

    async def wait(self) -> None:
        """Wait in the current room."""
        await self.sink(1)
        self.state.turns += 1
        self.emit(self.rnd(self.world.random.waiting))

    async def search(self, target: str | None) -> None:
        """Search the current room or a target."""
        self.state.turns += 1
        if target is not None:
            subject_ids = {item.id for item in self.subject_items()}
            if target in subject_ids and self.world.items[target].search == "":
                await self.search_inside(target)
            elif target in self.place().exits.values():
                await self.look(target)
            else:
                self.emit(self.world.items[target].search)
            return

        found_hidden = False
        for item in self.room_items():
            if item.hidden:
                item.hidden = False
                self.emit(item.first)
                found_hidden = True
        if found_hidden:
            return
        has_smoke_artifact = self.state.artifacts[2]
        if (
            self.place().look == "endless mud"
            and self.state.artifacts[:2] == [True, True]
            and not has_smoke_artifact
        ):
            self.state.artifacts[2] = True
            self.emit(self.text.artifacts.smoke_found)
            self.emit(MediaEvent("sound", "BELLS"))
        else:
            self.emit(self.place().search)
            if self.state.current != "troops_in":
                self.emit(self.rnd(self.world.random.mud))
            self.state.turns += 1

    async def search_inside(self, target: str) -> None:
        """Search inside an item."""
        if target == "fighter":
            if target in self.state.searched:
                self.emit(self.text.actions.search.fighter_searched)
            else:
                self.emit(self.text.actions.search.fighter_found)
            self.state.holding.add("lighter")
            self.state.searched.add("fighter")
        elif target == "pages":
            if target in self.state.searched:
                self.emit(self.text.system.no_pages)
            else:
                self.emit(self.text.actions.search.pages_search)
                self.emit(self.rnd(self.world.random.mud))
                self.emit(self.text.actions.search.pages_found)
                self.state.turns += 3
            self.state.holding.add("route")
            self.state.searched.add("pages")
            self.place().items.remove("pages")
        elif target == "box3":
            await self.run_action("box3_inside", None)
        elif target == "box4":
            await self.run_action("box4_inside", None)

    async def think(self) -> None:
        """List currently relevant actions."""
        for line in self.artifact_thoughts():
            self.emit(line)
        if self.state.condition("poison").active:
            self.emit(self.text.system.medkit_hint)
        if self.state.current == "cave_in":
            self.cave_think()
        active = [self.world.items[item] for item in self.active_item_ids()]
        options = self.think_text(self.room_items()) + self.think_text(active)
        if options in {"", "You can "}:
            self.emit(self.text.system.no_options)
        else:
            self.emit(options)
        await self.sink(0.25)
        self.state.turns += 0.25

    async def exit(self) -> None:
        """Ask for quit confirmation."""
        self.emit(self.text.system.exit_confirm)
        answer = parser(await self.prompt(), {"yes": ["yes", "y"], "no": ["no", "n"]})
        if "yes" in answer:
            raise Quit

    async def room(self) -> None:
        """Load the current room and trigger room-load actions."""
        place = self.place()
        if place.id not in self.state.visited:
            self.state.visited.add(place.id)
            if place.id != "cave_in":
                self.emit(place.first)
        elif place.id == "cave_in":
            self.emit(self.text.actions.cave.return_)
            self.state.turns += 3
        else:
            self.emit(
                self.text.render(self.text.templates.room_return, name=place.name)
            )

        if place.restricted:
            self.emit(place.restriction)
        for item in self.room_items(include_hidden=False):
            if item.name == "_load":
                for action in item.actions:
                    await self.run_action(action, None)

    async def status(self) -> None:
        """Apply recurring status rules."""
        rules.status(self)

    async def sink(self, amount: float = 1) -> None:
        """Apply sinking pressure for stationary actions."""
        await rules.sink(self, amount)

    def dead(self, why: str) -> None:
        """End this traversal with a death."""
        raise Death(why, list(self.state.artifacts))

    def cave_think(self) -> None:
        """Describe cave sense by room size."""
        describe_cave(self)

    def artifact_thoughts(self) -> list[str]:
        """Return artifact hint lines."""
        lines: list[str] = []
        if True in self.state.artifacts:
            lines.append(self.text.artifacts.intrusion)
        if self.state.artifacts[0]:
            lines.append(self.text.artifacts.earth)
        if self.state.artifacts[1]:
            lines.append(self.text.artifacts.stone)
        if self.state.artifacts[2]:
            lines.append(self.text.artifacts.smoke)
        return lines

    def think_text(self, items: Iterable[Item]) -> str:
        """Return the legacy action summary for items."""
        visible = [item for item in items if item.name != "_load" and not item.hidden]
        if not visible:
            return ""
        parts = []
        for item in visible:
            actions = list(item.actions.values())
            verb = (
                "search "
                if not actions
                else ", or ".join(action[0] for action in actions) + " "
            )
            parts.append(f"{verb}{item.name}")
        if len(parts) == 1:
            return self.text.render(self.text.templates.think_single, option=parts[0])
        return self.text.render(
            self.text.templates.think_many,
            options=", ".join(parts[:-1]),
            last_option=parts[-1],
        )

    def direction_tokens(self) -> dict[Token, list[str]]:
        """Return direction parser tokens for the current place."""
        aliases: dict[str, list[str]] = {}
        for direction, destination in self.place().exits.items():
            aliases.setdefault(destination, []).extend(self.directions[direction])
        return {
            ("direction", destination): words for destination, words in aliases.items()
        }

    def command_tokens(self) -> dict[Token, list[str]]:
        """Return general command parser tokens."""
        return {
            ("command", command): aliases
            for command, aliases in self.world.commands.items()
        }

    def subject_tokens(self) -> dict[Token, list[str]]:
        """Return visible and held subject parser tokens."""
        return {("subject", item.id): item.aliases for item in self.subject_items()}

    def action_tokens(self) -> dict[Token, list[str]]:
        """Return available action parser tokens."""
        actions: dict[str, list[str]] = {}
        for item in [
            *self.room_items(include_hidden=False),
            *[self.world.items[item] for item in self.active_item_ids()],
        ]:
            for action, aliases in item.actions.items():
                actions[action] = aliases
        return {("action", action): aliases for action, aliases in actions.items()}

    def extract(self, parsed: list[Token], kind: str) -> list[str]:
        """Extract token values by kind while preserving parse order."""
        return [value for token_kind, value in parsed if token_kind == kind]

    def place(self) -> Location:
        """Return the current place."""
        return self.world.locations[self.state.current]

    def room_items(self, *, include_hidden: bool = True) -> list[Item]:
        """Return items in the current room."""
        return [
            self.world.items[item]
            for item in self.place().items
            if include_hidden or not self.world.items[item].hidden
        ]

    def visible_items(self) -> list[Item]:
        """Return visible, non-load room items."""
        return [
            item
            for item in self.room_items(include_hidden=False)
            if item.name != "_load"
        ]

    def subject_items(self) -> list[Item]:
        """Return currently parseable subject items."""
        ids = [item.id for item in self.visible_items()] + list(self.active_item_ids())
        return [self.world.items[item] for item in ids]

    def active_item_ids(self) -> list[str]:
        """Return held item IDs plus active status items."""
        ids = set(self.state.holding)
        ids.update(self.active_condition_item_ids())
        return sorted(ids)

    def active_condition_item_ids(self) -> list[str]:
        """Return item IDs exposed by active player conditions."""
        ids = [
            item_id
            for condition_id, item_id in self.world.condition_items.items()
            if self.state.condition(condition_id).active
        ]
        return sorted(ids)

    def direction_name(self, destination: str) -> str:
        """Return the primary direction name for a destination."""
        for direction, place in self.place().exits.items():
            if place == destination:
                return direction
        return destination

    def _new_state(self, cave_room: str | None = None) -> GameState:
        """Create fresh traversal state."""
        rooms = ["small", "medium", "large", "unknown"]
        state = GameState()
        state.current = self.world.start
        state.previous = self.world.start
        state.cave_room = cave_room or rooms[self.rng.randint(0, 3)]
        return state


def build_world(seed: int | None = 0) -> World:
    """Build a typed view of a fresh engine world."""
    del seed
    return make_world()
