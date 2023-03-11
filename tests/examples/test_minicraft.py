import pytest
import pytest_check as check

import os
import networkx as nx
from hebg.unrolling import unroll_graph

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.examples.minicraft import MINICRAFT_ENVS


@pytest.mark.parametrize("env_class", MINICRAFT_ENVS)
def test_build_env(env_class):
    human_run = False
    env = env_class()
    if human_run:
        render_env_with_human(env)


@pytest.mark.parametrize("env_class", MINICRAFT_ENVS[:-2])
def test_can_solve(env_class):
    env: CraftingEnv = env_class(max_step=20)
    solving_behavior = env.solving_behavior(env.task)
    done = False
    observation = env.reset()
    while not done:
        action = solving_behavior(observation)
        observation, _reward, done, _ = env.step(action)

    if not env.task.terminated:
        print("\nCould not solve !\n\nBehavior:")
        unrolled = unroll_graph(solving_behavior.graph, add_prefix=True)
        for u, v in nx.bfs_edges(unrolled, source=unrolled.roots[0]):
            index = unrolled.edges[(u, v)]["index"]
            u_name = str(u).split(">")[-2:]
            v_name = str(v).split(">")[-2:]
            print(u_name, f"-{index}->", v_name)
    check.is_true(env.task.terminated)


@pytest.mark.parametrize("env_class", MINICRAFT_ENVS)
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
