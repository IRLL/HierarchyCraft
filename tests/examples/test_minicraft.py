import pytest
import pytest_check as check

import os
from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.examples.minicraft import (
    MiniCraftEmpty,
    MiniCraftFourRooms,
    MiniCraftMultiRoom,
    MiniCraftCrossing,
    MiniCraftDoorKey,
    # MiniCraftKeyCorridor,
)

minicraft_envs = [
    MiniCraftEmpty,
    MiniCraftFourRooms,
    MiniCraftMultiRoom,
    MiniCraftCrossing,
    MiniCraftDoorKey,
    # MiniCraftKeyCorridor,
]


@pytest.mark.parametrize("env_class", minicraft_envs)
def test_build_env(env_class):
    human_run = False
    env = env_class()
    if human_run:
        render_env_with_human(env)


@pytest.mark.parametrize("env_class", minicraft_envs)
def test_can_solve(env_class):
    env: CraftingEnv = env_class(max_step=20)
    solving_behavior = env.solving_behavior(env.task)
    done = False
    observation = env.reset()
    while not done:
        action = solving_behavior(observation)
        observation, _reward, done, _ = env.step(action)
    check.is_true(env.task.terminated)


@pytest.mark.parametrize("env_class", minicraft_envs)
def test_requirements_graph(env_class):
    draw = True
    env: CraftingEnv = env_class()
    env.world.requirements.graph
    if draw:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(16, 9))
        env.world.requirements.draw(ax)

        requirements_dir = "requirements_graphs"
        os.makedirs(requirements_dir, exist_ok=True)
        plt.tight_layout()
        fig.savefig(os.path.join(requirements_dir, f"{env.name}.png"), transparent=True)
        plt.close()
