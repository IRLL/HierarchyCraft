import networkx as nx
import pytest
import pytest_check as check

from hcraft.examples.recursive import LightRecursiveHcraftEnv, RecursiveHcraftEnv
from tests.custom_checks import check_isomorphic


def test_gym_make_recursive():
    gym = pytest.importorskip("gym")
    n_items = 10
    env: RecursiveHcraftEnv = gym.make("RecursiveHcraft-v1", n_items=n_items)
    check.equal(len(env.world.items), n_items)
    check.equal(env.name, "RecursiveHcraft-I10")


def test_recursive_requirements_graph():
    n_items = 4
    expected_graph = nx.DiGraph()
    expected_graph.add_edge(0, 1)
    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(0, 3)
    expected_graph.add_edge(1, 2)
    expected_graph.add_edge(1, 3)
    expected_graph.add_edge(2, 3)

    env = RecursiveHcraftEnv(n_items=n_items)
    check_isomorphic(env.world.requirements.graph, expected_graph)


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

    env = RecursiveHcraftEnv(n_items=n_items)
    env.reset()
    for action in actions:
        observation, done, _reward, _info = env.step(action)
        # Should only see items because no zones
        check.equal(observation.shape, (n_items,))

    check.is_true(done)


def test_gym_make_light_recursive():
    gym = pytest.importorskip("gym")
    n_items = 10
    n_required_previous = 3
    env: LightRecursiveHcraftEnv = gym.make(
        "LightRecursiveHcraft-v1",
        n_items=n_items,
        n_required_previous=n_required_previous,
    )
    check.equal(len(env.world.items), n_items)
    check.equal(env.name, "LightRecursiveHcraft-K3-I10")


def test_light_recursive_requirements_graph():
    n_items = 6
    n_required_previous = 3
    env = LightRecursiveHcraftEnv(
        n_items=n_items,
        n_required_previous=n_required_previous,
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

    check_isomorphic(env.world.requirements.graph, expected_graph)


def test_solve_light_recursive():
    n_items = 5  # [0, 1, 2, 3, 4]
    n_required_previous = 2
    actions = [
        0,  # 0
        1,  # 1 < 0
        0,  # 0
        2,  # 2 < 0 + 1
        0,  # 0
        1,  # 1
        3,  # 3 < 1 + 2
        0,  # 0
        1,  # 1
        2,  # 2 < 0 + 1
        4,  # 4 < 2 + 3
    ]

    env = LightRecursiveHcraftEnv(
        n_items=n_items,
        n_required_previous=n_required_previous,
    )
    env.reset()
    for action in actions:
        observation, done, _reward, _info = env.step(action)
        # Should only see items because no zones
        check.equal(observation.shape, (n_items,))

    check.is_true(done)
