from typing import List, Set, Tuple, Optional

import numpy as np

from crafting.world import Item, ItemStack, Zone, World
from crafting.transformation import Transformation


class CraftingEnv:
    def __init__(
        self,
        transformations: List[Transformation],
        start_zone: Optional[Zone] = None,
        invalid_reward: float = -10.0,
    ) -> None:
        self.transformations = transformations
        self.start_zone = start_zone
        self.invalid_reward = invalid_reward
        self.world = self._build_world()
        self._build_transformations()

        self.player_inventory = np.array([], dtype=np.uint16)
        self.position = np.array([], dtype=np.uint16)
        self.zones_inventories = np.array([], dtype=np.uint16)
        self._reset_state()

    @property
    def state(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.player_inventory, self.position, self.zones_inventories

    @property
    def observation(self) -> np.ndarray:
        current_zone_slot = self.position.nonzero()[0]
        return np.concatenate(
            (
                self.player_inventory,
                self.position,
                self.zones_inventories[current_zone_slot, :][0],
            )
        )

    @property
    def truncated(self) -> bool:
        return False

    @property
    def terminated(self) -> bool:
        return False

    def step(self, action: int):
        choosen_transformation = self.transformations[action]
        if not choosen_transformation.is_valid(*self.state):
            return self._step_output(self.invalid_reward)
        choosen_transformation.apply(
            self.player_inventory,
            self.position,
            self.zones_inventories,
        )
        return self._step_output(0)

    def _step_output(self, reward: float):
        return (self.observation, reward, self.terminated or self.truncated, {})

    def render(self):
        pass

    def reset(self, seed: int = 0):
        self._reset_state()

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

    def _build_transformations(self):
        for transformation in self.transformations:
            transformation.build(self.world)

    def _reset_state(self) -> None:
        self.player_inventory = np.zeros(self.world.n_items, dtype=np.uint16)

        self.position = np.zeros(self.world.n_zones, dtype=np.uint16)
        start_slot = 0  # Start in first Zone by default
        if self.start_zone is not None:
            start_slot = self.world.slot_from_zone(self.start_zone)
        self.position[start_slot] = 1

        self.zones_inventories = np.zeros(
            (self.world.n_zones, self.world.n_zones_items), dtype=np.uint16
        )


def _add_items_to(itemstacks: Optional[List[ItemStack]], items_set: Set[Item]):
    if itemstacks is not None:
        for itemstack in itemstacks:
            items_set.add(itemstack.item)
    return items_set
