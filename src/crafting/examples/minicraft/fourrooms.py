"""# MiniCraft - FourRooms"""


from typing import List

from crafting.elements import Item, Zone
from crafting.task import GetItemTask
from crafting.transformation import Transformation

from crafting.examples.minicraft.minicraft import MiniCraftEnv


class MiniCraftFourRooms(MiniCraftEnv):
    MINICRAFT_NAME = "FourRooms"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

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
        self.task = GetItemTask(self.GOAL)
        super().__init__(
            self.MINICRAFT_NAME,
            start_zone=self.SOUTH_WEST_ROOM,
            purpose=self.task,
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        find_goal = Transformation(
            "find_goal",
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.NORTH_EAST_ROOM],
        )

        reach_goal = Transformation(
            "reach_goal",
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            },
        )

        go_to_se = Transformation(
            "go_to_se",
            destination=self.SOUTH_EAST_ROOM,
            zones=[self.NORTH_EAST_ROOM, self.SOUTH_WEST_ROOM],
        )

        go_to_ne = Transformation(
            "go_to_ne",
            destination=self.NORTH_EAST_ROOM,
            zones=[self.SOUTH_EAST_ROOM, self.NORTH_WEST_ROOM],
        )

        go_to_sw = Transformation(
            "go_to_sw",
            destination=self.SOUTH_WEST_ROOM,
            zones=[self.NORTH_WEST_ROOM, self.SOUTH_EAST_ROOM],
        )

        go_to_nw = Transformation(
            "go_to_nw",
            destination=self.NORTH_WEST_ROOM,
            zones=[self.NORTH_EAST_ROOM, self.SOUTH_WEST_ROOM],
        )

        return [find_goal, reach_goal, go_to_ne, go_to_se, go_to_sw, go_to_nw]
