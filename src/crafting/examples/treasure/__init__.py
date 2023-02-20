from typing import List
import os

from crafting.env import CraftingEnv
from crafting.elements import Item, ItemStack, Zone
from crafting.world import world_from_transformations
from crafting.transformation import Transformation
from crafting.purpose import GetItemTask


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
            removed_zone_items=[self.CHEST],
            added_player_items=[self.GOLD],
        )

        SEARCH_KEY = Transformation(
            added_player_items=[self.KEY],
            zones=[self.KEY_ROOM],
        )

        UNLOCK_CHEST = Transformation(
            removed_zone_items=[self.LOCKED_CHEST],
            removed_player_items=[ItemStack(self.KEY, 2)],
            added_zone_items=[self.CHEST],
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
