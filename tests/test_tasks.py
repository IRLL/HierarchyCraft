from dataclasses import dataclass
from typing import Any

import numpy as np
import pytest
import pytest_check as check

from hcraft.elements import Item, Stack, Zone
from hcraft.task import GetItemTask, GoToZoneTask, PlaceItemTask
from hcraft.world import World
from tests.custom_checks import check_np_equal


@dataclass
class DummyState:
    player_inventory: Any = None
    position: Any = None
    zones_inventories: Any = None


def simple_world() -> World:
    return World(
        items=[Item("dirt"), Item("wood"), Item("stone"), Item("plank")],
        zones=[Zone("start"), Zone("other_zone")],
        zones_items=[Item("dirt"), Item("table"), Item("wood_house")],
        transformations=[],
    )


class TestGetItem:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world = simple_world()
        self.task = GetItemTask(Stack(Item("wood"), 3), reward=5)

    def test_build(self):
        """should build expected operations arrays based on the given world."""
        self.task.build(self.world)
        check_np_equal(self.task._terminate_player_items, np.array([0, 3, 0, 0]))

    def test_build_with_item_only(self):
        """should build even if the item is given without a stack."""
        task = GetItemTask(Item("wood"), reward=5)
        task.build(self.world)
        check_np_equal(task._terminate_player_items, np.array([0, 1, 0, 0]))

    def test_terminate(self):
        """should terminate only when the player has more than wanted items."""
        self.task.build(self.world)

        state = DummyState(player_inventory=np.array([10, 2, 10, 10]))
        check.is_false(self.task.is_terminal(state))
        state = DummyState(player_inventory=np.array([0, 3, 0, 0]))
        check.is_true(self.task.is_terminal(state))
        state = DummyState(player_inventory=np.array([0, 4, 0, 0]))
        check.is_true(self.task.is_terminal(state))

    def test_reward(self):
        """should reward only the first time the task terminates."""
        self.task.build(self.world)

        state = DummyState(player_inventory=np.array([10, 2, 10, 10]))
        check.equal(self.task.reward(state), 0)
        state = DummyState(player_inventory=np.array([0, 4, 0, 0]))
        check.equal(self.task.reward(state), 5)
        self.task.terminated = True
        check.equal(self.task.reward(state), 0)


class TestGoToZone:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world = simple_world()
        self.task = GoToZoneTask(Zone("other_zone"), reward=5)

    def test_build(self):
        """should build expected operations arrays based on the given world."""
        self.task.build(self.world)
        check_np_equal(self.task._terminate_position, np.array([0, 1]))

    def test_terminate(self):
        """should terminate only when the player is in the zone"""
        self.task.build(self.world)

        state = DummyState(position=np.array([1, 0]))
        check.is_false(self.task.is_terminal(state))
        state = DummyState(position=np.array([0, 1]))
        check.is_true(self.task.is_terminal(state))

    def test_reward(self):
        """should reward only the first time the task terminates."""
        self.task.build(self.world)

        state = DummyState(position=np.array([1, 0]))
        check.equal(self.task.reward(state), 0)
        state = DummyState(position=np.array([0, 1]))
        check.equal(self.task.reward(state), 5)
        self.task.terminated = True
        check.equal(self.task.reward(state), 0)


class TestPlaceItem:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world = simple_world()
        self.task = PlaceItemTask(
            Stack(Item("wood_house"), 2), Zone("other_zone"), reward=5
        )

    def test_build(self):
        """should build expected operations arrays based on the given world."""
        self.task.build(self.world)
        expected_op = np.array([[0, 0, 0], [0, 0, 2]])
        check_np_equal(self.task._terminate_zones_items, expected_op)

    def test_build_with_item_only(self):
        """should build even if the item is given without a stack."""
        task = PlaceItemTask(Item("wood_house"), Zone("other_zone"), reward=5)
        task.build(self.world)
        expected_op = np.array([[0, 0, 0], [0, 0, 1]])
        check_np_equal(task._terminate_zones_items, expected_op)

    def test_build_no_zone(self):
        """should consider any zone if none is given."""
        task = PlaceItemTask(Stack(Item("wood_house"), 2), None, reward=5)
        task.build(self.world)
        expected_op = np.array([[0, 0, 2], [0, 0, 2]])
        check_np_equal(task._terminate_zones_items, expected_op)

    def test_build_any_zones(self):
        """should consider any of given zones if multiple are given."""
        task = PlaceItemTask(
            Stack(Item("wood_house"), 2),
            [Zone("start"), Zone("other_zone")],
            reward=5,
        )
        task.build(self.world)
        expected_op = np.array([[0, 0, 2], [0, 0, 2]])
        check_np_equal(task._terminate_zones_items, expected_op)

    def test_terminate_specific_zone(self):
        """should terminate only when the given zone has more than wanted items."""
        self.task.build(self.world)

        state = DummyState(zones_inventories=np.array([[10, 10, 10], [10, 10, 0]]))
        check.is_false(self.task.is_terminal(state))
        state = DummyState(zones_inventories=np.array([[0, 0, 0], [0, 0, 2]]))
        check.is_true(self.task.is_terminal(state))

    def test_terminate_any_zone(self):
        """should terminate when any zone has more than wanted items."""
        task = PlaceItemTask(Stack(Item("wood_house"), 2), reward=5)
        task.build(self.world)

        state = DummyState(zones_inventories=np.array([[10, 10, 0], [10, 10, 0]]))
        check.is_false(task.is_terminal(state))
        state = DummyState(zones_inventories=np.array([[0, 0, 0], [0, 0, 2]]))
        check.is_true(task.is_terminal(state))
        state = DummyState(zones_inventories=np.array([[0, 0, 2], [0, 0, 0]]))
        check.is_true(task.is_terminal(state))

    def test_reward(self):
        """should reward only the first time the task terminates."""
        self.task.build(self.world)

        state = DummyState(zones_inventories=np.array([[10, 10, 10], [10, 10, 0]]))
        check.equal(self.task.reward(state), 0)
        state = DummyState(zones_inventories=np.array([[0, 0, 0], [0, 0, 2]]))
        check.equal(self.task.reward(state), 5)
        self.task.terminated = True
        check.equal(self.task.reward(state), 0)
