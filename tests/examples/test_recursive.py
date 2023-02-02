# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import pytest_check as check

import networkx as nx
from networkx import is_isomorphic

from crafting.examples.recursive import (
    RecursiveCraftingEnv,
    LightRecursiveCraftingEnv,
    # LighterRecursiveCraftingEnv,
)


def test_gym_make_recursive():
    gym = pytest.importorskip("gym")
    n_items = 10
    env: RecursiveCraftingEnv = gym.make("RecursiveCrafting-v1", n_items=n_items)
    check.equal(len(env.world.items), n_items)
    check.equal(env.name, "RecursiveCrafting-I10")


def test_recursive_requirements_graph():
    n_items = 4
    expected_graph = nx.DiGraph()
    expected_graph.add_edge(0, 1)
    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(0, 3)
    expected_graph.add_edge(1, 2)
    expected_graph.add_edge(1, 3)
    expected_graph.add_edge(2, 3)

    env = RecursiveCraftingEnv(n_items=n_items)
    check_isomorphic(env.requirements_graph, expected_graph)


def test_solve_recursive():
    n_items = 4  # [0, 1, 2, 3]
    actions = [
        0,  # 0
        1,  # 1 < 0
        0,  # 0
        2,  # 2 < 0 + 1
        0,  # 0
        1,  # 1
        3,  # 3 < 0 + 1 + 2
    ]

    env = RecursiveCraftingEnv(n_items=n_items)
    for action in actions:
        observation, done, _reward, _info = env.step(action)
        # Should only see items because no zones
        check.equal(observation.shape, (n_items,))

    check.is_true(done)


def test_gym_make_light_recursive():
    gym = pytest.importorskip("gym")
    n_items = 10
    n_required_previous = 3
    env: LightRecursiveCraftingEnv = gym.make(
        "LightRecursiveCrafting-v1",
        n_items=n_items,
        n_required_previous=n_required_previous,
    )
    check.equal(len(env.world.items), n_items)
    check.equal(env.name, "LightRecursiveCrafting-K3-I10")


def test_light_recursive_requirements_graph():
    n_items = 6
    n_required_previous = 3
    env = LightRecursiveCraftingEnv(
        n_items=n_items, n_required_previous=n_required_previous
    )
    expected_graph = nx.DiGraph()
    expected_graph.add_edge(0, 1)

    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(1, 2)

    expected_graph.add_edge(0, 3)
    expected_graph.add_edge(1, 3)
    expected_graph.add_edge(2, 3)

    expected_graph.add_edge(1, 4)
    expected_graph.add_edge(2, 4)
    expected_graph.add_edge(3, 4)

    expected_graph.add_edge(2, 5)
    expected_graph.add_edge(3, 5)
    expected_graph.add_edge(4, 5)

    check_isomorphic(env.requirements_graph, expected_graph)


# def test_gym_make_lighter_recursive():
#     gym = pytest.importorskip("gym")
#     n_items = 10
#     n_previous_items = 3
#     env: LighterRecursiveCraftingEnv = gym.make(
#         "LighterRecursiveCraftingEnv-v1",
#         n_items=n_items,
#         n_previous_items=n_previous_items,
#     )
#     check.equal(len(env.world.items), n_items)
#     check.equal(env.name, "LightRecursiveCraftingEnv-K3-I10")


# def test_lighter_recursive_requirements_graph(n_items: int, n_required_previous: int):
#     env = LighterRecursiveCraftingEnv(
#         n_items=n_items, n_required_previous=n_required_previous
#     )
#     expected_graph = DiGraph()
#     for item in env.world.items:
#         if item.item_id > 0:
#             expected_graph.add_edge(item.item_id - 1, item.item_id)
#         min_idx = max(0, item.item_id - n_required_previous)
#         for required_id in range(min_idx, item.item_id - 2):
#             expected_graph.add_edge(required_id, item.item_id)

#     check.is_true(is_isomorphic(env.world.requirements_graph, expected_graph))


def check_isomorphic(actual_graph: nx.Graph, expected_graph: nx.Graph):
    check.is_true(
        is_isomorphic(actual_graph, expected_graph),
        msg="Graphs are not isomorphic:"
        f"\n{list(actual_graph.edges())}"
        f"\n{list(expected_graph.edges())}",
    )
