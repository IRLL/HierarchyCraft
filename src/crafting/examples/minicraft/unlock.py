"""# MiniCraft - Unlock"""

import os
from typing import List

from crafting.elements import Item, Zone
from crafting.env import CraftingEnv
from crafting.task import PlaceItemTask
from crafting.transformation import Transformation
from crafting.world import world_from_transformations


class MiniCraftUnlock(CraftingEnv):
    """Reproduces the minigrid
    [Unlock](https://minigrid.farama.org/environments/minigrid/UnlockEnv/)
    gridworld environment as a crafting environment.

    ![Minigrid Unlock display](https://minigrid.farama.org/_images/UnlockEnv.gif)
    """

    START = Zone("start_room")
    """Start room."""

    KEY = Item("key")
    """Key used to unlock the door."""

    OPEN_DOOR = Item("open_door")
    """Open door between the two rooms."""
    LOCKED_DOOR = Item("locked_door")
    """Locked door between the two rooms, can be unlocked with a key."""

    def __init__(self, **kwargs) -> None:
        """
        Kwargs:
            See `crafting.env.CraftingEnv`
        """
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations,
            start_zone=self.START,
        )
        self.task = PlaceItemTask(self.OPEN_DOOR)
        world.resources_path = os.path.join(os.path.dirname(__file__), "resources")
        super().__init__(world, purpose=self.task, name="MiniCraftUnlock", **kwargs)

    def _build_transformations(self) -> List[Transformation]:
        transformations = []

        search_for_key = Transformation(
            inventory_changes={
                "current_zone": {"add": [self.KEY]},
                "player": {"max": [self.KEY]},
                self.START: {"max": [self.KEY]},
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

        return transformations
