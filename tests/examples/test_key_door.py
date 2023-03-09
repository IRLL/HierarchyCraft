import pytest
import pytest_check as check

from crafting.elements import Item, Zone
from crafting.examples.keydoor import KeyDoorCraftingEnv


def test_build_env():
    env = KeyDoorCraftingEnv()
    expected_items = {
        Item("key"),
        Item("ball"),
        Item("weight"),
    }
    check.equal(
        expected_items,
        set(env.world.items),
        msg=str(expected_items - set(env.world.items)),
    )
    expected_zones_items = {
        Item("open_door"),
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
    env = KeyDoorCraftingEnv(max_step=20)
    if draw:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        env.world.requirements.draw(ax, layout="spring")
        fig.savefig("keydoor_requirements_graph.png")
        plt.close()


def test_gym_make():
    gym = pytest.importorskip("gym")
    env: KeyDoorCraftingEnv = gym.make("KeyDoorCrafting-v1")
    check.equal(env.goal.name, "Get ball")
