# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import pytest_check as check
import numpy as np

from crafting.world import ItemStack, Item, Zone
from crafting.transformation import Transformation
from crafting.env import CraftingEnv

from tests.check_array import check_np_equal


class TestCratingEnv:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.n_items = 5
        self.n_zones_items = 2
        self.n_zones = 4

        self.items = [Item(str(i)) for i in range(self.n_items)]
        self.zones = [Zone(str(i)) for i in range(self.n_zones)]
        self.zones_items = [Item(f"z{i}") for i in range(self.n_zones_items)]

    def test_state_initialisation(self):
        env = CraftingEnv(
            items=self.items,
            zones=self.zones,
            zones_items=self.zones_items,
            transformations=[],
        )

        player_inventory, position, zones_inventories = env.state
        expected_player_inventory = np.zeros(self.n_items, np.uint16)
        check_np_equal(player_inventory, expected_player_inventory)

        expected_position = np.zeros(self.n_zones, np.uint16)
        expected_position[0] = 1
        check_np_equal(position, expected_position)

        expected_zones_inventories = np.zeros((self.n_items, self.n_zones), np.uint16)
        check_np_equal(zones_inventories, expected_zones_inventories)

    def test_start_zone(self):
        env = CraftingEnv(
            items=self.items,
            zones=self.zones,
            zones_items=self.zones_items,
            transformations=[],
            start_zone=self.zones[1],
        )

        _, position, _ = env.state
        expected_position = np.zeros(self.n_zones, np.uint16)
        expected_position[1] = 1
        check_np_equal(position, expected_position)

    def test_raise_missing_item_when_parsing_tranformations(self):
        wrong_tranfo = Transformation(
            removed_player_items=[ItemStack(self.zones_items[0])],
        )
        with pytest.raises(ValueError, match="Missing"):
            CraftingEnv(
                items=self.items,
                zones=self.zones,
                zones_items=self.zones_items,
                transformations=[wrong_tranfo],
            )

        wrong_tranfo = Transformation(
            added_zone_items=[ItemStack(self.items[0])],
        )
        with pytest.raises(ValueError, match="Missing"):
            CraftingEnv(
                items=self.items,
                zones=self.zones,
                zones_items=self.zones_items,
                transformations=[wrong_tranfo],
            )
