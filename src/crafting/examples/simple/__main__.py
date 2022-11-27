# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""Main module for MineCrafting environment."""

import os

from pathlib import Path
import matplotlib.pyplot as plt

from option_graph.metrics.complexity.histograms import nodes_histograms
from option_graph.metrics.complexity.complexities import learning_complexity

from crafting.env import CraftingEnv
from crafting.examples.simple.env import (
    StackedCraftingEnv,
    LightStackedCraftingEnv,
    LighterStackedCraftingEnv,
)


def save_solve_graph(env: CraftingEnv, plot_path: Path, unrolled_graphs=True):
    all_options = env.world.get_all_options()
    all_options_list = list(all_options.values())
    used_nodes_all = nodes_histograms(all_options_list)

    goal_item = env.tasks[0].goal_item
    option_name = f"Get {goal_item}"
    option = all_options.get(option_name)

    lcomp, comp_saved = learning_complexity(option, used_nodes_all)
    print(f"{option_name}: {lcomp} ({comp_saved})")

    figsize = (16 / 2 * (env.world.n_items + 1), 9 / 2 * (env.world.n_items + 1))
    _, ax = plt.subplots(figsize=figsize)
    fname = f"n={env.world.n_items}"
    fname += f"_t={lcomp + comp_saved}_s={comp_saved}_l={lcomp}"

    graph = option.graph
    if unrolled_graphs:
        graph = graph.unrolled_graph
        fname += "_unrolled"

    graph.draw(ax, draw_options_hulls=True)
    path = plot_path / fname
    plt.tight_layout()
    os.makedirs(plot_path, exist_ok=True)
    plt.savefig(path, dpi=240)
    print(f"Saved solve_graph at {path}")


def save_requirement_graph(env: CraftingEnv, plot_path: Path):
    _, ax = plt.subplots(figsize=(16, 9))
    env.world.draw_requirements_graph(ax)
    path = plot_path / f"n={n_items}_requirement_graph"
    os.makedirs(plot_path, exist_ok=True)
    plt.savefig(path, dpi=240)
    print(f"Saved requirement_graph at {path}")


if __name__ == "__main__":

    for n_items in range(9, 11):
        envs = [
            LightStackedCraftingEnv(n_items, 1),
            LightStackedCraftingEnv(n_items, 2),
            LightStackedCraftingEnv(n_items, 3),
            LighterStackedCraftingEnv(n_items, 3),
            LighterStackedCraftingEnv(n_items, 4),
            StackedCraftingEnv(n_items),
        ]
        for env in envs:
            plot_path = Path("Images") / "graphs" / env.name
            save_solve_graph(env, plot_path / "solve", unrolled_graphs=True)
            save_requirement_graph(env, plot_path / "requirement_graph")
