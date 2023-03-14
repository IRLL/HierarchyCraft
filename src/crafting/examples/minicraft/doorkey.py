"""# MiniCraft - DoorKey"""

from typing import List

from crafting.elements import Item, Zone, ItemStack
from crafting.task import GetItemTask
from crafting.transformation import Transformation

from crafting.examples.minicraft.minicraft import MiniCraftEnv


class MiniCraftDoorKey(MiniCraftEnv):
    MINICRAFT_NAME = "DoorKey"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    START = Zone("start_room")
    """Start room."""
    LOCKED_ROOM = Zone("locked_room")
    """Room behind a locked door."""

    KEY = Item("key")
    """Key used to unlock the door."""
    GOAL = Item("goal")
    """Goal to reach."""

    OPEN_DOOR = Item("open_door")
    """Open door between the two rooms."""
    LOCKED_DOOR = Item("locked_door")
    """Locked door between the two rooms, can be unlocked with a key."""

    def __init__(self, **kwargs) -> None:
        self.task = GetItemTask(self.GOAL)
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
                self.LOCKED_ROOM: {"max": [self.KEY]},
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
                "current_zone": {
                    "add": [self.LOCKED_DOOR],
                    "max": [self.LOCKED_DOOR, ItemStack(self.OPEN_DOOR, 0)],
                },
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

        move_to_locked_room = Transformation(
            "move_to_locked_room",
            destination=self.LOCKED_ROOM,
            inventory_changes={
                "current_zone": {
                    "remove": [self.OPEN_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
            zones=[self.START],
        )
        transformations.append(move_to_locked_room)

        move_to_start_room = Transformation(
            destination=self.START,
            zones=[self.LOCKED_ROOM],
        )
        transformations.append(move_to_start_room)

        find_goal = Transformation(
            "find_goal",
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.LOCKED_ROOM],
        )
        transformations.append(find_goal)

        reach_goal = Transformation(
            "reach_goal",
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            }
        )
        transformations.append(reach_goal)

        return transformations
