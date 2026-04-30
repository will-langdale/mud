"""World action handlers for Mud."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mud.events import MediaEvent

if TYPE_CHECKING:
    from mud.engine.engine import GameEngine

ActionHandler = Callable[["GameEngine"], Awaitable[None]]


@dataclass(slots=True)
class ForestRule:
    """One generated dense-forest direction rule."""

    correct: bool = False
    escape: bool = False
    text: str = ""


async def spark(engine: GameEngine) -> None:
    """Use the lighter."""
    engine.state.turns += 0.25
    engine.emit(engine.text.actions.lighter.spark)


async def stump_climb(engine: GameEngine) -> None:
    """Climb the stump."""
    break_stump(
        engine,
        engine.text.actions.stump.climb,
        engine.text.actions.stump.climb_item_first,
        engine.text.actions.stump.climb_location_first,
        engine.text.actions.stump.climb_search,
    )


async def stump_smash(engine: GameEngine) -> None:
    """Smash the stump."""
    break_stump(
        engine,
        engine.text.actions.stump.smash,
        engine.text.actions.stump.smash_item_first,
        engine.text.actions.stump.smash_location_first,
        engine.text.actions.stump.smash_search,
    )


def break_stump(
    engine: GameEngine,
    action_text: str,
    item_first: str,
    place_first: str,
    search: str,
) -> None:
    """Apply the shared broken-stump state transition."""
    engine.state.turns += 1
    engine.emit(action_text)
    engine.state.activate_condition("poison", started_turn=engine.state.turns)
    stump = engine.world.items["stump"]
    stump.first = item_first
    place = engine.place()
    place.first = place_first
    place.search = search
    place.name = engine.text.actions.stump.broken_name
    place.restricted = False
    stump.actions = {"stump_thru": ["go through", "through", "cross"]}
    engine.emit(stump.first)


async def stump_wade(engine: GameEngine) -> None:
    """Wade around the stump."""
    engine.state.turns += 3
    engine.emit(engine.text.actions.stump.wade)
    exits = list(engine.world.locations["snake"].exits.values())
    if engine.state.previous in exits:
        exits.remove(engine.state.previous)
    engine.state.previous = exits[0] if exits else engine.state.previous


async def stump_thru(engine: GameEngine) -> None:
    """Try to pass through the stump."""
    engine.emit(engine.text.actions.stump.through)


async def swamp_climb(engine: GameEngine) -> None:
    """Climb swamp trees."""
    engine.emit(engine.text.actions.swamp.tree_climb)
    engine.state.turns += 1


async def wood_climb(engine: GameEngine) -> None:
    """Climb wood trees."""
    engine.emit(engine.text.actions.forest.wood_climb)
    engine.state.turns += 1


async def wood_go(engine: GameEngine) -> None:
    """Resolve movement while lost in the dense forest."""
    active = True
    correct_steps = 0
    engine.state.turns += 1
    engine.emit(engine.rnd(engine.world.random.woods_lost))

    while active:
        rules, search = forest_rules(engine)
        engine.world.locations["wood_in"].search = search

        moved = False
        while not moved:
            await engine.status()
            parsed = engine.parse(await engine.prompt())
            looktry = ("command", "look") in parsed
            movetry = any(
                token[0] == "direction" or token == ("command", "move")
                for token in parsed
            )
            dirs = engine.extract(parsed, "direction")

            if not movetry:
                await engine.interpret(parsed)
            elif len(dirs) > 1:
                engine.emit(engine.text.system.confused)
                await engine.sink(0.25)
                engine.state.turns += 0.25
            elif not dirs:
                engine.emit(engine.text.system.where_go)
            else:
                direction = dirs[0]
                rule = rules[direction]
                if looktry:
                    engine.emit(rule.text)
                    await engine.sink(0.25)
                    engine.state.turns += 0.25
                elif rule.escape:
                    engine.emit(engine.text.actions.forest.edge)
                    engine.state.previous = "wood_in"
                    engine.state.current = "wood"
                    active = False
                    moved = True
                else:
                    correct_steps = correct_steps + 1 if rule.correct else 0
                    engine.emit(
                        engine.rnd(engine.world.random.movement)
                        % engine.direction_name(direction)
                    )
                    engine.emit(engine.rnd(engine.world.random.mud))
                    engine.emit(engine.rnd(engine.world.random.woods_lost))
                    if correct_steps == 3:
                        engine.dead(engine.text.actions.forest.captivity_death)
                    engine.state.turns += 1
                    moved = True


def forest_rules(engine: GameEngine) -> tuple[dict[str, ForestRule], str]:
    """Build one turn of randomized dense-forest direction rules."""
    directions = ["north", "east", "south", "west"]
    rules = {direction: ForestRule() for direction in directions}
    if engine.rng.randint(0, 2) == 0:
        rules[directions[engine.rng.randint(0, 3)]].escape = True

    while True:
        direction = directions[engine.rng.randint(0, 3)]
        if not rules[direction].escape:
            rules[direction].correct = True
            break

    search = engine.text.actions.forest.search_empty
    for direction, rule in rules.items():
        if rule.correct:
            if engine.rng.randint(0, 2) == 0:
                rule.text = engine.rnd(engine.world.random.woods)
                search = engine.text.render(
                    engine.text.templates.forest_tracks,
                    direction=direction,
                )
            else:
                rule.text = engine.rnd(engine.world.random.woods_correct)
        elif rule.escape:
            rule.text = engine.rnd(engine.world.random.woods_escape)
        else:
            rule.text = engine.rnd(engine.world.random.woods)
    return rules, search


async def leeches_rid(engine: GameEngine) -> None:
    """Remove leeches."""
    engine.state.clear_condition("leeches", mark_cleared=True)
    engine.emit(engine.text.actions.leeches.remove)
    engine.state.turns += 1.5
    await engine.sink(1.5)


async def swamp_go(engine: GameEngine) -> None:
    """Trigger the swamp leech trap."""
    leeches = engine.state.condition("leeches")
    if leeches.cleared:
        return
    engine.emit(engine.text.actions.swamp.leeches_begin)
    if not leeches.active:
        engine.state.activate_condition("leeches", count=0)


async def sand_forward(engine: GameEngine) -> None:
    """Enter and resolve the sandy mire."""
    engine.state.current = "sand_in"
    await engine.room()
    active = True
    engine.state.turns += 1
    count = 0
    while active:
        sandrand = engine.rng.randint(0, 10)
        parsed = engine.parse(await engine.prompt())
        await engine.status()
        looktry = ("command", "look") in parsed
        movetry = any(
            token[0] == "direction" or token == ("command", "move") for token in parsed
        )
        dirs = engine.extract(parsed, "direction")
        if len(dirs) > 1:
            engine.emit(engine.text.system.confused)
            await engine.sink(0.25)
            engine.state.turns += 0.25
        elif (sandrand > 8 and movetry and not looktry) or count == 6:
            engine.emit(engine.text.actions.sand.escape)
            active = False
            await engine.interpret(parsed)
        else:
            engine.state.turns += 1
            if movetry and not looktry and dirs:
                engine.emit(
                    engine.rnd(engine.world.random.movement)
                    % engine.direction_name(dirs[0])
                )
                engine.emit(engine.rnd(engine.world.random.exhaustion))
            else:
                active = False
                engine.dead(engine.text.actions.sand.death)
        count += 1


async def sand_backward(engine: GameEngine) -> None:
    """Back away from the sandy mire."""
    engine.state.current = engine.state.previous


async def troops_forward(engine: GameEngine) -> None:
    """Approach the troops."""
    engine.dead(engine.text.actions.troops.approach_death)


async def troops_backward(engine: GameEngine) -> None:
    """Back away from the troops."""
    engine.emit(engine.text.actions.troops.fall_back)
    await engine.sink(1)
    engine.state.turns += 1
    engine.state.current = "troops"


async def stones_listen(engine: GameEngine) -> None:
    """Listen to the stones."""
    engine.emit(engine.text.actions.stones.listen)
    if engine.state.artifacts[0] and not engine.state.artifacts[1]:
        engine.state.artifacts[1] = True
        engine.emit(engine.text.artifacts.stone)
    if engine.state.current == "troops":
        engine.emit(engine.text.actions.troops.voices)
    if engine.state.current == "troops_in":
        engine.emit(engine.text.actions.stones.troops_close)


async def stones_climb(engine: GameEngine) -> None:
    """Try to climb the stones."""
    engine.emit(engine.text.actions.stones.climb)


async def cave_enter(engine: GameEngine) -> None:
    """Enter the cave."""
    engine.emit(engine.text.actions.cave.enter)
    engine.emit(engine.text.actions.cave.fall)
    engine.emit(MediaEvent("bg", 255))
    engine.emit(engine.text.actions.cave.landing)
    engine.emit(MediaEvent("music", ("cave", -1)))
    engine.state.current = "cave_in"
    engine.state.cave_dir = engine.rng.choice(list(engine.place().exits.values()))
    await engine.room()
    engine.state.turns += 1


def describe_cave(engine: GameEngine) -> None:
    """Describe cave sense by room size."""
    mapping = {
        "small": engine.text.actions.cave.sense_small,
        "medium": engine.text.actions.cave.sense_medium,
        "large": engine.text.actions.cave.sense_large,
        "unknown": engine.text.actions.cave.sense_unknown,
    }
    engine.emit(mapping[engine.state.cave_room])


async def flare_fire(engine: GameEngine) -> None:
    """Fire the flare."""
    engine.state.turns += 0.25
    await engine.sink(0.25)
    engine.world.items["flare"].actions.clear()
    engine.world.items["flare"].look = engine.text.actions.flare.after_look
    engine.world.items["flare"].search = engine.text.actions.flare.after_search
    engine.emit(engine.text.actions.flare.fire)


async def box3_inside(engine: GameEngine) -> None:
    """Search the large crate."""
    if "box3" in engine.state.searched:
        engine.emit(engine.text.actions.boxes.box3_empty)
    else:
        engine.emit(engine.text.actions.boxes.box3_found)
    engine.state.holding.add("flare")
    engine.state.searched.add("box3")


async def medkit_use(engine: GameEngine) -> None:
    """Use the medkit."""
    engine.state.turns += 1
    await engine.sink(1)
    poison = engine.state.condition("poison")
    if poison.active:
        engine.emit(engine.text.actions.medkit.use_poisoned)
        engine.state.clear_condition("poison")
    else:
        engine.emit(engine.text.actions.medkit.use_unneeded)


async def box4_inside(engine: GameEngine) -> None:
    """Search the flat case."""
    if "box4" in engine.state.searched:
        engine.emit(engine.text.actions.boxes.box4_empty)
    else:
        engine.emit(engine.text.actions.boxes.box4_found)
    engine.state.holding.add("medkit")
    engine.state.searched.add("box4")


async def boat_enter(engine: GameEngine) -> None:
    """Enter the log boat."""
    engine.emit(engine.text.actions.boat.enter)
    if engine.rng.randint(0, 3) == 0:
        engine.dead(engine.text.actions.boat.death)
    engine.emit(engine.text.actions.boat.swept_right)
    engine.emit(engine.text.actions.boat.nightmares)
    engine.emit(MediaEvent("bg", 255))
    engine.emit(" ")
    engine.emit(MediaEvent("reset", ""))
    engine.emit(engine.text.actions.boat.restart)
    engine.emit(MediaEvent("bg", 0))
    engine.state.turns += 3
    engine.state.current = "wood"
    await engine.room()
    await engine.status()


async def water_enter(engine: GameEngine) -> None:
    """Enter the river water."""
    engine.state.turns += 2
    engine.emit(engine.text.actions.water.enter)
    if engine.rng.randint(0, 10) < 2:
        engine.dead(engine.text.actions.water.death)
    engine.emit(engine.text.actions.water.escape)


async def fog_go(engine: GameEngine) -> None:
    """Resolve movement while lost in fog."""
    exits = ["plane", "debris", "snake", "blankse", "cave", "blanksw"]
    active = True
    move_count = 0

    while active:
        fogrand = engine.rng.randint(0, 10)
        engine.world.locations["fog"].first = engine.text.actions.fog.inside_first
        await engine.status()
        parsed = engine.parse(await engine.prompt())
        looktry = ("command", "look") in parsed
        movetry = any(
            token[0] == "direction" or token == ("command", "move") for token in parsed
        )
        dirs = engine.extract(parsed, "direction")

        if len(dirs) > 1:
            engine.emit(engine.text.system.confused)
            await engine.sink(0.25)
            engine.state.turns += 0.25
            continue

        engine.state.turns += 1
        if fogrand > 6 and movetry and not looktry and dirs:
            escape_fog(engine, exits)
            active = False
        elif looktry:
            engine.emit(engine.rnd(engine.world.random.fog))
        elif movetry and dirs:
            engine.emit(
                engine.rnd(engine.world.random.movement)
                % engine.direction_name(dirs[0])
            )
            engine.emit(engine.rnd(engine.world.random.fog))
            engine.emit(engine.rnd(engine.world.random.mud))
            move_count += 1
        elif movetry:
            engine.emit(engine.text.system.where_go)
        else:
            engine.emit(engine.rnd(engine.world.random.fog))
            await engine.interpret(parsed)

        if active and move_count == 6 and movetry and not looktry and dirs:
            escape_fog(engine, exits)
            active = False


def escape_fog(engine: GameEngine, exits: list[str]) -> None:
    """Move out of the fog into a randomized neighboring location."""
    engine.emit(engine.text.actions.fog.escape)
    engine.world.locations["fog"].first = engine.text.actions.fog.return_first
    engine.state.previous = "fog"
    engine.state.current = exits[engine.rng.randint(0, len(exits) - 1)]
    engine.state.visited.add(engine.state.current)
    engine.emit(engine.place().first)


ACTION_HANDLERS: dict[str, ActionHandler] = {
    "spark": spark,
    "stump_climb": stump_climb,
    "stump_wade": stump_wade,
    "stump_smash": stump_smash,
    "stump_thru": stump_thru,
    "swamp_climb": swamp_climb,
    "wood_climb": wood_climb,
    "wood_go": wood_go,
    "leeches_rid": leeches_rid,
    "sand_forward": sand_forward,
    "sand_backward": sand_backward,
    "swamp_go": swamp_go,
    "stones_climb": stones_climb,
    "stones_listen": stones_listen,
    "troops_forward": troops_forward,
    "troops_backward": troops_backward,
    "cave_enter": cave_enter,
    "flare_fire": flare_fire,
    "box3_inside": box3_inside,
    "box4_inside": box4_inside,
    "medkit_use": medkit_use,
    "boat_enter": boat_enter,
    "water_enter": water_enter,
    "fog_go": fog_go,
}
