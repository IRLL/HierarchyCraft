# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Options

All useful options to get any item

"""

from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.items import MC_CRAFT_ITEMS, MC_FOUDABLE_ITEMS, COBBLESTONE
from crafting.examples.minecraft.tools import MC_TOOLS, WOODEN_PICKAXE

MC_WORLD = McWorld()
ALL_GET_OPTIONS = MC_WORLD.get_all_options()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    MC_GETABLE_ITEMS = MC_FOUDABLE_ITEMS + MC_CRAFT_ITEMS + MC_TOOLS[1:]
    for item in MC_GETABLE_ITEMS:
        option = ALL_GET_OPTIONS[item.item_id]
        print(option)

        # if item.item_id in [COBBLESTONE.item_id, WOODEN_PICKAXE.item_id]:
        fig, ax = plt.subplots()
        option.draw_graph(ax)
        plt.title(str(item))
        plt.show()
