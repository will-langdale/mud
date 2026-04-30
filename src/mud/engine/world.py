"""Declarative world data for Mud."""

from __future__ import annotations

from mud.engine.model import Item, Location, World
from mud.engine.text import ItemText, LocationText, TextAssets


def build_world(text: TextAssets | None = None) -> World:
    """Build a fresh mutable world instance."""
    store = text or TextAssets.load()

    def item(item_id: str) -> ItemText:
        return store.items[item_id]

    def location(location_id: str) -> LocationText:
        return store.locations[location_id]

    items = {
        "lighter": Item(
            "lighter",
            ["lighter", "zippo"],
            "the ailing lighter",
            item("lighter").first,
            item("lighter").look,
            item("lighter").search,
        ),
        "fighter": Item(
            "fighter",
            ["fighter", "plane", "aircraft", "craft"],
            "the fighter aircraft",
            item("fighter").first,
            item("fighter").look,
            item("fighter").search,
        ),
        "stump": Item(
            "stump",
            ["stump", "log", "tree"],
            "the gigantic, crumbling log",
            item("stump").first,
            item("stump").look,
            item("stump").search,
        ),
        "route": Item(
            "route",
            ["route itinerary", "notes", "route", "itinerary", "course", "manifest"],
            "the plane's route itinerary",
            item("route").first,
            item("route").look,
            item("route").search,
        ),
        "pages": Item(
            "pages",
            ["pages", "page", "notes", "paper", "papers"],
            "the scattered pages from the plane",
            item("pages").first,
            item("pages").look,
            item("pages").search,
            hidden=True,
        ),
        "swamptrees": Item(
            "swamptrees",
            ["trees", "tree"],
            "the knarled trees",
            item("swamptrees").first,
            item("swamptrees").look,
            item("swamptrees").search,
        ),
        "woodtrees": Item(
            "woodtrees",
            ["trees", "tree"],
            "the towering trees",
            item("woodtrees").first,
            item("woodtrees").look,
            item("woodtrees").search,
        ),
        "leeches": Item(
            "leeches",
            [
                "wormlike creatures",
                "leech",
                "leeches",
                "leechs,",
                "worms",
                "worm",
                "creatures",
                "creature",
                "animals",
                "animal",
                "black",
            ],
            "the writhing black worms",
            item("leeches").first,
            item("leeches").look,
            item("leeches").search,
        ),
        "sandtrap": Item(
            "sandtrap",
            ["sand", "mire", "sandy", "mud"],
            "the murky, sandy mire",
            item("sandtrap").first,
            item("sandtrap").look,
            item("sandtrap").search,
        ),
        "trooptrap": Item(
            "trooptrap",
            [
                "troops",
                "column",
                "men",
                "soldiers",
                "soliders",
                "solider",
                "soldier",
                "company",
                "army",
                "group",
            ],
            "the plodding group of soldiers",
            item("trooptrap").first,
            item("trooptrap").look,
            item("trooptrap").search,
        ),
        "stones": Item(
            "stones",
            ["stones", "rocks", "monoliths", "standing", "boulders"],
            "the standing stones",
            item("stones").first,
            item("stones").look,
            item("stones").search,
        ),
        "cavetrap": Item(
            "cavetrap",
            ["cave", "cavern", "opening", "rock", "rocky", "fissure"],
            "the rocky fissure",
            item("cavetrap").first,
            item("cavetrap").look,
            item("cavetrap").search,
        ),
        "box1": Item(
            "box1",
            ["small", "metal", "cache"],
            "a small cache, made from a lightweight metal",
            item("box1").first,
            item("box1").look,
            item("box1").search,
        ),
        "box2": Item(
            "box2",
            ["square", "wood", "wooden", "cabinet", "cupboard"],
            "a square and sturdy wooden cabinet",
            item("box2").first,
            item("box2").look,
            item("box2").search,
        ),
        "flare": Item(
            "flare",
            ["flare", "flaregun"],
            "the flare",
            item("flare").first,
            item("flare").look,
            item("flare").search,
        ),
        "box3": Item(
            "box3",
            ["large", "holey", "holed", "hole", "crate"],
            "a large crate, riddled with holes",
            item("box3").first,
            item("box3").look,
            item("box3").search,
        ),
        "medkit": Item(
            "medkit",
            ["medkit", "syringes", "health", "medical", "kit"],
            "the small emergency medical kit",
            item("medkit").first,
            item("medkit").look,
            item("medkit").search,
        ),
        "box4": Item(
            "box4",
            ["long", "flatgreen", "case"],
            "a long, flat, muddy-green case",
            item("box4").first,
            item("box4").look,
            item("box4").search,
        ),
        "bodies": Item(
            "bodies",
            ["bodies", "body", "corpses", "corpse"],
            "the scattered corpses",
            item("bodies").first,
            item("bodies").look,
            item("bodies").search,
        ),
        "boat": Item(
            "boat",
            ["log", "float", "wood"],
            "the length of decaying log",
            item("boat").first,
            item("boat").look,
            item("boat").search,
            hidden=True,
        ),
        "water": Item(
            "water",
            ["water", "river", "waterway"],
            "the slow, dark waterway",
            item("water").first,
            item("water").look,
            item("water").search,
        ),
        "aagun": Item(
            "aagun",
            ["gun", "anti-aircraft", "aircraft", "anti", "cannon", "artillery"],
            "the sinking gun",
            item("aagun").first,
            item("aagun").look,
            item("aagun").search,
        ),
        "swamp_load": Item("swamp_load", [""], "_load", "", "", ""),
        "wood_load": Item("wood_load", [""], "_load", "", "", ""),
        "fog_load": Item("fog_load", [""], "_load", "", "", ""),
    }

    items["lighter"].actions = {"spark": ["spark", "light", "flick"]}
    items["stump"].actions = {
        "stump_climb": ["climb", "clamber"],
        "stump_wade": ["wade around", "wade"],
        "stump_smash": ["smash through", "smash", "break through", "break"],
    }
    items["swamptrees"].actions = {"swamp_climb": ["climb", "clamber"]}
    items["woodtrees"].actions = {"wood_climb": ["climb", "clamber"]}
    items["leeches"].actions = {
        "leeches_rid": ["pull off", "kill", "get rid of", "clear", "pull"]
    }
    items["sandtrap"].actions = {
        "sand_forward": [
            "continue into",
            "yes",
            "forward",
            "forwards",
            "go",
            "continue",
            "into",
            "proceed",
        ],
        "sand_backward": ["leave", "no", "backward", "backwards"],
    }
    items["trooptrap"].actions = {
        "troops_forward": [
            "continue into",
            "yes",
            "forward",
            "forwards",
            "go",
            "continue",
            "into",
            "proceed",
            "approach",
        ],
        "troops_backward": [
            "leave",
            "no",
            "backward",
            "backwards",
            "dont",
            "fall",
            "back",
        ],
    }
    items["stones"].actions = {
        "stones_climb": ["climb", "clamber"],
        "stones_listen": ["listen to", "listen", "to", "hear"],
    }
    items["cavetrap"].actions = {"cave_enter": ["enter", "into", "in", "go", "explore"]}
    items["box3"].actions = {"box3_inside": ["search"]}
    items["flare"].actions = {"flare_fire": ["fire", "shoot", "send up"]}
    items["box4"].actions = {"box4_inside": ["search"]}
    items["medkit"].actions = {"medkit_use": ["use", "inject", "apply"]}
    items["boat"].actions = {
        "boat_enter": [
            "float into the river with",
            "paddle",
            "use",
            "get",
            "push",
            "off",
            "float",
            "down",
            "length",
        ]
    }
    items["water"].actions = {"water_enter": ["try to swim into", "swim", "water"]}
    items["swamp_load"].actions = {"swamp_go": []}
    items["wood_load"].actions = {"wood_go": []}
    items["fog_load"].actions = {"fog_go": []}

    locations = {
        "plane": Location(
            "plane",
            location("plane").name,
            location("plane").first,
            location("plane").look,
            location("plane").search,
            {"north": "sand", "east": "snake", "south": "fog", "west": "debris"},
            items=["fighter"],
        ),
        "snake": Location(
            "snake",
            location("snake").name,
            location("snake").first,
            location("snake").look,
            location("snake").search,
            {"north": "sand", "east": "log", "south": "fog", "west": "plane"},
            True,
            location("snake").restriction,
            ["stump"],
        ),
        "sand": Location(
            "sand",
            location("sand").name,
            location("sand").first,
            location("sand").look,
            location("sand").search,
            {"north": "swamp", "east": "blankne", "south": "plane", "west": "blanknw"},
            True,
            location("sand").restriction,
            ["sandtrap"],
        ),
        "sand_in": Location(
            "sand_in",
            location("sand_in").name,
            location("sand_in").first,
            location("sand_in").look,
            location("sand_in").search,
            {"north": "swamp", "east": "blankne", "south": "plane", "west": "blanknw"},
        ),
        "debris": Location(
            "debris",
            location("debris").name,
            location("debris").first,
            location("debris").look,
            location("debris").search,
            {"north": "sand", "east": "plane", "south": "fog", "west": "gun"},
            items=["box1", "box2", "box3", "box4"],
        ),
        "fog": Location(
            "fog",
            location("fog").name,
            location("fog").first,
            location("fog").look,
            location("fog").search,
            {"north": "plane", "east": "blankse", "south": "cave", "west": "blanksw"},
            True,
            location("fog").restriction,
            ["fog_load"],
        ),
        "blanksw": Location(
            "blanksw",
            location("blanksw").name,
            location("blanksw").first,
            location("blanksw").look,
            location("blanksw").search,
            {"north": "gun", "east": "fog", "south": "cave", "west": "troops"},
        ),
        "log": Location(
            "log",
            location("log").name,
            location("log").first,
            location("log").look,
            location("log").search,
            {"north": "blankne", "east": "wood", "south": "blankse", "west": "snake"},
            items=["pages"],
        ),
        "swamp": Location(
            "swamp",
            location("swamp").name,
            location("swamp").first,
            location("swamp").look,
            location("swamp").search,
            {"north": "river", "east": "blankne", "south": "sand", "west": "blanknw"},
            items=["swamp_load", "swamptrees"],
        ),
        "gun": Location(
            "gun",
            location("gun").name,
            location("gun").first,
            location("gun").look,
            location("gun").search,
            {
                "north": "blanknw",
                "east": "debris",
                "south": "blanksw",
                "west": "troops",
            },
            items=["aagun"],
        ),
        "cave": Location(
            "cave",
            location("cave").name,
            location("cave").first,
            location("cave").look,
            location("cave").search,
            {"north": "fog", "east": "blankse", "south": "cave", "west": "blanksw"},
            items=["cavetrap"],
        ),
        "cave_in": Location(
            "cave_in",
            location("cave_in").name,
            location("cave_in").first,
            location("cave_in").look,
            location("cave_in").search,
            {"north": "fog", "east": "blankse", "south": "cave", "west": "blanksw"},
        ),
        "wood": Location(
            "wood",
            location("wood").name,
            location("wood").first,
            location("wood").look,
            location("wood").search,
            {"north": "blankne", "east": "wood_in", "south": "blankse", "west": "log"},
            items=["woodtrees"],
        ),
        "wood_in": Location(
            "wood_in",
            location("wood_in").name,
            location("wood_in").first,
            location("wood_in").look,
            location("wood_in").search,
            {"north": "north", "east": "east", "south": "south", "west": "west"},
            items=["wood_load", "woodtrees"],
        ),
        "river": Location(
            "river",
            location("river").name,
            location("river").first,
            location("river").look,
            location("river").search,
            {"north": "river", "east": "swamp", "south": "swamp", "west": "swamp"},
            items=["boat", "water"],
        ),
        "troops": Location(
            "troops",
            location("troops").name,
            location("troops").first,
            location("troops").look,
            location("troops").search,
            {
                "north": "blanknw",
                "east": "gun",
                "south": "blanksw",
                "west": "troops_in",
            },
            items=["stones"],
        ),
        "troops_in": Location(
            "troops_in",
            location("troops_in").name,
            location("troops_in").first,
            location("troops_in").look,
            location("troops_in").search,
            {
                "north": "troops_in",
                "east": "troops",
                "south": "troops_in",
                "west": "troops_in",
            },
            True,
            location("troops_in").restriction,
            ["trooptrap", "stones"],
        ),
        "blankse": Location(
            "blankse",
            location("blankse").name,
            location("blankse").first,
            location("blankse").look,
            location("blankse").search,
            {"north": "log", "east": "wood", "south": "cave", "west": "fog"},
        ),
        "blanknw": Location(
            "blanknw",
            location("blanknw").name,
            location("blanknw").first,
            location("blanknw").look,
            location("blanknw").search,
            {"north": "swamp", "east": "sand", "south": "gun", "west": "troops"},
        ),
        "blankne": Location(
            "blankne",
            location("blankne").name,
            location("blankne").first,
            location("blankne").look,
            location("blankne").search,
            {"north": "swamp", "east": "wood", "south": "log", "west": "sand"},
        ),
    }

    return World(
        locations=locations,
        items=items,
        condition_items={"leeches": "leeches"},
        start="plane",
        random=store.random,
        commands={
            "look": ["look", "examine"],
            "move": ["move", "go", "walk", "run", "g"],
            "help": ["help", "h"],
            "think": ["think", "consider", "appraise", "mull", "t"],
            "search": ["search", "loot", "salvage", "find"],
            "wait": ["wait", "rest", "sleep", "stop"],
            "shout": ["talk", "scream", "shout", "speak", "call"],
            "exit": ["quit", "exit"],
        },
    )
