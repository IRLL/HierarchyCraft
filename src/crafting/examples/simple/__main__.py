# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""Main module for MineCrafting environment."""

import os
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
from hebg.metrics.complexity.complexities import learning_complexity
from hebg.metrics.histograms import behaviors_histograms
from hebg.unrolling import unroll_graph
from hebg import HEBGraph, Behavior

from crafting.env import CraftingEnv
from crafting.examples.simple import (
    LighterRecursiveCraftingEnv,
    LightRecursiveCraftingEnv,
    RecursiveCraftingEnv,
)


def get_solving_behavior(env: CraftingEnv) -> Behavior:
    all_behaviors = env.world.get_all_behaviors()
    goal_item = env.tasks[0].goal_item
    behavior_name = f"Get {goal_item}"
    return all_behaviors.get(behavior_name)


def get_nodes_histograms(env: CraftingEnv):
    all_behaviors = env.world.get_all_behaviors()
    all_behaviors_list = list(all_behaviors.values())
    return behaviors_histograms(all_behaviors_list)


def save_solve_codegens(graph: HEBGraph, savepath: Path):
    os.makedirs(savepath.parent, exist_ok=True)
    with open(savepath, "w", encoding="utf-8") as file:
        file.write(graph.generate_source_code())
        print(f"Saved generated source code at {savepath}")


def save_solve_graph(graph: HEBGraph, savepath: Path, figsize=(16, 3)):
    fig, ax = plt.subplots(figsize=figsize)
    graph.draw(ax, draw_hulls=True)
    plt.tight_layout()
    os.makedirs(savepath.parent, exist_ok=True)
    plt.savefig(savepath, dpi=240)
    print(f"Saved solve_graph at {savepath}")
    plt.close(fig)


def save_requirement_graph(env: CraftingEnv, savepath: Path):
    fig, ax = plt.subplots(figsize=(16, 9))
    env.world.draw_requirements_graph(ax)
    path = savepath / f"n={env.world.n_items}_requirement_graph.png"
    os.makedirs(savepath, exist_ok=True)
    plt.savefig(path, dpi=240)
    print(f"Saved requirement_graph at {path}")
    plt.close(fig)


def save__all_envs_graphs():
    for n_items in range(3, 11):
        envs: List[CraftingEnv] = [
            LightRecursiveCraftingEnv(n_items, 1),
            LightRecursiveCraftingEnv(n_items, 2),
            LightRecursiveCraftingEnv(n_items, 3),
            LighterRecursiveCraftingEnv(n_items, 3),
            LighterRecursiveCraftingEnv(n_items, 4),
            RecursiveCraftingEnv(n_items),
        ]
        for env in envs:
            used_nodes_all = get_nodes_histograms(env)
            solving_behavior = get_solving_behavior(env)
            lcomp, comp_saved = learning_complexity(solving_behavior, used_nodes_all)
            print(f"|-|{env.name}|-| {solving_behavior}: {lcomp} ({comp_saved})")
            filename = f"n={env.world.n_items}"
            filename += f"_t={lcomp + comp_saved}_s={comp_saved}_l={lcomp}"
            plot_path = Path("Images") / "graphs" / env.name
            figsize = (
                16 / 2 * (env.world.n_items + 1),
                9 / 2 * (env.world.n_items + 1),
            )
            save_requirement_graph(env, plot_path / "requirement_graph")
            save_solve_graph(
                solving_behavior.graph,
                plot_path / "solve" / (filename + ".png"),
                figsize=figsize,
            )
            codepath = Path("generated_codes/simple")
            save_solve_codegens(solving_behavior.graph, codepath / f"{filename}.py")
            save_solve_codegens(
                unroll_graph(solving_behavior.graph),
                codepath / f"{filename}_unrolled.py",
            )


if __name__ == "__main__":
    save__all_envs_graphs()
