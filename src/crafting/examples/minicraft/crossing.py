import os
from typing import List

from crafting.elements import Item, Zone
from crafting.env import CraftingEnv
from crafting.purpose import Purpose, GetItemTask
from crafting.transformation import Transformation
from crafting.world import world_from_transformations


class MiniCraftCrossing(CraftingEnv):
    """Reproduces the crossing minigrid environment as a crafting environment."""

    ROOM = Zone("0")
    """The one and only room."""

    GOAL = Item("goal")
    """Goal to reach."""

    LAVA = Item("lava")
    """Lava, it burns."""

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
        purpose = Purpose()
        self.task = GetItemTask(self.GOAL)
        purpose.add_task(self.task, terminal_groups="goal")
        die_in_lava = GetItemTask(self.LAVA, reward=-1)
        purpose.add_task(die_in_lava, terminal_groups="die")
        world.resources_path = resources_path
        super().__init__(world, purpose=purpose, name="MiniCraftCrossing", **kwargs)

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

        find_lava = Transformation(
            inventory_changes={
                "current_zone": {"add": [self.LAVA], "max": [self.LAVA]},
            },
            zones=[self.ROOM],
        )

        reach_lava = Transformation(
            inventory_changes={
                "player": {"add": [self.LAVA]},
                "current_zone": {"remove": [self.LAVA]},
            }
        )
        return [find_goal, reach_goal, find_lava, reach_lava]
