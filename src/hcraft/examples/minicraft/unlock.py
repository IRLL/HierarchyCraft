"""# MiniCraft - Unlock"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import PlaceItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniHCraftUnlock(MiniCraftEnv):
    MINICRAFT_NAME = "Unlock"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    START = Zone("start_room")
    """Start room."""

    KEY = Item("key")
    """Key used to unlock the door."""

    OPEN_DOOR = Item("open_door")
    """Open door between the two rooms."""
    LOCKED_DOOR = Item("locked_door")
    """Locked door between the two rooms, can be unlocked with a key."""

    def __init__(self, **kwargs) -> None:
        self.task = PlaceItemTask(self.OPEN_DOOR)
        super().__init__(
            self.MINICRAFT_NAME,
            purpose=self.task,
            start_zone=self.START,
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        transformations = []

        search_for_key = Transformation(
            "search_for_key",
            inventory_changes=[
                Yield(CURRENT_ZONE, self.KEY, create=1, max=0),
                Yield(PLAYER, self.KEY, create=0, max=0),
            ],
            zones=[self.START],
        )
        transformations.append(search_for_key)

        pickup = Transformation(
            "pickup_key",
            inventory_changes=[
                Use(CURRENT_ZONE, self.KEY, consume=1),
                Yield(PLAYER, self.KEY, create=1),
            ],
        )
        put_down = Transformation(
            "put_down_key",
            inventory_changes=[
                Use(PLAYER, self.KEY, consume=1),
                Yield(CURRENT_ZONE, self.KEY, create=1),
            ],
        )
        transformations += [pickup, put_down]

        search_for_door = Transformation(
            "search_for_door",
            inventory_changes=[
                Yield(CURRENT_ZONE, self.LOCKED_DOOR, max=0),
                Yield(CURRENT_ZONE, self.OPEN_DOOR, create=0, max=0),
            ],
            zones=[self.START],
        )
        transformations.append(search_for_door)

        unlock_door = Transformation(
            "unlock_door",
            inventory_changes=[
                Use(PLAYER, self.KEY),
                Use(CURRENT_ZONE, self.LOCKED_DOOR, consume=1),
                Yield(CURRENT_ZONE, self.OPEN_DOOR, create=1),
            ],
        )
        transformations.append(unlock_door)

        return transformations
