from typing import List, Tuple, Optional


import numpy as np

from crafting.world import Item, ItemStack, Zone, World
from crafting.transformation import Transformation


class CraftingEnv:
    def __init__(
        self,
        items: List[Item],
        zones: List[Zone],
        zones_items: List[Zone],
        transformations: List[Transformation],
        start_zone: Optional[Zone] = None,
    ) -> None:
        self.world = World(items, zones, zones_items)
        self.transformations = transformations
        self.start_zone = start_zone
        self._validate_transformations()
        self.state = self._init_state()

    def step(self, action: int):
        pass

    def render(self):
        pass

    def reset(self, seed: int = 0):
        pass

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

    def _validate_transformations(self):
        def check_items_in(items: Optional[List[ItemStack]], items_list: List[Item]):
            if items is None:
                return
            for itemstack in items:
                if itemstack.item not in items_list:
                    raise ValueError(f"Missing {itemstack.item} in {items_list}.")

        for transfo in self.transformations:
            check_items_in(transfo.removed_player_items, self.world.items)
            check_items_in(transfo.added_player_items, self.world.items)
            check_items_in(transfo.removed_destination_items, self.world.zones_items)
            check_items_in(transfo.added_destination_items, self.world.zones_items)
            check_items_in(transfo.removed_zone_items, self.world.zones_items)
            check_items_in(transfo.added_zone_items, self.world.zones_items)
