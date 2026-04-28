# ruff: noqa

import inspect, sys, random, time

from mud.events import MediaEvent

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
            tensetext(
                "The light flares and sputters out, and with it your breath. Your heart pounds in your chest as you consider what you saw in the black, silent cavern. A thousand eyes on a thousand faces, quiet, blinking, staring at you, just out of reach. A thousand bodies, caked in mud, surrounding you, upright, a hollow crowd intent on you at their centre. It is deathly dark. You feel sick. The darkness beats down upon you."
            )
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
            tensetext(
                "The lighter manages a brief spark, and you catch a glimpse of a hopeful exit to the %s."
                % directions[cavedir][0]
            )
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
    "Beneath caked mud, the side of the lighter bears a red symbol.",
    "With filthy hands you pull the lighter apart. There is very little fluid left. You manage to piece it back together, though muck certainly now clogs the mechanisms.",
    {},
)


class Fighter(Item):
    def inside(self):
        global searched

        if self in searched:
            tensetext(
                "The plane's first aid kit is gone, perhaps wherever the cockpit door went."
            )
        else:
            tensetext(
                "The plane's first aid kit is gone, perhaps wherever the cockpit door went. You find a lighter wedged beneath the aircraft's seat."
            )

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
        tensetext(
            "You feel for two reasonably sturdy handholds and with a grunt, haul yourself from the mud. Instantly the trunk crumbles beneath you, and you are plunged into the writhing mess of worms, beetles and insects within. You flail wildly, grasping at parts of the rotting log that crumble in your fists, your entire body covered in crawling animals and sucking mud. You feel a sharp pain in your left hand. Somehow you struggle to your feet, utterly covered in mud and with creeping insects in your hair and clothes. With disgust, you clear them off as best you can, but you stop dead as you clean you hands. The puncture marks are small, but the skin is swelling and a widening patch of blotchy crimson is darkening your palm."
        )
        poisonif = True
        poisonlen = turns

        self.firstsight = "The massive trunk has been cleaved in two, with easy passage between either side."
        currentloc.firstsight = "The massive trunk has been cleaved in two, with easy passage between either side."
        tensetext(stump.firstsight)
        currentloc.search = "The log teems with writhing, pullulating insect life. The lurking snake is nowhere to be seen."
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
        tensetext(
            "The mud is deep and sticky here. It takes a great deal of time and considerable effort, but you circumnavigate the giant trunk. Covered to the chest in mud, with splatters across your face and in your hair, you can continue."
        )

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
        tensetext(
            "You punch the log and you fist sinks through with such ease that you're instantly shoulder-deep and off-balance. Pulling your arm out brings away a significant chunk of the log, and with it a teeming multitude of beetles, worms, and insects that cover your arm, and fall into the mud around you. Shaking as many off you arms and hand as possible, you pull away more of the log, until there is enough of a gap to squeeze through. Now covered in crawling animals, you inch your way through, and it is only once firmly between the two halves that you hear an angry hiss. The bite is so powerful that your hand is wrenched away as the snake escapes. You pass the log, and the puncture marks are small, but the skin is swelling and a widening patch of blotchy crimson is darkening your hand."
        )
        poisonif = True
        poisonlen = turns

        self.firstsight = "The massive trunk has been cleaved in two, with easy passage between either side."
        currentloc.firstsight = "The massive trunk has been cleaved in two, with easy passage between either side."
        currentloc.search = "The log teems with writhing, pullulating insect life. The lurking snake is nowhere to be seen."
        currentloc.name = "at the riddled treestump, split in two"
        currentloc.restricmov = False

        del currentloc.items[stump][stump.climb]
        del currentloc.items[stump][stump.smash]
        currentloc.items[stump][stump.thru] = ["go through", "through", "cross"]
        currentloc.loaditems()
        currentloc.getactions()

    def thru(self):
        tensetext(
            "You trudge through the mud that lays between the two halves of the collapsed trunk, and can go in any direction."
        )


stump = Stump(
    ["stump", "log", "tree"],
    "the gigantic, crumbling log",
    "The long, mud-covered, blackened trunk lies directly across the way forward.",
    "The bark appears weak and crumbly, gnawed at by countless insects.",
    "The log teems with writhing, pullulating insect life, with something bigger moving beneath the horrid mess.",
    {},
)

route = Item(
    ["route itinerary", "notes", "route", "itinerary", "course", "manifest"],
    "the plane's route itinerary",
    "Though muddy, torn and battered, the route itinerary still bears some legible script",
    'Flicking through the pages, one section stands out through smears of grime: "but circle around and approach from west".',
    'Flicking through the pages, one section stands out through smears of grime: "but circle around and approach from west".',
    {},
)


class Pages(Item):
    def inside(self):
        global searched
        global turns

        if self in searched:
            tensetext("No pages remain in the scrubland.")
        else:
            tensetext(
                "You scrabble helplessly about the mud, snatching battered sheets from prickly branches and smearing away mud with mud-smeared hands."
            )
            tensetext(rndtext(obs[2]))
            tensetext(
                "Though each step is gruelling, you grab page after page. At last you have them all. They are a tattered section of the plane's route itinerary."
            )
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
    "Some papers from the plane have blown this way, caught, muddy and tattered in the brittle branches.",
    "Anything could be on what's left of the notes, but without searching them all it's hard to know what information remains, if any.",
    "",
    {},
)


class Swamptrees(Item):
    def climb(self):
        global turns
        tensetext(
            "You find a tentative hold on a tree and wrench yourself up. The tree collapses immediately, and you are plunged into the filthy water. You burst from the surface, gasping for air, covered in the rotting filth of the swamp."
        )
        turns += 1


swamptrees = Swamptrees(
    ["trees", "tree"],
    "the knarled trees",
    "Knarled black trees reach out of the swamp.",
    "The trees don't look strong enough to carry any weight, and too smooth to gain any purchase on.",
    "You can't find anything in the withered branches of the trees.",
    {},
)


class Woodtrees(Item):
    def climb(self):
        global turns
        tensetext(
            "Every time you work your fingers into the tree's bark the strength to lift yourself leaves you. You stand, holding the tree, sinking powerlessly into the mire."
        )
        turns += 1


woodtrees = Woodtrees(
    ["trees", "tree"],
    "the towering trees",
    "A thousand trees stretch into the distance around you.",
    "The trees don't look strong enough to carry any weight, and too smooth to gain any purchase on.",
    "You move from tree to tree but you can't find anything in their withered branches.",
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

        tensetext(
            "You pull the wormlike things painfully from your arms and legs, leaving slowly bleeding wounds. You take off your shirt, wind it into a tight coil, and use it to bat them from your back and chest. It takes considerable time, but you carefully remove each of the black creatures while slowly sinking further and further into the mud."
        )
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
    "There are a handful of rapidly growing wormlike things hanging off your skin.",
    "You're covered in perhaps a dozen black worms, and they appear to be sucking at your flesh, growing as they do.",
    "The creatures are all over you - arms, legs, neck, and under your clothes.",
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
                    tensetext(
                        "You feel the mud becoming more solid beneath you, sticky but relatively shallow."
                    )
                    sandif = False
                    await interpret(do)
                else:
                    turns += 1
                    if movetry == True and looktry == False:
                        tensetext(rndtext(obs[1]) % directions[sand_movedir][0])
                        tensetext(rndtext(obs[4]))
                    else:
                        sandif = False
                        dead(
                            "Faltering for only a moment you sink irrevocably, and you are helpless as the mud and sand close over your face. You realise that you will never breathe or see again. The mire has taken you."
                        )

            sandcount += 1

    def backward(self):
        global currentloc

        currentloc = prevloc[0]
        dirdictupdate()


sandtrap = Sandtrap(
    ["sand", "mire", "sandy", "mud"],
    "the murky, sandy mire",
    "The loose and sandy mud stretches on into the distance.",
    "The sandy mud seems a little thinner than the sucking mess you're traversed.",
    "You reach a tentative leg into the sandy mud and find yourself sinking far quicker and deeper than before.",
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

            wood_in.search = "You wander the immediate woods, the mire sucking at your steps, but there's no traces or markings to be found."

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
                                wood_movedir = i

                        if looktry == True:
                            tensetext(wood_movedir[2])
                            await sink(0.25)
                            turns += 0.25
                        else:
                            if wood_movedir[0] == True:
                                woods_correct += 1
                            elif wood_movedir[0] == False:
                                woods_correct = 0

                            if wood_movedir[1] == True:
                                woodif = False
                                woods_movedyet = True

                                tensetext(
                                    "You're getting towards the edge of the woodland, the mud still dragging at you with every step."
                                )

                                currentloc = wood
                                dirdictupdate()
                            else:
                                tensetext(rndtext(obs[1]) % wood_movedir[3])
                                tensetext(rndtext(obs[2]))
                                tensetext(rndtext(obs[11]))

                                if woods_correct == 3:
                                    dead(
                                        "The trees begin to be replaced by stumps, and the forest clears around you. You wearily plod forward, your legs screaming with the effort of your constant trudge, yet you think your steps are becoming easier - yes - the mud is becoming shallower. You see a wooden palisade ahead of you, and a makeshift gate. Before you even notice them two uniformed figures in red tunics are rushing towards you, their guns raised. Their eyes dart about your body, until their expressions change, and they toss their weapons to one side. They grab you forcefully, and drag you backwards towards the wall. You vision reels upwards and you go limp, staring at the infinite sky. Shouts come from all around and you're taken inside a small tent, a figure strapping you firmly to a bed. There is fear in their eyes. Someone in a white coat puts his hand around your jaw and firmly pushes your head back and to the right. The tent stinks of decay. You feel a slight prick in your neck. You sink softly to sleep."
                                    )

                                turns += 1
                                woods_movedyet = True
                else:
                    await interpret(do)


woodtrap_load = Woodtrap([""], "_load", "", "", "", {})


class Trooptrap(Item):
    def forward(self):
        dead(
            "You stagger from the monolith, staring grim and square at the soldiers' backs. Each pace aches as you slowly get closer and closer, until one glances behind. A shout goes up and the dragged ropes are dropped, rifles haphazardly drawn with gaunt, fearful faces behind the sights. Silence hangs in the air. You take a step and a rattle of shots accompanies explosions of pain across your body. You drop, shattered, the world blurring to nothing."
        )

    async def backward(self):
        global currentloc
        global turns

        tensetext(
            "You remain pressed anxiously against the monolith, you heartbeat slowing as the soldiers move ahead of you."
        )
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
    "The soldiers wear matching uniforms with blue armbands, mottled by mud and blood. They carry rifles, and the lone figure with the aerial pack leads them. The equipment they drag looks like heavy artillery shells.",
    "You cannot search the troops without approaching them.",
    {},
)


class Stones(Item):
    def listen(self):
        global artifacts

        tensetext(
            "Endless dry whispers whip around the standing stones, their rough tops and erratic placement creating strange tunnels and echoes, distorting and bending every sound."
        )

        if artifacts[0] == True and artifacts[1] == False:
            artifacts[1] = True
            tensetext("The sound of static fills the air, alone amongst the stone.")

        if currentloc == troops:
            tensetext("You think you hear voices, but you can't be certain.")
        if currentloc == troops_in:
            tensetext(
                "The voices of the soldiers warp and strain around the standing stones."
            )

    def climb(self):
        tensetext("The stones are too vast and smooth to scale.")


stones = Stones(
    ["stones", "rocks", "monoliths", "standing", "boulders"],
    "the standing stones",
    "A series of standing stones rise around you.",
    "The smallest reaching to your head and the largest many times your height, hundreds of standing stones puncture the mud like a gigantic savage cemetery. The tops taper to often jagged peaks, no two seeming alike.",
    "You can find nothing in or around the stones - they mark the mud and nothing more.",
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

        tensetext(
            "You take a few tentative steps into the rocky opening. You lean forward, peering into the gloom, and sense a yawning depth opening just ahead. You shiver, your stomach cold. You try to find a stable place on the rock - anywhere that you might rest and finally stand still, even for a moment. You step forward, exhausted. Your foot twists painfully on a slippery rock, plunging you headlong and downwards, inescapably, into the dark of the cave."
        )
        tensetext(
            "In total darkness you are mercilessly thrown against the tunnel's steep and jagged edges."
        )
        timecol = MediaEvent("bg", 255)
        tensetext(timecol)
        tensetext(
            "You tumble endlessly, sightless. For a fleeting moment the constant pummelling ceases, and in the black deep it feels as though you're weightless, floating. You feel your bones crunch as you hit the mud, and are quickly subsumed. Writhing with panic you wrench yourself to your feet. You may be bleeding, you may be broken in a dozen ways, and you may be coated in filth, but you are deep under the earth, and it is deathly dark in all directions. You continue to sink into the mire."
        )
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
                    tensetext(
                        "Arms groping for an opening you blindly flatten yourself through a slim crevice. Sideways you proceed, deep in the mud and dark, the rock faces so tight you can barely move, but must. Your throat tightens when you see what could be a speck of light far ahead."
                    )
                    tensetext(
                        "You don't know how long it takes, but you force your stiff and aching body through the crushing rock until you at last emerge back into the endless mire, the light burning your eyes. Breathless, battered and exhausted, the mud continues to drag you down, and you must continue."
                    )
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
                        tensetext(
                            "You've no idea how far this cavern stretches - the fathomless space is deafening."
                        )
                    if cavecurrent == "unknown":
                        tensetext(
                            "The space seems to spiral impossibly away, and then seem so crushingly close your heart pounds."
                        )
                else:
                    await interpret(do)

            if caverand < 2:
                if wormcount == 0:
                    tensetext(
                        "You can hear the mud heaving in a cavern nearby. Something massive is moving beneath the mud."
                    )
                    wormcount += 1
                elif wormcount == 1:
                    tensetext(
                        "You feel the mire creep higher up your legs as something truly huge rumbles through the dark mud ahead."
                    )
                    wormcount += 1
                elif wormcount == 2:
                    tensetext(
                        "The mire rises up around you as something unthinkably large circles you from under the mire. Perhaps it dives down or moves on, but you're almost sucked under with the receding mud."
                    )
                    wormcount += 1

    def cavethink(self):
        global cavecurrent

        if cavecurrent == "small":
            tensetext(
                "You sense something just out of your touch, and the chamber seems to press in an all sides."
            )
        if cavecurrent == "medium":
            tensetext(
                "The bleak cavern walls seem some way off, though how far you cannot tell."
            )
        if cavecurrent == "large":
            tensetext(
                "Your movements echo off into an impossible darkness, and you feel overwhelmed by silent space."
            )
        if cavecurrent == "unknown":
            tensetext(
                "The infinite dark air above seems to vibrate with sheer space. You turn to somehow escape it and find the rock all around you, hot, close, still."
            )


cavetrap = Cavetrap(
    ["cave", "cavern", "opening", "rock", "rocky", "fissure"],
    "the rocky fissure",
    "The opening in the rock face is the only visible blemish in the endless cliff face.",
    "The fissure seems large enough to enter, and may provide respite from the sucking mud.",
    "You cannot see far into the dark of the opening, but you suspect this could be a cave system.",
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
            fog.firstsight = "Each direction looks the same, and no landmarks can be seen through the thick cloud."
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
                        tensetext(
                            "The frigid cloud gives way to a thin mist, and you emerge from the fog."
                        )
                        fog.firstsight = "After a while the air takes on a chill, and your skin bristles. Before you know it, you find yourself utterly engulfed by fog, knee-deep in the mire."
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
    "Sitting obstinately in the mire, a small metal cache appears to have landed flat enough not to sink, yet.",
    "The ridging on the metal makes you think the cache may contain some sort of armaments.",
    "With a draining heave the metal creaks back. Inside are hundreds and hundreds of filthy machinegun bullets, shaken from their chains, and all but useless without a gun.",
    {},
)

box2 = Item(
    ["square", "wood", "wooden", "cabinet", "cupboard"],
    "a square and sturdy wooden cabinet",
    "Squat and sturdy, a wooden cabinet faces lazily toward the sky.",
    "Laying on its back, gravity seems to be all that holds the square wooden cabinet's door shut.",
    "It won't open. You can't work out what's stopping it: whether some sort of mechanism has collapsed or if something inside is somehow preventing the door opening out. Either way, you simply cannot open it, and the effort is leaving you deeply drained.",
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
        flare.look = "The flare looks dry enough to work, but you've run out of flares."
        flare.search = "Prising apart the flare with filthy hands it all appears to be in working order, but it's useless now that you've fired the flare."

        if currentloc == cave_in:
            if cavecurrent == "large":
                tensetext(
                    "You fire the flare high into the dark above you. The red light illuminates the great expanse of the cavern, and you can see a small passage to the %s that mud slowly slops from. The passage goes up."
                    % directions[cavedir][0]
                )
                cavehint = 6
                flareloc = currentloc
            elif cavecurrent == "unknown":
                tensetext(
                    "You fire the flare into the dark, and it's swallowed hungrily by the black. Once again, you are sightless, but in the brief glow, you swear you spotted a new way forward to your %s."
                    % directions[cavedir][0]
                )
                cavehint = 1
            elif cavecurrent == "medium":
                tensetext(
                    "The flare shoots into the dark but hits the cavern wall not far ahead, falling uselessly into the sucking mud. Though once more in the black, you're sure that the flare's red glow revealed some passage to the %s."
                    % directions[cavedir][0]
                )
                cavehint = 2
            else:
                tensetext(
                    "You fire the gun and throw yourself headlong into the mire as the hot flare richochets off the tight cavern walls. You surface into darkness covered in thick muck: the mud has swallowed the flare entirely. The black is absolute, and still you sink."
                )
        elif currentloc == wood_in:
            tensetext(
                "You fire the flare above you, but it doesn't make it through the canopy. You watch the flare fall, lit, wasted, back into the mud, where it is quickly sucked under."
            )
        else:
            flare_up = True
            flareloc = currentloc
            flare_turns = turns
            flare_path_east = routescan2_rec(flare_east, flareloc)
            flare_count = 1
            flare_path_west = routescan2_rec(flare_west, flareloc)

            flareloc.look += ". The murky red glow of the flare descends slowly"
            flareloc.firstsight += " High above, the flare hangs in the air, marking your location with a dull red."
            tensetext(
                "Holding the gun aloft you fire the flare high into the air. The light hangs eerily in the air, descending silently, slowly."
            )

            if currentloc == troops_in:
                tensetext(
                    "From behind the rock you hear the soldiers' footsteps immediately stop. A few hushed questions are shared in the terse silence. Shaking, you leave the safety of the boulder."
                )
            if currentloc == wood:
                tensetext(
                    "It takes a moment or two, but you hear movement in the trees, getting louder and closer quickly. A group of soldiers burst from the trees on all sides, each clutching a gun with nervous fear."
                )


flare = Flare(
    ["flare", "flaregun"],
    "the flare",
    "Though bent and dented, the flare appears intact.",
    "The flare looks damp, but dry enough to work, worn, but not enough to be broken.",
    "With mucky fingers you prise the flare from the gun. Everything is as it should be: firing mechanism, flare, trigger. This can certainly be used, and with shaking, filthy hands you reconstruct the fragile flaregun.",
    {},
)


class Box3(Item):
    def inside(self):
        global searched

        if self in searched:
            tensetext("There is nothing useful left inside.")
        else:
            tensetext(
                "It looks as the the box may have contained a rudimentary raft or lifejacket, but it's been riddled with holes and is beyond use. Deep in the container you find a loaded flaregun."
            )

        hidden = {flare: {flare.fire: ["fire", "shoot", "send up"]}}
        self.pickup(hidden)
        hidden.clear()
        searched.append(self)


box3 = Box3(
    ["large", "holey", "holed", "hole", "crate"],
    "a large crate, riddled with holes",
    "Shot through from every side, a large crate languishes in the mud at a perilous angle.",
    "The biggest crate in the area, you hold out little hope for what's inside given the grievous damage done to it.",
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
            tensetext(
                "You fumble, and your stomach knots as you nearly drop the syringes. Wide-eyed and shaking, you slide the hydrocortisone into your palm and inject. Wiping your forearm clean as best you can, you pray that you've managed to find a vein with the adeneline. Your heartbeat confirms. You are in desperate need of medical attention, but there's life left in you for now."
            )
            poisonif = False
        else:
            tensetext(
                "There is plenty wrong with your flagging body, but there's nothing in the emergency kit that will do you any good right now."
            )


medkit = Medkit(
    ["medkit", "syringes", "health", "medical", "kit"],
    "the small emergency medical kit",
    "The airtight metal case appears to have survived the mire unscathed.",
    "It's all that remains from the plane's medical supplies thanks to its protective case, but it could be vital.",
    "Inside the case, the two syringes of adrenaline and hydrocortisone are undamaged and ready to be uncapped and used at a moment's notice.",
    {},
)


class Box4(Item):
    def inside(self):
        global searched
        global turns

        if self in searched:
            tensetext("Nothing useful remains.")
        else:
            tensetext(
                "It's full to the brim with black mud. Tentatively you reach in, feeling carefully around the inside. Long filthy lengths of what could be bandages curl about your arms, and you are pricked once or twice by what you discover, as you hastily withdraw, to be empty syringes. Finally, your hands close around a small metal case. Inside are two prepared shots of adrenaline and hydrocortisone."
            )

        hidden = {medkit: {medkit.use: ["use", "inject", "apply"]}}
        self.pickup(hidden)
        hidden.clear()
        searched.append(self)


box4 = Box4(
    ["long", "flatgreen", "case"],
    "a long, flat, muddy-green case",
    "A long, flat box is all but buried in the mire.",
    "You can see flecks of green through the thickly-caked mud of the case, though you're unsure whether you'll be able to prise it open.",
    "",
    {},
)

bodies = Item(
    ["bodies", "body", "corpses", "corpse"],
    "the scattered corpses",
    "Your gut clenches. There are so many dead, so many lifeless in the mud.",
    "You cannot bear to look at each body for more than a moment, but you notice that though all seem to be wearing olive-green uniforms, some bear a red symbol, and others blue.",
    "Gagging slightly you try searching a few of the bodies. Dogtags with names you don't recognise, guns so riddled with mud you'll never get them clean enough to work, and various shattered tools of war: binoculars, water canteens, bandages smeared with mud, all unusable. As you search one body your fingers slip into a huge fleshy tear down the man's back, and you vomit profusely. You stop searching.",
    {},
)


class Boat(Item):
    async def enter(self):
        global turns
        global currentloc

        boatrand = random.randint(0, 3)

        tensetext(
            "Your muscles shaking with painful effort, you drag the floating log from the reeds it's buried within, pulling the sharp rushes back with your bare hands. It takes considerable time, but the moment the log is partly out in the waterway it's yanked firmly downstream with surprising strength, and it's all you can do to hang on. Gasping for breath, you realise the log isn't quite as buoyant as you thought - as you're dragged downstream you have to kick wildly to keep afloat, and you begin to panic as you realise if you don't continue your exhausting flailing you will drown, and you will die. You are utterly at the mercy of the river. It's not long before you notice a split in the water ahead, and you are powerless to decide which way you'll be taken. Alone and tired, freezing and aching in the water, the log lurches."
        )

        if boatrand == 0:
            dead(
                "You appear to be going to the right when a crosscurrent drags at your leg and rips you under the water, pulling you left. Already deathly weary, you kick with all your might, your lungs on fire and desperate for air. It's not enough. Your mouth bursts open to suck in air, and your chest fills with the icy, grimy water. You choke to blackness."
            )
        else:
            tensetext(
                "Still thrashing to stay afloat, the log pulls you to the right. The current speeds. You are having to kick harder and harder to keep your head above the water, and you're not sure how much longer you can carry on. You last perhaps a few minutes. The sky twists as you take your last look at it, open wide above you, and you sink into the inky abyss, your body broken, torn and spent. You feel your heart slow. The world slips away."
            )
            tensetext("Endless nightmares run through the dark.")
            timecol1 = MediaEvent("bg", 255)
            tensetext(timecol1)
            tensetext(" ")
            reset = MediaEvent("reset", "")
            tensetext(reset)
            tensetext(
                "Find them in the earth. Alone amongst the stone. Lost beneath the endless mud. You awaken face up, still, a canopy of trees above you. All is quiet and calm, and the desire to lie still and rest your bludgeoned body is overwhelming. The dank smell of rot fills the air. Something gives beneath you, just an inch, and you realise that you are once more sinking. You struggle, bruised and battered, to your feet. The mud rises quickly, and you must move on or perish."
            )
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
    "Pushing through the reeds around the waterway you discover a length of log trapped in the bed. Though rancid and decaying, it's buoyant enough that it may support some of your weight.",
    "The log is festering, but it looks strong enough to hold the weight of your torso, perhaps.",
    "You find a few crawling insects that you bat away.",
    {},
)


class Water(Item):
    def enter(self):
        global turns

        waterrand = random.randint(0, 10)
        turns += 2

        tensetext(
            "You dive forward into the waterway and the current rips you along. You kick wildly, writhing in the water, but a powerful riptide tugs you down. You're desperate for breath."
        )

        if waterrand < 2:
            dead(
                "It never comes. Your mouth, involuntarily, pops open like a burst balloon, and you suck down the icy filthy water. Choking and flailing you're sucked into the dark of the river. The world goes black."
            )
        else:
            tensetext(
                "Suddenly your outstretched hand is caught violently in a root, and you grasp at it with what strength you have. Though the sharp tendril cuts deep into your hand you haul yourself back to the reed bed, and burst choking from the dark water, your feet finding the muddy floor. Coughing and haggard, you feel mud rising to your submerged ankles, and you must move on."
            )


water = Water(
    ["water", "river", "waterway"],
    "the slow, dark waterway",
    "The dark river moves slow and forcefully ahead of you, and you are sheltered by the rushes around you.",
    "The water ahead is clear and black, unimpeded by the rushes, and you see nothing underneath. It look slow but strong, and you don't know how to swim.",
    "From under the surface you venture a leg into the moving body of water. It is pulled from you with enough strenth that you're almost pulled away, but you regain your balance.",
    {},
)

aagun = Item(
    ["gun", "anti-aircraft", "aircraft", "anti", "cannon", "artillery"],
    "the sinking gun",
    "The artillery sinks slowly into the thick slop.",
    "The gun is large, even half-sunk, towering over you. The long barrel faces the sky, and you can make out a space for shells just where it meets the mud, with two large iron wheels entrenched in the mire. This is an anti-aircraft gun.",
    "The gun has sunk so far into the mud you can't search it thoroughly, though the stink of gunpowder and the black debris around the barrel confirm that it was fired recently. There are muddy handprints around the wheels: someone tried desperately to stop the artillery sinking. The mud around the gun's base is pitted, as if several people have recently disturbed the mire.",
    {},
)

"""Place instantiation"""

plane = Place(
    "at the plane",
    "The hot, twisted metal of your aircraft sizzles as it sinks into the mire.",
    "a fighter aircraft on the horizon, stuck slowly sinking into the mud",
    {fighter: {}},
    False,
    "",
    "You pace the mud around the aircraft.  Amongst the unidentifiable, hissing contortions of metal debris you see the long muddy wound the crashed plane has carved into the mire. It leads west.",
)

snake = Place(
    "at the riddled treestump",
    "The black trunk of a titanic fallen tree crosses your path. Though massive, it looks fragile, riddled with rotten holes.",
    "a flat expanse of mire, with some large, long object far in the distance",
    {
        stump: {
            stump.climb: ["climb", "clamber"],
            stump.wade: ["wade around", "wade"],
            stump.smash: ["smash through", "smash", "break through", "break"],
        }
    },
    True,
    "The hulking log blocks your path. What do you do?",
    "A few crops of small faded plants and swarms of tiny insects cover the landscape, but nothing else is to be found except the hulking log.",
)

sand = Place(
    "at a sandy, muddy mess",
    "The bleak mud ahead appears less viscous, with fewer drab weeds able to take root.",
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
    "The only way forward is through the sloppy sandy mire, but the loose texture makes you hesitate. You can proceed, if you wish.",
    "There is nothing within the sandy mud, and you find nothing but insect bites and exhaustion.",
)

sand_in = Place(
    "in the thick of the sandy morass, and you are sinking quickly",
    "Plunging into the sandy mud you quickly find its fine consistency and depth simply replaces difficulty of movement with the exhausting need to move further and more consistently to avoid being sucked under. You cannot stop.",
    "an endless sandy morass",
    {},
    False,
    "",
    "There is nothing within the sandy mud, and you find nothing but insect bites and exhaustion.",
)

debris = Place(
    "at the strewn debris",
    "Ahead lies a deep but slowly-closing rut where the plane gouged its way across the bog. Unidentifiable blackened plane parts lean out of the muddy morass, sinking, with scattered papers, bags and mechanical detritus peppering its surface.",
    "some wreckage peppering a vast mud flat",
    {
        box1: {},
        box2: {},
        box3: {},
        box4: {},
    },
    False,
    "",
    "Searching the area reveals nothing further to the handful of containers that seem salvagable, sinking into the mire.",
)

fog = Place(
    "in an endless bogland, surrounded by fog",
    "After a while the air takes on a chill, and your skin bristles. Before you know it, you find yourself utterly engulfed by fog, knee-deep in the mire.",
    "an expanse of mud disappearing into a bank of cloud",
    {fog_load: {fog_load.go: []}},
    True,
    "",
    "You plunge your hands into the mire at random, looking for something in the haze. Your arms caked in filth you stand, and all you have discovered is more mud.",
)

blanksw = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    "Mud stretches forever, on every side. Yet as you stagger about, your eyes flicking about the filth, something gnaws at your gut. You sense there is something to be found here, but that it eludes you for now. It is with deep unease that you cease your efforts.",
)

log = Place(
    "in an expanse of mud, dotted with knarled shrubbery",
    "Larger flora begins to dot the expanse of mud. Something unseen flutters in the wind.",
    "a massive field of mire, with a few plants here and there",
    {pages: {}},
    False,
    "",
    "You can find nothing further among the scattered shrubs.",
)

swamp = Place(
    "at the swamp",
    "The mire becomes more and more fluid until you find yourself in swampland. Bent, gloomy trees find root between patchy beds of tall, sharp rushes. You are chest deep in thick, murky water.",
    "a sparse wetland, with rushes and trees",
    {
        swamp_load: {swamp_load.go: []},
        swamptrees: {swamptrees.climb: ["climb", "clamber"]},
    },
    False,
    "",
    "You slosh aimlessly about, the deep water tiring you quickly. You search about the rushes for something useful, but there is nothing to be found.",
)

gun = Place(
    "at the abandoned gun",
    "After some time you notice a shape twisting strangely from the bog. Once you get closer, you see it is a large mobile gun emplacement, lopsided and half-sunk. The smell of gunpowder hangs in the air, hot and dense. The mud is slowly claiming the sinking artillery.",
    "a vast flat bog, though perhaps there's something on the horizon",
    {aagun: {}},
    False,
    "",
    "You pace about the mire, and realise with a start that the pits and churns around the gun are the remains of footprints. They stretch west.",
)

cave = Place(
    "at the endless cliff",
    "You eventually reach a dark cliff that stretches as far as you can see. You notice a fissure a short distance from you large enough to enter.",
    "a field of mud, with a rocky formation on the horizon",
    {cavetrap: {cavetrap.enter: ["enter", "into", "in", "go", "explore"]}},
    False,
    "",
    "No matter how far along the cliff you go, there is nowhere to stop and rest but the fissure. No matter how far you travel, the cliff continues to stretch as far as you can see. You shudder a little.",
)

cave_in = Place(
    "lost deep in the endless black of a cave system",
    "",
    "black",
    {},
    False,
    "",
    "Without light, you find nothing hidden in the endless black.",
)

wood = Place(
    "in dense woodland",
    "The mire has taken on a slightly richer brown and larger plants have taken hold. You are shaded by the leafy arbour overhead, surrounded by a dense knot of trees, shurbs and vines rooted somewhere deep in the thick mud.",
    "a dense thicket beginning to take hold on the muddy plain",
    {woodtrees: {woodtrees.climb: ["climb", "clamber"]}},
    False,
    "",
    "Trudging between the trees in the thick mud you find strand disturbances. Could they be footsteps? They lead east.",
)

wood_in = Place(
    "deep in the mud of the dense forest",
    "As you move deeper into the woodland the trees seem to swallow you. You lose track of where you are, and more importantly, where you came from.",
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
    "The line of rushes stops suddenly, and you realise you are on the banks of a waterway. Sunk up to the chest but sheltered by the reeds you can feel the current pulling strongly east just ahead. You realise you cannot follow the river without entering the open water.",
    "a clear path of water weaving through the swamp's rushes, very far away",
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
    "You wade endlessly, tiring fast, but you find nothing more amongst the rushes.",
)

troops = Place(
    "at the boulders",
    "Monolithic boulders appear as you continue, jutting from the bog. Something whispers through the air - could it be voices? You don't understand.",
    "vast boulders beginning to rise from the muddy field, and perhaps mountains far in the distance",
    {
        stones: {
            stones.climb: ["climb", "clamber"],
            stones.listen: ["listen to", "listen", "to", "hear"],
        }
    },
    False,
    "",
    "You wander aimlessly between the stones, your feet heavy in the mud, and no two seem alike. The whispers about them seem to form strange and eerie dischords, forever changing.",
)

troops_in = Place(
    "unseen, flat against a towering stone, mere feet from some soldiers",
    "You stagger towards a group of soldiers marching through the mud away from you. Moving from stone to stone you observe: one wears a pack with a large aerial stretching skyward from it, topped by a small blue flag. Behind them they drag a sled of equipment with ropes taut against their sloping backs. It is too late once you realise you're too close - you could be discovered at any moment. Fearfully you flatten yourself against the nearest standing stone, unseen, but slowly sinking.",
    "the gigantic standing stones scattered across the mudflats like huge gravestones, with something moving amongst them far ahead",
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
    "You're so close you can hear their grunts of effort. Pinned, gasping, behind the stone, you can approach or fall back.",
    "If you move, you'll surely be discovered.",
)

blankse = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    "Mud stretches forever, on every side. Yet as you stagger about, your eyes flicking about the filth, something gnaws at your gut. You sense there is something to be found here, but that it eludes you for now. It is with deep unease that you cease your efforts.",
)

blanknw = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    "Mud stretches forever, on every side. Yet as you stagger about, your eyes flicking about the filth, something gnaws at your gut. You sense there is something to be found here, but that it eludes you for now. It is with deep unease that you cease your efforts.",
)

blankne = Place(
    "in an endless bogland",
    "The turgid mud stretches endlessly.",
    "endless mud",
    {},
    False,
    "",
    "Mud stretches forever, on every side. Yet as you stagger about, your eyes flicking about the filth, something gnaws at your gut. You sense there is something to be found here, but that it eludes you for now. It is with deep unease that you cease your efforts.",
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
                tensetext(
                    "You turn and turn, searching and searching, until there is nothing but mud, forever. Mud is all that you are. Mud is all you can be. Lost beneath the endless mud a wisp of smoke creeps by."
                )
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
    tensetext(
        "Your head is murky and it is a tremendous effort to recall anything at all. You can GO NORTH, SOUTH, EAST or WEST. You can LOOK in directions and at objects. You can SEARCH objects, or just the area you're in. You can THINK about what options are available at each location. You can cry for the only HELP you're getting."
    )
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
        "You cannot possibly proceed, and with exhausting effort turn back.",
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
        "A shift in the mud briefly releases the unmistakable smell of decaying flesh.",
        "The air is putrid.",
        "You wipe a brown-red moisture from your eyes.",
        "The rising heat from the bog is suffocating.",
        "Flies hop about the mud's surface.",
        "You try to wipe wet mud from your eyes and face.",
        "Mud has caked dry about your thighs, heavy and stiff.",
        "Your muscles ache from effort.",
        "Your collar worries at insect bites around your neck.",
        "You fall. Cursing, you try to clean your hands of the slop as best you can.",
        "Your foot snares on something in the mire, but you free it.",
        "You try to rub some of the dried mud from your matted hair.",
        "Your head pounds.",
        "You're desperately thirsty.",
        "Insects choke the air around you.",
        "You need to sit and rest, but there is nowhere.",
        "Standing still for a moment you begin to sink, and must move on.",
        "The buzz of insects is incessant.",
        "A misstep, and your leg sinks deep into the mire. You pull it out, exhausted. Wet mud glistens up to your hip.",
        "Sweat remoistens the mud about your face.",
        "Your forearms are red from sunburn, mottled with mud.",
        "You fall but catch yourself on a rotting stump. Standing, mud mixes with the blood of a jagged wound across your palm.",
        "Touching your neck you find dried blood from an unseen wound.",
        "Your head throbs.",
        "You feel dizzy.",
    ],
    [  # Time [3]
        "The afternoon sun beats down relentlessly.",
        "The sun has definitely sunk in the sky.",
        "The exhaustion of constant movement is wearing heavily on you.",
        "The low, orange sun casts long shadows across the mud.",
        "The sky's dark blue deepens swiftly.",
        "You are wracked, utterly, utterly wracked by tiredness. Every fibre of your body contorts with pain. Strange shapes cross your vision and you hear whispers and rustles and shouts that are terrifyingly real.",
        "It is a night of absolute black.",
    ],
    [  # Sand [4]
        "Your legs ache from constant movement, and you begin to slow.",
        "You must rest - you're desperate to rest.",
        "You think you see something on the horizon, but it's hard to make out.",
        "You don't know how much longer you can keep this up.",
        "Your right calf begins to cramp. It feels as though the muscle is tearing itself from your leg.",
        "Your entire body begins to slow from the exertion.",
        "Your head lolls back and you stare into the endless sky. You cannot go on.",
        "You have to stop.",
        "You cannot go on any longer.",
        "Your eyes explode with pain as wet sand splashes into them. The irritation is unbearable, and you are blind.",
        "Your heavy clothes drag in the muck.",
    ],
    [  # Wait [5]
        "Unable to stand still, you try to pace in place, slowly getting more and more exhausted.",
        "Eyes glazed over you shift your weight painfully from one leg to the other for a while. It brings no relief.",
        "From the second you stop moving, the surge of pain in your tired muscles nearly surpasses the agony of pushing on.",
        "Your slow sinking reminds you that you can never stop.",
        "You halt for a moment to give yourself the illusion of rest. You are not fooled.",
    ],
    [  # Shout [6]
        "You cough a few times, and spit up mud.",
        "You choke out a quiet rasp.",
        "You are too scared to make a sound.",
        "Your chapped lips are too agonising to open.",
        "Your lungs empty silently, and you nearly fall to your knees.",
        "You contort your lips and tongue but cannot form a word.",
        "You don't remember how.",
        "You open your mouth, and when nothing happens you feel intensely ashamed.",
        "How?",
    ],
    [  # Stretcher [7]
        "Your jaw clenches as you bump along.",
        "Every jolt of the stretcher twists you painfully.",
        "Your legs twitch and cramp agonisingly, unused to the stillness.",
        "Your eyes bore into the middle distance.",
        "You are quiet.",
        "The blanket around you is so tight you cannot move, and you fight back the urge to panic.",
        "The stretcher-bearers wheeze with effort.",
    ],
    [  # Fog [8]
        "The endless fog presses in on you.",
        "Every hair on your arms has pricked up in the damp cold.",
        "You think you see a shape moving somewhere ahead.",
        "You turn to check your progress, and lose track of which way you were facing.",
        "Your footprints disappear into the knee-high mire."
        "The cold air numbs your fingers.",
        "That way is north.",
        "That way is east.",
        "That way is south.",
        "That way is west.",
        "You hear a muddy splash somewhere deep in the fog.",
        "You can taste the moisture in the air, but it cannot quench your thirst.",
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
        "The creatures on your skin are muscular and deathly dry to touch.",
        "Wormlike creatures are feasting on your flesh.",
        "You feel the flick of a worm against your collarbone.",
        "You can feel things moving on your back, and you don't know how many.",
        "You're covered in writhing, pulsating wormlike things.",
    ],
    [  # Cave [10]
        "You plod onwards, the impenetrable black bearing down on you. Some change in the echoing muddy splashes makes you think you've passed to a new chamber.",
        "You come up against a smooth wet wall. Feeling your way along it you discover a low hole just above the mudline. On hands and knees you make your way through the revolting tunnel, mouth pressed against the stone above, sucking at the inch-high airspace that sustains you. At last you're able to kneel, then stand, panting and dragged down by the thick cloying mess.",
        "You feel a sucking pressure from up ahead, which suddenly dissipates into a stifling heat. This place feels different.",
        "Moving on, the sticking mud begins to feel lighter around your calves.",
        "Stumbling on, the echo of your sloshes begins to turn on itself, building over and over until you're amidst a nightmarish roar of sound. You don't recall it stopping, but it has.",
        "You think you've entered a new chamber, but something is wrong. It's as though some enduring background sound has been all of a sudden removed, but you don't remember what's gone. Silence haunts you.",
        "You stagger forth, arms outstretched, and find a corridor wide enough you can just touch both sides. You follow it for a while, the rock pressing in slightly, the faint touch becoming a firm, comforting push against your outstretched palms. You stride on. Your wrist catches on something sharp, and you clutch your hand - is it blood? You go to lean on the rockface, and nothing greets your shaking fingers. The dark seems somehow darker.",
        "The way forward seems to take you down, but something tells you you're actually going up. The feeling lasts for quite some time.",
        "A few steps and you crack your head on an overhanging rock and collapse immediately into the mud. Fighting to surface you find the mire reaches to the flat cavern roof. You panic, your hands pressing up and down the rough surface. At last you find a hold high above your head, and pull yourself onwards, upside down, until reaching for a second handhold you instead grasp at air. Pulling and thrashing you burst from the filth, and stagger onwards, gasping for breath, always sinking.",
        "You find a wall and follow its curve, feeling hopelessly ahead.",
        "You wander onwards, ever onwards.",
        "You touch the cave's walls as you trudge forwards, feeling the troughs and insets of the rock's texture.",
    ],
    [  # Woods - new locations [11]
        "You find yourself in a small clearing.",
        "You reach a small copse, with blank mud surrounding a tight knot of trees in the centre.",
        "The wood begins to close in and your present path becomes untenable.",
        "The foliage around you begins to look a little greener.",
        "Insects begin to swarm around you, and you cannot continue.",
        "The trees around you have become wilted and decayed.",
        "A caw startles your gaze upwards. Three black birds regard you for a moment, before taking flight into the foliage.",
        "A tree catches your attention. At first it looks as though it's been intricately carved, but looking closer it's the strange grain of the bark.",
        "You pause, unsure whether to continue this way.",
        "Trees twist together ahead, and you can't continue.",
        "An unthinkable screech pierces the air and stops you in your tracks.",
        "A low rustle high in the trees seems to circle you.",
        "The trees around you seem unfathomably tall.",
        "Something reeks. Looking about you realise that there are three bodies, almost completely rotten, hanging from a branch high in the canopy. You feel nauseous, you have to keep moving.",
    ],
    [  # Woods - clues to move forward [12]
        "The trees stretch on and on, but you notice a small scrap of red cloth fluttering amongst the branches of one.",
        "Some of the branches in that direction seem snapped and broken.",
        "A few of the trees have been felled, leaving a clear pathway.",
        "There are splashes of red daubed across a few trees that way.",
        "You notice some small round burns on a trunk that way.",
        "You think you can make out movement far ahead.",
        "The trees that way have been violently slashed and hacked.",
        "The forest has been cleared a little in that direction.",
    ],
    [  # Woods - clues to leave [13]
        "You can see light through the trees, and beyond it the plane of mud.",
        "The trees seem to thin that way, sparsely pucking the mud.",
        "The trees - you think that's the way you came into the wood.",
        "You can make out the mudplane somewhere through the trees.",
        "You can see the forest's edge.",
        "The treeline wanes perhaps a few hundred feet away.",
    ],
    [  # Woods - blank forest [14]
        "The trees stretch across the churning mire as far as you can see.",
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
        tensetext(
            "You stand still, exhausted, sinking slowly into the mud. Do you need HELP?"
        )
        await sink(0.25)
        turns += 0.25
        return

    """Restricts movement if location contains a puzzle or if sinking"""

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
            tensetext(
                "Warily you edge back into the cave system through the tight passage you left through, but are quickly lost once more in the impossible depths of the rock."
            )
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
            dead(
                "You struggle for breath and cannot find it. Blood pounds in your ears, your skin an inky violet. Collapsing into the mud you sink slowly beneath, wracked with paralysing pain."
            )
        elif poisonlen <= (turns - 6) and poisoncount == 2:
            tensetext(
                "Your chest is beginning to seize up and your hands have turned a dark purple, deepening quickly."
            )
            poisoncount = 3
        elif poisonlen <= (turns - 2) and poisoncount == 1:
            tensetext(
                "The puncture marks have turned black, and your hands and arms are rapidly turning a murky red."
            )
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
flare_weloc_templook = ""
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

    """Moves the search parties, handles behaviour if they cross one another or find you"""

    if flare_up == True:
        try:
            flare_eprevloc = flare_eloc
            flare_eloc = flare_path_east[time_e[time]]
            if "a few figures" in flare_path_east[time_e[time - 1]].look:
                flare_path_east[time_e[time - 1]].look = flare_eloc_templook
            if "a few figures" not in flare_eloc.look:
                flare_eloc_templook = flare_eloc.look
                flare_eloc.look += ". There are a few figures in olive green dotting the landscape. One wears a red tunic"
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
                flare_wloc.look += ". Tiny moving figures in olive green dot the landscape, one with a large communications aerial coming from his backpack, a blue flag atop it"
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
                dead(
                    "Before you know it, troops are approaching you from two sides. They fire on one another as they approach, bellowing murder, screams echoing around the desolate mud as each one goes down in a fountain of blood. You fall into the mud and try to crawl from the carnage. A bullet catches you in the ribs, then another in the shoulder. Deep in shock, wracked with pain, you lie still, sinking, bleeding."
                )

            flare_wloc.name += ", surrounded by bodies"
            flare_wloc.firstsight += " The bodies of a dozen or more men are slowly sinking into the mire, their bodies riddled with bullets, their blood mixing with the filth."
            flare_wloc.look = flare_wloc_templook
            flare_eloc.look = flare_eloc_templook

            flare_wloc.items[bodies] = {}
            flare_up = False

        if flare_eloc == currentloc or (
            flare_eprevloc == currentloc and prevloc[0] == flare_eloc
        ):
            tensetext(
                "You are faced by a grim uniformed group. You approach, each of them visibly wary, with a gun trained on you. Suddenly, one points at you and they all surge forward, weapons cast aside. You collapse into their arms, helpless, catatonic. Soon you are wrapped in a blanket, strapped to a stretcher, staring up at the endless sky."
            )
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
            dead(
                "You approach the uniformed men, who eye you cautiously, weapons raised. Suddenly, one points at you and shouts. Eyes wide with fear, the men open fire. Your shoulder jerks back as a bullet rips through your shoulder, and you collapse backwards. An explosion of pain in your thigh, then your jaw, then black."
            )

        for i in cart[currentloc]:
            if i == flare_eloc:
                tensetext(
                    "Shouts echo across the endless mud somewhere to the %s."
                    % directions[cart[currentloc][cart[currentloc].index(i)]][0]
                )

            if i == flare_wloc:
                tensetext(
                    "You can hear the faint slosh of footsteps somewhere to your %s."
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
            tensetext(
                "You attempt to wriggle free of the stretcher, but your bound too tightly in the blanket."
            )
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
            tensetext(
                "You don't think there's anything you can do - you're strapped too tightly to the stretcher."
            )

        time = int(turns - flarewin_turns)
        time2 = int(turns - flare_turns)

        near = False
        for i in cart[currentloc]:
            if i == flare_wloc:
                tensetext(
                    "You're not the only one who heard the footsteps. You hear a gruff whisper from someone and the company instantly doubles its pace. Their bristling nerves are palpable."
                )
                time_e = [x for x in range(1, (len(flare_path_east)))]
                near = True
        if near == False:
            time_e = [x for x in range(0, (len(flare_path_east))) for _ in (0, 1)]
            time_e.remove(0)

        if flare_eloc == flare_wloc:
            dead(
                "You stare vacant and helpless as shots and shouts ring across the mud. You're dropped forcefully as the company draw their weapons and return fire. A trail of machinegun bullets splatters across the mud, catching two men in front of you, before cross your stomach with two gaping wounds. Sprawled backwards, your legs numb, you gradually watch the sky darken to the sound of firearms."
            )

        if flare_eloc == wood:
            dead(
                "You finally arrive in an encampment. Shouts from your party bring several people running, and you are taken to a tent and transferred from stretcher to bed. Two uniformed people begin strapping you to the cot, and you don't resist. Looking over you, someone in a white coat grasps you forcefully by the shoulder with a faint and cold smile. The pain in your body dulls, and you sink to sleep."
            )

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
            tensetext(
                "Looking down you see you're sinking dangerously deep into the mud."
            )


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
            dead(
                "The mire closes over your face, and it's not long before your aching lungs force you to choke down the suffocating mud."
            )
        elif sinkcount >= 4:
            if currentloc == cave_in:
                tensetext(
                    "You face barely tops the mud in the black of the cave. You feel it ooze gently up around your ears and cheeks."
                )
            else:
                tensetext(
                    "You face the giant, empty sky, your face barely above the mud's surface. You feel it ooze gently up around your ears and cheeks."
                )
            turns += 1
            sinkcount += 0.5
            await whatnow()
            await status()
            await sink_death()
        elif sinkcount >= 3:
            tensetext(
                "Slowly you sink further and further, helplessly into the mud. Your abdomen. Your chest. Your shoulders."
            )
            turns += 1
            sinkcount += 0.5
            await whatnow()
            await status()
            await sink_death()
        elif sinkcount >= 2:
            tensetext(
                "You attempt to move your legs. Sucked up to the thigh, you begin to shake as you realise you cannot move."
            )
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
        tensetext(
            "You feel a sudden pain from one of the creatures on your arm. Knocking it off you see rapidly darkening punctures on your skin."
        )
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
        dead(
            "You are exhausted to the marrow of your bones. You take a step and realise that it is simply your last. You fall to your knees. You collapse bodily into the mire. The mud quietly subsumes you, and you convulse weakly as you choke to death in a dark muddy grave."
        )


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
        tensetext(
            "Endless filth. The wasted mud stretches and stretches and stretches. In a tiny corner of a riddled, impossible mire, a figure struggles free of a crashed plane. Looking around them, covered in a heavy muck that drags them down, down, they set off in some direction or other. They are empty. They are no one. There is simply sky, infinite sky, and mud, mud, endless mud. The open sky is an endless blue, find them in the earth. The broken bodies sucked below, devoid of worldly worth. The sound of static fills the air, alone amongst the stone. A yawning empty wasteland topples speech's fallow throne. Lost beneath the endless mud a wisp of smoke creeps by. A spirit's snuffed out wandering, a journey's final sigh."
        )
        timecol2 = MediaEvent("bg", 0)
        tensetext(timecol2)
        end = MediaEvent("end", 0)
        tensetext(end)
        tensetext(" ")
        tensetext("Mud. By Will Langdale. Created Summer/Autumn 2014.")
        sys.exit()

    if deaths == 0:
        music = MediaEvent("music", ("main", -1))
        tensetext(music)
        tensetext("Type HELP at the prompt for commands.")
        timecol = MediaEvent("bg", 0)
        tensetext(timecol)
        tensetext(" ")
        tensetext(
            "Endless blue. The open sky is an endless blue. The sound of static fills the air. A wisp of smoke creeps by. You are strapped into a leather seat in some sort of cockpit, but you're not moving. The controls are still, the radio bleats listless static, and the cockpit door is gone. Your head pulses with pain, and you feel dizzy. The smell of burning mixes with a dank, earthy musk. You THINK about what to do. Everything is spinning, but you need to free yourself and find out where you are. You SEARCH the cockpit and your fingers close around the buckles of your flight harness. You loosen it, pull off your helmet, and stand up. You LOOK at where you sat. You are in a crashed, olive fighter aircraft, covered in black scorches, with smoke billowing from under one wing. You LOOK in all directions, NORTH, EAST, SOUTH, WEST. Your heart pounds against your ribs. All around you, on every side. An endless, fathomless plain of mud. The craft groans and shifts, and you're thrown off-balance. You half-jump from the cockpit into the mire below, somehow remaining upright. The mud is surprisingly deep, quickly coming up to your calf. To your horror, you realise that it does not stop. If you stand still, you will sink, and you will drown. You don't know where you are, and your head throbs with a constant, disorienting pain. With difficulty, you take your first step into the sticky, sucking mud."
        )
    elif deaths <= 2:
        timecol1 = MediaEvent("bg", 255)
        tensetext(timecol1)
        tensetext(" ")
        reset = MediaEvent("reset", "")
        tensetext(reset)
        tensetext(
            "Endless blue. The open sky is an endless blue. The sound of static fills the air. A wisp of smoke creeps by. You feel for the sides of the cockpit and awkwardly stand up. All around you, on every side, an endless, fathomless plain of mud. You leap from the plane just as its weight shifts, and the mud begins, inevitably, to claim it. The mud rises up your calf, and you are sinking quickly. You must move on."
        )
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
        tensetext(
            "Endless blue. Find them in the earth. The open sky is an endless blue. Alone amongst the stone. The sound of static fills the air. A wisp of smoke creeps by. Lost beneath the endless mud."
        )
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
        tensetext(
            "Find them in the earth. Alone amongst the stone. Lost beneath the endless mud."
        )
        timecol = MediaEvent("bg", 0)
        tensetext(timecol)
        planenoise = MediaEvent("sound", "PLANE")
        tensetext(planenoise)

    await wrap()
