from typing import List, Tuple, Optional


import numpy as np

from crafting.world import Item, Zone, World
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
        self.n_transformations = len(transformations)
        self.start_zone = start_zone
        self.state = self._init_state()

    def _init_state(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        player_inventory = np.zeros(self.world.n_items, dtype=np.uint16)

        position = np.zeros(self.world.n_zones, dtype=np.uint16)
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

    def step(self, action: int):
        pass

    def render(self):
        pass

    def reset(self, seed: int = 0):
        pass
