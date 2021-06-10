# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Options

All useful options to get any item

"""

from crafting.examples.minecraft.world import McWorld

MC_WORLD = McWorld()
ALL_OPTIONS = MC_WORLD.get_all_options()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    options_keys = np.array([option_key for option_key, _ in ALL_OPTIONS.items()])
    options_complexities = np.array([option.complexity()[0] for _, option in ALL_OPTIONS.items()])
    complexity_rank = np.argsort(options_complexities)

    print("Complexity \t| Option")
    print("--------------------------------")
    for rank in complexity_rank:
        option_key = options_keys[rank]
        try:
            option_key = int(option_key)
            option_name = MC_WORLD.item_from_id[option_key]
        except ValueError:
            option_name = option_key

        option = ALL_OPTIONS[option_key]
        title = str(option_name)
        complexity = options_complexities[rank]
        print(f"{complexity}\t\t| {title}")

        if hasattr(option, 'draw_graph'):
            title += f" - Complexity:{complexity}"
            fig, ax = plt.subplots()
            option.draw_graph(ax)
            plt.title(title)
            plt.show()
