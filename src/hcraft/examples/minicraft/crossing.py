"""# MiniCraft - Crossing"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.purpose import Purpose, GetItemTask
from hcraft.transformation import Transformation

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniCraftCrossing(MiniCraftEnv):
    MINICRAFT_NAME = "Crossing"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    ROOM = Zone("room")
    """The one and only room."""

    GOAL = Item("goal")
    """Goal to reach."""

    LAVA = Item("lava")
    """Lava, it burns."""

    def __init__(self, **kwargs) -> None:
        purpose = Purpose()
        self.task = GetItemTask(self.GOAL)
        purpose.add_task(self.task, terminal_groups="goal")
        die_in_lava = GetItemTask(self.LAVA, reward=-1)
        purpose.add_task(die_in_lava, terminal_groups="die")
        super().__init__(
            self.MINICRAFT_NAME,
            start_zone=self.ROOM,
            purpose=purpose,
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

        find_lava = Transformation(
            "find_lava",
            inventory_changes={
                "current_zone": {"add": [self.LAVA], "max": [self.LAVA]},
            },
            zones=[self.ROOM],
        )

        reach_lava = Transformation(
            "reach_lava",
            inventory_changes={
                "player": {"add": [self.LAVA]},
                "current_zone": {"remove": [self.LAVA]},
            },
        )
        return [find_goal, reach_goal, find_lava, reach_lava]
