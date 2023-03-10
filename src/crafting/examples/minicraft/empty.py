"""# MiniCraft - Empty"""

import os
from typing import List

from crafting.elements import Item, Zone
from crafting.env import CraftingEnv
from crafting.task import GetItemTask
from crafting.transformation import Transformation
from crafting.world import world_from_transformations


class MiniCraftEmpty(CraftingEnv):
    """Reproduces the minigrid
    [Empty](https://minigrid.farama.org/environments/minigrid/EmptyEnv/)
    gridworld environment as a crafting environment.

    ![Minigrid Empty display](https://minigrid.farama.org/_images/EmptyEnv.gif)
    """

    ROOM = Zone("0")
    """The one and only room."""

    GOAL = Item("goal")
    """Goal to reach."""

    def __init__(self, **kwargs) -> None:
        """
        Kwargs:
            See `crafting.env.CraftingEnv`
        """
        resources_path = os.path.join(os.path.dirname(__file__), "resources")
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations, start_zone=self.ROOM
        )
        self.task = GetItemTask(self.GOAL)
        world.resources_path = resources_path
        super().__init__(world, purpose=self.task, name="MiniCraftEmpty", **kwargs)

    def _build_transformations(self) -> List[Transformation]:
        find_goal = Transformation(
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.ROOM],
        )

        reach_goal = Transformation(
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            }
        )
        return [find_goal, reach_goal]
