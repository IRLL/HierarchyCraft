from typing import List, Set, Tuple, Optional


import numpy as np

from crafting.world import Item, ItemStack, Zone, World
from crafting.transformation import Transformation


class CraftingEnv:
    def __init__(
        self,
        transformations: List[Transformation],
        start_zone: Optional[Zone] = None,
    ) -> None:
        self.transformations = transformations
        self.world = self._build_world()
        self.start_zone = start_zone
        (
            self.player_inventory,
            self.position,
            self.zones_inventories,
        ) = self._init_state()

    @property
    def state(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.player_inventory, self.position, self.zones_inventories

    def step(self, action: int):
        pass

    def render(self):
        pass

    def reset(self, seed: int = 0):
        pass

    def _build_world(self) -> World:
        items, zones, zones_items = set(), set(), set()
        for transfo in self.transformations:
            if transfo.destination is not None:
                zones.add(transfo.destination)
            if transfo.zones is not None:
                zones |= set(transfo.zones)
            items = _add_items_to(transfo.removed_player_items, items)
            items = _add_items_to(transfo.added_player_items, items)
            zones_items = _add_items_to(transfo.removed_destination_items, zones_items)
            zones_items = _add_items_to(transfo.added_destination_items, zones_items)
            zones_items = _add_items_to(transfo.removed_zone_items, zones_items)
            zones_items = _add_items_to(transfo.added_zone_items, zones_items)

        return World(list(items), list(zones), list(zones_items))

    def _init_state(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        player_inventory = np.zeros(self.world.n_items, dtype=np.uint16)

        position = np.zeros(self.world.n_zones, dtype=np.uint16)
        start_slot = 0  # Start in first Zone by default
        if self.start_zone is not None:
            start_slot = self.world.slot_from_zone(self.start_zone)
        position[start_slot] = 1

        zones_inventories = np.zeros(
            (self.world.n_items, self.world.n_zones), dtype=np.uint16
        )

        return (
            player_inventory,
            position,
            zones_inventories,
        )


def _add_items_to(itemstacks: Optional[List[ItemStack]], items_set: Set[Item]):
    if itemstacks is not None:
        for itemstack in itemstacks:
            items_set.add(itemstack.item)
    return items_set
