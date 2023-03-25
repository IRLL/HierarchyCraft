"""# MiniCraft - MultiRoom"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniHCraftMultiRoom(MiniCraftEnv):
    MINICRAFT_NAME = "MultiRoom"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    GOAL = Item("goal")
    """Goal to reach."""

    def __init__(self, n_rooms: int = 6, **kwargs) -> None:
        self.rooms = [Zone(str(i + 1)) for i in range(n_rooms)]
        self.task = GetItemTask(self.GOAL)
        super().__init__(
            self.MINICRAFT_NAME,
            purpose=self.task,
            start_zone=self.rooms[0],
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        transformations = []
        find_goal = Transformation(
            "find_goal",
            inventory_changes=[Yield(CURRENT_ZONE, self.GOAL, max=0)],
            zones=[self.rooms[-1]],
        )
        transformations.append(find_goal)

        reach_goal = Transformation(
            "reach_goal",
            inventory_changes=[
                Use(CURRENT_ZONE, self.GOAL, consume=1),
                Yield(PLAYER, self.GOAL),
            ],
        )
        transformations.append(reach_goal)

        for i, room in enumerate(self.rooms):
            connected_rooms = []
            if i > 0:
                connected_rooms.append(self.rooms[i - 1])
            if i < len(self.rooms) - 1:
                connected_rooms.append(self.rooms[i + 1])
            go_to_room = Transformation(
                f"go_to_{room}",
                destination=room,
                zones=connected_rooms,
            )
            transformations.append(go_to_room)

        return transformations
