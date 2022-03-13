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
        weights: Union[List[float], Dict[str, float]] = None,
        can_end: Union[List[bool], Dict[str, bool]] = None,
        early_stopping: str = "all",
    ):
        """_summary_

        Args:
            tasks (List[Task]): List of tasks to compose the list.
            weights (Union[List[float], Dict[str, float]], optional):
                Weight of tasks used for reward. Defaults to one.
            can_end (Union[List[bool], Dict[str, bool]], optional):
                Whether task can end the environment. Defaults to all False.
            early_stopping (str, optional):
                If 'all', all task that can end have to be done to stop the environment.
                If 'any', any task that can end will stop the environment when done.
                Defaults to "all".
        Raises:
            TypeError: A given task is not an instance of Task.
        """

        self.tasks = tasks if tasks is not None else []
        for task in self.tasks:
            if not isinstance(task, Task):
                raise TypeError(
                    f"tasks must be subclassed from :class:`crafting.Task` but was {type(task)}"
                )

        self.weights = self._build_dict(weights, 1)
        self.can_end = self._build_dict(can_end, False)
        self.early_stopping = early_stopping
        self.dones = [False for _ in self.tasks]

    def _build_dict(self, values, default) -> dict:
        if values is None:
            values = {task.name: default for task in self.tasks}
        elif isinstance(values, list):
            values = {task.name: end for task, end in zip(self.tasks, values)}

        if isinstance(values, dict):
            for task in self.tasks:
                if task.name not in values:
                    values[task.name] = default
            return values
        raise TypeError("Cannot map given values to tasks.")

    def _get_task_weight(self, task: Task):
        return self.weights[task.name]

    def _get_task_can_end(self, task: Task):
        return self.can_end[task.name]

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

    def add(self, task: Task, weight: float = 1.0, can_end: bool = False):
        """Add a new task to the TaskList.

        Args:
            task (Task): Task to be added, must be an instance of Task.
            weight (float, optional): Weight of this task rewards. Defaults to 1.0.
            can_end (bool, optional): If True, this task could make the env done when completed.
                See TaskList early_stopping for more details. Defaults to False.
        """
        assert isinstance(task, Task), "Can only add Task to TaskList."
        self.tasks += [task]
        self.weights[task.name] = weight
        self.can_end[task.name] = can_end

    def __call__(self, observation, previous_observation, action):
        if self.tasks is None:
            return 0, False

        accumulated_reward = 0
        dones = []

        for task in self.tasks:
            reward, done = task(observation, previous_observation, action)
            accumulated_reward += reward * self._get_task_weight(task)
            if self._get_task_can_end(task):
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
            all_options = world.get_all_options()
            solving_option = all_options[f"Get {item}"]
            graph = solving_option.graph
            if reward_shaping == RewardShaping.ALL_USEFUL:
                graph = graph.unrolled_graph
            achivement_items = list(get_items_in_graph(graph, all_options=all_options))

        for success_item in achivement_items:
            self.add_achivement_getitem(success_item.item_id, shaping_value)


def get_task_from_name(
    task_name: str, world: "World", **kwargs
) -> Union[Task, TaskObtainItem]:
    """Build a Task in the given World from a given name.

    Examples:
        # To build a TaskObtainItem:
        task = get_task_from_name('obtain_*(itemid)')
        # To build a TaskObtainItem for a random item:
        task = get_task_from_name('obtain_*random*')

    Args:
        task_name (str): Name of the task to build.
        world (World): World in which to build the task.

    Kwargs:
        Are passed to Task constructor.

    Raises:
        ValueError: If the task name could not be resolved.
        ValueError: If the item name after 'obtain_' tag could not be resolved.

    Returns:
        Task: Built task.
    """
    rng = np.random.RandomState(kwargs.pop("seed", None))
    if task_name.startswith("obtain_"):
        item_name = "".join(task_name.split("_")[1:])
        if "random" in item_name:
            random_item = rng.choice(world.getable_items)
            return TaskObtainItem(world, random_item, **kwargs)
        if "(" in item_name:
            item_id = int(item_name.split("(")[1].split(")")[0])
            item = world.item_from_id[item_id]
            return TaskObtainItem(world, item, **kwargs)
        raise ValueError(
            f"No item found with name {item_name}." f"Available items: {world.items}"
        )
    raise ValueError(f"Could not resolve task name: {task_name}.")
