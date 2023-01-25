import pytest
import pytest_check as check

import numpy as np

from crafting.world import World, Zone, Item
from crafting.purpose import Purpose
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


class DummyTask(Task):
    def __init__(self, reward) -> None:
        self.is_built = False
        self._reward = reward

    def reward(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> float:
        return self._reward

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return position == 1

    def build(self, world: World) -> None:
        self.is_built = True


class TestPurposeSingleTask:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.get_wood = DummyTask(reward=5)
        self.purpose = Purpose(self.get_wood)

    def test_build(self):
        self.purpose.build(world=None)
        check.is_true(self.get_wood.is_built)

    def test_reward(self):
        reward = self.purpose.reward(None, None, None)
        check.equal(reward, 5)

    def test_is_terminal(self):
        check.is_false(self.purpose.is_terminal(None, 0, None))
        check.is_true(self.purpose.is_terminal(None, 1, None))
