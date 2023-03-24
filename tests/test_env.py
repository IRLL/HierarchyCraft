from typing import List

import numpy as np
import pytest
import pytest_check as check
from pytest_mock import MockerFixture

from hcraft.elements import Item, Stack, Zone
from hcraft.env import HcraftEnv
from hcraft.task import GetItemTask
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE
from hcraft.world import world_from_transformations
from tests.custom_checks import check_np_equal
from tests.envs import classic_env, player_only_env, zone_only_env


class TestCratingEnv:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        (
            self.env,
            self.world,
            self.named_transformations,
            self.start_zone,
            self.items,
            self.zones,
            self.zones_items,
        ) = classic_env()
        self.transformations: List[Transformation] = list(
            self.named_transformations.values()
        )
        self.env.reset()

    def test_world_initialisation(self):
        """should find all items, zones and zones_items in transformations."""
        check.equal(set(self.env.world.zones), set(self.zones))
        check.equal(set(self.env.world.items), set(self.items))
        check.equal(set(self.env.world.zones_items), set(self.zones_items))

    def test_state_initialisation(self):
        """should initialize the state as expected."""
        expected_player_inventory = np.zeros(len(self.items), np.int32)
        check_np_equal(self.env.state.player_inventory, expected_player_inventory)

        expected_position = np.zeros(len(self.zones), np.int32)
        start_zone_slot = self.env.world.zones.index(self.start_zone)
        expected_position[start_zone_slot] = 1
        check_np_equal(self.env.state.position, expected_position)

        expected_zones_inventories = np.zeros(
            (len(self.zones), len(self.zones_items)), np.int32
        )
        check_np_equal(self.env.state.zones_inventories, expected_zones_inventories)

    def test_start_zone(self):
        """position should be in start zone at initialization if given,
        even if zone is not in transformations."""
        new_start_zone = Zone("new_start_zone")
        world = world_from_transformations(
            self.transformations, start_zone=new_start_zone
        )
        env = HcraftEnv(world)
        expected_position = np.zeros(len(env.world.zones), np.int32)
        expected_position[env.world.zones.index(new_start_zone)] = 1
        check_np_equal(env.state.position, expected_position)

    def test_start_items(self):
        """player inventory should be filled with start_items at initialization if given,
        even if items are not in any transformations."""
        start_item = Item("start_item")
        world = world_from_transformations(
            self.transformations,
            start_zone=self.start_zone,
            start_items=[Stack(start_item, 2), Stack(Item("wood"), 3)],
        )
        env = HcraftEnv(world)
        expected_items = np.zeros(env.world.n_items, np.int32)
        expected_items[env.world.items.index(start_item)] = 2
        expected_items[env.world.items.index(Item("wood"))] = 3
        check_np_equal(env.state.player_inventory, expected_items)

    def test_start_zones_items(self):
        """zones inventories should be filled with start_zones_items at initialization if given,
        even if items and zones are not in any transformations."""
        new_zone = Zone("new_zone")
        new_zone_item = Item("new_zone_item")
        world = world_from_transformations(
            self.transformations,
            start_zone=self.start_zone,
            start_zones_items={
                new_zone: [Stack(new_zone_item, 2), Stack(Item("wood"), 3)],
            },
        )
        env = HcraftEnv(world)
        zone_slot = env.world.zones.index(new_zone)
        expected_position = np.zeros_like(env.state.zones_inventories, np.int32)
        new_zone_item_slot = env.world.zones_items.index(new_zone_item)
        expected_position[zone_slot, new_zone_item_slot] = 2
        wood_item_slot = env.world.zones_items.index(Item("wood"))
        expected_position[zone_slot, wood_item_slot] = 3
        check_np_equal(env.state.zones_inventories, expected_position)

    def test_observation(self):
        """observation should only show items of current zone."""
        self.env.state.player_inventory[1] = 2
        start_zone_index = self.env.world.zones.index(self.start_zone)
        self.env.state.zones_inventories[start_zone_index, 0] = 3
        self.env.state.zones_inventories[start_zone_index, 1] = 1
        expected_observation = np.array([0, 2, 0, 0, 0, 3, 1])
        expected_observation[3 + start_zone_index] = 1
        check_np_equal(self.env.state.observation, expected_observation)

    def test_step_move(self):
        """move transformation should work correctly."""
        start_zone_slot = self.env.world.slot_from_zone(self.start_zone)
        expected_positon = np.zeros(self.env.world.n_zones)
        expected_positon[start_zone_slot] = 1
        check_np_equal(self.env.state.position, expected_positon)
        action = self.transformations.index(
            self.named_transformations.get("move_to_other_zone")
        )
        self.env.step(action)
        expected_positon = np.zeros(self.env.world.n_zones)
        expected_positon[1 - start_zone_slot] = 1
        check_np_equal(self.env.state.position, expected_positon)

    def test_step_search(self):
        """step transformation should work correctly."""
        wood_slot = self.env.world.items.index(Item("wood"))

        check.equal(self.env.state.player_inventory[wood_slot], 0)
        action = self.transformations.index(
            self.named_transformations.get("search_wood")
        )
        self.env.step(action)
        check.equal(self.env.state.player_inventory[wood_slot], 1)

    def test_step_craft(self):
        """craft transformation should work correctly."""
        wood_slot = self.env.world.items.index(Item("wood"))
        plank_slot = self.env.world.items.index(Item("plank"))
        action = self.transformations.index(
            self.named_transformations.get("craft_plank")
        )

        # Invalid craft does not change state
        self.env.step(action)
        check.equal(self.env.state.player_inventory[wood_slot], 0)
        check.equal(self.env.state.player_inventory[plank_slot], 0)

        # Valid craft does change state
        self.env.state.player_inventory[wood_slot] = 1
        self.env.step(action)
        check.equal(self.env.state.player_inventory[wood_slot], 0)
        check.equal(self.env.state.player_inventory[plank_slot], 4)

    def test_reset(self):
        """reset should reset the state."""
        # Initialize an ongoing env
        start_zone_index = self.env.world.zones.index(self.start_zone)
        self.env.state.position[start_zone_index] = 0
        self.env.state.position[1 - start_zone_index] = 1
        self.env.state.player_inventory[0] = 2
        self.env.state.zones_inventories[0, 0] = 3
        self.env.state.zones_inventories[1, 1] = 4

        observation = self.env.reset()
        check.greater(observation.shape[0], 0)
        expected_player_inventory = np.zeros(len(self.env.world.items), np.int32)
        check_np_equal(self.env.state.player_inventory, expected_player_inventory)

        expected_position = np.zeros(len(self.env.world.zones), np.int32)
        expected_position[start_zone_index] = 1
        check_np_equal(self.env.state.position, expected_position)

        expected_zones_inventories = np.zeros(
            (len(self.env.world.zones), len(self.env.world.zones_items)), np.int32
        )
        check_np_equal(self.env.state.zones_inventories, expected_zones_inventories)

    def test_single_task(self):
        """task should affect the reward and environement termination."""
        task = GetItemTask(Item("wood"), reward=5)
        env = HcraftEnv(self.world, purpose=task)
        env.reset()
        action = env.world.transformations.index(
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
        env = HcraftEnv(self.world, purpose=tasks)
        env.reset()
        action = env.world.transformations.index(
            self.named_transformations.get("search_wood")
        )
        _, reward, done, _ = env.step(action)
        check.equal(reward, 5)
        check.is_false(done)

        action = env.world.transformations.index(
            self.named_transformations.get("search_stone")
        )
        _, reward, done, _ = env.step(action)
        check.equal(reward, 10)
        check.is_true(done)

    def test_actions_mask(self):
        check_np_equal(self.env.action_masks(), np.array([1, 1, 1, 0, 0, 0]))

        _, _, _, infos = self.env.step(
            self.env.world.transformations.index(
                self.named_transformations.get("search_wood")
            )
        )
        check_np_equal(self.env.action_masks(), np.array([1, 1, 1, 1, 0, 0]))
        check_np_equal(infos["action_is_legal"], np.array([1, 1, 1, 1, 0, 0]))

    def test_max_step(self):
        """max_step should truncate the episode after desired number of steps."""
        env = HcraftEnv(self.world, max_step=3)
        env.reset()
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
    env, _, named_transformations = player_only_env()[:3]
    env.reset()

    expected_discovered_items = np.zeros(env.world.n_items)
    check_np_equal(env.state.discovered_items, expected_discovered_items)
    action = env.world.transformations.index(named_transformations.get("search_wood"))
    _, _, _, _ = env.step(action)
    expected_discovered_items[env.world.items.index(Item("wood"))] = 1
    check_np_equal(env.state.discovered_items, expected_discovered_items)

    action = env.world.transformations.index(named_transformations.get("craft_plank"))
    _, _, _, _ = env.step(action)
    expected_discovered_items[env.world.items.index(Item("plank"))] = 1
    check_np_equal(env.state.discovered_items, expected_discovered_items)

    env.reset()
    expected_discovered_items = np.zeros(env.world.n_items)
    check_np_equal(env.state.discovered_items, expected_discovered_items)


def test_discovered_zones_items():
    """zones items should be discovered if they have been obtained anytime in this episode."""
    env, _, named_transformations = zone_only_env()[:3]
    env.reset()

    expected_discovered_zones_items = np.zeros(env.world.n_zones_items)
    check_np_equal(env.state.discovered_zones_items, expected_discovered_zones_items)
    action = env.world.transformations.index(named_transformations.get("search_wood"))
    _, _, _, _ = env.step(action)
    expected_discovered_zones_items[env.world.zones_items.index(Item("wood"))] = 1
    check_np_equal(env.state.discovered_zones_items, expected_discovered_zones_items)

    action = env.world.transformations.index(named_transformations.get("craft_plank"))
    _, _, _, _ = env.step(action)
    expected_discovered_zones_items[env.world.zones_items.index(Item("plank"))] = 1
    check_np_equal(env.state.discovered_zones_items, expected_discovered_zones_items)

    env.reset()
    expected_discovered_items = np.zeros(env.world.n_zones_items)
    check_np_equal(env.state.discovered_zones_items, expected_discovered_items)


def test_discovered_zones():
    """zones should be discovered if player has been in them anytime in this episode."""
    env, _, named_transformations = classic_env()[:3]
    env.reset()

    expected_discovered_zones = np.zeros(env.world.n_zones)
    expected_discovered_zones[env.world.zones.index(Zone("start"))] = 1
    check_np_equal(env.state.discovered_zones, expected_discovered_zones)

    action = env.world.transformations.index(
        named_transformations.get("move_to_other_zone")
    )
    _, _, _, _ = env.step(action)
    expected_discovered_zones[env.world.zones.index(Zone("other_zone"))] = 1
    check_np_equal(env.state.discovered_zones, expected_discovered_zones)

    env.reset()
    expected_discovered_zones = np.zeros(env.world.n_zones)
    expected_discovered_zones[env.world.zones.index(Zone("start"))] = 1
    check_np_equal(env.state.discovered_zones, expected_discovered_zones)


def test_discovered_transformations():
    """transformation should be discovered if player has applied it anytime in the episode."""
    env, _, named_transformations = classic_env()[:3]
    env.reset()

    expected_discovered_transformations = np.zeros(len(env.world.transformations))
    check_np_equal(
        env.state.discovered_transformations, expected_discovered_transformations
    )

    action = env.world.transformations.index(
        named_transformations.get("move_to_other_zone")
    )
    _, _, _, _ = env.step(action)
    expected_discovered_transformations[action] = 1
    check_np_equal(
        env.state.discovered_transformations, expected_discovered_transformations
    )

    action = env.world.transformations.index(named_transformations.get("search_wood"))
    _, _, _, _ = env.step(action)
    expected_discovered_transformations[action] = 1
    check_np_equal(
        env.state.discovered_transformations, expected_discovered_transformations
    )

    env.reset()
    expected_discovered_transformations = np.zeros(len(env.world.transformations))
    check_np_equal(
        env.state.discovered_transformations, expected_discovered_transformations
    )


def test_observation_no_zone_no_zone_items():
    """observation should only show player items if no zone and no zone_items."""
    env = player_only_env()[0]
    env.reset()
    check.equal(env.state.observation.shape, (env.world.n_items,))


def test_observation_one_zone_no_player_items():
    """observation should only show zone items if one zone and no player items."""
    env = zone_only_env()[0]
    env.reset()
    check.equal(
        env.state.observation.shape, (env.world.n_zones + env.world.n_zones_items,)
    )


def test_treasure_env(mocker: MockerFixture):
    """Ensure that the example environment from the documenation is working properly."""
    pytest.importorskip("pygame")
    pytest.importorskip("pygame_menu")

    HUMAN_ACTIONS = [0]

    def fake_human_action(*args, **kwargs):
        return HUMAN_ACTIONS.pop(0)

    mocker.patch("hcraft.render.human.get_human_action", fake_human_action)

    from hcraft.elements import Item

    CHEST = Item("treasure_chest")
    GOLD = Item("gold")

    from hcraft.transformation import Transformation

    TAKE_GOLD_FROM_CHEST = Transformation(
        inventory_changes=[
            Use(CURRENT_ZONE, CHEST),
            Yield(PLAYER, GOLD),
        ]
    )

    from hcraft.elements import Zone

    TREASURE_ROOM = Zone("treasure_room")

    from hcraft.world import world_from_transformations

    WORLD = world_from_transformations(
        transformations=[TAKE_GOLD_FROM_CHEST],
        start_zone=TREASURE_ROOM,
        start_zones_items={TREASURE_ROOM: [CHEST]},
    )

    from hcraft.env import HcraftEnv
    from hcraft.purpose import GetItemTask

    get_gold_task = GetItemTask(GOLD)
    env = HcraftEnv(WORLD, purpose=get_gold_task)

    from hcraft.render.human import render_env_with_human

    render_env_with_human(env)

    KEY = Item("key")
    KEY_ROOM = Zone("key_room")
    START_ROOM = Zone("start_room")

    SEARCH_KEY = Transformation(
        inventory_changes=[
            Yield(PLAYER, KEY, max=1),
        ],
        zones=[KEY_ROOM],
    )

    LOCKED_CHEST = Item("locked_chest")
    UNLOCK_CHEST = Transformation(
        inventory_changes=[
            Use(PLAYER, KEY, 2),
            Use(CURRENT_ZONE, LOCKED_CHEST, consume=1),
            Yield(CURRENT_ZONE, CHEST),
        ],
    )

    MOVE_TO_KEY_ROOM = Transformation(
        destination=KEY_ROOM,
        zones=[START_ROOM],
    )
    MOVE_TO_TREASURE_ROOM = Transformation(
        destination=TREASURE_ROOM,
        zones=[START_ROOM],
    )
    MOVE_TO_START_ROOM = Transformation(
        destination=START_ROOM,
    )

    WORLD_2 = world_from_transformations(
        transformations=[
            TAKE_GOLD_FROM_CHEST,
            SEARCH_KEY,
            UNLOCK_CHEST,
            MOVE_TO_KEY_ROOM,
            MOVE_TO_TREASURE_ROOM,
            MOVE_TO_START_ROOM,
        ],
        start_zone=START_ROOM,
        start_zones_items={TREASURE_ROOM: [LOCKED_CHEST]},
    )
    env = HcraftEnv(WORLD_2, purpose=get_gold_task, max_step=7)

    HUMAN_ACTIONS = [3, 1, 1, 5, 4, 2, 0]
    render_env_with_human(env)
    check.is_true(env.purpose.terminal_groups[0].terminated)

    import os

    import hcraft

    treasure_path = os.path.dirname(hcraft.__file__)
    resources_path = os.path.join(treasure_path, "examples", "treasure", "resources")
    WORLD_2.resources_path = resources_path
    env = HcraftEnv(WORLD_2, purpose=get_gold_task, max_step=7)
    HUMAN_ACTIONS = [3, 1, 1, 5, 4, 2, 0]
    render_env_with_human(env)
    check.is_true(env.purpose.terminal_groups[0].terminated)


def test_class_tresure_env(mocker: MockerFixture):
    pytest.importorskip("pygame")
    pytest.importorskip("pygame_menu")

    def fake_human_action(*args, **kwargs):
        return 0

    mocker.patch("hcraft.render.human.get_human_action", fake_human_action)

    from hcraft.examples.treasure import TreasureEnv
    from hcraft.render.human import render_env_with_human

    env = TreasureEnv(max_step=10)
    render_env_with_human(env)
