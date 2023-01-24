from typing import Optional, List

import numpy as np

from crafting.world import Item, Zone, World


class Transformation:
    def __init__(
        self,
        destination: Optional[Zone] = None,
        zones: Optional[List[Zone]] = None,
    ) -> None:
        self.destination = destination
        self.zones = zones

    def _build_ops(self, world: World) -> np.ndarray:
        self.destination_ops = np.zeros(world.n_zones, dtype=np.uint16)
