import networkx as nx

from crafting.elements import Item, Zone
from crafting.examples.keydoor import KeyDoorCraftingEnv

import pytest
import pytest_check as check
from tests.custom_checks import check_isomorphic


def test_build_env():
    env = KeyDoorCraftingEnv()
    expected_items = {
        Item("key"),
        Item("ball"),
    }
    check.equal(
        expected_items,
        set(env.world.items),
        msg=str(expected_items - set(env.world.items)),
    )
    expected_zones_items = {
        Item("open_door"),
        Item("closed_door"),
        Item("locked_door"),
        Item("key"),
        Item("ball"),
    }
    check.equal(
        expected_zones_items,
        set(env.world.zones_items),
        msg=str(expected_zones_items - set(env.world.zones_items)),
    )
    expected_zones = {
        Zone("start_room"),
        Zone("ball_room"),
    }
    check.equal(
        expected_zones,
        set(env.world.zones),
        msg=str(expected_zones - set(env.world.zones)),
    )


def test_can_solve():
    env = KeyDoorCraftingEnv(max_step=20)
    solving_behavior = env.solving_behavior(env.goal)
    done = False
    observation = env.reset()
    while not done:
        action = solving_behavior(observation)
        observation, _reward, done, _ = env.step(action)
    check.is_true(env.goal.terminated)


def test_requirements_graph():
    draw = False

    expected_graph = nx.DiGraph()
    expected_graph.add_edge("START#", "start_room")
    expected_graph.add_edge("start_room", "key_in_zone")
    expected_graph.add_edge("key_in_zone", "key")
    expected_graph.add_edge("key", "key_in_zone")
    expected_graph.add_edge("key", "closed_door")
    expected_graph.add_edge("key", "open_door")
    expected_graph.add_edge("start_room", "locked_door")
    expected_graph.add_edge("ball_room", "locked_door")
    expected_graph.add_edge("locked_door", "closed_door")
    expected_graph.add_edge("locked_door", "open_door")
    expected_graph.add_edge("start_room", "closed_door")
    expected_graph.add_edge("ball_room", "closed_door")
    expected_graph.add_edge("closed_door", "open_door")
    expected_graph.add_edge("start_room", "open_door")
    expected_graph.add_edge("ball_room", "open_door")
    expected_graph.add_edge("open_door", "ball_room")
    expected_graph.add_edge("start_room", "ball_room")
    expected_graph.add_edge("open_door", "start_room")
    expected_graph.add_edge("ball_room", "start_room")
    expected_graph.add_edge("ball_in_zone", "ball")
    expected_graph.add_edge("ball", "ball_in_zone")
    expected_graph.add_edge("ball_room", "ball_in_zone")

    env = KeyDoorCraftingEnv(max_step=20)
    check_isomorphic(env.world.requirements.digraph, expected_graph)

    if draw:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        env.world.requirements.draw(ax, layout="spring")
        plt.show()
        plt.close()


def test_gym_make():
    gym = pytest.importorskip("gym")
    env: KeyDoorCraftingEnv = gym.make("KeyDoorCrafting-v1")
    check.equal(env.goal.name, "Get ball")
