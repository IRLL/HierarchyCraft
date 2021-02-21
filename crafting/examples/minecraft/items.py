# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Items

All used minecraft items.
They are two kinds of items: Base items that can be found
and Craft items that can only be obtain through crafting.

"""

from crafting.examples.minecraft.abc import Block, Item

# Items
DIRT = Block(3, 'dirt', hardness=0.5)
COBBLESTONE = Block(4, 'cobblestone', hardness=2)
STONE = Block(1, 'stone', hardness=1.5, drops=[COBBLESTONE])
WOOD_PLANK = Block(5, 'wood_plank', hardness=2)
GOLD_ORE = Block(14, 'gold_ore', hardness=3)
IRON_ORE = Block(15, 'iron_ore', hardness=3)
WOOD = Block(17, 'wood', hardness=2)
DIAMOND = Item(264, 'diamond', max_stack=64)
DIAMOND_ORE = Block(264, 'diamond', hardness=3, drops=[DIAMOND])
IRON_INGOT = Item(265, 'iron_ingot', max_stack=64)
GOLD_INGOT = Item(266, 'gold_ingot', max_stack=64)
REEDS = Item(83, 'reeds', max_stack=64)
EGG = Item(344, 'egg', max_stack=64)
PAPER = Item(339, 'paper', max_stack=64)
BOOK = Item(340, 'book', max_stack=64)
LEATHER = Item(334, 'leather', max_stack=64)
OBSIDIAN = Block(49, 'obsidian', hardness=50)
REDSTONE = Item(331, 'redstone', max_stack=64)
REDSTONE_ORE = Block(331, 'redstone', hardness=3, drops=[REDSTONE])
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
