"""# MiniCraft - UnlockPickup"""

from typing import List

from hcraft.elements import Item, Zone
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE


from hcraft.examples.minicraft.minicraft import MiniCraftEnv


class MiniHCraftUnlockPickup(MiniCraftEnv):
    MINICRAFT_NAME = "UnlockPickup"
    __doc__ = MiniCraftEnv.description(MINICRAFT_NAME)

    START = Zone("start_room")
    """Start room."""
    BOX_ROOM = Zone("box_room")
    """Room with a box inside."""

    KEY = Item("key")
    """Key used to unlock the door."""
    BOX = Item("box")
    """Box to pickup."""
    WEIGHT = Item("weight")
    """Weight of carried items, can only be less than 1."""

    OPEN_DOOR = Item("open_door")
    """Open door between the two rooms."""
    LOCKED_DOOR = Item("locked_door")
    """Locked door between the two rooms, can be unlocked with a key."""

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
            inventory_changes = [
                Yield(CURRENT_ZONE, item, create=1),
                # Prevent searching if already found
                Yield(PLAYER, item, create=0, max=0),
            ]
            # Prevent searching if item was placed elsewhere
            inventory_changes += [Yield(zone, item, create=0, max=0) for zone in zones]
            search_for_item = Transformation(
                f"search_for_{item.name}",
                inventory_changes=inventory_changes,
                zones=[zone],
            )
            transformations.append(search_for_item)

            pickup = Transformation(
                f"pickup_{item.name}",
                inventory_changes=[
                    Use(CURRENT_ZONE, item, consume=1),
                    Yield(PLAYER, item, create=1),
                    # WEIGHT prevents carrying more than one item
                    Yield(PLAYER, self.WEIGHT, create=1, max=0),
                ],
            )
            put_down = Transformation(
                f"put_down_{item.name}",
                inventory_changes=[
                    Use(PLAYER, item, consume=1),
                    Yield(CURRENT_ZONE, item, create=1),
                    # WEIGHT prevents carrying more than one item
                    Use(PLAYER, self.WEIGHT, consume=1),
                ],
            )
            transformations += [pickup, put_down]

        search_for_door = Transformation(
            "search_for_door",
            inventory_changes=[
                Yield(CURRENT_ZONE, self.LOCKED_DOOR, max=0),
                Yield(CURRENT_ZONE, self.OPEN_DOOR, create=0, max=0),
            ],
            zones=[self.START],
        )
        transformations.append(search_for_door)

        unlock_door = Transformation(
            "unlock_door",
            inventory_changes=[
                Use(PLAYER, self.KEY),
                Use(CURRENT_ZONE, self.LOCKED_DOOR, consume=1),
                Yield(CURRENT_ZONE, self.OPEN_DOOR),
            ],
        )
        transformations.append(unlock_door)

        move_to_box_room = Transformation(
            "move_to_box_room",
            destination=self.BOX_ROOM,
            inventory_changes=[Use(CURRENT_ZONE, self.OPEN_DOOR)],
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
