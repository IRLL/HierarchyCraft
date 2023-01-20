# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import pytest_check as check

from networkx import is_isomorphic, DiGraph

from crafting.examples.simple import TowerCraftingEnv


def test_gym_make():
    gym = pytest.importorskip("gym")
    env: TowerCraftingEnv = gym.make("TowerCrafting-v1", height=3, width=2)
    check.equal(env.height, 3)
    check.equal(env.width, 2)
    check.equal(env.world.n_items, 7)
    check.is_in("TowerCrafting", env.name)


def test_tower_requirements_graph_1_1():
    """should have expected structure

    #1#
    #0#

    """
    height = 1
    width = 1
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = DiGraph()
    expected_graph.add_edge(0, 1)

    for recipe in env.world.recipes:
        print(recipe)
    check.is_true(is_isomorphic(env.world.requirements_graph, expected_graph))


def test_tower_requirements_graph_1_2():
    """should have expected structure

    #2#
    #01#

    """
    height = 1
    width = 2
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = DiGraph()
    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(1, 2)

    for recipe in env.world.recipes:
        print(recipe)
    check.is_true(is_isomorphic(env.world.requirements_graph, expected_graph))


def test_tower_requirements_graph_3_2():
    """should have expected structure

    #6##
    #45#
    #23#
    #01#

    """
    height = 3
    width = 2
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = DiGraph()
    expected_graph.add_edge(5, 6)
    expected_graph.add_edge(4, 6)
    expected_graph.add_edge(2, 5)
    expected_graph.add_edge(3, 5)
    expected_graph.add_edge(2, 4)
    expected_graph.add_edge(3, 4)
    expected_graph.add_edge(0, 3)
    expected_graph.add_edge(1, 3)
    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(1, 2)

    for recipe in env.world.recipes:
        print(recipe)
    check.is_true(is_isomorphic(env.world.requirements_graph, expected_graph))


def test_tower_accessible_items():
    env = TowerCraftingEnv(height=2, width=3)
    for foundable_item in env.world.items[: env.width]:
        check.is_in(foundable_item, env.world.zones[0].items)
