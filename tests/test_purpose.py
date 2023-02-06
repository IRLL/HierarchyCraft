from typing import List

import pytest
import pytest_check as check

import numpy as np

from crafting.env import CraftingEnv
from crafting.world import World, ItemStack, Item
from crafting.purpose import Purpose, RewardShaping
from crafting.task import Task, GetItemTask
from crafting.transformation import Transformation


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
        self.env = CraftingEnv([])

    def test_build(self):
        self.purpose.build(self.env)
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
        self.env = CraftingEnv([])

    def test_build(self):
        self.purpose.build(self.env)
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

    def test_add_task_with_default_reward_shaping(self):
        purpose = Purpose()
        purpose.add_task(self.go_to_0)
        check.equal(purpose.reward_shaping[self.go_to_0], RewardShaping.NONE)

    def test_add_task_with_specific_reward_shaping(self):
        purpose = Purpose()
        purpose.add_task(self.go_to_0, "required")
        check.equal(
            purpose.reward_shaping[self.go_to_0], RewardShaping.REQUIRED_ACHIVEMENTS
        )


class TestPurposeRewardShaping:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.items = [Item(str(i)) for i in range(4)]
        # Item 0
        search_0 = Transformation(added_player_items=[self.items[0]])
        # Item 0 > Item 1
        craft_1 = Transformation(
            removed_player_items=[self.items[0]],
            added_player_items=[self.items[1]],
        )
        # Item 1 > Item 2
        craft_2 = Transformation(
            removed_player_items=[self.items[1]],
            added_player_items=[self.items[2]],
        )
        # Item 2 > 2 * Item 2
        craft_2_with_2 = Transformation(
            removed_player_items=[self.items[2]],
            added_player_items=[ItemStack(self.items[2], 2)],
        )
        # Item 3
        search_3 = Transformation(added_player_items=[self.items[3]])

        self.get_item_2 = GetItemTask(self.items[2], reward=10.0)
        self.env = CraftingEnv(
            transformations=[search_0, craft_1, craft_2, craft_2_with_2, search_3]
        )

    def test_no_reward_shaping(self):
        purpose = Purpose()
        purpose.add_task(self.get_item_2, RewardShaping.NONE)
        check.equal(purpose.tasks, [self.get_item_2])

    def test_all_achievements_shaping(self):
        purpose = Purpose()
        purpose.add_task(self.get_item_2, reward_shaping=RewardShaping.ALL_ACHIVEMENTS)
        purpose.build(self.env)
        self._check_get_item_task(self.items, purpose=purpose)

    def test_inputs_achivements_shaping(self):
        purpose = Purpose()
        purpose.add_task(
            self.get_item_2,
            reward_shaping=RewardShaping.INPUTS_ACHIVEMENT,
        )
        purpose.build(self.env)
        self._check_get_item_task([self.items[1]], purpose=purpose)

    def test_requires_achivements_shaping(self):
        purpose = Purpose()
        purpose.add_task(
            self.get_item_2,
            reward_shaping=RewardShaping.REQUIRED_ACHIVEMENTS,
        )
        purpose.build(self.env)
        self._check_get_item_task(self.items[:2], purpose=purpose)

    @staticmethod
    def _check_get_item_task(items: List[Item], purpose: Purpose):
        all_items_stacks = [ItemStack(item) for item in items]
        expected_task_names = ["Get 2"] + [
            GetItemTask.get_name(item_stack) for item_stack in all_items_stacks
        ]
        task_names = [task.name for task in purpose.tasks]
        check.equal(sorted(task_names), sorted(expected_task_names))
