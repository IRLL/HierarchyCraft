# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Options

All useful options to get any item

"""

from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.items import MC_CRAFT_ITEMS, MC_FOUDABLE_ITEMS
from crafting.examples.minecraft.tools import MC_TOOLS

MC_WORLD = McWorld()
ALL_GET_OPTIONS = MC_WORLD.get_all_options()

if __name__ == "__main__":
    MC_GETABLE_ITEMS = MC_FOUDABLE_ITEMS + MC_CRAFT_ITEMS + MC_TOOLS[1:]
    for item in MC_GETABLE_ITEMS:
        option = ALL_GET_OPTIONS[item.item_id]
        print(option)
        print(option.get_graph())
