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
            added_player_items=[ItemStack(self.wood)],
        )

        self.stone = Item("stone")
        self.search_stone = Transformation(
            added_player_items=[ItemStack(self.stone, 1)],
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

        self.wood_house = Item("wood house")
        self.build_house = Transformation(
            removed_player_items=[ItemStack(self.plank, 32), ItemStack(self.wood, 8)],
            added_zone_items=[ItemStack(self.wood_house)],
        )

        self.items = [self.wood, self.stone, self.plank]
        self.zones_items = [self.table, self.wood_house]
        self.transformations = [
            self.move_to_other_zone,
            self.search_wood,
            self.search_stone,
            self.craft_plank,
            self.craft_table,
            self.build_house,
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
            (len(self.zones), len(self.zones_items)), np.uint16
        )
        check_np_equal(zones_inventories, expected_zones_inventories)

    def test_start_zone(self):
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        _, position, _ = env.state
        expected_position = np.zeros(len(self.zones), np.uint16)
        expected_position[env.world.zones.index(self.start_zone)] = 1
        check_np_equal(position, expected_position)

    def test_observation(self):
        env = CraftingEnv(self.transformations)
        env.player_inventory[1] = 2
        start_zone_index = 0
        env.zones_inventories[start_zone_index, 0] = 3
        env.zones_inventories[start_zone_index, 1] = 1
        expected_observation = np.array([0, 2, 0, 1, 0, 3, 1])
        check_np_equal(env.observation, expected_observation)

    def test_step_move(self):
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)

        start_zone_slot = env.world.slot_from_zone(self.start_zone)
        expected_positon = np.zeros(env.world.n_zones)
        expected_positon[start_zone_slot] = 1
        check_np_equal(env.position, expected_positon)
        action = self.transformations.index(self.move_to_other_zone)
        env.step(action)
        expected_positon = np.zeros(env.world.n_zones)
        expected_positon[1 - start_zone_slot] = 1
        check_np_equal(env.position, expected_positon)

    def test_step_search(self):
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        wood_slot = env.world.items.index(self.wood)

        check.equal(env.player_inventory[wood_slot], 0)
        action = self.transformations.index(self.search_wood)
        env.step(action)
        check.equal(env.player_inventory[wood_slot], 1)

    def test_step_craft(self):
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        wood_slot = env.world.items.index(self.wood)
        plank_slot = env.world.items.index(self.plank)
        action = self.transformations.index(self.craft_plank)

        # Invalid craft does not change state
        env.step(action)
        check.equal(env.player_inventory[wood_slot], 0)
        check.equal(env.player_inventory[plank_slot], 0)

        # Valid craft does change state
        env.player_inventory[wood_slot] = 1
        env.step(action)
        check.equal(env.player_inventory[wood_slot], 0)
        check.equal(env.player_inventory[plank_slot], 4)

    def test_reset(self):
        env = CraftingEnv(self.transformations)

        # Initialize an ongoing env
        env.position[0] = 0
        env.position[1] = 1
        env.player_inventory[0] = 2
        env.zones_inventories[0, 0] = 3
        env.zones_inventories[1, 1] = 4

        env.reset()
        expected_player_inventory = np.zeros(len(self.items), np.uint16)
        check_np_equal(env.player_inventory, expected_player_inventory)

        expected_position = np.zeros(len(self.zones), np.uint16)
        expected_position[0] = 1
        check_np_equal(env.position, expected_position)

        expected_zones_inventories = np.zeros(
            (len(self.zones), len(self.zones_items)), np.uint16
        )
        check_np_equal(env.zones_inventories, expected_zones_inventories)