from typing import List, Tuple


import numpy as np

from crafting.world import Item, Zone
from crafting.transformation import Transformation


class CraftingEnv:
    def __init__(
        self,
        items: List[Item],
        zones: List[Zone],
        transformations: List[Transformation],
    ) -> None:
        self.items = items
        self.n_items = len(items)
        self.zones = zones
        self.n_zones = len(zones)
        self.transformations = transformations
        self.n_transformations = len(transformations)
        self.state = self._init_state()

    def _init_state(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        player_inventory = np.zeros(self.n_items, dtype=np.uint16)
        position = np.zeros(self.n_zones, dtype=np.uint16)
        position[0] = 1
        zones_inventories = np.zeros((self.n_items, self.n_zones), dtype=np.uint16)

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
