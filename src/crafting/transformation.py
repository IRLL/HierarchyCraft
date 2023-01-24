from typing import Optional, List, Tuple

import numpy as np

from crafting.world import Item, ItemStack, Zone, World


class Transformation:

    OPERATIONS = [
        "destination",
        "zones",
        "removed_player_items",
        "added_player_items",
        "removed_destination_items",
        "added_destination_items",
        "removed_zone_items",
        "added_zone_items",
    ]

    def __init__(
        self,
        destination: Optional[Zone] = None,
        zones: Optional[List[Zone]] = None,
        removed_player_items: Optional[List[ItemStack]] = None,
        added_player_items: Optional[List[ItemStack]] = None,
        removed_destination_items: Optional[List[ItemStack]] = None,
        added_destination_items: Optional[List[ItemStack]] = None,
        removed_zone_items: Optional[List[ItemStack]] = None,
        added_zone_items: Optional[List[ItemStack]] = None,
    ) -> None:
        self.destination = destination
        self._destination = None

        self.zones = zones
        self._zones = None

        self.removed_player_items = removed_player_items
        self._removed_player_items = None
        self.added_player_items = added_player_items
        self._added_player_items = None

        self.removed_destination_items = removed_destination_items
        self._removed_destination_items = None
        self.added_destination_items = added_destination_items
        self._added_destination_items = None

        self.removed_zone_items = removed_zone_items
        self._removed_zone_items = None
        self.added_zone_items = added_zone_items
        self._added_zone_items = None

    def apply(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventories: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        position_slot: int = position.nonzero()[0]
        if self._added_player_items is not None:
            player_inventory += self._added_player_items
        if self._removed_player_items is not None:
            player_inventory -= self._removed_player_items
        if self._added_zone_items is not None:
            zones_inventories[position_slot, :] += self._added_zone_items
        if self._removed_zone_items is not None:
            zones_inventories[position_slot, :] -= self._removed_zone_items
        if self._destination is not None:
            destination_slot: int = self._destination.nonzero()[0]
            if self._added_destination_items is not None:
                zones_inventories[destination_slot, :] += self._added_destination_items
            if self._removed_destination_items is not None:
                zones_inventories[
                    destination_slot, :
                ] -= self._removed_destination_items
            position[...] = self._destination
        return player_inventory, position, zones_inventories

    def is_valid(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventories: np.ndarray,
    ) -> bool:
        if self._zones is not None and not np.any(np.multiply(self._zones, position)):
            return False
        if self._removed_player_items is not None and not np.all(
            player_inventory >= self._removed_player_items
        ):
            return False

        if self._removed_zone_items is not None:
            current_zone_slot = position.nonzero()[0]
            current_zone_inventory = zones_inventories[current_zone_slot, :]
            if not np.all(current_zone_inventory >= self._removed_zone_items):
                return False

        if (
            self._destination is not None
            and self._removed_destination_items is not None
        ):
            destination_zone_slot = self._destination.nonzero()[0]
            destination_inventory = zones_inventories[destination_zone_slot, :]
            if not np.all(destination_inventory >= self._removed_destination_items):
                return False
        return True

    def build(self, world: World) -> None:
        for op_name in self.OPERATIONS:
            if getattr(self, op_name) is not None:
                builder = getattr(self, f"_build_{op_name}_op")
                builder(world)

    def _build_destination_op(self, world: World) -> None:
        self._destination = np.zeros(world.n_zones, dtype=np.uint16)
        self._destination[world.slot_from_zone(self.destination)] = 1

    def _build_zones_op(self, world: World) -> None:
        self._zones = np.zeros(world.n_zones, dtype=np.uint16)
        for zone in self.zones:
            self._zones[world.slot_from_zone(zone)] = 1

    def _build_removed_player_items_op(self, world: World) -> None:
        self._build_items_op("removed_player_items", world.items)

    def _build_added_player_items_op(self, world: World) -> None:
        self._build_items_op("added_player_items", world.items)

    def _build_removed_destination_items_op(self, world: World) -> None:
        self._build_items_op("removed_destination_items", world.zones_items)

    def _build_added_destination_items_op(self, world: World) -> None:
        self._build_items_op("added_destination_items", world.zones_items)

    def _build_removed_zone_items_op(self, world: World) -> None:
        self._build_items_op("removed_zone_items", world.zones_items)

    def _build_added_zone_items_op(self, world: World) -> None:
        self._build_items_op("added_zone_items", world.zones_items)

    def _build_items_op(self, op_name: str, world_item_list: List[Item]):
        operation = np.zeros(len(world_item_list), dtype=np.uint16)
        itemstacks: List[ItemStack] = getattr(self, op_name)
        for itemstack in itemstacks:
            item_slot = world_item_list.index(itemstack.item)
            operation[item_slot] = itemstack.quantity
        setattr(self, f"_{op_name}", operation)
