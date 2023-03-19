import os
from typing import List

from crafting.elements import Item, Stack, Zone
from crafting.env import CraftingEnv
from crafting.purpose import GetItemTask
from crafting.transformation import Transformation
from crafting.world import world_from_transformations


class TreasureEnv(CraftingEnv):
    """A simple environment used in for the env building tutorial."""

    TREASURE_ROOM = Zone("treasure_room")
    """Room containing the treasure."""
    KEY_ROOM = Zone("key_room")
    """Where all the keys are stored."""
    START_ROOM = Zone("start_room")
    """Where the player starts."""

    CHEST = Item("treasure_chest")
    """Treasure chest containing gold."""
    LOCKED_CHEST = Item("locked_chest")
    """Treasure chest containing gold ... but it's locked."""
    GOLD = Item("gold")
    """Gold! well the pixel version at least."""
    KEY = Item("key")
    """A key ... it can probably unlock things."""

    def __init__(self, **kwargs) -> None:
        folder = os.path.dirname(__file__)
        resources_path = os.path.join(folder, "resources")
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations,
            start_zone=self.START_ROOM,
            start_zones_items={self.TREASURE_ROOM: [self.LOCKED_CHEST]},
        )
        world.resources_path = resources_path
        super().__init__(
            world, purpose=GetItemTask(self.GOLD), name="TreasureCrafting", **kwargs
        )

    def _build_transformations(self) -> List[Transformation]:
        TAKE_GOLD_FROM_CHEST = Transformation(
            inventory_changes={
                "player": {"add": [self.GOLD]},
                "current_zone": {"remove": [self.CHEST]},
            }
        )

        SEARCH_KEY = Transformation(
            inventory_changes={
                "player": {"add": [self.KEY]},
            },
            zones=[self.KEY_ROOM],
        )

        UNLOCK_CHEST = Transformation(
            inventory_changes={
                "player": {"remove": [Stack(self.KEY, 2)]},
                "current_zone": {"remove": [self.LOCKED_CHEST], "add": [self.CHEST]},
            }
        )

        MOVE_TO_KEY_ROOM = Transformation(
            destination=self.KEY_ROOM,
            zones=[self.START_ROOM],
        )
        MOVE_TO_TREASURE_ROOM = Transformation(
            destination=self.TREASURE_ROOM,
            zones=[self.START_ROOM],
        )
        MOVE_TO_START_ROOM = Transformation(
            destination=self.START_ROOM,
        )

        return [
            TAKE_GOLD_FROM_CHEST,
            SEARCH_KEY,
            UNLOCK_CHEST,
            MOVE_TO_KEY_ROOM,
            MOVE_TO_TREASURE_ROOM,
            MOVE_TO_START_ROOM,
        ]
