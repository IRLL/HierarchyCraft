# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import pytest_check as check
import gym

from hypothesis import given
from hypothesis.strategies import integers

from networkx import is_isomorphic, DiGraph

from crafting.examples.simple import (
    RecursiveCraftingEnv,
    LightRecursiveCraftingEnv,
    LighterRecursiveCraftingEnv,
)


def test_gym_make():
    env: RecursiveCraftingEnv = gym.make("RecursiveCrafting-v1", n_items=10)
    check.equal(len(env.world.items), 10)
    check.equal(env.name, "RecursiveCrafting")


def test_gym_make_without_n_items():
    with pytest.raises(
        TypeError, match="missing 1 required positional argument: 'n_items'"
    ):
        gym.make("RecursiveCrafting-v1")


@given(integers(3, 8))
def test_recursive_requirements_graph(n_items: int):
    env = RecursiveCraftingEnv(n_items=n_items)
    expected_graph = DiGraph()
    for item in env.world.items:
        for required_id in range(item.item_id):
            expected_graph.add_edge(required_id, item.item_id)

    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))


@given(integers(3, 8), integers(2, 6))
def test_light_recursive_requirements_graph(n_items: int, n_required_previous: int):
    env = LightRecursiveCraftingEnv(
        n_items=n_items, n_required_previous=n_required_previous
    )
    expected_graph = DiGraph()
    for item in env.world.items:
        min_idx = max(0, item.item_id - n_required_previous)
        for required_id in range(min_idx, item.item_id):
            expected_graph.add_edge(required_id, item.item_id)

    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))


@given(integers(3, 8), integers(3, 6))
def test_lighter_recursive_requirements_graph(n_items: int, n_required_previous: int):
    env = LighterRecursiveCraftingEnv(
        n_items=n_items, n_required_previous=n_required_previous
    )
    expected_graph = DiGraph()
    for item in env.world.items:
        if item.item_id > 0:
            expected_graph.add_edge(item.item_id - 1, item.item_id)
        min_idx = max(0, item.item_id - n_required_previous)
        for required_id in range(min_idx, item.item_id - 2):
            expected_graph.add_edge(required_id, item.item_id)

    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))
