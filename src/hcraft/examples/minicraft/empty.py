"""# MiniCraft - Empty"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniHCraftEmpty(MiniCraftEnv):
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
            inventory_changes=[Yield(CURRENT_ZONE, self.GOAL, max=0)],
            zones=[self.ROOM],
        )

        reach_goal = Transformation(
            "reach_goal",
            inventory_changes=[
                Use(CURRENT_ZONE, self.GOAL, consume=1),
                Yield(PLAYER, self.GOAL),
            ],
        )
        return [find_goal, reach_goal]
