# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=no-self-use, attribute-defined-outside-init, protected-access

""" Test of abstract Task classes behavior """

from dataclasses import dataclass
from typing import List

import pytest
import pytest_check as check
from pytest_mock import MockerFixture

import numpy as np

from crafting.task import (
    RewardShaping,
    Task,
    TaskList,
    TaskObtainItem,
    get_random_task,
    get_task,
    get_task_by_complexity,
    get_task_from_name,
)
from crafting.world.items import Item


@dataclass
class DummyItem:
    """DummyItem"""

    item_id: int
    name: str

    def __hash__(self) -> int:
        return self.name.__hash__()


@dataclass
class DummyBehavior:
    """DummyItem"""

    item: DummyItem
    complexity: int

    def __post_init__(self):
        self.name = f"Get {self.item.name}"

    def __hash__(self) -> int:
        return self.name.__hash__()


class DummyWorld:
    """DummyWorld"""

    def __init__(self, n_items=7, n_action=5):
        self.n_items = n_items
        self.n_actions = n_action
        self.items = [DummyItem(i, f"item_{i}") for i in range(self.n_items)]
        self.item_from_id = {item.item_id: item for item in self.items}
        self.item_from_name = {item.name: item for item in self.items}
        self.getable_items = self.items

    def get_all_behaviors(self):
        """Create dummy behaviors from the DummyWorld"""
        return {
            f"Get {item.name}": DummyBehavior(item, (i // 2 * 2) ** 2)
            for i, item in enumerate(self.items)
        }


class TestTask:
    """Task"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.world = DummyWorld()
        self.previous_observation = np.ones(10)
        self.observation = 2 * np.ones(10)
        self.action = 2

    def test_init(self):
        """should instanciate correctly."""
        task = Task("task_name", self.world)
        check.equal(task.name, "task_name")
        check.equal(task.world, self.world)

    def test_call(self, mocker: MockerFixture):
        """should call `done` and `reward` on call."""
        mocker.patch("crafting.task.Task.reward", lambda *args: 1)
        mocker.patch("crafting.task.Task.done", lambda *args: True)
        task = Task("task_name", self.world)
        reward, done = task(self.observation, self.previous_observation, self.action)

        check.equal(reward, 1)
        check.is_true(done)


class TestTaskList:
    """TaskList"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup dummy tasks"""
        self.world = DummyWorld()
        self.previous_observation = np.ones(10)
        self.observation = 2 * np.ones(10)
        self.action = 2
        self.task_observe_123 = Task("obs_123", self.world)
        self.task_observe_123.reward = lambda obs, prev_obs, act: 2.1 * np.all(
            obs == 2 * np.ones(10)
        )
        self.task_prev_observe_312 = Task("prev_obs_312", self.world)
        self.task_prev_observe_312.reward = lambda obs, prev_obs, act: 3.4 * np.all(
            prev_obs == np.ones(10)
        )
        self.task_action_observe_213 = Task("action_213", self.world)
        self.task_action_observe_213.reward = lambda obs, prev_obs, act: 4.7 * (
            act == 2
        )
        self.tasks = [
            self.task_observe_123,
            self.task_prev_observe_312,
            self.task_action_observe_213,
        ]

    def test_init(self):
        """should instanciate correctly."""
        TaskList(self.tasks)

    def test_init_raise_not_task(self):
        """should raise TypeError if a task doesn't subclass crafting.Task."""
        tasks = [self.task_observe_123, "task_str"]
        with pytest.raises(TypeError, match=r".*must be.*crafting.Task.*"):
            TaskList(tasks)

    def test_call_none_task(self):
        """should return (0, False) if tasks is None."""
        tasks = TaskList(None)
        reward, done = tasks(self.observation, self.previous_observation, self.action)
        check.equal(reward, 0)
        check.is_false(done)

    def test_call(self, mocker: MockerFixture):
        """should return accumulated rewards and done on call."""
        mocker.patch("crafting.task.TaskList._get_task_weight", lambda *args: 1)
        mocker.patch("crafting.task.TaskList._get_task_can_end", lambda *args: True)
        mocker.patch("crafting.task.TaskList._stacked_dones", lambda *args: True)
        tasks = TaskList(self.tasks)
        reward, done = tasks(self.observation, self.previous_observation, self.action)
        check.equal(reward, 10.2)
        check.is_true(done)


class TestTaskListGetTaskWeight:
    """TaskList._get_task_weight"""

    def setup(self):
        """Setup dummy tasks"""
        self.world = DummyWorld()
        self.task_observe_123 = Task("obs_123", self.world)
        self.task_prev_observe_312 = Task("prev_obs_312", self.world)
        self.task_action_observe_213 = Task("action_213", self.world)
        self.tasks = [
            self.task_observe_123,
            self.task_prev_observe_312,
            self.task_action_observe_213,
        ]

    def test_list(self):
        """should assign weights correctly if tasks_weights is a list."""
        expected_tasks_weights = [0.2, 0.1, 5]
        self.tasklist = TaskList(self.tasks, weights=expected_tasks_weights)
        for i, task in enumerate(self.tasklist.tasks):
            value = self.tasklist._get_task_weight(task)
            expected = expected_tasks_weights[i]
            check.equal(value, expected)

    def test_dict(self):
        """should assign weights correctly if tasks_weights is a dict."""
        expected_tasks_weights = {
            task.name: weight for task, weight in zip(self.tasks, [0.2, 0.1, 5])
        }
        self.tasklist = TaskList(self.tasks, weights=expected_tasks_weights)
        for task in self.tasklist.tasks:
            value = self.tasklist._get_task_weight(task)
            expected = expected_tasks_weights[task.name]
            check.equal(value, expected)

    def test_none(self):
        """should assign weights of 1 if tasks_weights is None."""
        self.tasklist = TaskList(self.tasks)
        for task in self.tasklist.tasks:
            value = self.tasklist._get_task_weight(task)
            check.equal(value, 1)


class TestTaskListGetTaskCanEnd:
    """TaskList._get_task_can_end"""

    def setup(self):
        """Setup dummy tasks"""
        self.world = DummyWorld()
        self.task_observe_123 = Task("obs_123", self.world)
        self.task_prev_observe_312 = Task("prev_obs_312", self.world)
        self.task_action_observe_213 = Task("action_213", self.world)
        self.tasks = [
            self.task_observe_123,
            self.task_prev_observe_312,
            self.task_action_observe_213,
        ]

    def test_list(self):
        """should assign `can_end` correctly if tasks_can_end is a list."""
        expected_tasks_can_end = [True, False, True]
        self.tasklist = TaskList(self.tasks, can_end=expected_tasks_can_end)
        for i, task in enumerate(self.tasklist.tasks):
            value = self.tasklist._get_task_can_end(task)
            check.equal(value, expected_tasks_can_end[i])

    def test_dict(self):
        """should assign `can_end` correctly if tasks_can_end is a dict."""
        expected_tasks_can_end = {
            task.name: can_end for task, can_end in zip(self.tasks, [True, False, True])
        }
        self.tasklist = TaskList(self.tasks, can_end=expected_tasks_can_end)
        for task in self.tasklist.tasks:
            value = self.tasklist._get_task_can_end(task)
            expected = expected_tasks_can_end[task.name]
            check.equal(value, expected)

    def test_none(self):
        """should assign False to all if tasks_can_end is None."""
        self.tasklist = TaskList(self.tasks)
        for task in self.tasklist.tasks:
            check.is_false(self.tasklist._get_task_can_end(task))


class TestTaskListStackDones:
    """TestList._stack_dones"""

    def test_all(self):
        """should return True only if all dones are True if early_stopping is 'all'."""
        tests = TaskList(None, early_stopping="all")

        done = tests.dones = [True, False, True]
        check.is_false(tests._stacked_dones())

        done = tests.dones = [True, True, True]
        check.is_true(tests._stacked_dones())

    def test_any(self):
        """should return True if any dones is True if early_stopping is 'any'."""
        tests = TaskList(None, early_stopping="any")

        tests.dones = [True, False, True]
        check.is_true(tests._stacked_dones())

        tests.dones = [False, False, False]
        check.is_false(tests._stacked_dones())

    def test_raise_othervalue(self):
        """should raise ValueError if early_stopping is not in ('any', 'all')."""
        tests = TaskList(None, early_stopping="x")
        tests.dones = [True, False, True]
        with pytest.raises(ValueError, match=r"Unknown value for early_stopping.*"):
            tests._stacked_dones()


def dummy_init(self, **kwargs):
    for arg_name, arg_value in kwargs.items():
        setattr(self, arg_name, arg_value)


class TestTaskObtainItem:
    """TaskObtainItem"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        """Setup reused fixtures."""
        self.init_mocker = mocker.patch("crafting.task.Task.__init__", dummy_init)
        self.add_achivement_mocker = mocker.patch(
            "crafting.task.Task.add_achivement_getitem"
        )

        def dummy_get_items_in_graph(graph: "DummyGraph", *args, **kwargs):
            return graph.items_in_graph

        self.get_items_in_graph_mocker = mocker.patch(
            "crafting.task.get_items_in_graph", dummy_get_items_in_graph
        )

        class DummyItem:
            def __init__(self, item_id: int) -> None:
                self.item_id = item_id

            def __repr__(self) -> str:
                return f"DummyItem({self.item_id})"

        self.dummy_items = [DummyItem(i) for i in range(5)]
        self.dummy_item = self.dummy_items[1]

        class DummyGraph:
            def __init__(
                self,
                item: DummyItem,
                direct_needed_items: List[DummyItem],
                all_needed_items: List[DummyItem],
                graph_type: str = "rolled",
            ) -> None:
                self.graph_type = graph_type
                self.item = item

                if graph_type == "rolled":
                    self.items_in_graph = direct_needed_items
                    self.unrolled_graph = DummyGraph(
                        item, direct_needed_items, all_needed_items, "unrolled"
                    )
                else:
                    self.items_in_graph = all_needed_items

        class DummyGetItem:
            def __init__(
                self,
                item: DummyItem,
                direct_needed_items: List[DummyItem],
                all_needed_items: List[DummyItem],
            ) -> None:
                self.item = item
                self.graph = DummyGraph(item, direct_needed_items, all_needed_items)

        class DummyWorld:
            items = self.dummy_items

            def get_all_behaviors(self):
                return {
                    f"Get {item}": DummyGetItem(
                        item, [self.items[i + 1]], self.items[i + 1 :]
                    )
                    for i, item in enumerate(self.items[:-1])
                }

        self.dummy_world = DummyWorld()
        self.shaping_value = 42

    def test_goal_item(self):
        """should have given item as goal_item and ending achivement."""

        task = TaskObtainItem(world=self.dummy_world, item=self.dummy_item)
        check.equal(task.goal_item, self.dummy_item)
        self.add_achivement_mocker.assert_called_with(
            self.dummy_item, 10, end_task=True
        )

    def test_reward_shaping_all(self):
        """should give achivement value for every world item."""

        TaskObtainItem(
            world=self.dummy_world,
            item=self.dummy_item,
            reward_shaping=RewardShaping.ALL,
            shaping_value=self.shaping_value,
        )

        is_called = {item.item_id: False for item in self.dummy_items}
        check.equal(
            self.add_achivement_mocker.call_args_list[0].args,
            (self.dummy_item, 10),
        )
        check.equal(
            self.add_achivement_mocker.call_args_list[0].kwargs, {"end_task": True}
        )

        for call in self.add_achivement_mocker.call_args_list[1:]:
            item_called: Item = call.args[0]
            is_called[item_called.item_id] = True
            check.equal(call.args[1], self.shaping_value)

        check.is_true(all(is_called.values()))

    def test_reward_shaping_direct_useful(self):
        """should give achivement value for items in solving behavior rolled graph."""

        TaskObtainItem(
            world=self.dummy_world,
            item=self.dummy_item,
            reward_shaping=RewardShaping.DIRECT_USEFUL,
            shaping_value=self.shaping_value,
        )

        is_called = {item.item_id: False for item in self.dummy_items}
        expected_called_items = [self.dummy_items[2].item_id]

        check.equal(
            self.add_achivement_mocker.call_args_list[0].args,
            (self.dummy_item, 10),
        )
        check.equal(
            self.add_achivement_mocker.call_args_list[0].kwargs, {"end_task": True}
        )
        for call in self.add_achivement_mocker.call_args_list[1:]:
            item_called: Item = call.args[0]
            is_called[item_called.item_id] = True
            check.equal(call.args[1], self.shaping_value)

        for item in self.dummy_items:
            item_is_called = is_called[item.item_id]
            if item.item_id in expected_called_items:
                check.is_true(item_is_called, f"{item} was not called when expected.")
            else:
                check.is_false(item_is_called, f"{item} was called when not expected.")

    def test_reward_shaping_all_useful(self):
        """should give achivement value for every item in solving behavior unrolled graph."""

        TaskObtainItem(
            world=self.dummy_world,
            item=self.dummy_item,
            reward_shaping=RewardShaping.ALL_USEFUL,
            shaping_value=self.shaping_value,
        )

        is_called = {item.item_id: False for item in self.dummy_items}
        expected_called_items = [item.item_id for item in self.dummy_items[2:]]

        check.equal(
            self.add_achivement_mocker.call_args_list[0].args,
            (self.dummy_item, 10),
        )
        check.equal(
            self.add_achivement_mocker.call_args_list[0].kwargs, {"end_task": True}
        )
        for call in self.add_achivement_mocker.call_args_list[1:]:
            item_called: Item = call.args[0]
            is_called[item_called.item_id] = True
            check.equal(call.args[1], self.shaping_value)

        for item in self.dummy_items:
            item_is_called = is_called[item.item_id]
            if item.item_id in expected_called_items:
                check.is_true(item_is_called, f"{item} was not called when expected.")
            else:
                check.is_false(item_is_called, f"{item} was called when not expected.")


class TestGetTaskFromName:
    "get_task_from_name"

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.world = DummyWorld()
        self.task_obtain_item_mocker = mocker.patch(
            "crafting.task.TaskObtainItem", lambda world, item, **kwargs: item.item_id
        )

    def test_obtain_item_by_id(self):
        """should get correct item by id for TaskObtainItem."""
        wanted_item_id = 2
        task_name = f"obtain_{wanted_item_id}"

        item_id = get_task_from_name(self.world, task_name)
        check.equal(item_id, wanted_item_id)

    def test_obtain_item_by_literal(self):
        """should get correct item by literal name for TaskObtainItem."""
        wanted_item_id = 2
        wanted_item_name = self.world.item_from_id[wanted_item_id].name
        task_name = f"obtain_{wanted_item_name}"

        item_id = get_task_from_name(self.world, task_name)
        check.equal(item_id, wanted_item_id)

    def test_raise_could_not_resolve(self):
        """should raise error if unknowed task."""
        with pytest.raises(ValueError, match=".* could not be resolved."):
            get_task_from_name(self.world, "x")


class TestGetRandomTask:
    "get_random_task"

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.world = DummyWorld()
        self.task_obtain_item_mocker = mocker.patch(
            "crafting.task.TaskObtainItem", lambda world, item, **kwargs: item.item_id
        )

    def test_obtain_random_item_same_seed(self):
        """should get the same random item for the same seed."""
        seed = 42
        item_id_1 = get_random_task(self.world, seed=seed)
        item_id_2 = get_random_task(self.world, seed=seed)
        check.equal(item_id_1, item_id_2)

    def test_obtain_random_item_diff_seed(self):
        """should get different random item for different seeds."""
        item_id_1 = get_random_task(self.world, seed=42)
        item_id_2 = get_random_task(self.world, seed=43)
        check.not_equal(item_id_1, item_id_2)


class TestGetTaskByComplexity:
    "get_task_by_complexity"

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.world = DummyWorld()
        self.task_obtain_item_mocker = mocker.patch(
            "crafting.task.TaskObtainItem", lambda world, item, **kwargs: item.item_id
        )
        self.lcomplexity_mocker = mocker.patch(
            "crafting.task.learning_complexity",
            lambda behavior, used_nodes_all: (behavior.complexity, 0),
        )
        self.behaviors_histograms = mocker.patch("crafting.task.behaviors_histograms")

    def test_get_best(self):
        """should retrieve the closest TaskObtainItem in terms of complexity."""
        wanted_complexity = 5
        expected_item_id = 2
        item_id = get_task_by_complexity(self.world, wanted_complexity)
        check.equal(item_id, expected_item_id)


class TestGetTask:
    "get_task"

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.world = DummyWorld()
        self.random_mocker = mocker.patch("crafting.task.get_random_task")
        self.complexity_mocker = mocker.patch("crafting.task.get_task_by_complexity")
        self.name_mocker = mocker.patch("crafting.task.get_task_from_name")

    def test_by_name(self):
        """should get task by name by default."""
        get_task(self.world, task_name="obtain_2")

        check.is_false(self.random_mocker.called)
        check.is_false(self.complexity_mocker.called)
        check.is_true(self.name_mocker.called)

    def test_random_task(self):
        """should get a random obtain_item task if random_task is True."""
        seed = 42
        get_task(self.world, random_task=True, seed=seed)

        check.is_true(self.random_mocker.called)
        check.is_false(self.complexity_mocker.called)
        check.is_false(self.name_mocker.called)

        check.equal(self.random_mocker.call_args[0][1], seed)

    def test_random_in_name(self):
        """should get a random obtain_item task if random in task_name."""
        seed = 42
        get_task(self.world, task_name="obtain_random", seed=seed)

        check.is_true(self.random_mocker.called)
        check.is_false(self.complexity_mocker.called)
        check.is_false(self.name_mocker.called)

        check.equal(self.random_mocker.call_args[0][1], seed)

    def test_by_complexity(self):
        """should get a task by complexity if task_complexity is given."""
        task_complexity = 243
        get_task(self.world, task_complexity=task_complexity)

        check.is_false(self.random_mocker.called)
        check.is_true(self.complexity_mocker.called)
        check.is_false(self.name_mocker.called)

        check.equal(self.complexity_mocker.call_args[0][1], task_complexity)
