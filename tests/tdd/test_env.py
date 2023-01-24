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
        self.start_zone = Zone("start")
        self.other_zone = Zone("other_zone")
        self.zones = [self.start_zone, self.other_zone]

        self.move_to_other_zone = Transformation(
            destination=self.other_zone,
            zones=[self.start_zone],
        )

        self.wood = Item("wood")
        self.search_wood = Transformation(
            added_player_items=[ItemStack(self.wood, 2)],
        )

        self.plank = Item("plank")
        self.craft_plank = Transformation(
            removed_player_items=[ItemStack(self.wood, 1)],
            added_player_items=[ItemStack(self.plank, 4)],
        )

        self.table = Item("table")
        self.craft_table = Transformation(
            removed_player_items=[ItemStack(self.plank, 4)],
            added_zone_items=[ItemStack(self.table)],
        )

        self.items = [self.wood, self.plank]
        self.zones_items = [self.table]
        self.transformations = [
            self.move_to_other_zone,
            self.search_wood,
            self.craft_plank,
            self.craft_table,
        ]

    def test_world_initialisation(self):
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        check.equal(set(env.world.zones), set(self.zones))
        check.equal(set(env.world.items), set(self.items))
        check.equal(set(env.world.zones_items), set(self.zones_items))

    def test_state_initialisation(self):
        env = CraftingEnv(self.transformations)

        player_inventory, position, zones_inventories = env.state
        expected_player_inventory = np.zeros(len(self.items), np.uint16)
        check_np_equal(player_inventory, expected_player_inventory)

        expected_position = np.zeros(len(self.zones), np.uint16)
        expected_position[0] = 1
        check_np_equal(position, expected_position)

        expected_zones_inventories = np.zeros(
            (len(self.zones_items), len(self.zones)), np.uint16
        )
        check_np_equal(zones_inventories, expected_zones_inventories)

    def test_start_zone(self):
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        _, position, _ = env.state
        expected_position = np.zeros(len(self.zones), np.uint16)
        expected_position[env.world.zones.index(self.start_zone)] = 1
        check_np_equal(position, expected_position)
