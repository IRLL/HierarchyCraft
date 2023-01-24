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
        self._destination = None
        self.zones = zones
        self._zones = None

    def _build_ops(self, world: World) -> None:
        if self.destination is not None:
            self._build_destination_op(world)
        if self.zones is not None:
            self._build_zones_op(world)

    def _build_destination_op(self, world: World) -> None:
        self._destination = np.zeros(world.n_zones, dtype=np.uint16)
        self._destination[world.slot_from_zone(self.destination)] = 1

    def _build_zones_op(self, world: World) -> None:
        self._zones = np.zeros(world.n_zones, dtype=np.uint16)
        for zone in self.zones:
            self._zones[world.slot_from_zone(zone)] = 1
