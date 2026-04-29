# ruff: noqa

import copy, inspect, sys, random

from mud.events import MediaEvent
from mud.engine.text import TextStore

TEXT = TextStore.load()


def text(key, **values):
    """Render a narrative text asset."""
    if values:
        return TEXT.render(key, **values)
    return TEXT.get(key)


"""Global variables 1"""

holding = {}
turns = 0
searched = []

"""Is pygame in use?"""

pyg_init = False
pyg_textcompile = []
input_handler = None
output_handler = None
quit_handler = None


def configure_io(input_callback, output_callback, quit_callback=None):
    """Configure the callbacks used by the single-process wrapper."""
    global input_handler
    global output_handler
    global quit_handler
    global pyg_init

    input_handler = input_callback
    output_handler = output_callback
    quit_handler = quit_callback
    pyg_init = True


"""Holds changeable commands that can be done"""

placeacts = {}
itemacts = {}

"""Custom death exception"""


class DeathError(Exception):
    def __init__(self, value):
        self.value = value
        self.art = artifacts


"""Place and item classes"""


class Place:
    def __init__(self, name, firstsight, look, items, restricmov, restricwhy, search):
        self.name = name
        self.firstsight = firstsight
        self.look = look
        self.items = items
        self.restricmov = restricmov
        self.restricwhy = restricwhy
        self.search = search

    def stay(self):
        return self

    def getactions(self):
        global placeacts
        placeacts.clear()

        for i in self.items:
            placeacts.update(i.actions)

    def listitems(self):
        for i in list(self.items.keys()):
            tensetext(i.firstsight)

    def loaditems(self):
        global subjects
        subjects.clear()

        for i in list(self.items.keys()):
            if i.reflib[0] != "hidden":
                i.actions.clear()
                i.actions.update(self.items[i])
                subjects[i] = i.reflib


class Item:
    def __init__(self, reflib, name, firstsight, look, search, actions):
        self.reflib = reflib
        self.name = name
        self.firstsight = firstsight
        self.look = look
        self.search = search
        self.actions = actions

    def pickup(self, hidden):
        global holding

        for i in list(hidden.keys()):
            i.actions.update(hidden[i])
            holding[i] = i.reflib


def holding_init():
    """Updates itemacts with actions for whatever is held"""
    itemacts.clear()

    for i in holding:
        itemacts.update(i.actions)


"""Specific item subclasses and item instantiation"""


class Lighter(Item):
    def spark(self):
        global turns
        global caveghosts
        global caveghosts_turn
        global cavehint
        global artifacts

        turns += 0.25
        ghostrand = random.randint(0, 1)

        if currentloc == cave_in and caveghosts == False and ghostrand == 1:
            tensetext(text("legacy.line_0139_001"))
            dark = MediaEvent("sound", "DARK")
            tensetext(dark)
            caveghosts = True
            caveghosts_turn = turns
            if artifacts[0] == False:
                artifacts[0] = True
                tensetext("The open sky is an endless blue, find them in the earth.")
        elif (currentloc == cave_in and caveghosts == True) or (
            currentloc == cave_in and ghostrand != 1
        ):
            if turns <= caveghosts_turn + 0.75:
                tensetext("Shaking, you fumble with the mechanism.")
            tensetext(text("legacy.line_0154_002") % directions[cavedir][0])
            if turns <= caveghosts_turn + 0.75:
                tensetext("The blank mud of the cavern stretches into empty dark.")
            if cavehint <= 1:
                cavehint = 1
        else:
            tensetext("Flicking the lighter you produce a short-lived flame.")


lighter = Lighter(
    ["lighter", "zippo"],
    "the ailing lighter",
    "The zippo is a battered steel affair.",
    text("legacy.line_0169_003"),
    text("legacy.line_0170_004"),
    {},
)


class Fighter(Item):
    def inside(self):
        global searched

        if self in searched:
            tensetext(text("legacy.line_0181_005"))
        else:
            tensetext(text("legacy.line_0185_006"))

        hidden = {lighter: {lighter.spark: ["spark", "light", "flick"]}}
        self.pickup(hidden)
        hidden.clear()
        searched.append(self)


fighter = Fighter(
    ["fighter", "plane", "aircraft", "craft"],
    "the fighter aircraft",
    "The one-person aircraft is damaged beyond repair.",
    "The olive fuselage bears a single red symbol.",
    "",
    {},
)


class Stump(Item):
    def climb(self):
        global turns
        global poisonif
        global poisonlen

        turns += 1
        tensetext(text("legacy.line_0212_007"))
        poisonif = True
        poisonlen = turns

        self.firstsight = text("legacy.line_0217_008")
        currentloc.firstsight = text("legacy.line_0218_009")
        tensetext(stump.firstsight)
        currentloc.search = text("legacy.line_0220_010")
        currentloc.name = "at the riddled treestump, split in two"
        currentloc.restricmov = False

        del currentloc.items[stump][stump.climb]
        del currentloc.items[stump][stump.smash]
        currentloc.items[stump][stump.thru] = ["go through", "through", "cross"]
        currentloc.loaditems()
        currentloc.getactions()

    def wade(self):
        global turns
        global prevloc

        turns += 3
        tensetext(text("legacy.line_0236_011"))

        loc = prevloc
        prevloc = []
        for i in cart[snake]:
            prevloc.append(i)
        prevloc.remove(loc[0])

    def smash(self):
        global turns
        global poisonif
        global poisonlen

        turns += 1
        tensetext(text("legacy.line_0252_012"))
        poisonif = True
        poisonlen = turns

        self.firstsight = text("legacy.line_0257_013")
        currentloc.firstsight = text("legacy.line_0258_014")
        currentloc.search = text("legacy.line_0259_015")
        currentloc.name = "at the riddled treestump, split in two"
        currentloc.restricmov = False

        del currentloc.items[stump][stump.climb]
        del currentloc.items[stump][stump.smash]
        currentloc.items[stump][stump.thru] = ["go through", "through", "cross"]
        currentloc.loaditems()
        currentloc.getactions()

    def thru(self):
        tensetext(text("legacy.line_0271_016"))


stump = Stump(
    ["stump", "log", "tree"],
    "the gigantic, crumbling log",
    text("legacy.line_0278_017"),
    text("legacy.line_0279_018"),
    text("legacy.line_0280_019"),
    {},
)

route = Item(
    ["route itinerary", "notes", "route", "itinerary", "course", "manifest"],
    "the plane's route itinerary",
    text("legacy.line_0287_020"),
    text("legacy.line_0288_021"),
    text("legacy.line_0289_022"),
    {},
)


class Pages(Item):
    def inside(self):
        global searched
        global turns

        if self in searched:
            tensetext("No pages remain in the scrubland.")
        else:
            tensetext(text("legacy.line_0303_023"))
            tensetext(rndtext(obs[2]))
            tensetext(text("legacy.line_0307_024"))
            turns += 3

        hidden = {route: {}}
        self.pickup(hidden)
        hidden.clear()
        searched.append(self)

        del currentloc.items[pages]
        currentloc.loaditems()
        currentloc.getactions()


pages = Pages(
    ["hidden", "pages", "page", "notes", "paper", "papers"],
    "the scattered pages from the plane",
    text("legacy.line_0324_025"),
    text("legacy.line_0325_026"),
    "",
    {},
)


class Swamptrees(Item):
    def climb(self):
        global turns
        tensetext(text("legacy.line_0335_027"))
        turns += 1


swamptrees = Swamptrees(
    ["trees", "tree"],
    "the knarled trees",
    "Knarled black trees reach out of the swamp.",
    text("legacy.line_0344_028"),
    text("legacy.line_0345_029"),
    {},
)


class Woodtrees(Item):
    def climb(self):
        global turns
        tensetext(text("legacy.line_0354_030"))
        turns += 1


woodtrees = Woodtrees(
    ["trees", "tree"],
    "the towering trees",
    "A thousand trees stretch into the distance around you.",
    text("legacy.line_0363_031"),
    text("legacy.line_0364_032"),
    {},
)


class Leeches(Item):
    def leechstart(self):
        global leechcount
        global leechsucked

        if leechsucked == True:
            return
        else:
            leechsucked = True
            leechcount = 0

    async def rid(self):
        global leechcount
        global leechsucked
        global turns
        global holding

        leechcount = 0
        leechsucked = False
        del holding[leeches]

        tensetext(text("legacy.line_0391_033"))
        turns += 1.5
        await sink(1.5)


leeches = Leeches(
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
    text("legacy.line_0412_034"),
    text("legacy.line_0413_035"),
    text("legacy.line_0414_036"),
    {},
)


class Swamptrap(Item):
    def go(self):
        tensetext("You can feel movement beneath the water.")
        leeches.leechstart()


swamp_load = Swamptrap([""], "_load", "", "", "", {})


class Sandtrap(Item):
    async def forward(self):
        global turns
        global currentloc

        currentloc = sand_in
        await room()
        sandif = True
        turns += 1
        sandcount = 0

        m = {}
        m[move] = commands[move]
        movecom = dictmerge(directions, m)

        while sandif == True:
            sandrand = random.randint(0, 10)
            looktry = False
            movetry = False

            do = parser(
                await prompt(),
                dictmerge(directions, commands, subjects, placeacts, holding, itemacts),
            )

            await status()

            for i in do:
                if i == examine:
                    looktry = True
                for x in list(movecom.keys()):
                    if i == x:
                        movetry = True

            sand_dupedir = 0
            sand_movedir = ""

            for i in list(directions.keys()):
                if i in do:
                    sand_dupedir += 1
                    sand_movedir = i

            if sand_dupedir > 1:
                tensetext("You don't know what to do or where to be. Do you need HELP?")
                await sink(0.25)
                turns += 0.25
            else:
                if (
                    sandrand > 8 and movetry == True and looktry == False
                ) or sandcount == 6:
                    tensetext(text("legacy.line_0479_037"))
                    sandif = False
                    await interpret(do)
                else:
                    turns += 1
                    if movetry == True and looktry == False:
                        tensetext(rndtext(obs[1]) % directions[sand_movedir][0])
                        tensetext(rndtext(obs[4]))
                    else:
                        sandif = False
                        dead(text("legacy.line_0491_038"))

            sandcount += 1

    def backward(self):
        global currentloc

        currentloc = prevloc[0]
        dirdictupdate()


sandtrap = Sandtrap(
    ["sand", "mire", "sandy", "mud"],
    "the murky, sandy mire",
    "The loose and sandy mud stretches on into the distance.",
    text("legacy.line_0507_039"),
    text("legacy.line_0508_040"),
    {},
)


class Woodtrap(Item):
    async def go(self):
        global turns
        global currentloc

        holding_init()

        woodif = True
        woods_correct = 0
        turns += 1
        tensetext(rndtext(obs[11]))

        m = {}
        m[move] = commands[move]
        movecom = dictmerge(directions, m)

        while woodif == True:
            await status()

            wood_in.search = text("legacy.line_0532_041")

            woods_n = [False, False, "", "north"]
            woods_e = [False, False, "", "east"]
            woods_s = [False, False, "", "south"]
            woods_w = [False, False, "", "west"]
            woods_dirs = [woods_n, woods_e, woods_s, woods_w]

            if random.randint(0, 2) == 0:
                woods_dirs[random.randint(0, 3)][1] = True

            woods_dupecheck = False
            woods_forward = ""

            while woods_dupecheck == False:
                woods_forward = random.randint(0, 3)
                if woods_dirs[woods_forward][1] == False:
                    woods_dirs[woods_forward][0] = True
                    woods_dupecheck = True

            for i in woods_dirs:
                if i[0] == True:
                    if random.randint(0, 2) == 0:
                        i[2] = rndtext(obs[14])
                        wood_in.search = (
                            "The mud has been disturbed, and the tracks lead %s." % i[3]
                        )
                    else:
                        i[2] = rndtext(obs[12])
                elif i[1] == True:
                    i[2] = rndtext(obs[13])
                else:
                    i[2] = rndtext(obs[14])

            woods_movedyet = False

            while woods_movedyet == False:
                movetry = False
                looktry = False
                await status()

                do = parser(
                    await prompt(),
                    dictmerge(
                        directions, commands, subjects, placeacts, holding, itemacts
                    ),
                )

                for i in do:
                    if i == examine:
                        looktry = True
                    for x in list(movecom.keys()):
                        if i == x:
                            movetry = True

                if movetry == True:
                    wood_dupedir = 0
                    wood_movedir = ""
                    wood_moveinfo = [False, False, "", ""]

                    for i in list(directions.keys()):
                        if i in do:
                            wood_dupedir += 1
                            wood_movedir = i

                    if wood_dupedir > 1:
                        tensetext(
                            "You don't know what to do or where to be. Do you need HELP?"
                        )
                        await sink(0.25)
                        turns += 0.25
                    else:
                        for i in woods_dirs:
                            if i[3] == wood_movedir:
                                wood_moveinfo = i

                        if looktry == True:
                            tensetext(wood_moveinfo[2])
                            await sink(0.25)
                            turns += 0.25
                        else:
                            if wood_moveinfo[0] == True:
                                woods_correct += 1
                            elif wood_moveinfo[0] == False:
                                woods_correct = 0

                            if wood_moveinfo[1] == True:
                                woodif = False
                                woods_movedyet = True

                                tensetext(text("legacy.line_0623_042"))

                                currentloc = wood
                                dirdictupdate()
                            else:
                                tensetext(rndtext(obs[1]) % wood_moveinfo[3])
                                tensetext(rndtext(obs[2]))
                                tensetext(rndtext(obs[11]))

                                if woods_correct == 3:
                                    dead(text("legacy.line_0635_043"))

                                turns += 1
                                woods_movedyet = True
                else:
                    await interpret(do)


woodtrap_load = Woodtrap([""], "_load", "", "", "", {})


class Trooptrap(Item):
    def forward(self):
        dead(text("legacy.line_0650_044"))

    async def backward(self):
        global currentloc
        global turns

        tensetext(text("legacy.line_0658_045"))
        await sink(1)
        turns += 1
        currentloc = troops
        dirdictupdate()


trooptrap = Trooptrap(
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
    "A column of soldiers wearily plods through the sticky mud.",
    text("legacy.line_0681_046"),
    "You cannot search the troops without approaching them.",
    {},
)


class Stones(Item):
    def listen(self):
        global artifacts

        tensetext(text("legacy.line_0692_047"))

        if artifacts[0] == True and artifacts[1] == False:
            artifacts[1] = True
            tensetext("The sound of static fills the air, alone amongst the stone.")

        if currentloc == troops:
            tensetext("You think you hear voices, but you can't be certain.")
        if currentloc == troops_in:
            tensetext(text("legacy.line_0703_048"))

    def climb(self):
        tensetext("The stones are too vast and smooth to scale.")


stones = Stones(
    ["stones", "rocks", "monoliths", "standing", "boulders"],
    "the standing stones",
    "A series of standing stones rise around you.",
    text("legacy.line_0714_049"),
    text("legacy.line_0715_050"),
    {},
)

caverooms = ["small", "medium", "large", "unknown"]
cavecurrent = caverooms[random.randint(0, 3)]
cavehint = 0
caveghosts = False
caveghosts_turn = 0
cavedir = "west"


class Cavetrap(Item):
    async def enter(self):
        global turns
        global currentloc
        global been
        global caverooms
        global cavecurrent
        global cavedir
        global cavehint
        global timedisplayed

        tensetext(text("legacy.line_0739_051"))
        tensetext(text("legacy.line_0742_052"))
        timecol = MediaEvent("bg", 255)
        tensetext(timecol)
        tensetext(text("legacy.line_0747_053"))
        music = MediaEvent("music", ("cave", -1))
        tensetext(music)

        currentloc = cave_in
        cavedir = list(directions.keys())[random.randint(0, 3)]
        await room()
        holding_init()

        caveif = True
        turns += 1
        cavecount = 0
        wormcount = 0
        m = {}
        m[move] = commands[move]
        movecom = dictmerge(directions, m)

        while caveif == True:
            caverand = random.randint(0, 10)
            movetry = False
            looktry = False

            do = parser(
                await prompt(),
                dictmerge(directions, commands, subjects, placeacts, holding, itemacts),
            )

            await status()

            if cavedir in do:
                caverand += cavehint

            for i in do:
                if i == examine:
                    looktry = True
                for x in list(movecom.keys()):
                    if i == x:
                        movetry = True

            cave_dupedir = 0
            cave_movedir = ""

            for i in list(directions.keys()):
                if i in do:
                    cave_dupedir += 1
                    cave_movedir = i

            if cave_dupedir > 1:
                tensetext("You don't know what to do or where to be. Do you need HELP?")
                await sink(0.25)
                turns += 0.25
            else:
                if (
                    (cavecount >= 4 or (cavehint > 0 and cavecount >= 1))
                    and caverand > 7
                    and movetry == True
                    and looktry == False
                ) or flareloc == currentloc:
                    tensetext(rndtext(obs[1]) % directions[cave_movedir][0])
                    tensetext(text("legacy.line_0808_054"))
                    tensetext(text("legacy.line_0811_055"))
                    timecol1 = MediaEvent("bg", 0)
                    tensetext(timecol1)
                    music2 = MediaEvent("music", ("main", -1))
                    tensetext(music2)
                    turns += 3
                    currentloc = cave
                    tensetext(obs[3][timeprogress - 1])
                    timedisplayed.append(timeprogress - 1)
                    caveif = False
                    return
                elif movetry == True and looktry == False:
                    tensetext(rndtext(obs[1]) % directions[cave_movedir][0])
                    tensetext(rndtext(obs[10]))
                    cavedir = list(directions.keys())[random.randint(0, 3)]
                    turns += 1
                    cavecount += 1
                    cavehint = 0
                elif looktry == True and movetry == False:
                    tensetext("Impenetrable black, you are utterly blind.")
                    self.cavethink()
                elif looktry == True and movetry == True:
                    tensetext("You stare blankly into the darkness.")
                    if cavecurrent == "small":
                        tensetext(
                            "There may be somewhere to go, perhaps a few feet away."
                        )
                    if cavecurrent == "medium":
                        tensetext(
                            "The cavern wall sounds like it's not a huge distance."
                        )
                    if cavecurrent == "large":
                        tensetext(text("legacy.line_0845_056"))
                    if cavecurrent == "unknown":
                        tensetext(text("legacy.line_0849_057"))
                else:
                    await interpret(do)

            if caverand < 2:
                if wormcount == 0:
                    tensetext(text("legacy.line_0857_058"))
                    wormcount += 1
                elif wormcount == 1:
                    tensetext(text("legacy.line_0862_059"))
                    wormcount += 1
                elif wormcount == 2:
                    tensetext(text("legacy.line_0867_060"))
                    wormcount += 1

    def cavethink(self):
        global cavecurrent

        if cavecurrent == "small":
            tensetext(text("legacy.line_0876_061"))
        if cavecurrent == "medium":
            tensetext(text("legacy.line_0880_062"))
        if cavecurrent == "large":
            tensetext(text("legacy.line_0884_063"))
        if cavecurrent == "unknown":
            tensetext(text("legacy.line_0888_064"))


cavetrap = Cavetrap(
    ["cave", "cavern", "opening", "rock", "rocky", "fissure"],
    "the rocky fissure",
    text("legacy.line_0895_065"),
    text("legacy.line_0896_066"),
    text("legacy.line_0897_067"),
    {},
)


class Fogtrap(Item):
    async def go(self):
        global turns
        global currentloc
        global been
        global fog

        foglocs = [plane, debris, snake, blankse, cave, blanksw]

        holding_init()

        if currentloc not in been:
            been.append(currentloc)
            tensetext(currentloc.firstsight)

        fogif = True
        fogcount = 0

        m = {}
        m[move] = commands[move]
        movecom = dictmerge(directions, m)

        while fogif == True:
            fogrand = random.randint(0, 10)
            movetry = False
            looktry = False
            fog.firstsight = text("legacy.line_0928_068")
            await status()

            do = parser(
                await prompt(),
                dictmerge(directions, commands, subjects, placeacts, holding, itemacts),
            )

            for i in do:
                if i == examine:
                    looktry = True
                for x in list(movecom.keys()):
                    if i == x:
                        movetry = True

            fog_dupedir = 0
            fog_movedir = ""

            for i in list(directions.keys()):
                if i in do:
                    fog_dupedir += 1
                    fog_movedir = i

            if fog_dupedir > 1:
                tensetext("You don't know what to do or where to be. Do you need HELP?")
                await sink(0.25)
                turns += 0.25
            else:
                turns += 1

                if fogrand <= 6:
                    if looktry == True:
                        tensetext(rndtext(obs[8]))
                    elif movetry == True:
                        tensetext(rndtext(obs[1]) % directions[fog_movedir][0])
                        tensetext(rndtext(obs[8]))
                        tensetext(rndtext(obs[2]))
                        fogcount += 1
                    else:
                        tensetext(rndtext(obs[8]))
                        await interpret(do)
                elif fogrand > 6 or fogcount == 6 and movetry == True:
                    if movetry == True and looktry == False:
                        tensetext(text("legacy.line_0972_069"))
                        fog.firstsight = text("legacy.line_0974_070")
                        fogif = False
                        currentloc = foglocs[random.randint(0, 5)]
                        if currentloc not in been:
                            been.append(currentloc)
                        dirdictupdate()
                        tensetext(currentloc.firstsight)
                    else:
                        if looktry == True:
                            tensetext(rndtext(obs[8]))
                        elif movetry == True:
                            tensetext(rndtext(obs[1]) % directions[fog_movedir][0])
                            tensetext(rndtext(obs[8]))
                            tensetext(rndtext(obs[2]))
                            fogcount += 1
                        else:
                            tensetext(rndtext(obs[8]))
                            await interpret(do)
                else:
                    tensetext(rndtext(obs[8]))
                    await interpret(do)


fog_load = Fogtrap([""], "_load", "", "", "", {})

box1 = Item(
    ["small", "metal", "cache"],
    "a small cache, made from a lightweight metal",
    text("legacy.line_1002_071"),
    text("legacy.line_1003_072"),
    text("legacy.line_1004_073"),
    {},
)

box2 = Item(
    ["square", "wood", "wooden", "cabinet", "cupboard"],
    "a square and sturdy wooden cabinet",
    text("legacy.line_1011_074"),
    text("legacy.line_1012_075"),
    text("legacy.line_1013_076"),
    {},
)


class Flare(Item):
    async def fire(self):
        global turns
        global flare_turns
        global flare_up
        global flareloc
        global flare_path_east
        global flare_path_west
        global flare_count
        global cavehint

        turns += 0.25
        await sink(0.25)

        self.actions.clear()
        flare.look = text("legacy.line_1033_077")
        flare.search = text("legacy.line_1034_078")

        if currentloc == cave_in:
            if cavecurrent == "large":
                tensetext(text("legacy.line_1039_079") % directions[cavedir][0])
                cavehint = 6
                flareloc = currentloc
            elif cavecurrent == "unknown":
                tensetext(text("legacy.line_1046_080") % directions[cavedir][0])
                cavehint = 1
            elif cavecurrent == "medium":
                tensetext(text("legacy.line_1052_081") % directions[cavedir][0])
                cavehint = 2
            else:
                tensetext(text("legacy.line_1058_082"))
        elif currentloc == wood_in:
            tensetext(text("legacy.line_1062_083"))
        else:
            flare_up = True
            flareloc = currentloc
            flare_turns = turns
            flare_path_east = routescan2_rec(flare_east, flareloc)
            flare_count = 1
            flare_path_west = routescan2_rec(flare_west, flareloc)

            flareloc.look += ". The murky red glow of the flare descends slowly"
            flareloc.firstsight += text("legacy.line_1073_084")
            tensetext(text("legacy.line_1075_085"))

            if currentloc == troops_in:
                tensetext(text("legacy.line_1080_086"))
            if currentloc == wood:
                tensetext(text("legacy.line_1084_087"))


flare = Flare(
    ["flare", "flaregun"],
    "the flare",
    "Though bent and dented, the flare appears intact.",
    text("legacy.line_1092_088"),
    text("legacy.line_1093_089"),
    {},
)


class Box3(Item):
    def inside(self):
        global searched

        if self in searched:
            tensetext("There is nothing useful left inside.")
        else:
            tensetext(text("legacy.line_1106_090"))

        hidden = {flare: {flare.fire: ["fire", "shoot", "send up"]}}
        self.pickup(hidden)
        hidden.clear()
        searched.append(self)


box3 = Box3(
    ["large", "holey", "holed", "hole", "crate"],
    "a large crate, riddled with holes",
    text("legacy.line_1118_091"),
    text("legacy.line_1119_092"),
    "",
    {},
)


class Medkit(Item):
    async def use(self):
        global poisonif
        global turns

        turns += 1
        await sink(1)

        if poisonif == True:
            tensetext(text("legacy.line_1135_093"))
            poisonif = False
        else:
            tensetext(text("legacy.line_1140_094"))


medkit = Medkit(
    ["medkit", "syringes", "health", "medical", "kit"],
    "the small emergency medical kit",
    text("legacy.line_1147_095"),
    text("legacy.line_1148_096"),
    text("legacy.line_1149_097"),
    {},
)


class Box4(Item):
    def inside(self):
        global searched
        global turns

        if self in searched:
            tensetext("Nothing useful remains.")
        else:
            tensetext(text("legacy.line_1163_098"))

        hidden = {medkit: {medkit.use: ["use", "inject", "apply"]}}
        self.pickup(hidden)
        hidden.clear()
        searched.append(self)


box4 = Box4(
    ["long", "flatgreen", "case"],
    "a long, flat, muddy-green case",
    "A long, flat box is all but buried in the mire.",
    text("legacy.line_1176_099"),
    "",
    {},
)

bodies = Item(
    ["bodies", "body", "corpses", "corpse"],
    "the scattered corpses",
    text("legacy.line_1184_100"),
    text("legacy.line_1185_101"),
    text("legacy.line_1186_102"),
    {},
)


class Boat(Item):
    async def enter(self):
        global turns
        global currentloc

        boatrand = random.randint(0, 3)

        tensetext(text("legacy.line_1199_103"))

        if boatrand == 0:
            dead(text("legacy.line_1204_104"))
        else:
            tensetext(text("legacy.line_1208_105"))
            tensetext("Endless nightmares run through the dark.")
            timecol1 = MediaEvent("bg", 255)
            tensetext(timecol1)
            tensetext(" ")
            reset = MediaEvent("reset", "")
            tensetext(reset)
            tensetext(text("legacy.line_1217_106"))
            timecol2 = MediaEvent("bg", 0)
            tensetext(timecol2)

            turns += 3

            currentloc = wood
            await room()
            await status()
            dirdictupdate()


boat = Boat(
    ["hidden", "log", "float", "wood"],
    "the length of decaying log",
    text("legacy.line_1233_107"),
    text("legacy.line_1234_108"),
    "You find a few crawling insects that you bat away.",
    {},
)


class Water(Item):
    def enter(self):
        global turns

        waterrand = random.randint(0, 10)
        turns += 2

        tensetext(text("legacy.line_1248_109"))

        if waterrand < 2:
            dead(text("legacy.line_1253_110"))
        else:
            tensetext(text("legacy.line_1257_111"))


water = Water(
    ["water", "river", "waterway"],
    "the slow, dark waterway",
    text("legacy.line_1264_112"),
    text("legacy.line_1265_113"),
    text("legacy.line_1266_114"),
    {},
)

aagun = Item(
    ["gun", "anti-aircraft", "aircraft", "anti", "cannon", "artillery"],
    "the sinking gun",
    "The artillery sinks slowly into the thick slop.",
    text("legacy.line_1274_115"),
    text("legacy.line_1275_116"),
    {},
)

"""Place instantiation"""

plane = Place(
    "at the plane",
    text("legacy.line_1283_117"),
    text("legacy.line_1284_118"),
    {fighter: {}},
    False,
    "",
    text("legacy.line_1288_119"),
)

snake = Place(
    "at the riddled treestump",
    text("legacy.line_1293_120"),
    text("legacy.line_1294_121"),
    {
        stump: {
            stump.climb: ["climb", "clamber"],
            stump.wade: ["wade around", "wade"],
            stump.smash: ["smash through", "smash", "break through", "break"],
        }
    },
    True,
    "The hulking log blocks your path. What do you do?",
    text("legacy.line_1304_122"),
)

sand = Place(
    "at a sandy, muddy mess",
    text("legacy.line_1309_123"),
    "mud, as far as the eye can see",
    {
        sandtrap: {
            sandtrap.forward: [
                "continue into",
                "yes",
                "forward",
                "forwards",
                "go",
                "continue",
                "into",
                "proceed",
            ],
            sandtrap.backward: ["leave", "no", "backward", "backwards"],
        }
    },
    True,
    text("legacy.line_1327_124"),
    text("legacy.line_1328_125"),
)

sand_in = Place(
    text("legacy.line_1332_126"),
    text("legacy.line_1333_127"),
    "an endless sandy morass",
    {},
    False,
    "",
    text("legacy.line_1338_128"),
)

debris = Place(
    "at the strewn debris",
    text("legacy.line_1343_129"),
    "some wreckage peppering a vast mud flat",
    {
        box1: {},
        box2: {},
        box3: {},
        box4: {},
    },
    False,
    "",
    text("legacy.line_1353_130"),
)

fog = Place(
    "in an endless bogland, surrounded by fog",
    text("legacy.line_1358_131"),
    "an expanse of mud disappearing into a bank of cloud",
    {fog_load: {fog_load.go: []}},
    True,
    "",
    text("legacy.line_1363_132"),
)

blanksw = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    text("legacy.line_1373_133"),
)

log = Place(
    "in an expanse of mud, dotted with knarled shrubbery",
    text("legacy.line_1378_134"),
    "a massive field of mire, with a few plants here and there",
    {pages: {}},
    False,
    "",
    "You can find nothing further among the scattered shrubs.",
)

swamp = Place(
    "at the swamp",
    text("legacy.line_1388_135"),
    "a sparse wetland, with rushes and trees",
    {
        swamp_load: {swamp_load.go: []},
        swamptrees: {swamptrees.climb: ["climb", "clamber"]},
    },
    False,
    "",
    text("legacy.line_1396_136"),
)

gun = Place(
    "at the abandoned gun",
    text("legacy.line_1401_137"),
    text("legacy.line_1402_138"),
    {aagun: {}},
    False,
    "",
    text("legacy.line_1406_139"),
)

cave = Place(
    "at the endless cliff",
    text("legacy.line_1411_140"),
    "a field of mud, with a rocky formation on the horizon",
    {cavetrap: {cavetrap.enter: ["enter", "into", "in", "go", "explore"]}},
    False,
    "",
    text("legacy.line_1416_141"),
)

cave_in = Place(
    "lost deep in the endless black of a cave system",
    "",
    "black",
    {},
    False,
    "",
    text("legacy.line_1426_142"),
)

wood = Place(
    "in dense woodland",
    text("legacy.line_1431_143"),
    "a dense thicket beginning to take hold on the muddy plain",
    {woodtrees: {woodtrees.climb: ["climb", "clamber"]}},
    False,
    "",
    text("legacy.line_1436_144"),
)

wood_in = Place(
    "deep in the mud of the dense forest",
    text("legacy.line_1441_145"),
    "the thick foliage growing thicker still",
    {
        woodtrap_load: {woodtrap_load.go: []},
        woodtrees: {woodtrees.climb: ["climb", "clamber"]},
    },
    False,
    "",
    "",
)

river = Place(
    "at the waterway",
    text("legacy.line_1454_146"),
    text("legacy.line_1455_147"),
    {
        boat: {
            boat.enter: [
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
        },
        water: {water.enter: ["try to swim into", "swim", "water"]},
    },
    False,
    "",
    text("legacy.line_1474_148"),
)

troops = Place(
    "at the boulders",
    text("legacy.line_1479_149"),
    text("legacy.line_1480_150"),
    {
        stones: {
            stones.climb: ["climb", "clamber"],
            stones.listen: ["listen to", "listen", "to", "hear"],
        }
    },
    False,
    "",
    text("legacy.line_1489_151"),
)

troops_in = Place(
    text("legacy.line_1493_152"),
    text("legacy.line_1494_153"),
    text("legacy.line_1495_154"),
    {
        trooptrap: {
            trooptrap.forward: [
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
            trooptrap.backward: [
                "leave",
                "no",
                "backward",
                "backwards",
                "dont",
                "fall",
                "back",
            ],
        },
        stones: {
            stones.climb: ["climb", "clamber"],
            stones.listen: ["listen to", "listen", "to", "hear"],
        },
    },
    True,
    text("legacy.line_1525_155"),
    "If you move, you'll surely be discovered.",
)

blankse = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    text("legacy.line_1536_156"),
)

blanknw = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    text("legacy.line_1546_157"),
)

blankne = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    text("legacy.line_1556_158"),
)

"""Global variables 2"""

currentloc = plane
prevloc = [plane]
been = []

"""Map of the game and dictionary of direction commands"""

cart = {
    plane: [sand, snake, fog, debris],
    snake: [sand, log, fog, plane],
    sand: [swamp, blankne, plane, blanknw],
    sand_in: [swamp, blankne, plane, blanknw],
    debris: [sand, plane, fog, gun],
    fog: [plane, blankse, cave, blanksw],
    blanksw: [gun, fog, cave, troops],
    log: [blankne, wood, blankse, snake],
    swamp: [river, blankne, sand, blanknw],
    gun: [blanknw, debris, blanksw, troops],
    cave: [fog, blankse, cave.stay(), blanksw],
    cave_in: [fog, blankse, cave.stay(), blanksw],
    wood: [blankne, wood_in, blankse, log],
    wood_in: ["north", "east", "south", "west"],
    river: [river.stay(), swamp, swamp, swamp],
    troops: [blanknw, gun, blanksw, troops_in],
    blankse: [log, wood, cave, fog],
    blanknw: [swamp, sand, gun, troops],
    blankne: [swamp, wood, log, sand],
    troops_in: [troops_in.stay(), troops, troops_in.stay(), troops_in.stay()],
}

directions = {
    cart[currentloc][0]: ["north", "n", "up", "u"],
    cart[currentloc][1]: ["east", "e", "right", "r"],
    cart[currentloc][2]: ["south", "s", "down", "d"],
    cart[currentloc][3]: ["west", "w", "left", "l"],
}


def move(*dir):
    """Changes current location to the one specified in cart after a given dir"""
    global currentloc
    global prevloc
    global turns

    if dir != ():
        turns += 2

        tensetext(rndtext(obs[2]))
        tensetext(rndtext(obs[1]) % directions[dir[0]][0])

        if currentloc.restricmov == False:
            prevloc = []
            prevloc.append(currentloc)

        currentloc = dir[0]
        dirdictupdate()
    else:
        tensetext("Where do you want to go?")


def dirdictupdate():
    """Refreshes the direction dictionary after a move to a new location"""
    global directions

    directions.clear()

    newdirections = {
        0: ["north", "n", "up", "u"],
        1: ["east", "e", "right", "r"],
        2: ["south", "s", "down", "d"],
        3: ["west", "w", "left", "l"],
    }

    newcount = 0

    for i in cart[currentloc]:
        if i not in list(directions.keys()):
            directions[i] = newdirections[newcount]
        else:
            for j in newdirections[newcount]:
                directions[i].append(j)
        newcount += 1


async def examine(*obj):
    """Looks at items or in directions"""
    global turns

    if obj != ():
        if (obj[0] in directions) == True:
            tensetext("You see %s." % obj[0].look)
        else:
            if obj[0].reflib[0] != "hidden":
                tensetext(obj[0].look)
    else:
        if currentloc != cave_in:
            tensetext(currentloc.firstsight)
            currentloc.listitems
        else:
            cavetrap.cavethink()
            currentloc.listitems

    await sink(0.25)
    turns += 0.25


def shout(*obj):
    """If you try to talk"""
    tensetext(rndtext(obs[6]))


async def wait(*obj):
    """Waits a turn in your current location"""
    global turns
    await sink(1)
    turns += 1
    tensetext(rndtext(obs[5]))


async def search(*obj):
    """Returns search function of an item"""
    global turns
    global artifacts

    turns += 1

    if obj != ():
        if (obj[0] in subjects) == True:
            if obj[0].search == "":
                await call(obj[0].inside)
            else:
                tensetext(obj[0].search)
        elif (obj[0] in directions) == True:
            await examine(obj[0])
        else:
            tensetext(obj[0].search)
    else:
        hiddentrue = False
        for i in currentloc.items:
            if i.reflib[0] == "hidden":
                del i.reflib[0]
                tensetext(i.firstsight)
                hiddentrue = True
        if hiddentrue == False:
            if currentloc.look == "endless mud" and (
                artifacts[0] == True and artifacts[1] == True and artifacts[2] == False
            ):
                artifacts[2] = True
                tensetext(text("legacy.line_1709_159"))
                bells = MediaEvent("sound", "BELLS")
                tensetext(bells)
            else:
                tensetext(currentloc.search)
                if currentloc != troops_in:
                    tensetext(rndtext(obs[2]))
                turns += 1


async def help(*com):
    """General help for commands"""
    global turns
    tensetext(text("system.help"))
    await sink(0.25)
    turns += 0.25


async def exit():
    """Quits the game"""
    tensetext("Are you certain? All you've discovered will be lost.")

    do = parser(await prompt(), yn)

    if "yes" in do:
        if quit_handler is not None:
            quit_handler()
        sys.exit()


def think_compile(lib):
    """Returns what you can do with a particular dictionary"""
    options = "You can "
    ia = ""

    for i in lib:
        actions = list(i.actions.keys())
        i1 = i.name
        a1 = ""
        if actions == []:
            a1 = "search "
        for x in list(i.actions.keys()):
            a1 += i.actions[x][0]
            if x != actions[len(actions) - 1]:
                a1 += ", or "
            else:
                a1 += " "
        ia += a1 + i1
        if i != list(lib.keys())[len(lib) - 1]:
            if len(lib) >= 2:
                if i == list(lib.keys())[len(lib) - 2]:
                    ia += ", or "
                else:
                    ia += ", "
            else:
                ia += ", "
        else:
            ia += "."
    options += ia

    return options


async def think(*tho):
    """Lets you know what can be done in a room"""
    global turns
    thinkhere = ""
    heldhere = ""

    if True in artifacts:
        tensetext("A thought that's not your own eats into your mind.")
    if artifacts[0] == True:
        tensetext("The open sky is an endless blue, find them in the earth.")
    if artifacts[1] == True:
        tensetext("The sound of static fills the air, alone amongst the stone.")
    if artifacts[2] == True:
        tensetext("Lost beneath the endless mud a wisp of smoke creeps by.")

    if poisonif == True:
        tensetext("Surely the plane had some medical supplies?")

    if currentloc == cave_in:
        cavetrap.cavethink()

    if len(currentloc.items) != 0:
        items_loadless = {}
        for i in currentloc.items:
            if "_load" not in i.name and i.reflib[0] != "hidden":
                items_loadless[i] = currentloc.items[i]
        thinkhere = think_compile(items_loadless)

    if holding != {}:
        heldhere = think_compile(holding)

    if thinkhere == "You can ":
        thinkhere = ""

    if (thinkhere + heldhere) == "" or (thinkhere + heldhere) == "You can ":
        tensetext("There is nothing to do but move on.")
    else:
        tensetext(thinkhere + heldhere)

    await sink(0.25)
    turns += 0.25


"""Dictionary of general commands"""

commands = {
    examine: ["look", "examine"],
    move: ["move", "go", "walk", "run", "g"],
    help: ["help", "h"],
    think: ["think", "consider", "appraise", "mull", "t"],
    search: ["search", "loot", "salvage", "find"],
    wait: ["wait", "rest", "sleep", "stop"],
    shout: ["talk", "scream", "shout", "speak", "call"],
    exit: ["quit", "exit"],
}

"""Dictionary for yes/no input"""

yn = {"yes": ["yes", "y"], "no": ["no", "n"]}

"""Holds names of items for parser to check against"""

subjects = {}

"""Obstacles and problems"""

obs = [
    [  # Unassailable problems [0]
        "The mud is too deep, too sticky.",
        text("legacy.line_1842_160"),
    ],
    [  # Movements [1]
        "You stumble %s.",
        "You stagger %s.",
        "You manage to go %s.",
        "You think you've gone %s.",
        "It's almost certain you've gone %s.",
        "You went %s, but--, yes.",
        "You try %s.",
        "You went %s, yes.",
    ],
    [  # Flavour [2]
        "The mud sucks at your feet.",
        "Each step aches.",
        "The stench of rotting flora is everywhere.",
        "You spit mud from your mouth.",
        "Something brushes you beneath the mud, and is gone.",
        "You can taste gravel between your teeth.",
        "You wipe muddy snot from your upper lip.",
        "Your tongue sticks at your dry palate.",
        "Your breath scratches your raw throat.",
        text("legacy.line_1864_161"),
        "The air is putrid.",
        "You wipe a brown-red moisture from your eyes.",
        "The rising heat from the bog is suffocating.",
        "Flies hop about the mud's surface.",
        "You try to wipe wet mud from your eyes and face.",
        "Mud has caked dry about your thighs, heavy and stiff.",
        "Your muscles ache from effort.",
        "Your collar worries at insect bites around your neck.",
        text("legacy.line_1873_162"),
        "Your foot snares on something in the mire, but you free it.",
        "You try to rub some of the dried mud from your matted hair.",
        "Your head pounds.",
        "You're desperately thirsty.",
        "Insects choke the air around you.",
        "You need to sit and rest, but there is nowhere.",
        text("legacy.line_1880_163"),
        "The buzz of insects is incessant.",
        text("legacy.line_1882_164"),
        "Sweat remoistens the mud about your face.",
        "Your forearms are red from sunburn, mottled with mud.",
        text("legacy.line_1885_165"),
        text("legacy.line_1886_166"),
        "Your head throbs.",
        "You feel dizzy.",
    ],
    [  # Time [3]
        "The afternoon sun beats down relentlessly.",
        "The sun has definitely sunk in the sky.",
        text("legacy.line_1893_167"),
        "The low, orange sun casts long shadows across the mud.",
        "The sky's dark blue deepens swiftly.",
        text("legacy.line_1896_168"),
        "It is a night of absolute black.",
    ],
    [  # Sand [4]
        text("legacy.line_1900_169"),
        "You must rest - you're desperate to rest.",
        text("legacy.line_1902_170"),
        "You don't know how much longer you can keep this up.",
        text("legacy.line_1904_171"),
        "Your entire body begins to slow from the exertion.",
        text("legacy.line_1906_172"),
        "You have to stop.",
        "You cannot go on any longer.",
        text("legacy.line_1909_173"),
        "Your heavy clothes drag in the muck.",
    ],
    [  # Wait [5]
        text("legacy.line_1913_174"),
        text("legacy.line_1914_175"),
        text("legacy.line_1915_176"),
        "Your slow sinking reminds you that you can never stop.",
        text("legacy.line_1917_177"),
    ],
    [  # Shout [6]
        "You cough a few times, and spit up mud.",
        "You choke out a quiet rasp.",
        "You are too scared to make a sound.",
        "Your chapped lips are too agonising to open.",
        text("legacy.line_1924_178"),
        "You contort your lips and tongue but cannot form a word.",
        "You don't remember how.",
        text("legacy.line_1927_179"),
        "How?",
    ],
    [  # Stretcher [7]
        "Your jaw clenches as you bump along.",
        "Every jolt of the stretcher twists you painfully.",
        text("legacy.line_1933_180"),
        "Your eyes bore into the middle distance.",
        "You are quiet.",
        text("legacy.line_1936_181"),
        "The stretcher-bearers wheeze with effort.",
    ],
    [  # Fog [8]
        "The endless fog presses in on you.",
        "Every hair on your arms has pricked up in the damp cold.",
        "You think you see a shape moving somewhere ahead.",
        text("legacy.line_1943_182"),
        text("legacy.line_1944_183"),
        "That way is north.",
        "That way is east.",
        "That way is south.",
        "That way is west.",
        "You hear a muddy splash somewhere deep in the fog.",
        text("legacy.line_1951_184"),
        "There is no start, no end, no progress.",
        "There is a very slight breeze against your face.",
        "The wind tousles at your muddy hair from behind.",
        "The back of your right hand feels a chilly pang.",
        "You shove your left hand in your pocket to keep it warm.",
        "You're unsure if you've walked a mile or a few feet.",
        "You lose some feeling in your toes.",
    ],
    [  # Leeches [9]
        "Thick, black creatures are all over your body.",
        "You can feel movement from under your clothes.",
        "Some black worms fatten on your legs.",
        "Something writhes against your skin.",
        "Dark worms pulsate and grow on your flesh.",
        text("legacy.line_1966_185"),
        "Wormlike creatures are feasting on your flesh.",
        "You feel the flick of a worm against your collarbone.",
        text("legacy.line_1969_186"),
        "You're covered in writhing, pulsating wormlike things.",
    ],
    [  # Cave [10]
        text("legacy.line_1973_187"),
        text("legacy.line_1974_188"),
        text("legacy.line_1975_189"),
        text("legacy.line_1976_190"),
        text("legacy.line_1977_191"),
        text("legacy.line_1978_192"),
        text("legacy.line_1979_193"),
        text("legacy.line_1980_194"),
        text("legacy.line_1981_195"),
        text("legacy.line_1982_196"),
        "You wander onwards, ever onwards.",
        text("legacy.line_1984_197"),
    ],
    [  # Woods - new locations [11]
        "You find yourself in a small clearing.",
        text("legacy.line_1988_198"),
        text("legacy.line_1989_199"),
        "The foliage around you begins to look a little greener.",
        "Insects begin to swarm around you, and you cannot continue.",
        "The trees around you have become wilted and decayed.",
        text("legacy.line_1993_200"),
        text("legacy.line_1994_201"),
        "You pause, unsure whether to continue this way.",
        "Trees twist together ahead, and you can't continue.",
        text("legacy.line_1997_202"),
        "A low rustle high in the trees seems to circle you.",
        "The trees around you seem unfathomably tall.",
        text("legacy.line_2000_203"),
    ],
    [  # Woods - clues to move forward [12]
        text("legacy.line_2003_204"),
        text("legacy.line_2004_205"),
        text("legacy.line_2005_206"),
        text("legacy.line_2006_207"),
        "You notice some small round burns on a trunk that way.",
        "You think you can make out movement far ahead.",
        "The trees that way have been violently slashed and hacked.",
        "The forest has been cleared a little in that direction.",
    ],
    [  # Woods - clues to leave [13]
        text("legacy.line_2013_208"),
        "The trees seem to thin that way, sparsely pucking the mud.",
        text("legacy.line_2015_209"),
        "You can make out the mudplane somewhere through the trees.",
        "You can see the forest's edge.",
        "The treeline wanes perhaps a few hundred feet away.",
    ],
    [  # Woods - blank forest [14]
        text("legacy.line_2021_210"),
        "The dense forest spreads ahead.",
        "Foliage covers the tree-pocked mire.",
        "The woods stretch ahead of you.",
        "The canopy casts a dark path.",
        "The mud stretches on and on beneath the trees.",
    ],
]

"""Core game functions"""


async def prompt():
    """Raw input"""
    global textrecord
    global pyg_textcompile

    if pyg_init == True and input_handler is not None:
        enter = input_handler()
        if inspect.isawaitable(enter):
            enter = await enter
    else:
        enter = input("> ")

    textrecord.append(enter)
    return enter


def tensetext(x):
    """Requires rawinput after each period or question mark. Keeps big text on the screen."""
    global pyg_textcompile

    tense = []
    sent = ""
    count = 0

    if pyg_init == True and output_handler is not None:
        output_handler(x)
    else:
        for i in x:
            if i != "." and i != "?" and i != "~":
                sent += i
                count += 1
                if count >= 70 and i == " ":
                    sent += "\n"
                    count = 0
            else:
                sent += i
                tense.append(sent)
                sent = ""
                count = 0

        for i in tense:
            if i == "~":
                sys.stdout.write("\n")
            else:
                sys.stdout.write(f"{i.lstrip(' ')}\n")
            if tensetext_display == True:
                sys.stdout.write(f"{input('')}\n")


def rndtext(x):
    """Generates a random line from a given list in obs"""
    return x[random.randint(0, (len(x) - 1))]


def dictmerge(*libs):
    """Compiles the dictionaries it's given into one"""
    uberdict = {}

    for i in libs:
        uberdict.update(i)

    return uberdict


def parser(input, dictionary):
    """Takes an input and returns a list of anything that matches a command in a dictionary, or any variation of it"""
    input = str(input).lower()
    nodigits = "".join(i for i in input if not i.isdigit())
    sentence = nodigits.split()
    output = []

    for i in list(dictionary.keys()):
        out = set(sentence).isdisjoint(set(dictionary[i]))
        if out == False:
            output.append(i)

    return output


async def call(action, *args):
    """Call an engine action and await it if it is asynchronous."""
    result = action(*args)
    if inspect.isawaitable(result):
        return await result
    return result


async def interpret(parsed):
    """Takes parsed commands and processes them"""
    global turns

    """Loads parsed commands into four categories"""
    com = parsed
    dir = []
    spc = []
    sub = []

    testdics = (
        (list(directions.keys()), dir),
        (dictmerge(placeacts, itemacts), spc),
        ((list(subjects.keys()) + list(holding.keys())), sub),
    )

    for j in testdics:
        for i in com:
            for x in j[0]:
                if i == x:
                    j[1].append(i)
                    com.remove(i)

    """Handles multiple contradictory commands and empty commands"""

    allinputs = com, dir, spc, sub
    count = 0
    for i in allinputs:
        if len(i) > 1:
            tensetext("You don't know what to do or where to be. Do you need HELP?")
            await sink(0.25)
            turns += 0.25
            return
        if len(i) == 0:
            count += 1
    if count == len(allinputs):
        tensetext(text("system.invalid"))
        await sink(0.25)
        turns += 0.25
        return

    text("legacy.line_2161_211")

    if len(dir) > 0:
        if (
            currentloc.restricmov == True
            and dir[0] not in prevloc
            and (len(com) == 0 or move in com)
        ) or (dir[0] == currentloc.stay() and (len(com) == 0 or move in com)):
            await sink(0.25)
            turns += 0.25
            tensetext("You can't go that way right now.")
            return

    if sinkdying == True:
        for i in placeacts:
            if i in spc:
                tensetext("You try to move, but you can't reach to do that.")
                await sink(0.25)
                turns += 0.25
                return
        for j in list(subjects.keys()):
            if j in sub:
                tensetext("You try to move, but you can't reach to do that.")
                await sink(0.25)
                turns += 0.25
                return
        if wait in com:
            tensetext("Alone, you wait to die.")
            await sink(1)
            turns += 1

    """Order of interpretation"""

    try:
        await call(com[0], dir[0])
    except (ValueError, IndexError):
        try:
            move(dir[0])
        except (
            ValueError,
            IndexError,
        ):
            try:
                await call(com[0], sub[0])
            except (ValueError, IndexError, TypeError, AttributeError):
                try:
                    await call(com[0])
                except (ValueError, IndexError, AttributeError):
                    try:
                        await call(spc[0], sub[0])
                    except (ValueError, IndexError, TypeError):
                        try:
                            await call(spc[0])
                        except (ValueError, IndexError):
                            try:
                                await examine(sub[0])
                            except:
                                return


async def whatnow():
    """Collects parsed input data and returns interpreted results of the actions"""
    await interpret(
        parser(
            await prompt(),
            dictmerge(directions, commands, subjects, placeacts, holding, itemacts),
        )
    )


async def room():
    """Loads the current area"""
    global been
    global turns

    currentloc.loaditems()
    currentloc.getactions()
    holding_init()

    if currentloc not in been:
        if currentloc == "cave_in":
            been.append(currentloc)
        else:
            been.append(currentloc)
            tensetext(currentloc.firstsight)
    else:
        if currentloc == cave_in:
            tensetext(text("legacy.line_2249_212"))
            turns += 3
        else:
            tensetext("You are %s." % currentloc.name)

    if currentloc.restricmov == True:
        tensetext(currentloc.restricwhy)

    for i in list(subjects.keys()):
        if "_load" in i.name:
            await call(i.go)

    if turns_display == True:
        sys.stdout.write(f"{turns}\n")


def dead(why):
    """Prints death reasons, restarts game"""
    raise DeathError(why)


"""Deals with the effects of poison"""

poisonif = False
poisonlen = 0
poisoncount = 0


def poison():
    global poisoncount

    if poisonif == True:
        if poisonlen <= (turns - 10):
            dead(text("legacy.line_2284_213"))
        elif poisonlen <= (turns - 6) and poisoncount == 2:
            tensetext(text("legacy.line_2288_214"))
            poisoncount = 3
        elif poisonlen <= (turns - 2) and poisoncount == 1:
            tensetext(text("legacy.line_2293_215"))
            poisoncount = 2
        elif poisonlen <= turns and poisoncount == 0:
            poisoncount = 1


"""Functions for dealing with flare usage"""

flare_east = [[wood]]
flare_west = [[troops_in]]
flare_path_east = []
flare_path_west = []
flare_eloc = wood
flare_wloc = troops
flare_eloc_templook = ""
flare_wloc_templook = ""
flare_weloc_templook = ""
flareloc_tempfirstsight = ""
flare_count = 1
flare_up = False
flareloc = currentloc
flare_turns = 0
flarewin_turns = 0
time_e = []
time_w = []
flare_eprevloc = wood
flare_wprevloc = troops


def routescan2_rec(begin, target):
    """Finds quickest route between two locations"""
    global flare_east
    global flare_west
    global flare_count

    if target in begin[0]:
        return begin[0]
    else:
        for i in begin:
            if len(i) == flare_count:
                try:
                    for x in cart[i[len(i) - 1]]:
                        if x != i[0]:
                            newi = []
                            for j in i:
                                newi.append(j)
                            newi.append(x)
                            newj = []
                            for j in newi:
                                newj.append(j)
                            begin.append(newj)
                            if x == target:
                                return newi
                except KeyError:
                    pass

        flare_count += 1
        return routescan2_rec(begin, target)


async def flarefunc():
    """Recurring function for when the flare is up"""
    global flare_eloc
    global flare_wloc
    global flare_up
    global flare_eloc_templook
    global flare_wloc_templook
    global flareloc_tempfirstsight
    global turns
    global flare_path_east
    global flare_count
    global flarewin_turns
    global time_e
    global time_w

    """Handles the speed at which the search parties move"""

    time = int(turns - flare_turns)
    time_e = [x for x in range(0, (len(flare_path_east))) for _ in (0, 1, 2)]
    time_w = [x for x in range(0, (len(flare_path_west))) for _ in (0, 1, 2)]

    if time_e != []:
        for i in reversed(time_e):
            time_e.append(i)
        mid = time_e.pop(len(time_e) // 2)
        time_e = [y for y in time_e if y != mid]
        for i in range(0, 3):
            time_e.insert((len(time_e) // 2), mid)

    if time_w != []:
        for i in reversed(time_w):
            time_w.append(i)
        mid = time_w.pop(len(time_w) // 2)
        time_w = [y for y in time_w if y != mid]
        for i in range(0, 3):
            time_w.insert((len(time_w) // 2), mid)

    text("legacy.line_2391_216")

    if flare_up == True:
        try:
            flare_eprevloc = flare_eloc
            flare_eloc = flare_path_east[time_e[time]]
            if "a few figures" in flare_path_east[time_e[time - 1]].look:
                flare_path_east[time_e[time - 1]].look = flare_eloc_templook
            if "a few figures" not in flare_eloc.look:
                flare_eloc_templook = flare_eloc.look
                flare_eloc.look += text("legacy.line_2401_217")
                if flare_path_east[time_e[time + 1]] == currentloc:
                    flare_eloc.look += ". They're coming this way"
                else:
                    flare_eloc.look += ". They're not coming towards you"
        except IndexError:
            pass
        try:
            flare_wprevloc = flare_wloc
            flare_wloc = flare_path_west[time_w[time]]
            if "dot the landscape" in flare_path_west[time_w[time - 1]].look:
                flare_path_west[time_w[time - 1]].look = flare_wloc_templook
            if "dot the landscape" not in flare_wloc.look:
                flare_wloc_templook = flare_wloc.look
                flare_wloc.look += text("legacy.line_2415_218")
                if (
                    flare_path_west[time_w[time + 1]] == currentloc
                    or flare_path_west[time_w[time + 2]] == currentloc
                ):
                    flare_wloc.look += ". They're coming this way"
                else:
                    flare_wloc.look += ". They're not coming towards you"
        except IndexError:
            pass

        if flare_wloc == flare_eloc:
            if flare_wloc in been:
                been.remove(flare_wloc)

            if flare_wloc == currentloc:
                dead(text("legacy.line_2432_219"))

            flare_wloc.name += ", surrounded by bodies"
            flare_wloc.firstsight += text("legacy.line_2436_220")
            flare_wloc.look = flare_wloc_templook
            flare_eloc.look = flare_eloc_templook

            flare_wloc.items[bodies] = {}
            flare_up = False

        if flare_eloc == currentloc or (
            flare_eprevloc == currentloc and prevloc[0] == flare_eloc
        ):
            tensetext(text("legacy.line_2447_221"))
            turns += 1
            flarewin_turns = turns
            del flare_east[:]
            flare_east.append([currentloc])
            flare_count = 1
            flare_path_east = routescan2_rec(flare_east, wood)
            await flare_win()

        if flare_wloc == currentloc or (
            flare_wprevloc == currentloc and prevloc[0] == flare_wloc
        ):
            dead(text("legacy.line_2461_222"))

        for i in cart[currentloc]:
            if i == flare_eloc:
                tensetext(
                    "Shouts echo across the endless mud somewhere to the %s."
                    % directions[cart[currentloc][cart[currentloc].index(i)]][0]
                )

            if i == flare_wloc:
                tensetext(
                    text("legacy.line_2473_223")
                    % directions[cart[currentloc][cart[currentloc].index(i)]][0]
                )


async def flare_win():
    """Win condition for being found by your allies"""
    global flare_eloc
    global flare_wloc
    global turns
    global currentloc
    global time_e

    stretcher = True

    m = {}
    m[move] = commands[move]
    movecom = dictmerge(directions, m)

    while stretcher == True:
        movetry = False
        looktry = False
        thinktry = False

        do = parser(
            await prompt(),
            dictmerge(directions, commands, subjects, placeacts, holding, itemacts),
        )

        for i in do:
            if i == examine:
                looktry = True
            if i == think:
                thinktry = True
            for x in list(movecom.keys()):
                if i == x:
                    movetry = True

        if movetry == True and looktry == False:
            tensetext(text("legacy.line_2513_224"))
        elif looktry == True:
            tensetext("All you can see is the blank, open sky above.")
        elif thinktry == True:
            if True in artifacts:
                tensetext("A thought that's not your own eats into your mind.")
            if artifacts[0] == True:
                tensetext("The open sky is an endless blue, find them in the earth.")
            if artifacts[1] == True:
                tensetext("The sound of static fills the air, alone amongst the stone.")
            if artifacts[2] == True:
                tensetext("Lost beneath the endless mud a wisp of smoke creeps by.")
            tensetext(text("legacy.line_2527_225"))

        time = int(turns - flarewin_turns)
        time2 = int(turns - flare_turns)

        near = False
        for i in cart[currentloc]:
            if i == flare_wloc:
                tensetext(text("legacy.line_2537_226"))
                time_e = [x for x in range(1, (len(flare_path_east)))]
                near = True
        if near == False:
            time_e = [x for x in range(0, (len(flare_path_east))) for _ in (0, 1)]
            time_e.remove(0)

        if flare_eloc == flare_wloc:
            dead(text("legacy.line_2547_227"))

        if flare_eloc == wood:
            dead(text("legacy.line_2552_228"))

        turns += 1
        flare_eloc = flare_path_east[time_e[time]]
        try:
            flare_wloc = flare_path_west[time_w[time2]]
        except IndexError:
            pass

        try:
            tensetext("You think you've been carried %s." % directions[flare_eloc][0])
        except KeyError:
            tensetext("Your group moves on.")
        currentloc = flare_eloc
        dirdictupdate()
        tensetext(rndtext(obs[7]))


"""Handles sinking if you don't move"""

sinkstart = -1
sinkcount = 0
sinkdying = False


async def sink(*t):
    global sinkcount
    global sinkstart
    global sinkdying

    if sinkstart == -1:
        sinkstart = turns

    if turns - sinkcount != sinkstart and sinkdying == False:
        sinkstart = -1
        sinkcount = 0
    else:
        if t != ():
            sinkcount += t[0]
        else:
            sinkcount += 1

        if sinkcount >= 2:
            sinkdying = True
            await sink_death()
        elif sinkcount > 1:
            tensetext("You're having trouble shifting your weight.")
        elif sinkcount >= 0.75:
            tensetext(text("legacy.line_2602_229"))


async def sink_death():
    global turns
    global currentloc
    global prevloc
    global sinkdying
    global sinkcount

    currentloc.restricmov = True
    prevloc = []

    while sinkdying == True:
        if sinkcount >= 5:
            sinkdying = False
            dead(text("legacy.line_2620_230"))
        elif sinkcount >= 4:
            if currentloc == cave_in:
                tensetext(text("legacy.line_2625_231"))
            else:
                tensetext(text("legacy.line_2629_232"))
            turns += 1
            sinkcount += 0.5
            await whatnow()
            await status()
            await sink_death()
        elif sinkcount >= 3:
            tensetext(text("legacy.line_2638_233"))
            turns += 1
            sinkcount += 0.5
            await whatnow()
            await status()
            await sink_death()
        elif sinkcount >= 2:
            tensetext(text("legacy.line_2647_234"))
            turns += 1
            sinkcount += 0.5
            await whatnow()
            await status()
            await sink_death()
        else:
            tensetext("You flounder deep in the mud, utterly stuck.")
            sinkcount += 0.25
            await whatnow()
            await status()
            await sink_death()


"""Handles being affected by leeches"""

leechcount = 0
leechsucked = False


def leeched():
    global leechcount
    global leechsucked
    global poisonif
    global poisonlen

    leechcoms = {
        leeches: {leeches.rid: ["pull off", "kill", "get rid of", "clear", "pull"]}
    }

    if leechsucked == True and prevloc[0] == swamp:
        leeches.pickup(leechcoms)

    if leechsucked == True and currentloc != swamp:
        tensetext(rndtext(obs[9]))
        leechcount += 1

    if leechcount == 5:
        tensetext(text("legacy.line_2687_235"))
        poisonif = True
        poisonlen = turns


"""Handles the relentless march of time"""

timeprogress = 0
timedisplayed = []


def time():
    global timeprogress
    global timedisplayed

    if turns >= 3 and timeprogress == 0 and 0 not in timedisplayed:
        if currentloc != cave_in:
            tensetext(obs[3][0])
            timecol = MediaEvent("bg", 20)
            tensetext(timecol)
            timedisplayed.append(0)
        timeprogress = 1
    if turns >= 10 and timeprogress == 1 and 1 not in timedisplayed:
        if currentloc != cave_in:
            tensetext(obs[3][1])
            timecol = MediaEvent("bg", 40)
            tensetext(timecol)
            timedisplayed.append(1)
        timeprogress = 2
    if turns >= 15 and timeprogress == 2 and 2 not in timedisplayed:
        if currentloc != cave_in:
            tensetext(obs[3][2])
            timedisplayed.append(2)
        timeprogress = 3
    if turns >= 17 and timeprogress == 3 and 3 not in timedisplayed:
        if currentloc != cave_in:
            tensetext(obs[3][3])
            timecol = MediaEvent("bg", 90)
            tensetext(timecol)
            timedisplayed.append(3)
        timeprogress = 4
    if turns >= 23 and timeprogress == 4 and 4 not in timedisplayed:
        if currentloc != cave_in:
            tensetext(obs[3][4])
            timecol = MediaEvent("bg", 130)
            tensetext(timecol)
            timedisplayed.append(4)
        timeprogress = 5
    if turns >= 24 and timeprogress == 5 and 5 not in timedisplayed:
        if currentloc != cave_in:
            tensetext(obs[3][5])
            timedisplayed.append(5)
        timeprogress = 6
    if turns >= 28 and timeprogress == 6 and 6 not in timedisplayed:
        if currentloc != cave_in:
            tensetext(obs[3][6])
            timecol = MediaEvent("bg", 170)
            tensetext(timecol)
            timedisplayed.append(6)
        timeprogress = 7
    if turns >= 30:
        dead(text("legacy.line_2750_236"))


"""Sends SFX for particular locations"""

musicloc = ""


def music():
    global musicloc

    if musicloc != currentloc:
        if currentloc == river:
            sfx = MediaEvent("sound", "RIVER")
            tensetext(sfx)
        if currentloc == troops:
            sfx = MediaEvent("sound", "WHISPERS")
            tensetext(sfx)
        if currentloc == wood:
            sfx = MediaEvent("sound", "BIRDS")
            tensetext(sfx)

    musicloc = currentloc


async def status():
    """Handles status effects"""
    poison()
    await flarefunc()
    leeched()
    time()
    music()


async def wrap():
    """Recurring function that runs the game"""
    while True:
        await status()
        await room()
        await whatnow()


"""Final global variables that handle game progress and errors"""

artifacts = [False, False, False]
turns_display = False
tensetext_display = False
textrecord = []


async def start(deaths, turns, tense, artifact_meta):
    """Starts the game"""
    global turns_display
    global tensetext_display
    global artifacts
    global pyg_init

    if turns == True:
        turns_display = True

    if tense == True:
        tensetext_display = True

    artifacts = artifact_meta

    if False in artifacts:
        pass
    else:
        timecol1 = MediaEvent("bg", 255)
        tensetext(timecol1)
        tensetext(" ")
        reset = MediaEvent("reset", "")
        tensetext(reset)
        tensetext(text("intro.final_ending"))
        timecol2 = MediaEvent("bg", 0)
        tensetext(timecol2)
        end = MediaEvent("end", 0)
        tensetext(end)
        tensetext(" ")
        tensetext(text("intro.final_credit"))
        sys.exit()

    if deaths == 0:
        music = MediaEvent("music", ("main", -1))
        tensetext(music)
        tensetext(text("intro.help_prompt"))
        timecol = MediaEvent("bg", 0)
        tensetext(timecol)
        tensetext(" ")
        tensetext(text("intro.first_run"))
    elif deaths <= 2:
        timecol1 = MediaEvent("bg", 255)
        tensetext(timecol1)
        tensetext(" ")
        reset = MediaEvent("reset", "")
        tensetext(reset)
        tensetext(text("intro.restart_early"))
        timecol = MediaEvent("bg", 0)
        tensetext(timecol)
        planenoise = MediaEvent("sound", "PLANE")
        tensetext(planenoise)
    elif deaths <= 4:
        timecol1 = MediaEvent("bg", 255)
        tensetext(timecol1)
        tensetext(" ")
        reset = MediaEvent("reset", "")
        tensetext(reset)
        tensetext(text("intro.restart_mid"))
        timecol = MediaEvent("bg", 0)
        tensetext(timecol)
        planenoise = MediaEvent("sound", "PLANE")
        tensetext(planenoise)
    else:
        timecol1 = MediaEvent("bg", 255)
        tensetext(timecol1)
        tensetext(" ")
        reset = MediaEvent("reset", "")
        tensetext(reset)
        tensetext(text("intro.restart_late"))
        timecol = MediaEvent("bg", 0)
        tensetext(timecol)
        planenoise = MediaEvent("sound", "PLANE")
        tensetext(planenoise)

    await wrap()


_STATE_EXCLUDES = {
    "_INITIAL_STATE",
    "_STATE_EXCLUDES",
    "_capture_initial_state",
    "_is_state_value",
    "reset_state",
}
_INITIAL_STATE = {}


def _is_state_value(name, value):
    """Return whether a module global is part of mutable runtime state."""
    if name.startswith("__") or name in _STATE_EXCLUDES:
        return False
    return not (
        inspect.ismodule(value)
        or inspect.isfunction(value)
        or inspect.isclass(value)
        or inspect.ismethod(value)
    )


def _capture_initial_state():
    """Capture initial module state with object relationships intact."""
    state = {
        name: value for name, value in globals().items() if _is_state_value(name, value)
    }
    _INITIAL_STATE.update(copy.deepcopy(state))


def reset_state():
    """Reset the runtime to its initial world and traversal state."""
    globals().update(copy.deepcopy(_INITIAL_STATE))


_capture_initial_state()
