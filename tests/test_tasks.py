import pytest
import pytest_check as check
import numpy as np

from crafting.world import ItemStack, Item, Zone, World
from crafting.task import GoToZoneTask, GetItemTask, PlaceItemTask

from tests.check_array import check_np_equal


class TestGetItem:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world = World(
            items=[Item("dirt"), Item("wood"), Item("stone"), Item("plank")],
            zones=[Zone("start"), Zone("other_zone")],
            zones_items=[Item("dirt"), Item("table"), Item("wood_house")],
        )
        self.task = GetItemTask(ItemStack(Item("wood"), 3), reward=5)

    def test_build(self):
        """should build expected operations arrays based on the given world."""
        self.task.build(self.world)
        check_np_equal(self.task._terminate_player_items, np.array([0, 3, 0, 0]))

    def test_terminate(self):
        """should terminate only when the player has more than wanted items."""
        self.task.build(self.world)

        state = np.array([10, 2, 10, 10]), None, None
        check.is_false(self.task.is_terminal(*state))
        state = np.array([0, 3, 0, 0]), None, None
        check.is_true(self.task.is_terminal(*state))
        state = np.array([0, 4, 0, 0]), None, None
        check.is_true(self.task.is_terminal(*state))

    def test_reward(self):
        """should reward only the first time the task terminates."""
        self.task.build(self.world)

        state = np.array([10, 2, 10, 10]), None, None
        check.equal(self.task.reward(*state), 0)
        state = np.array([0, 4, 0, 0]), None, None
        check.equal(self.task.reward(*state), 5)
        check.equal(self.task.reward(*state), 0)


class TestGoToZone:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world = World(
            items=[Item("dirt"), Item("wood"), Item("stone"), Item("plank")],
            zones=[Zone("start"), Zone("other_zone")],
            zones_items=[Item("dirt"), Item("table"), Item("wood_house")],
        )
        self.task = GoToZoneTask(Zone("other_zone"), reward=5)

    def test_build(self):
        """should build expected operations arrays based on the given world."""
        self.task.build(self.world)
        check_np_equal(self.task._terminate_position, np.array([0, 1]))

    def test_terminate(self):
        """should terminate only when the player is in the zone"""
        self.task.build(self.world)

        state = None, np.array([1, 0]), None
        check.is_false(self.task.is_terminal(*state))
        state = None, np.array([0, 1]), None
        check.is_true(self.task.is_terminal(*state))

    def test_reward(self):
        """should reward only the first time the task terminates."""
        self.task.build(self.world)

        state = None, np.array([1, 0]), None
        check.equal(self.task.reward(*state), 0)
        state = None, np.array([0, 1]), None
        check.equal(self.task.reward(*state), 5)
        check.equal(self.task.reward(*state), 0)


class TestPlaceItem:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world = World(
            items=[Item("dirt"), Item("wood"), Item("stone"), Item("plank")],
            zones=[Zone("start"), Zone("other_zone")],
            zones_items=[Item("dirt"), Item("table"), Item("wood_house")],
        )
        self.task = PlaceItemTask(
            ItemStack(Item("wood_house"), 2), Zone("other_zone"), reward=5
        )

    def test_build(self):
        """should build expected operations arrays based on the given world."""
        self.task.build(self.world)
        expected_op = np.array([[0, 0, 0], [0, 0, 2]])
        check_np_equal(self.task._terminate_zones_items, expected_op)

    def test_terminate(self):
        """should terminate only when the given zone has more than wanted items."""
        self.task.build(self.world)

        state = None, None, np.array([[10, 10, 10], [10, 10, 0]])
        check.is_false(self.task.is_terminal(*state))
        state = None, None, np.array([[0, 0, 0], [0, 0, 2]])
        check.is_true(self.task.is_terminal(*state))
        state = None, None, np.array([[0, 0, 0], [0, 0, 3]])
        check.is_true(self.task.is_terminal(*state))

    def test_reward(self):
        """should reward only the first time the task terminates."""
        self.task.build(self.world)

        state = None, None, np.array([[10, 10, 10], [10, 10, 0]])
        check.equal(self.task.reward(*state), 0)
        state = None, None, np.array([[0, 0, 0], [0, 0, 2]])
        check.equal(self.task.reward(*state), 5)
        check.equal(self.task.reward(*state), 0)
