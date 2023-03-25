"""# MiniCraft - KeyCorridor"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniHCraftKeyCorridor(MiniCraftEnv):
    MINICRAFT_NAME = "KeyCorridor"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    START = Zone("start_room")
    """Start room."""
    KEY_ROOM = Zone("key_room")
    """Room containing a key."""
    LOCKED_ROOM = Zone("locked_room")
    """Room behind a locked door."""

    KEY = Item("key")
    """Key used to unlock locked door."""
    BALL = Item("ball")
    """Ball to pickup."""
    WEIGHT = Item("weight")
    """Weight of carried items."""

    OPEN_DOOR = Item("open_door")
    """Opened lockedroom door."""
    OPEN_KEY_DOOR = Item("blue_open_door")
    """Opened keyroom door."""
    CLOSED_KEY_DOOR = Item("blue_closed_door")
    """Closed keyroom door."""
    LOCKED_DOOR = Item("locked_door")
    """Locked door, can be unlocked with a key."""

    def __init__(self, **kwargs) -> None:
        self.task = GetItemTask(self.BALL)
        super().__init__(
            self.MINICRAFT_NAME,
            start_zone=self.START,
            start_zones_items={
                self.START: [self.CLOSED_KEY_DOOR, self.LOCKED_DOOR],
                self.LOCKED_ROOM: [self.BALL],
            },
            purpose=self.task,
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        transformations = []

        # Ensure key cannot be created if anywhere else
        search_for_key = Transformation(
            "search_for_key",
            inventory_changes=[
                Yield(CURRENT_ZONE, self.KEY, create=1, max=0),
                Yield(PLAYER, self.KEY, create=0, max=0),
                Yield(self.START, self.KEY, create=0, max=0),
                Yield(self.KEY_ROOM, self.KEY, create=0, max=0),
                Yield(self.LOCKED_ROOM, self.KEY, create=0, max=0),
            ],
            zones=[self.KEY_ROOM],
        )
        transformations.append(search_for_key)

        pickup = Transformation(
            "pickup_key",
            inventory_changes=[
                Use(CURRENT_ZONE, self.KEY, consume=1),
                Yield(PLAYER, self.KEY),
                Yield(PLAYER, self.WEIGHT, max=0),
            ],
        )
        put_down = Transformation(
            "put_down_key",
            inventory_changes=[
                Use(PLAYER, self.KEY, consume=1),
                Use(PLAYER, self.WEIGHT, consume=1),
                Yield(CURRENT_ZONE, self.KEY, create=1),
            ],
        )
        transformations += [pickup, put_down]

        open_door = Transformation(
            "open_door",
            inventory_changes=[
                Use(CURRENT_ZONE, self.CLOSED_KEY_DOOR, consume=1),
                Yield(CURRENT_ZONE, self.OPEN_KEY_DOOR, create=1),
            ],
        )
        transformations.append(open_door)

        move_to_key_room = Transformation(
            "move_to_key_room",
            destination=self.KEY_ROOM,
            inventory_changes=[Use(CURRENT_ZONE, self.OPEN_KEY_DOOR)],
            zones=[self.START],
        )
        transformations.append(move_to_key_room)

        move_to_start_room = Transformation(
            "move_to_start_room",
            destination=self.START,
            zones=[self.KEY_ROOM, self.LOCKED_ROOM],
        )
        transformations.append(move_to_start_room)

        unlock_door = Transformation(
            "unlock_door",
            inventory_changes=[
                Use(PLAYER, self.KEY),
                Use(CURRENT_ZONE, self.LOCKED_DOOR, consume=1),
                Yield(CURRENT_ZONE, self.OPEN_DOOR, create=1),
            ],
        )
        transformations.append(unlock_door)

        move_to_locked_room = Transformation(
            "move_to_locked_room",
            destination=self.LOCKED_ROOM,
            inventory_changes=[Use(CURRENT_ZONE, self.OPEN_DOOR)],
            zones=[self.START],
        )
        transformations.append(move_to_locked_room)

        pickup_ball = Transformation(
            "pickup_ball",
            inventory_changes=[
                Use(CURRENT_ZONE, self.BALL, consume=1),
                Yield(PLAYER, self.BALL),
                Yield(PLAYER, self.WEIGHT, max=0),
            ],
        )
        transformations.append(pickup_ball)

        return transformations
