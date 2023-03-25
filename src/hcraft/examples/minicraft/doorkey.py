"""# MiniCraft - DoorKey"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniHCraftDoorKey(MiniCraftEnv):
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

        # Ensure key cannot be created if anywhere else
        search_for_key = Transformation(
            "search_for_key",
            inventory_changes=[
                Yield(CURRENT_ZONE, self.KEY, create=1, max=0),
                Yield(PLAYER, self.KEY, create=0, max=0),
                Yield(self.START, self.KEY, create=0, max=0),
                Yield(self.LOCKED_ROOM, self.KEY, create=0, max=0),
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

        move_to_locked_room = Transformation(
            "move_to_locked_room",
            destination=self.LOCKED_ROOM,
            inventory_changes=[Use(CURRENT_ZONE, self.OPEN_DOOR)],
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
            inventory_changes=[Yield(CURRENT_ZONE, self.GOAL, max=0)],
            zones=[self.LOCKED_ROOM],
        )
        transformations.append(find_goal)

        reach_goal = Transformation(
            "reach_goal",
            inventory_changes=[
                Use(CURRENT_ZONE, self.GOAL, consume=1),
                Yield(PLAYER, self.GOAL),
            ],
        )
        transformations.append(reach_goal)

        return transformations
