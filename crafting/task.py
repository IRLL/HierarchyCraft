# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=unused-argument, no-self-use

""" Task to defines objectives """

import logging
import os
import pickle
from typing import TYPE_CHECKING, List, Optional, Union, Dict
from enum import Enum

from tqdm import tqdm
import numpy as np

from option_graph.metrics.complexity import learning_complexity
from option_graph.metrics.complexity.histograms import nodes_histograms

from crafting.options.utils import get_items_in_graph

if TYPE_CHECKING:
    from crafting.options.options import GetItem
    from crafting.world.world import World
    from crafting.world.items import Item
    from option_graph.option import Option


class Task:

    """Abstract class for any task"""

    def __init__(self, name, world: "World"):
        self.name = name
        self.world = world

        self.achievements_items = set()
        self.achievements_items_values = np.zeros(self.world.n_items)
        self.achievements_items_done = np.zeros(self.world.n_items, dtype=bool)

        self.items_values = np.zeros(self.world.n_items)
        self.action_values = np.zeros(self.world.n_actions)

        self.items_end_task_at = np.inf * np.ones(self.world.n_items, dtype=np.int32)
        self.action_end_task = np.zeros(self.world.n_actions, dtype=bool)

        self.reset()

    def add_achivement_getitem(self, item: "Item", value, end_task=False):
        """Makes getting `item_id` for the first time an achievement with reward `value`."""
        self.achievements_items.add(item)
        item_slot = self.world.item_id_to_slot[item.item_id]
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
        goal_reward: float = 10.0,
        reward_shaping: RewardShaping = RewardShaping.NONE,
        shaping_value: float = 1.0,
    ):
        """Task of obtaining a given item.

        Can have reward shaping of different types.

        Args:
            world (World): World in which the task will be defined.
            item (Item): Goal Item to obtain.
            goal_reward (float, optional): Reward given when item is obtained.
                Defaults to 10.
            reward_shaping (RewardShaping, optional): Type of reward shaping.
                Defaults to RewardShaping.NONE.
            shaping_value (float, optional): Value used for reward shaping if any.
                Defaults to 1.
        """
        super().__init__(f"obtain_{item}", world)
        self.goal_item = item
        self.add_achivement_getitem(self.goal_item, goal_reward, end_task=True)

        # Reward shaping
        achivement_items: List["Item"] = []
        if reward_shaping is None or reward_shaping == RewardShaping.NONE:
            pass
        elif reward_shaping == RewardShaping.ALL:
            achivement_items = world.items
        elif reward_shaping in (RewardShaping.ALL_USEFUL, RewardShaping.DIRECT_USEFUL):
            all_options = world.get_all_options()
            solving_option = all_options[f"Get {item}"]
            graph = solving_option.graph
            if reward_shaping == RewardShaping.ALL_USEFUL:
                graph = graph.unrolled_graph
            achivement_items = list(get_items_in_graph(graph, all_options=all_options))
        else:
            raise ValueError(
                f"Unknown reward_shaping: {reward_shaping} of type {type(reward_shaping)}"
            )

        for success_item in achivement_items:
            self.add_achivement_getitem(success_item, shaping_value)


def get_task_from_name(world: "World", task_name: str, **kwargs):
    """Get Task for a given task name.

    Args:
        world (World): _description_
        task_name (str): Name of the task to find.

    Raises:
        ValueError: If the item name after task name could not be resolved.

    Returns:
        Task: The Task object corresponding in the given World.
    """
    if "obtain_" in task_name:
        item_name = task_name[len("obtain_") :]
        # With id
        if item_name.isnumeric():
            item_id = int(item_name)
            item = world.item_from_id[item_id]
        # With name
        else:
            item = world.item_from_name[item_name]
        return TaskObtainItem(world, item, **kwargs)
    raise ValueError(f"Task with name {task_name} could not be resolved.")


def get_random_task(world: "World", seed: int = None, **kwargs):
    """Get a random Task from a given World.

    Args:
        world (World): The world in which to pick an item for the obtainitem task.
        seed (int, optional): Seed for randomness reproductibility, random seed if None.
            Defaults to None.

    Returns:
        TaskObtainItem: The task of obtaining a random item from the given World.
    """
    rng = np.random.RandomState(seed)  # pylint: disable=no-member
    random_item = rng.choice(world.getable_items)
    return TaskObtainItem(world, random_item, **kwargs)


def get_task_by_complexity(
    world: "World", task_complexity: float, cache_path: str = None, **kwargs
):
    """Get the obtain item task with the closest complexity to the one given.

    If the two closest tasks have the same complexity, this will only ever return the first one.

    Args:
        world (World): The world in which to pick items for the obtain item tasks.
        task_complexity (float): The wanted task complexity.
        cache_path (str, optional): Path to caching file. No caching if None. Defaut to None.

    Returns:
        TaskObtainItem: The task of obtaining an item from the given World
            with the closest complexity to the one wanted.
    """

    def _get_items_complexities(item_options: List["Option"]):
        items_complexities = {}
        used_nodes_all = nodes_histograms(all_options_list)
        for option in tqdm(item_options, desc="Computing complexities"):
            learn_comp, saved_comp = learning_complexity(option, used_nodes_all)
            total_comp = learn_comp + saved_comp
            items_complexities[option] = total_comp
        return items_complexities

    def _load_or_build_cache(cache_path: str, item_options: List["Option"]):
        if not cache_path.endswith(".pickle"):
            cache_path += ".pickle"
        if not os.path.isfile(cache_path):
            items_complexities = _get_items_complexities(item_options)

            os.makedirs(os.path.split(cache_path)[0], exist_ok=True)
            with open(cache_path, "wb") as cache:
                pickle.dump(items_complexities, cache)
                logging.info("Cached complexities to %s", cache_path)

        else:
            with open(cache_path, "rb") as cache:
                items_complexities = pickle.load(cache)
        return items_complexities

    # Get & save solving option
    all_options = world.get_all_options()
    all_options_list = list(all_options.values())
    item_options = [option for option in all_options_list if hasattr(option, "item")]

    # Compute complexities
    if cache_path:
        items_complexities = _load_or_build_cache(cache_path, item_options)
    else:
        items_complexities = _get_items_complexities(item_options)

    # Get closest item
    items_complexities_arr = np.array(list(items_complexities.values()))
    items_options_arr = np.array(list(items_complexities.keys()))

    order = np.argsort((items_complexities_arr - task_complexity) ** 2)
    ordered_options: List["GetItem"] = items_options_arr[order]

    return TaskObtainItem(world, ordered_options[0].item, **kwargs)


def get_task(
    world: "World",
    task_name: str = "",
    task_complexity: float = None,
    cache_path: Optional[str] = None,
    random_task: bool = False,
    seed: int = None,
    **kwargs,
) -> Union[Task, TaskObtainItem]:
    """Build a Task in the given World from given instructions.

    Examples:
        # To build a TaskObtainItem to get item with id 2:
        task = get_task(world, 'obtain_2')
        # To build a TaskObtainItem for a random item with seed 42:
        task = get_task(world, random_task=True, seed=42)
        # To build a TaskObtainItem for an item with complexity as close as possible to 243:
        task = get_task(world, task_complexity=243)

    Args:
        world (World): World in which to build the task.
        task_name (str, optional): Name of the task to build.
        task_complexity (float, optional): Complexity of the task wanted.
        cache_path (str, optional): Path to caching file for complexities.
            No caching if None. Defaut to None.
        random_task (bool): Force random task to be chosen.
        seed (int, optional): Seed used for random task selection if random.

    Kwargs:
        Passed to Task constructor.

    Raises:
        AssertionError: If none of task_name, task_complexity or random_task was given.
        ValueError: If the item name after task name could not be resolved.

    Returns:
        Task: Built task.
    """
    random_task = random_task or "random" in task_name
    assert random_task or task_name is not None or task_complexity is not None

    if random_task:
        return get_random_task(world, seed, **kwargs)
    if task_complexity is not None:
        return get_task_by_complexity(
            world, task_complexity, cache_path=cache_path, **kwargs
        )
    return get_task_from_name(world, task_name, **kwargs)
