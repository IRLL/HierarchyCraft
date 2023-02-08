from typing import List

import numpy as np
import pytest
import pytest_check as check

from crafting.env import CraftingEnv
from crafting.task import GetItemTask
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone
from tests.custom_checks import check_np_equal
from tests.envs import classic_env, zone_only_env, player_only_env


class TestCratingEnv:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        (
            self.named_transformations,
            self.start_zone,
            self.items,
            self.zones,
            self.zones_items,
        ) = classic_env()
        self.transformations: List[Transformation] = list(
            self.named_transformations.values()
        )

    def test_world_initialisation(self):
        """should find all items, zones and zones_items in transformations."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        check.equal(set(env.world.zones), set(self.zones))
        check.equal(set(env.world.items), set(self.items))
        check.equal(set(env.world.zones_items), set(self.zones_items))

    def test_state_initialisation(self):
        """should initialize the state as expected."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)

        player_inventory, position, zones_inventories = env.state
        expected_player_inventory = np.zeros(len(self.items), np.uint16)
        check_np_equal(player_inventory, expected_player_inventory)

        expected_position = np.zeros(len(self.zones), np.uint16)
        start_zone_slot = env.world.zones.index(self.start_zone)
        expected_position[start_zone_slot] = 1
        check_np_equal(position, expected_position)

        expected_zones_inventories = np.zeros(
            (len(self.zones), len(self.zones_items)), np.uint16
        )
        check_np_equal(zones_inventories, expected_zones_inventories)

    def test_start_zone(self):
        """position should be in start zone at initialization if given,
        even if zone is not in transformations."""
        new_start_zone = Zone("new_start_zone")
        env = CraftingEnv(self.transformations, start_zone=new_start_zone)
        _, position, _ = env.state
        expected_position = np.zeros(len(env.world.zones), np.uint16)
        expected_position[env.world.zones.index(new_start_zone)] = 1
        check_np_equal(position, expected_position)

    def test_start_items(self):
        """player inventory should be filled with start_items at initialization if given,
        even if items are not in any transformations."""
        start_item = Item("start_item")
        env = CraftingEnv(
            self.transformations,
            start_zone=self.start_zone,
            start_items=[ItemStack(start_item, 2), ItemStack(Item("wood"), 3)],
        )
        player_items, _, _ = env.state
        expected_items = np.zeros(env.world.n_items, np.uint16)
        expected_items[env.world.items.index(start_item)] = 2
        expected_items[env.world.items.index(Item("wood"))] = 3
        check_np_equal(player_items, expected_items)

    def test_start_zones_items(self):
        """zones inventories should be filled with start_zones_items at initialization if given,
        even if items and zones are not in any transformations."""
        new_zone = Zone("new_zone")
        new_zone_item = Item("new_zone_item")

        env = CraftingEnv(
            self.transformations,
            start_zone=self.start_zone,
            start_zones_items={
                new_zone: [ItemStack(new_zone_item, 2), ItemStack(Item("wood"), 3)],
            },
        )
        _, _, zones_inventories = env.state
        zone_slot = env.world.zones.index(new_zone)
        expected_position = np.zeros_like(zones_inventories, np.int32)
        new_zone_item_slot = env.world.zones_items.index(new_zone_item)
        expected_position[zone_slot, new_zone_item_slot] = 2
        wood_item_slot = env.world.zones_items.index(Item("wood"))
        expected_position[zone_slot, wood_item_slot] = 3
        check_np_equal(zones_inventories, expected_position)

    def test_observation(self):
        """observation should only show items of current zone."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        env.player_inventory[1] = 2
        start_zone_index = env.world.zones.index(self.start_zone)
        env.zones_inventories[start_zone_index, 0] = 3
        env.zones_inventories[start_zone_index, 1] = 1
        expected_observation = np.array([0, 2, 0, 0, 0, 3, 1])
        expected_observation[3 + start_zone_index] = 1
        check_np_equal(env.observation, expected_observation)

    def test_step_move(self):
        """move transformation should work correctly."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)

        start_zone_slot = env.world.slot_from_zone(self.start_zone)
        expected_positon = np.zeros(env.world.n_zones)
        expected_positon[start_zone_slot] = 1
        check_np_equal(env.position, expected_positon)
        action = self.transformations.index(
            self.named_transformations.get("move_to_other_zone")
        )
        env.step(action)
        expected_positon = np.zeros(env.world.n_zones)
        expected_positon[1 - start_zone_slot] = 1
        check_np_equal(env.position, expected_positon)

    def test_step_search(self):
        """step transformation should work correctly."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        wood_slot = env.world.items.index(Item("wood"))

        check.equal(env.player_inventory[wood_slot], 0)
        action = self.transformations.index(
            self.named_transformations.get("search_wood")
        )
        env.step(action)
        check.equal(env.player_inventory[wood_slot], 1)

    def test_step_craft(self):
        """craft transformation should work correctly."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        wood_slot = env.world.items.index(Item("wood"))
        plank_slot = env.world.items.index(Item("plank"))
        action = self.transformations.index(
            self.named_transformations.get("craft_plank")
        )

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
        """reset should reset the state."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)

        # Initialize an ongoing env
        start_zone_index = env.world.zones.index(self.start_zone)
        env.position[start_zone_index] = 0
        env.position[1 - start_zone_index] = 1
        env.player_inventory[0] = 2
        env.zones_inventories[0, 0] = 3
        env.zones_inventories[1, 1] = 4

        env.reset()
        expected_player_inventory = np.zeros(len(env.world.items), np.uint16)
        check_np_equal(env.player_inventory, expected_player_inventory)

        expected_position = np.zeros(len(env.world.zones), np.uint16)
        expected_position[start_zone_index] = 1
        check_np_equal(env.position, expected_position)

        expected_zones_inventories = np.zeros(
            (len(env.world.zones), len(env.world.zones_items)), np.uint16
        )
        check_np_equal(env.zones_inventories, expected_zones_inventories)

    def test_single_task(self):
        """task should affect the reward and environement termination."""
        task = GetItemTask(Item("wood"), reward=5)
        env = CraftingEnv(
            self.transformations, start_zone=self.start_zone, purpose=task
        )
        action = env.transformations.index(
            self.named_transformations.get("search_wood")
        )
        _, reward, done, _ = env.step(action)
        check.equal(reward, 5)
        check.is_true(done)

    def test_purpose(self):
        """multi tasks should be converted to purpose."""
        tasks = [
            GetItemTask(Item("wood"), reward=5),
            GetItemTask(Item("stone"), reward=10),
        ]
        env = CraftingEnv(
            self.transformations, start_zone=self.start_zone, purpose=tasks
        )
        action = env.transformations.index(
            self.named_transformations.get("search_wood")
        )
        _, reward, done, _ = env.step(action)
        check.equal(reward, 5)
        check.is_false(done)

        action = env.transformations.index(
            self.named_transformations.get("search_stone")
        )
        _, reward, done, _ = env.step(action)
        check.equal(reward, 10)
        check.is_true(done)

    def test_actions_mask(self):
        env = CraftingEnv(self.transformations, self.start_zone)
        check_np_equal(env.actions_mask, np.array([1, 1, 1, 0, 0, 0]))

        _, _, _, infos = env.step(
            env.transformations.index(self.named_transformations.get("search_wood"))
        )
        check_np_equal(env.actions_mask, np.array([1, 1, 1, 1, 0, 0]))
        check_np_equal(infos["action_is_legal"], np.array([1, 1, 1, 1, 0, 0]))

    def test_max_step(self):
        """max_step should truncate the episode after desired number of steps."""
        env = CraftingEnv(self.transformations, start_zone=self.start_zone, max_step=3)
        _, _, done, _ = env.step(0)
        check.is_false(done)
        check.is_false(env.truncated)
        _, _, done, _ = env.step(0)
        check.is_false(done)
        check.is_false(env.truncated)
        _, _, done, _ = env.step(0)
        check.is_true(done)
        check.is_true(env.truncated)


def test_discovered_items():
    """items should be discovered if they have been obtained anytime in this episode."""
    named_transformations, start_zone, _, _, _ = player_only_env()
    transformations = list(named_transformations.values())
    env = CraftingEnv(transformations, start_zone=start_zone)

    expected_discovered_items = np.zeros(env.world.n_items)
    check_np_equal(env.discovered_items, expected_discovered_items)
    action = env.transformations.index(named_transformations.get("search_wood"))
    _, _, _, _ = env.step(action)
    expected_discovered_items[env.world.items.index(Item("wood"))] = 1
    check_np_equal(env.discovered_items, expected_discovered_items)

    action = env.transformations.index(named_transformations.get("craft_plank"))
    _, _, _, _ = env.step(action)
    expected_discovered_items[env.world.items.index(Item("plank"))] = 1
    check_np_equal(env.discovered_items, expected_discovered_items)

    env.reset()
    expected_discovered_items = np.zeros(env.world.n_items)
    check_np_equal(env.discovered_items, expected_discovered_items)


def test_discovered_zones_items():
    """zones items should be discovered if they have been obtained anytime in this episode."""
    named_transformations, start_zone, _, _, _ = zone_only_env()
    transformations = list(named_transformations.values())
    env = CraftingEnv(transformations, start_zone=start_zone)

    expected_discovered_zones_items = np.zeros(env.world.n_zones_items)
    check_np_equal(env.discovered_zones_items, expected_discovered_zones_items)
    action = env.transformations.index(named_transformations.get("search_wood"))
    _, _, _, _ = env.step(action)
    expected_discovered_zones_items[env.world.zones_items.index(Item("wood"))] = 1
    check_np_equal(env.discovered_zones_items, expected_discovered_zones_items)

    action = env.transformations.index(named_transformations.get("craft_plank"))
    _, _, _, _ = env.step(action)
    expected_discovered_zones_items[env.world.zones_items.index(Item("plank"))] = 1
    check_np_equal(env.discovered_zones_items, expected_discovered_zones_items)

    env.reset()
    expected_discovered_items = np.zeros(env.world.n_zones_items)
    check_np_equal(env.discovered_zones_items, expected_discovered_items)


def test_discovered_zones():
    """zones should be discovered if player has been in them anytime in this episode."""
    named_transformations, start_zone, _, _, _ = classic_env()
    transformations = list(named_transformations.values())
    env = CraftingEnv(transformations, start_zone=start_zone)

    expected_discovered_zones = np.zeros(env.world.n_zones)
    expected_discovered_zones[env.world.zones.index(Zone("start"))] = 1
    check_np_equal(env.discovered_zones, expected_discovered_zones)

    action = env.transformations.index(named_transformations.get("move_to_other_zone"))
    _, _, _, _ = env.step(action)
    expected_discovered_zones[env.world.zones.index(Zone("other_zone"))] = 1
    check_np_equal(env.discovered_zones, expected_discovered_zones)

    env.reset()
    expected_discovered_zones = np.zeros(env.world.n_zones)
    expected_discovered_zones[env.world.zones.index(Zone("start"))] = 1
    check_np_equal(env.discovered_zones, expected_discovered_zones)


def test_discovered_transformations():
    named_transformations, start_zone, _, _, _ = classic_env()
    transformations = list(named_transformations.values())
    env = CraftingEnv(transformations, start_zone=start_zone)

    expected_discovered_transformations = np.zeros(len(env.transformations))
    check_np_equal(env.discovered_transformations, expected_discovered_transformations)

    action = env.transformations.index(named_transformations.get("move_to_other_zone"))
    _, _, _, _ = env.step(action)
    expected_discovered_transformations[action] = 1
    check_np_equal(env.discovered_transformations, expected_discovered_transformations)

    action = env.transformations.index(named_transformations.get("search_wood"))
    _, _, _, _ = env.step(action)
    expected_discovered_transformations[action] = 1
    check_np_equal(env.discovered_transformations, expected_discovered_transformations)

    env.reset()
    expected_discovered_transformations = np.zeros(len(env.transformations))
    check_np_equal(env.discovered_transformations, expected_discovered_transformations)


def test_observation_no_zone_no_zone_items():
    """observation should only show player items if no zone and no zone_items."""
    names_transformations, _, _, _, _ = player_only_env()
    transformations = list(names_transformations.values())
    env = CraftingEnv(transformations)
    check.equal(env.observation.shape, (env.world.n_items,))


def test_observation_one_zone_no_player_items():
    """observation should only show zone items if one zone and no player items."""
    names_transformations, start_zone, _, _, _ = zone_only_env()
    transformations = list(names_transformations.values())
    env = CraftingEnv(transformations, start_zone=start_zone)
    check.equal(env.observation.shape, (env.world.n_zones + env.world.n_zones_items,))
