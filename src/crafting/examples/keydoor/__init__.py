"""# KeyDoorBall example

Example inspired from classic gridworld examples.


Directly inspired from minigrid
[DoorKey](https://minigrid.farama.org/environments/minigrid/DoorKeyEnv/)
and [KeyCorridor](https://minigrid.farama.org/environments/minigrid/KeyCorridorEnv/).

![](https://github.com/Farama-Foundation/Minigrid/blob/master/figures/door-key-curriculum.gif?raw=true)

"""

import os
from typing import List

from crafting.env import CraftingEnv
from crafting.elements import Item, Zone
from crafting.transformation import Transformation
from crafting.task import GetItemTask
from crafting.world import world_from_transformations

# gym is an optional dependency
try:
    import gym

    gym.register(
        id="KeyDoorCrafting-v1",
        entry_point="crafting.examples.keydoor:KeyDoorCraftingEnv",
    )
except ImportError:
    pass


class KeyDoorCraftingEnv(CraftingEnv):
    """Reproduces the classic KeyDoor gridworld environment as a Crafting environment."""

    START = Zone("start_room")
    """Start room."""
    BALL_ROOM = Zone("ball_room")
    """Ball room behind a locked door."""

    KEY = Item("key")
    """Key used to unlock the door."""
    BALL = Item("ball")
    """Ball to pickup in the ball room."""

    OPEN_DOOR = Item("open_door")
    """Open door between the two rooms."""
    CLOSED_DOOR = Item("closed_door")
    """Close door between the two rooms, can be opened without a key."""
    LOCKED_DOOR = Item("locked_door")
    """Locked door between the two rooms, can be unlocked with a key."""

    def __init__(self, **kwargs) -> None:
        """
        Kwargs:
            See `crafting.env.CraftingEnv`
        """
        resources_path = os.path.join(os.path.dirname(__file__), "resources")
        transformations = self._build_transformations()
        world = world_from_transformations(
            transformations=transformations,
            start_zone=self.START,
            start_zones_items={self.BALL_ROOM: [self.BALL]},
        )
        self.goal = GetItemTask(self.BALL)
        world.resources_path = resources_path
        super().__init__(world, purpose=self.goal, name="KeyDoorCrafting", **kwargs)

    def _build_transformations(self) -> List[Transformation]:
        transformations = []

        search_for_key = Transformation(added_zone_items=[self.KEY], zones=[self.START])
        transformations.append(search_for_key)
        for carriable_item in (self.KEY, self.BALL):
            pickup = Transformation(
                removed_zone_items=[carriable_item], added_player_items=[carriable_item]
            )
            put_down = Transformation(
                removed_player_items=[carriable_item], added_zone_items=[carriable_item]
            )
            transformations += [pickup, put_down]

        search_for_door = Transformation(
            added_zones_items={
                self.START: [self.LOCKED_DOOR],
                self.BALL_ROOM: [self.LOCKED_DOOR],
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(search_for_door)

        unlock_door = Transformation(
            removed_player_items=[self.KEY],
            added_player_items=[self.KEY],
            removed_zones_items={
                self.START: [self.LOCKED_DOOR],
                self.BALL_ROOM: [self.LOCKED_DOOR],
            },
            added_zones_items={
                self.START: [self.CLOSED_DOOR],
                self.BALL_ROOM: [self.CLOSED_DOOR],
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(unlock_door)

        open_door = Transformation(
            removed_zones_items={
                self.START: [self.CLOSED_DOOR],
                self.BALL_ROOM: [self.CLOSED_DOOR],
            },
            added_zones_items={
                self.START: [self.OPEN_DOOR],
                self.BALL_ROOM: [self.OPEN_DOOR],
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(open_door)

        move_to_ball_room = Transformation(
            destination=self.BALL_ROOM,
            removed_zone_items=[self.OPEN_DOOR],
            added_zone_items=[self.OPEN_DOOR],
            zones=[self.START],
        )
        transformations.append(move_to_ball_room)

        move_to_start_room = Transformation(
            destination=self.START,
            removed_zone_items=[self.OPEN_DOOR],
            added_zone_items=[self.OPEN_DOOR],
            zones=[self.BALL_ROOM],
        )
        transformations.append(move_to_start_room)

        return transformations
