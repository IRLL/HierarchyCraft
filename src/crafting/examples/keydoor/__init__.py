"""# KeyDoorBall example

Example inspired from classic gridworld examples.


Directly inspired from minigrid
[DoorKey](https://minigrid.farama.org/environments/minigrid/DoorKeyEnv/)
and [KeyCorridor](https://minigrid.farama.org/environments/minigrid/KeyCorridorEnv/).

![](https://github.com/Farama-Foundation/Minigrid/blob/master/figures/door-key-curriculum.gif?raw=true)

"""

import os
from typing import List

from crafting.elements import Item, Zone
from crafting.env import CraftingEnv
from crafting.task import GetItemTask
from crafting.transformation import Transformation
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

    WEIGHT = Item("weight")
    """Weight of carried items."""

    OPEN_DOOR = Item("open_door")
    """Open door between the two rooms."""
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

        search_for_key = Transformation(
            inventory_changes={
                "current_zone": {"add": [self.KEY]},
                "player": {"max": [self.KEY]},
                self.START: {"max": [self.KEY]},
                self.BALL_ROOM: {"max": [self.KEY]},
            },
            zones=[self.START],
        )
        transformations.append(search_for_key)

        carriable_items = (self.KEY, self.BALL)
        for carriable_item in carriable_items:
            pickup = Transformation(
                inventory_changes={
                    "player": {
                        "add": [carriable_item, self.WEIGHT],
                        "max": [self.WEIGHT],
                    },
                    "current_zone": {"remove": [carriable_item]},
                },
            )
            put_down = Transformation(
                inventory_changes={
                    "player": {"remove": [carriable_item, self.WEIGHT]},
                    "current_zone": {"add": [carriable_item]},
                },
            )
            transformations += [pickup, put_down]

        search_for_door = Transformation(
            inventory_changes={
                self.START: {"add": [self.LOCKED_DOOR], "max": [self.LOCKED_DOOR]},
                self.BALL_ROOM: {"add": [self.LOCKED_DOOR], "max": [self.LOCKED_DOOR]},
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(search_for_door)

        unlock_door = Transformation(
            inventory_changes={
                "player": {
                    "remove": [self.KEY],
                    "add": [self.KEY],
                },
                self.START: {
                    "remove": [self.LOCKED_DOOR],
                    "add": [self.OPEN_DOOR],
                },
                self.BALL_ROOM: {
                    "remove": [self.LOCKED_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(unlock_door)

        move_to_ball_room = Transformation(
            destination=self.BALL_ROOM,
            inventory_changes={
                "current_zone": {
                    "remove": [self.OPEN_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
            zones=[self.START],
        )
        transformations.append(move_to_ball_room)

        move_to_start_room = Transformation(
            destination=self.START,
            inventory_changes={
                "current_zone": {
                    "remove": [self.OPEN_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
            zones=[self.BALL_ROOM],
        )
        transformations.append(move_to_start_room)

        return transformations
