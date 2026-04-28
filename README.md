# 🥾 Mud

A text adventure created in Autumn/Winter 2014, and ported to modern Python in Spring 2026.

[Deployed and playable on itch.io](https://illiter8.itch.io/mud).

Mud is a text adventure inspired by the experiences of people faced with problems so unfathomably life-changing that it's all they can do to keep living in the shadow of them. Its exact genesis came from someone who cared for their adult son who had suffered a traumatic brain injury. I felt that the medium of a game was an excellent fit for repeatedly attempting to surmount an insurmountable goal, and a text adventure in particular was germane to the sense of limitation in perception and potential action that I wanted to create.

Stylistically I was inspired by the work of Adam Cadre and Nick Montfort, both of whom expanded my idea of what a text adventure could be.

## Controls

- `SPACE` generally moves the displayed text along — hold it down if you get bored
- `ENTER` submits whatever you've typed
- `HELP` shows some basic commands
- `QUIT` closes the game after a `YES`/`NO` prompt
- `WALK` / `GO` moves you around, but entering a direction alone works just as well — the game accepts `NORTH` / `SOUTH` / `EAST` / `WEST`, or the shorthand `N` / `E` / `S` / `W` (e.g. `N` is equivalent to `WALK NORTH`)
- `THINK` shows context-specific actions available to you — everything you can do in the current area, plus anything you can do with items you're holding (note: `LOOK` and `SEARCH` are omitted unless they're your only options)
- `LOOK` can be used in three ways:
  - On its own — see what's around you
  - With a direction (e.g. `LOOK WEST`) — see what's that way
  - On an item (e.g. `LOOK SCARF`) — examine it
- `SEARCH` can be used in two ways:
  - On its own — search the current area
  - On an item (e.g. `SEARCH SCARF`) — check if anything is concealed within it
- Context-specific commands will appear as you play — `THINK` will help you discover them
- There are also some hidden commands that felt too natural not to handle — try `WAIT` a few times and see what happens

## Development

Environments and dependencies are managed with [uv](https://docs.astral.sh/uv/).

Task running is done with [just](https://just.systems/man/en/). Get started:

```bash
just
```

[Pre-commit hooks](https://pre-commit.com/) are in use and should be installed:

```bash
pre-commit install
```
