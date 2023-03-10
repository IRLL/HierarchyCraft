"""# MiniCraft - MultiRoom"""

import os
from typing import List

from crafting.elements import Item, Zone
from crafting.env import CraftingEnv
from crafting.task import GetItemTask
from crafting.transformation import Transformation
from crafting.world import world_from_transformations


class MiniCraftMultiRoom(CraftingEnv):
    """Reproduces the minigrid
    [MultiRoom](https://minigrid.farama.org/environments/minigrid/MultiRoomEnv/)
    gridworld environment as a crafting environment.

    ![Minigrid MultiRoom display](https://minigrid.farama.org/_images/MultiRoomEnv.gif)
    """

    GOAL = Item("goal")
    """Goal to reach."""

    def __init__(self, n_rooms: int = 6, **kwargs) -> None:
        """
        Kwargs:
            See `crafting.env.CraftingEnv`
        """
        resources_path = os.path.join(os.path.dirname(__file__), "resources")
        self.rooms = [Zone(str(i + 1)) for i in range(n_rooms)]
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations, start_zone=self.rooms[0]
        )
        self.task = GetItemTask(self.GOAL)
        world.resources_path = resources_path
        super().__init__(world, purpose=self.task, name="MiniCraftMultiRoom", **kwargs)

    def _build_transformations(self) -> List[Transformation]:
        transformations = []
        find_goal = Transformation(
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.rooms[-1]],
        )
        transformations.append(find_goal)

        reach_goal = Transformation(
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            }
        )
        transformations.append(reach_goal)

        for i, room in enumerate(self.rooms):
            connected_rooms = []
            if i > 0:
                connected_rooms.append(self.rooms[i - 1])
            if i < len(self.rooms) - 1:
                connected_rooms.append(self.rooms[i + 1])
            go_to_room = Transformation(destination=room, zones=connected_rooms)
            transformations.append(go_to_room)

        return transformations
