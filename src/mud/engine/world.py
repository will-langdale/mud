"""World construction boundary for the engine.

The current runtime is still driven by the legacy-authored world definitions in
``mud.engine.runtime``. This module is the typed boundary used by new code and tests
while that data is progressively moved into declarative assets.
"""

from __future__ import annotations

from mud.engine import runtime
from mud.engine.model import Item, Location, World


def build_world() -> World:
    """Build a typed view of the currently configured runtime world."""
    locations: dict[str, Location] = {}
    items: dict[str, Item] = {}

    for place in runtime.cart:
        place_id = place.name.replace(" ", "_").replace(",", "").lower()
        locations[place_id] = Location(
            id=place_id,
            name=place.name,
            first_sight_key=place.firstsight,
            look_key=place.look,
            search_key=place.search,
            restricted=place.restricmov,
            restriction_key=place.restricwhy,
        )

        for item in place.items:
            item_id = item.name.replace(" ", "_").replace(",", "").lower()
            items.setdefault(
                item_id,
                Item(
                    id=item_id,
                    aliases=list(item.reflib),
                    name=item.name,
                    first_sight_key=item.firstsight,
                    look_key=item.look,
                    search_key=item.search,
                    hidden=len(item.reflib) > 0 and item.reflib[0] == "hidden",
                ),
            )

    return World(locations=locations, items=items, start_location="at_the_plane")
