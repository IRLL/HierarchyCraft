# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""Main module for MineCrafting environment."""

import os
from crafting.task import TaskObtainItem
import matplotlib.pyplot as plt

from option_graph.metrics.complexity.histograms import nodes_histograms
from option_graph.metrics.complexity.complexities import learning_complexity

from crafting.render.render import render_env_with_human
from crafting.examples.minecraft.env import MineCraftingEnv

env = MineCraftingEnv(
    verbose=1,
    max_step=50
)
env.add_task(TaskObtainItem(env.world, env.world.item_from_name["enchanting_table"]))

plot_options_graphs_path = os.path.join("Images", "OptionsGraphs")
unrolled_graphs = True
plot_requirement_graph = False

if plot_options_graphs_path is not None:
    os.makedirs(plot_options_graphs_path, exist_ok=True)

all_options = env.world.get_all_options()
all_options_list = list(all_options.values())
used_nodes_all = nodes_histograms(all_options_list)

for option_name, option in all_options.items():
    if option_name == f"Get {env.world.item_from_id[270]}":
        lcomp, comp_saved = learning_complexity(option, used_nodes_all)
        print(f"{option_name}: {lcomp} ({comp_saved})")
        if plot_options_graphs_path is not None:
            fig, ax = plt.subplots(figsize=(16, 9))
            fname = option_name.replace(" ", "_").lower()

            graph = option.graph
            if unrolled_graphs:
                graph = graph.unrolled_graph
                fname += "_unrolled"

            graph.draw(ax, draw_options_hulls=True)
            path = os.path.join(plot_options_graphs_path, fname)
            plt.tight_layout()
            plt.savefig(path, dpi=240)
            print(f"Saved option_graph at {path}")

if plot_requirement_graph:
    env.world.draw_requirements_graph()

render_env_with_human(env)
