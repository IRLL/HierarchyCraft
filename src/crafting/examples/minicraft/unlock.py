"""# MiniCraft - Unlock"""

from typing import List

from crafting.elements import Item, Zone
from crafting.task import PlaceItemTask
from crafting.transformation import Transformation

from crafting.examples.minicraft.minicraft import MiniCraftEnv


class MiniCraftUnlock(MiniCraftEnv):
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
            inventory_changes={
                "current_zone": {"add": [self.KEY]},
                "player": {"max": [self.KEY]},
                self.START: {"max": [self.KEY]},
            },
            zones=[self.START],
        )
        transformations.append(search_for_key)

        pickup = Transformation(
            "pickup_key",
            inventory_changes={
                "player": {"add": [self.KEY]},
                "current_zone": {"remove": [self.KEY]},
            },
        )
        put_down = Transformation(
            "put_down_key",
            inventory_changes={
                "player": {"remove": [self.KEY]},
                "current_zone": {"add": [self.KEY]},
            },
        )
        transformations += [pickup, put_down]

        search_for_door = Transformation(
            "search_for_door",
            inventory_changes={
                "current_zone": {"add": [self.LOCKED_DOOR], "max": [self.LOCKED_DOOR]},
            },
            zones=[self.START],
        )
        transformations.append(search_for_door)

        unlock_door = Transformation(
            "unlock_door",
            inventory_changes={
                "player": {
                    "remove": [self.KEY],
                    "add": [self.KEY],
                },
                "current_zone": {
                    "remove": [self.LOCKED_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
        )
        transformations.append(unlock_door)

        return transformations
