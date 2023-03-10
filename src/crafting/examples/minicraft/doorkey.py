"""# MiniCraft - DoorKey"""

import os
from typing import List

from crafting.elements import Item, Zone
from crafting.env import CraftingEnv
from crafting.task import GetItemTask
from crafting.transformation import Transformation
from crafting.world import world_from_transformations


class MiniCraftDoorKey(CraftingEnv):
    """Reproduces the minigrid
    [DoorKey](https://minigrid.farama.org/environments/minigrid/DoorKeyEnv/)
    gridworld environment as a crafting environment.

    ![Minigrid DoorKey display](https://minigrid.farama.org/_images/DoorKeyEnv.gif)
    """

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
        """
        Kwargs:
            See `crafting.env.CraftingEnv`
        """
        resources_path = os.path.join(os.path.dirname(__file__), "resources")
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations,
            start_zone=self.START,
        )
        self.task = GetItemTask(self.GOAL)
        world.resources_path = resources_path
        super().__init__(world, purpose=self.task, name="MiniCraftDoorKey", **kwargs)

    def _build_transformations(self) -> List[Transformation]:
        transformations = []

        search_for_key = Transformation(
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
            inventory_changes={
                "player": {"add": [self.KEY]},
                "current_zone": {"remove": [self.KEY]},
            },
        )
        put_down = Transformation(
            inventory_changes={
                "player": {"remove": [self.KEY]},
                "current_zone": {"add": [self.KEY]},
            },
        )
        transformations += [pickup, put_down]

        search_for_door = Transformation(
            inventory_changes={
                "current_zone": {"add": [self.LOCKED_DOOR], "max": [self.LOCKED_DOOR]},
            },
            zones=[self.START],
        )
        transformations.append(search_for_door)

        unlock_door = Transformation(
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
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.LOCKED_ROOM],
        )
        transformations.append(find_goal)

        reach_goal = Transformation(
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            }
        )
        transformations.append(reach_goal)

        return transformations
