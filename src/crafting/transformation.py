from typing import Optional, List

import numpy as np

from crafting.world import ItemStack, Zone, World


class Transformation:
    def __init__(
        self,
        destination: Optional[Zone] = None,
        zones: Optional[List[Zone]] = None,
        removed_player_items: Optional[List[ItemStack]] = None,
        added_player_items: Optional[List[ItemStack]] = None,
    ) -> None:
        self.destination = destination
        self._destination = None
        self.zones = zones
        self._zones = None
        self.removed_player_items = removed_player_items
        self._removed_player_items = None
        self.added_player_items = added_player_items
        self._added_player_items = None

    def _build_ops(self, world: World) -> None:
        if self.destination is not None:
            self._build_destination_op(world)
        if self.zones is not None:
            self._build_zones_op(world)
        if self.removed_player_items is not None:
            self._build_removed_player_items_op(world)
        if self.added_player_items is not None:
            self._build_added_player_items_op(world)

    def _build_destination_op(self, world: World) -> None:
        self._destination = np.zeros(world.n_zones, dtype=np.uint16)
        self._destination[world.slot_from_zone(self.destination)] = 1

    def _build_zones_op(self, world: World) -> None:
        self._zones = np.zeros(world.n_zones, dtype=np.uint16)
        for zone in self.zones:
            self._zones[world.slot_from_zone(zone)] = 1

    def _build_removed_player_items_op(self, world: World) -> None:
        self._removed_player_items = np.zeros(world.n_items, dtype=np.uint16)
        for itemstack in self.removed_player_items:
            item_slot = world.slot_from_item(itemstack.item)
            self._removed_player_items[item_slot] = itemstack.quantity

    def _build_added_player_items_op(self, world: World) -> None:
        self._added_player_items = np.zeros(world.n_items, dtype=np.uint16)
        for itemstack in self.added_player_items:
            item_slot = world.slot_from_item(itemstack.item)
            self._added_player_items[item_slot] = itemstack.quantity
