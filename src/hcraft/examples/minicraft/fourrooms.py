from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


MINICRAFT_NAME = "FourRooms"
__doc__ = MiniCraftEnv.description(MINICRAFT_NAME, for_module_header=True)


class MiniHCraftFourRooms(MiniCraftEnv):
    MINICRAFT_NAME = MINICRAFT_NAME
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    SOUTH_WEST_ROOM = Zone("South-West")
    """South west room."""

    SOUTH_EAST_ROOM = Zone("South-East")
    """South east room."""

    NORTH_WEST_ROOM = Zone("North-West")
    """North west room."""

    NORTH_EAST_ROOM = Zone("North-East")
    """North east room."""

    GOAL = Item("goal")
    """Goal to reach."""

    def __init__(self, **kwargs) -> None:
        self.task = GetItemTask(self.GOAL)

        self.ROOMS = [
            self.SOUTH_WEST_ROOM,
            self.SOUTH_EAST_ROOM,
            self.NORTH_EAST_ROOM,
            self.NORTH_WEST_ROOM,
        ]

        super().__init__(
            self.MINICRAFT_NAME,
            start_zone=self.SOUTH_WEST_ROOM,
            purpose=self.task,
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        find_goal = Transformation(
            "find-goal",
            inventory_changes=[Yield(CURRENT_ZONE, self.GOAL, max=0)],
            zone=self.NORTH_EAST_ROOM,
        )

        reach_goal = Transformation(
            "reach-goal",
            inventory_changes=[
                Use(CURRENT_ZONE, self.GOAL, consume=1),
                Yield(PLAYER, self.GOAL),
            ],
        )

        moves = []
        for room_id, destination in enumerate(self.ROOMS):
            for neighbor_room in [
                self.ROOMS[room_id - 1],
                self.ROOMS[room_id % len(self.ROOMS)],
            ]:
                moves.append(
                    Transformation(
                        f"go-to-{destination.name}-from-{neighbor_room.name}",
                        destination=destination,
                        zone=neighbor_room,
                    )
                )

        return [find_goal, reach_goal] + moves
