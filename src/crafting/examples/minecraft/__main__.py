# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""Main module for MineCrafting environment."""

import os

import matplotlib.pyplot as plt
from hebg.metrics.complexity.complexities import learning_complexity
from hebg.metrics.histograms import behaviors_histograms

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.render.render import render_env_with_human
from crafting.task import TaskObtainItem

env = MineCraftingEnv(verbose=1, max_step=50, render_mode="rgb_array")
env.add_task(TaskObtainItem(env.world, env.world.item_from_name["enchanting_table"]))

plot_hebgraphs_path = os.path.join("Images", "HEBGraphs")
unrolled_graphs = True
plot_requirement_graph = False

if plot_hebgraphs_path is not None:
    os.makedirs(plot_hebgraphs_path, exist_ok=True)

all_behaviors = env.world.get_all_behaviors()
all_behaviors_list = list(all_behaviors.values())
used_nodes_all = behaviors_histograms(all_behaviors_list)

for behavior_name, behavior in all_behaviors.items():
    if behavior_name == f"Get {env.world.item_from_id[270]}":
        lcomp, comp_saved = learning_complexity(behavior, used_nodes_all)
        print(f"{behavior_name}: {lcomp} ({comp_saved})")
        if plot_hebgraphs_path is not None:
            fig, ax = plt.subplots(figsize=(16, 9))
            fname = behavior_name.replace(" ", "_").lower()

            graph = behavior.graph
            if unrolled_graphs:
                graph = graph.unrolled_graph
                fname += "_unrolled"

            graph.draw(ax, draw_hulls=True)
            path = os.path.join(plot_hebgraphs_path, fname)
            plt.tight_layout()
            plt.savefig(path, dpi=240)
            print(f"Saved heb_graph at {path}")

if plot_requirement_graph:
    env.world.draw_requirements_graph()

render_env_with_human(env)
