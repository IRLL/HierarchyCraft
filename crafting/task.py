# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=unused-argument, no-self-use

""" Task to defines objectives """

from typing import TYPE_CHECKING, List, Union, Dict
from enum import Enum

import numpy as np

from crafting.options.utils import get_items_in_graph

if TYPE_CHECKING:
    from crafting.world.world import World
    from crafting.world.items import Item


class Task:

    """Abstract class for any task"""

    def __init__(self, name, world: "World"):
        self.name = name
        self.world = world

        self.achievements_items_values = np.zeros(self.world.n_items)
        self.achievements_items_done = np.zeros(self.world.n_items, dtype=bool)

        self.items_values = np.zeros(self.world.n_items)
        self.action_values = np.zeros(self.world.n_actions)

        self.items_end_task_at = np.inf * np.ones(self.world.n_items, dtype=np.int32)
        self.action_end_task = np.zeros(self.world.n_actions, dtype=bool)

        self.reset()

    def add_achivement_getitem(self, item_id, value, end_task=False):
        """Makes getting `item_id` for the first time an achievement with reward `value`."""
        item_slot = self.world.item_id_to_slot[item_id]
        self.achievements_items_values[item_slot] += value
        if end_task:
            self.items_end_task_at[item_slot] = 1

    def add_item_value(self, item_id, value, end_task_at=None):
        """Attributes a reward `value` for each unit of the item `item_id`."""
        item_slot = self.world.item_id_to_slot[item_id]
        self.items_values[item_slot] += value
        if end_task_at is not None:
            self.items_end_task_at[item_slot] = end_task_at

    def reward(self, observation, previous_observation, action):
        """Attribute a reward to the current transition"""
        diff_items = (
            observation[: self.world.n_items]
            - previous_observation[: self.world.n_items]
        )

        achived_items = np.logical_and(
            np.logical_not(self.achievements_items_done),
            observation[: self.world.n_items] > 0,
        )

        reward = np.sum(achived_items * self.achievements_items_values)
        reward += np.sum(diff_items * self.items_values)
        reward += self.action_values[action]

        self.achievements_items_done = np.logical_or(
            observation[: self.world.n_items] > 0, self.achievements_items_done
        )

        return reward

    def done(self, observation, previous_observation, action):
        """Return True if the task is done, used for early stopping"""
        item_done = np.any(observation[: self.world.n_items] >= self.items_end_task_at)
        action_done = self.action_end_task[action]
        return item_done or action_done

    def reset(self):
        """Reset the task."""
        self.achievements_items_done = np.zeros(self.world.n_items, dtype=bool)

    def __call__(self, observation, previous_observation, action):
        reward = self.reward(observation, previous_observation, action)
        done = self.done(observation, previous_observation, action)
        return reward, done

    def __repr__(self) -> str:
        return self.name


class TaskList:

    """Wrapper for a list of tasks"""

    def __init__(
        self,
        tasks: List[Task],
        tasks_weights: Union[List[float], Dict[str, float]] = None,
        tasks_can_end: Union[List[bool], Dict[str, bool]] = None,
        early_stopping: str = "all",
    ):

        self.tasks = tasks if tasks is not None else []
        for task in self.tasks:
            if not isinstance(task, Task):
                raise TypeError(
                    f"tasks must be subclassed from :class:`crafting.Task` but was {type(task)}"
                )

        self.tasks_weights = tasks_weights
        self.tasks_can_end = tasks_can_end
        self.early_stopping = early_stopping
        self.dones = [False for _ in self.tasks]

    def _get_task_weight(self, task, i):
        if isinstance(self.tasks_weights, list):
            return self.tasks_weights[i]
        if isinstance(self.tasks_weights, dict):
            return self.tasks_weights[task.name]
        return 1

    def _get_task_can_end(self, task, i):
        if isinstance(self.tasks_can_end, list):
            return self.tasks_can_end[i]
        if isinstance(self.tasks_can_end, dict):
            return self.tasks_can_end[task.name]
        return False

    def _stacked_dones(self):
        if len(self.dones) == 0:
            return False
        if self.early_stopping == "all":
            return all(self.dones)
        if self.early_stopping == "any":
            return any(self.dones)
        raise ValueError(f"Unknown value for early_stopping: {self.early_stopping}")

    def reset(self):
        """Reset all tasks for a new episode."""
        for task in self.tasks:
            task.reset()

    def __getitem__(self, index: int):
        return self.tasks[index]

    def __call__(self, observation, previous_observation, action):
        if self.tasks is None:
            return 0, False

        accumulated_reward = 0
        dones = []

        for i, task in enumerate(self.tasks):
            reward, done = task(observation, previous_observation, action)
            accumulated_reward += reward * self._get_task_weight(task, i)
            if self._get_task_can_end(task, i):
                dones.append(done)

        self.dones = dones
        return accumulated_reward, self._stacked_dones()

    def __repr__(self) -> str:
        return "[" + ", ".join(repr(task) for task in self.tasks) + "]"


class RewardShaping(Enum):
    """Enumeration of all posible reward shaping types."""

    NONE = 0  # No reward shaping
    ALL = 1  # Items give rewards when first obtained.
    ALL_USEFUL = 2  # Items in unrolled solving option give rewards when first obtained.
    DIRECT_USEFUL = 3  # Items in solving option give rewards when first obtained.


class TaskObtainItem(Task):

    """Obtaining a given item_id"""

    def __init__(
        self,
        world: "World",
        item: "Item",
        reward_shaping: RewardShaping = RewardShaping.NONE,
        shaping_value: float = 0.0,
    ):
        """Task of obtaining a given item.

        Can have reward shaping of different types.

        Args:
            world (World): World in which the task will be defined.
            item (Item): Goal Item to obtain.
            reward_shaping (RewardShaping, optional): Type of reward shaping.
                Defaults to RewardShaping.NONE.
            shaping_value (float, optional): Value used for reward shaping if any.
                Defaults to 0.
        """
        super().__init__(f"obtain_{item}", world)
        self.goal_item = item
        self.add_achivement_getitem(self.goal_item.item_id, 10, end_task=True)

        # Reward shaping
        achivement_items: List["Item"] = []
        if reward_shaping == RewardShaping.ALL:
            achivement_items = world.items
        elif reward_shaping in (RewardShaping.ALL_USEFUL, RewardShaping.DIRECT_USEFUL):
            solving_option = world.get_all_options()[f"Get {item}"]
            graph = solving_option.graph
            if reward_shaping == RewardShaping.ALL_USEFUL:
                graph = graph.unrolled_graph
            achivement_items = list(get_items_in_graph(graph))

        for success_item in achivement_items:
            self.add_achivement_getitem(success_item.item_id, shaping_value)
