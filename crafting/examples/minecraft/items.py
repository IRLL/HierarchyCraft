# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Items

All used minecraft items.
They are two kinds of items: Base items that can be found
and Craft items that can only be obtain through crafting.

"""

from crafting.world.items import Item

# Items
DIRT = Item(3, 'dirt', max_stack=64)
COBBLESTONE = Item(4, 'cobblestone', max_stack=64)
WOOD_PLANK = Item(5, 'wood_plank', max_stack=64)
GOLD_ORE = Item(14, 'gold_ore', max_stack=64)
IRON_ORE = Item(15, 'iron_ore', max_stack=64)
WOOD = Item(17, 'wood', max_stack=64)
DIAMOND = Item(264, 'diamond', max_stack=64)
IRON_INGOT = Item(265, 'iron_ingot', max_stack=64)
GOLD_INGOT = Item(266, 'gold_ingot', max_stack=64)
REEDS = Item(83, 'reeds', max_stack=64)
EGG = Item(344, 'egg', max_stack=64)
PAPER = Item(339, 'paper', max_stack=64)
BOOK = Item(340, 'book', max_stack=64)
LEATHER = Item(334, 'leather', max_stack=64)
OBSIDIAN = Item(49, 'obsidian', max_stack=64)
REDSTONE = Item(331, 'redstone', max_stack=64)
CLOCK = Item(347, 'clock', max_stack=64)
ENCHANTING_TABLE = Item(116, 'enchanting_table', max_stack=64)
STICK = Item(280, 'stick', max_stack=64)

MC_BASE_ITEMS = [
    DIRT,
    COBBLESTONE,
    GOLD_ORE,
    IRON_ORE,
    WOOD,
    DIAMOND,
    REEDS,
    EGG,
    LEATHER,
    OBSIDIAN,
    REDSTONE,
]

MC_CRAFT_ITEMS = [
    WOOD_PLANK,
    STICK,
    IRON_INGOT,
    GOLD_INGOT,
    PAPER,
    BOOK,
    CLOCK,
    ENCHANTING_TABLE
]

MC_ITEMS = MC_BASE_ITEMS + MC_CRAFT_ITEMS

if __name__ == "__main__":
    print('Base items: ', str(MC_BASE_ITEMS))
    print('Craft items: ', str(MC_CRAFT_ITEMS))
