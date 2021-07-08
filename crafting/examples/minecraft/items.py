# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Items

All used minecraft items.
They are three kinds of items: Loots and Blocks that can be found,
and other items that can only be obtain through crafting.

"""

from crafting.examples.minecraft.abc import Block, Item, Loot
from crafting.examples.minecraft.tools import *

#: Items
DIAMOND = Item(264, 'diamond') #: DIAMOND
IRON_INGOT = Item(265, 'iron_ingot') #: IRON_INGOT
GOLD_INGOT = Item(266, 'gold_ingot') #: GOLD_INGOT
PAPER = Item(339, 'paper') #: PAPER
BOOK = Item(340, 'book') #: BOOK
REDSTONE = Item(331, 'redstone') #: REDSTONE
CLOCK = Item(347, 'clock') #: CLOCK
ENCHANTING_TABLE = Item(116, 'enchanting_table') #: ENCHANTING_TABLE
STICK = Item(280, 'stick') #: STICK

#: Blocks
DIRT = Block(3, 'dirt', hardness=0.5) #: DIRT
COBBLESTONE = Block(4, 'cobblestone', hardness=2, required_tools=PICKAXES) #: COBBLESTONE
STONE = Block(1, 'stone', hardness=1.5, drops=[COBBLESTONE], required_tools=PICKAXES) #: STONE
WOOD_PLANK = Block(5, 'wood_plank', hardness=2, required_tools=[None] + AXES) #: WOOD_PLANK
GOLD_ORE = Block(14, 'gold_ore', hardness=3, required_tools=PICKAXES[2:]) #: GOLD_ORE
IRON_ORE = Block(15, 'iron_ore', hardness=3, required_tools=PICKAXES[1:]) #: IRON_ORE
WOOD = Block(17, 'wood', hardness=2, required_tools=[None] + AXES) #: WOOD
DIAMOND_ORE = Block(56, 'diamond_ore', hardness=3,
    drops=[DIAMOND], required_tools=PICKAXES[2:]) #: DIAMOND_ORE
OBSIDIAN = Block(49, 'obsidian', hardness=50, required_tools=[DIAMOND_PICKAXE]) #: OBSIDIAN
REDSTONE_ORE = Block(73, 'redstone_ore', hardness=3,
    drops=[REDSTONE], required_tools=PICKAXES[2:]) #: REDSTONE_ORE

#: Loots
REEDS = Loot(83, 'reeds', stack_size=3) #: REEDS
EGG = Loot(344, 'egg') #: EGG
LEATHER = Loot(334, 'leather', stack_size=2, required_tools=SWORDS) #: LEATHER

MC_BLOCKS = [
    DIRT,
    STONE,
    COBBLESTONE,
    GOLD_ORE,
    IRON_ORE,
    WOOD,
    DIAMOND_ORE,
    OBSIDIAN,
    REDSTONE_ORE,
]

MC_BASE_ITEMS = [
    DIAMOND,
    REDSTONE,
    REEDS,
    EGG,
    LEATHER,
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

MC_FOUDABLE_ITEMS = [
    DIRT,
    EGG,
    COBBLESTONE,
    GOLD_ORE,
    IRON_ORE,
    WOOD,
    DIAMOND,
    OBSIDIAN,
    REDSTONE,
    REEDS,
    LEATHER,
]

MC_SEARCHABLE_ITEMS = [
    DIRT,
    EGG,
    STONE,
    GOLD_ORE,
    IRON_ORE,
    WOOD,
    DIAMOND_ORE,
    OBSIDIAN,
    REDSTONE_ORE,
    REEDS,
    LEATHER,
]

MC_ITEMS = MC_BLOCKS + MC_BASE_ITEMS + MC_CRAFT_ITEMS

if __name__ == "__main__":
    print('Blocks: ', str(MC_BLOCKS))
    print('Base items: ', str(MC_BASE_ITEMS))
    print('Craft items: ', str(MC_CRAFT_ITEMS))
