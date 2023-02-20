import networkx as nx
import pytest
import pytest_check as check

from crafting.examples.tower import TowerCraftingEnv
from tests.custom_checks import check_isomorphic


def test_gym_make():
    gym = pytest.importorskip("gym")
    env: TowerCraftingEnv = gym.make("TowerCrafting-v1", height=3, width=2)
    check.equal(env.height, 3)
    check.equal(env.width, 2)
    check.equal(env.world.n_items, 3 * 2 + 1)
    check.is_in("TowerCrafting", env.name)


def test_tower_requirements_graph_1_1():
    """should have expected structure

    #1#
    #0#

    """
    height = 1
    width = 1
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = nx.DiGraph()
    expected_graph.add_edge(0, 1)
    check_isomorphic(env.world.requirements.graph, expected_graph)


def test_tower_requirements_graph_1_2():
    """should have expected structure

    #2#
    #01#

    """
    height = 1
    width = 2
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = nx.DiGraph()
    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(1, 2)

    check_isomorphic(env.world.requirements.graph, expected_graph)


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
    expected_graph = nx.DiGraph()
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

    check_isomorphic(env.world.requirements.graph, expected_graph)


def test_tower_accessible_items():
    """items from the base of the tower should be accessible from the start."""
    env = TowerCraftingEnv(height=2, width=3)
    searchable_items = env.world.items[: env.width]
    for transfo in env.world.transformations:
        if any(item in searchable_items for item in transfo.added_player_items):
            check.equal(len(transfo.removed_player_items), 0)
