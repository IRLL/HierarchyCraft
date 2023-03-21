"""# MiniCraft - MultiRoom"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniCraftMultiRoom(MiniCraftEnv):
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
            inventory_changes={
                "current_zone": {"add": [self.GOAL], "max": [self.GOAL]},
            },
            zones=[self.rooms[-1]],
        )
        transformations.append(find_goal)

        reach_goal = Transformation(
            "reach_goal",
            inventory_changes={
                "player": {"add": [self.GOAL]},
                "current_zone": {"remove": [self.GOAL]},
            },
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
