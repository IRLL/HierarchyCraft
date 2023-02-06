import pytest
import pytest_check as check

import numpy as np

from crafting.world import World, Zone, Item
from crafting.purpose import Purpose, RewardShaping
from crafting.task import Task


class TestNoPurpose:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.purpose = Purpose(None)

    def test_reward(self):
        reward = self.purpose.reward(None, None, None)
        check.equal(reward, 0)

    def test_is_terminal(self):
        check.is_false(self.purpose.is_terminal(None, None, None))


def test_time_penalty():
    purpose = Purpose(None, timestep_reward=-1)
    check.equal(purpose.reward(None, None, None), -1)


class DummyPosEqualTask(Task):
    def __init__(self, reward, goal_position) -> None:
        self.is_built = False
        self._reward = reward
        self.goal_position = goal_position

    def reward(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> float:
        if position == self.goal_position:
            return self._reward
        return 0.0

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return position == self.goal_position

    def build(self, world: World) -> None:
        self.is_built = True


class TestPurposeSingleTask:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.go_to_1 = DummyPosEqualTask(reward=5, goal_position=1)
        self.purpose = Purpose(self.go_to_1)

    def test_build(self):
        self.purpose.build(world=None)
        check.is_true(self.go_to_1.is_built)

    def test_reward(self):
        check.equal(self.purpose.reward(None, 0, None), 0)
        check.equal(self.purpose.reward(None, 1, None), 5)

    def test_is_terminal(self):
        check.is_false(self.purpose.is_terminal(None, 0, None))
        check.is_true(self.purpose.is_terminal(None, 1, None))


class TestPurposeMultiTasks:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.go_to_0 = DummyPosEqualTask(reward=10, goal_position=0)
        self.go_to_1 = DummyPosEqualTask(reward=5, goal_position=1)
        self.purpose = Purpose([self.go_to_0, self.go_to_1])

    def test_build(self):
        self.purpose.build(world=None)
        for task in [self.go_to_0, self.go_to_1]:
            check.is_true(task.is_built)

    def test_reward(self):
        check.equal(self.purpose.reward(None, 0, None), 10)
        check.equal(self.purpose.reward(None, 1, None), 5)
        check.equal(self.purpose.reward(None, 2, None), 0)

    def test_is_terminal_all(self):
        check.is_false(self.purpose.is_terminal(None, 2, None))
        check.is_false(self.purpose.is_terminal(None, 0, None))  # Task 0 ends
        check.is_true(self.purpose.is_terminal(None, 1, None))  # Task 1 ends

    def test_add_task_with_reward_shaping(self):
        purpose = Purpose()
        purpose.add_task(self.go_to_0)
        check.equal(purpose.reward_shaping[self.go_to_0], RewardShaping.NONE)
