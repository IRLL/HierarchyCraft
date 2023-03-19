"""# MiniCraft - BlockedUnlockPickup"""

from typing import List

from crafting.elements import Item, Zone, Stack
from crafting.task import GetItemTask
from crafting.transformation import Transformation

from crafting.examples.minicraft.minicraft import MiniCraftEnv


class MiniCraftBlockedUnlockPickup(MiniCraftEnv):
    MINICRAFT_NAME = "BlockedUnlockPickup"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    START = Zone("start_room")
    """Start room."""
    BOX_ROOM = Zone("box_room")
    """Room with a box inside."""

    KEY = Item("key")
    """Key used to unlock the door."""
    BOX = Item("box")
    """Box to pickup."""
    BALL = Item("ball")
    """Ball blocking the door."""
    WEIGHT = Item("weight")
    """Weight of carried items, can only be less than 1."""

    OPEN_DOOR = Item("open_door")
    """Open door between the two rooms."""
    LOCKED_DOOR = Item("locked_door")
    """Locked door between the two rooms, can be unlocked with a key."""
    BLOCKED_DOOR = Item("blocked_door")
    """Open but blocked door between the two rooms."""
    BLOCKED_LOCKED_DOOR = Item("blocked_locked_door")
    """Locked and blocked door between the two rooms."""

    def __init__(self, **kwargs) -> None:
        self.task = GetItemTask(self.BOX)
        super().__init__(
            self.MINICRAFT_NAME,
            purpose=self.task,
            start_zone=self.START,
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        transformations = []

        zones = (self.START, self.BOX_ROOM)
        items_in_zone = [(self.KEY, self.START), (self.BOX, self.BOX_ROOM)]

        for item, zone in items_in_zone:
            inventory_changes = {
                "current_zone": {"add": [item]},
                # Prevent searching if already found
                "player": {"max": [item]},
            }
            # Prevent searching if item was placed elsewhere
            inventory_changes.update(
                {zone: {"max": [item]} for zone in zones},
            )
            search_for_item = Transformation(
                f"search_for_{item.name}",
                inventory_changes=inventory_changes,
                zones=[zone],
            )
            transformations.append(search_for_item)

        for item in (self.KEY, self.BOX, self.BALL):
            pickup = Transformation(
                f"pickup_{item.name}",
                inventory_changes={
                    "player": {
                        "add": [item, self.WEIGHT],
                        # Prevent carrying more than one item
                        "max": [self.WEIGHT],
                    },
                    "current_zone": {"remove": [item]},
                },
            )
            put_down = Transformation(
                f"put_down_{item.name}",
                inventory_changes={
                    "player": {"remove": [item, self.WEIGHT]},
                    "current_zone": {"add": [item]},
                },
            )
            transformations += [pickup, put_down]

        search_for_door = Transformation(
            "search_for_door",
            inventory_changes={
                "current_zone": {
                    "add": [self.BLOCKED_LOCKED_DOOR],
                    # Prevent creating door if door was already found
                    "max": [
                        self.BLOCKED_LOCKED_DOOR,
                        Stack(self.BLOCKED_DOOR, 0),
                        Stack(self.LOCKED_DOOR, 0),
                        Stack(self.OPEN_DOOR, 0),
                    ],
                },
            },
            zones=[self.START],
        )
        transformations.append(search_for_door)

        unblock_locked_door = Transformation(
            "unblock_locked_door",
            inventory_changes={
                "player": {
                    "add": [self.BALL, self.WEIGHT],
                    "max": [self.WEIGHT],
                },
                "current_zone": {
                    "remove": [self.BLOCKED_LOCKED_DOOR],
                    "add": [self.LOCKED_DOOR],
                },
            },
        )
        transformations.append(unblock_locked_door)

        block_locked_door = Transformation(
            "block_locked_door",
            inventory_changes={
                "player": {
                    "remove": [self.BALL, self.WEIGHT],
                },
                "current_zone": {
                    "remove": [self.LOCKED_DOOR],
                    "add": [self.BLOCKED_LOCKED_DOOR],
                },
            },
        )
        transformations.append(block_locked_door)

        unlock_door = Transformation(
            "unlock_door",
            inventory_changes={
                "player": {
                    "remove": [self.KEY],
                    "add": [self.KEY],
                },
                "current_zone": {
                    "remove": [self.LOCKED_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
        )
        transformations.append(unlock_door)

        block_door = Transformation(
            "block_door",
            inventory_changes={
                "player": {
                    "remove": [self.BALL, self.WEIGHT],
                },
                "current_zone": {
                    "remove": [self.OPEN_DOOR],
                    "add": [self.BLOCKED_DOOR],
                },
            },
        )
        transformations.append(block_door)

        unblock_door = Transformation(
            "unblock_door",
            inventory_changes={
                "player": {
                    "add": [self.BALL, self.WEIGHT],
                    "max": [self.WEIGHT],
                },
                "current_zone": {
                    "remove": [self.BLOCKED_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
        )
        transformations.append(unblock_door)

        move_to_box_room = Transformation(
            "move_to_box_room",
            destination=self.BOX_ROOM,
            inventory_changes={
                "current_zone": {
                    "remove": [self.OPEN_DOOR],
                    "add": [self.OPEN_DOOR],
                },
            },
            zones=[self.START],
        )
        transformations.append(move_to_box_room)

        move_to_start_room = Transformation(
            "move_to_start_room",
            destination=self.START,
            zones=[self.BOX_ROOM],
        )
        transformations.append(move_to_start_room)

        return transformations
