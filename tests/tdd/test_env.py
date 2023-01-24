# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import pytest_check as check
import numpy as np

from typing import List, Tuple
from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    name: str


@dataclass(frozen=True)
class Zone:
    name: str


class Transformation:
    pass


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
        self.state = self._init_state(items, zones, transformations)

    def _init_state(
        self,
        items: List[Item],
        zones: List[Zone],
        transformations: List[Transformation],
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        player_inventory = np.zeros(self.n_items, dtype=np.uint16)
        position = np.zeros(self.n_zones, dtype=np.uint16)
        position[0] = 1
        zones_inventories = np.zeros((self.n_items, self.n_zones), dtype=np.uint16)

        return (
            player_inventory,
            position,
            zones_inventories,
        )

    def slot_from_item(self, item: Item) -> int:
        return self.items.index(item)

    def slot_from_zone(self, zone: Zone) -> int:
        return self.zones.index(zone)

    def step(self, action: int):
        pass

    def render(self):
        pass

    def reset(self, seed: int = 0):
        pass


class TestCratingEnv:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.n_items = 5
        self.n_zones = 4
        self.n_transformations = 6

        self.items = [Item(str(i)) for i in range(self.n_items)]
        self.zones = [Zone(str(i)) for i in range(self.n_zones)]
        self.transformations = [Transformation() for _ in range(self.n_transformations)]

        self.env = CraftingEnv(
            items=self.items,
            zones=self.zones,
            transformations=self.transformations,
        )

    def test_state_initialisation(self):
        player_inventory, position, zones_inventories = self.env.state
        expected_player_inventory = np.zeros(self.n_items)
        check_np_equal(player_inventory, expected_player_inventory)

        expected_position = np.zeros(self.n_zones)
        expected_position[0] = 1
        check_np_equal(position, expected_position)

        expected_zones_inventories = np.zeros((self.n_items, self.n_zones))
        check_np_equal(zones_inventories, expected_zones_inventories)

    def test_slot_from_item(self):
        item_3 = self.items[3]
        check.equal(self.env.slot_from_item(item_3), 3)

    def test_slot_from_zone(self):
        zone_3 = self.zones[3]
        check.equal(self.env.slot_from_zone(zone_3), 3)


def check_np_equal(array: np.ndarray, expected_array: np.ndarray):
    check.is_true(
        np.all(array == expected_array),
        msg=f"Got:\n{array}\nExpected:\n{expected_array}\nDiff:{array-expected_array}",
    )
