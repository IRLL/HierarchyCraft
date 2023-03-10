"""# MiniCraft - FourRooms"""


import os
from typing import List

from crafting.elements import Item, Zone
from crafting.env import CraftingEnv
from crafting.task import GetItemTask
from crafting.transformation import Transformation
from crafting.world import world_from_transformations


class MiniCraftFourRooms(CraftingEnv):
    """Reproduces the minigrid
    [FourRooms](https://minigrid.farama.org/environments/minigrid/FourRoomsEnv/)
    gridworld environment as a crafting environment.

    ![Minigrid FourRooms display](https://minigrid.farama.org/_images/FourRoomsEnv.gif)
    """

    SOUTH_WEST_ROOM = Zone("SW")
    """South west room."""

    SOUTH_EAST_ROOM = Zone("SE")
    """South east room."""

    NORTH_WEST_ROOM = Zone("NW")
    """North west room."""

    NORTH_EAST_ROOM = Zone("NE")
    """North east room."""

    GOAL = Item("goal")
    """Goal to reach."""

    def __init__(self, **kwargs) -> None:
        """
        Kwargs:
            See `crafting.env.CraftingEnv`
        """
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations, start_zone=self.SOUTH_WEST_ROOM
        )
        self.task = GetItemTask(self.GOAL)
        world.resources_path = os.path.join(os.path.dirname(__file__), "resources")
        super().__init__(world, purpose=self.task, name="MiniCraftFourRooms", **kwargs)

    def _build_transformations(self) -> List[Transformation]:
        find_goal = Transformation(
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.NORTH_EAST_ROOM],
        )

        reach_goal = Transformation(
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            }
        )

        go_to_se = Transformation(
            destination=self.SOUTH_EAST_ROOM,
            zones=[self.NORTH_EAST_ROOM, self.SOUTH_WEST_ROOM],
        )

        go_to_ne = Transformation(
            destination=self.NORTH_EAST_ROOM,
            zones=[self.SOUTH_EAST_ROOM, self.NORTH_WEST_ROOM],
        )

        go_to_sw = Transformation(
            destination=self.SOUTH_WEST_ROOM,
            zones=[self.NORTH_WEST_ROOM, self.SOUTH_EAST_ROOM],
        )

        go_to_nw = Transformation(
            destination=self.NORTH_WEST_ROOM,
            zones=[self.NORTH_EAST_ROOM, self.SOUTH_WEST_ROOM],
        )

        return [find_goal, reach_goal, go_to_ne, go_to_se, go_to_sw, go_to_nw]
