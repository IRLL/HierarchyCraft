# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=unused-argument, no-self-use

""" Task to defines objectives """

from typing import TYPE_CHECKING, List, Union, Dict

import numpy as np

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

    def _stack_dones(self, dones):
        if len(dones) == 0:
            return False
        if self.early_stopping == "all":
            return all(dones)
        if self.early_stopping == "any":
            return any(dones)
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

        done = self._stack_dones(dones)
        return accumulated_reward, done

    def __repr__(self) -> str:
        return "[" + ", ".join(repr(task) for task in self.tasks) + "]"


class TaskObtainItem(Task):

    """Obtaining a given item_id"""

    def __init__(self, world: "World", item: "Item"):
        super().__init__(f"obtain_{item}", world)
        self.add_achivement_getitem(item.item_id, 10, end_task=True)
