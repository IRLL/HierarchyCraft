"""# MiniCraft - Empty"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniCraftEmpty(MiniCraftEnv):
    MINICRAFT_NAME = "Empty"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    ROOM = Zone("room")
    """The one and only room."""

    GOAL = Item("goal")
    """Goal to reach."""

    def __init__(self, **kwargs) -> None:
        self.task = GetItemTask(self.GOAL)
        super().__init__(
            self.MINICRAFT_NAME,
            purpose=self.task,
            start_zone=self.ROOM,
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        find_goal = Transformation(
            "find_goal",
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.ROOM],
        )

        reach_goal = Transformation(
            "reach_goal",
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            },
        )
        return [find_goal, reach_goal]
