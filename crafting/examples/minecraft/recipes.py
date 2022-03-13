# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Recipes

All used Minecraft recipies.

"""

from crafting.world.items import ItemStack
from crafting.world.recipes import Recipe

from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *

# Hand-Crafting items
#: Recipe of WOOD_PLANK
R_WOOD_PLANK = Recipe(
    5, inputs=[ItemStack(WOOD, 1)], outputs=[ItemStack(WOOD_PLANK, 4)]
)
#: Recipe of STICK
R_STICK = Recipe(280, inputs=[ItemStack(WOOD_PLANK, 2)], outputs=[ItemStack(STICK, 4)])
R_HAND = [R_WOOD_PLANK, R_STICK]

# Zone modifiers
#: Recipe of CRAFTING_TABLE (enable 'has_crafting' zone property)
R_CRAFTING_TABLE = Recipe(
    58,
    inputs=[ItemStack(WOOD_PLANK, 4)],
    added_properties={"has_crafting": True},
)
#: Recipe of FURNACE (enable 'has_furnace' zone property)
R_FURNACE = Recipe(
    61,
    inputs=[ItemStack(COBBLESTONE, 8)],
    added_properties={"has_furnace": True},
    needed_properties={"has_crafting": True},
)
R_ZONE = [R_CRAFTING_TABLE, R_FURNACE]

# Smelting
#: Recipe of IRON_INGOT using PLANK
R_IRON_INGOT_PLANK = Recipe(
    265,
    inputs=[ItemStack(IRON_ORE, 3), ItemStack(WOOD_PLANK, 2)],
    outputs=[ItemStack(IRON_INGOT, 3)],
    needed_properties={"has_furnace": True},
)
#: Recipe of GOLD_INGOT using PLANK
R_GOLD_INGOT_PLANK = Recipe(
    266,
    inputs=[ItemStack(GOLD_ORE, 3), ItemStack(WOOD_PLANK, 2)],
    outputs=[ItemStack(GOLD_INGOT, 3)],
    needed_properties={"has_furnace": True},
)
R_SMELTING = [R_IRON_INGOT_PLANK, R_GOLD_INGOT_PLANK]

# Wooden Tools
#: Recipe of WOODEN_PICKAXE
R_WOODEN_PICKAXE = Recipe(
    270,
    inputs=[ItemStack(WOOD_PLANK, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(WOODEN_PICKAXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of WOODEN_AXE
R_WOODEN_AXE = Recipe(
    271,
    inputs=[ItemStack(WOOD_PLANK, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(WOODEN_AXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of WOODEN_SWORD
R_WOODEN_SWORD = Recipe(
    268,
    inputs=[ItemStack(WOOD_PLANK, 2), ItemStack(STICK, 1)],
    outputs=[ItemStack(WOODEN_SWORD)],
    needed_properties={"has_crafting": True},
)
R_WOODEN_TOOLS = [R_WOODEN_PICKAXE, R_WOODEN_AXE, R_WOODEN_SWORD]

# Stone Tools
#: Recipe of STONE_PICKAXE
R_STONE_PICKAXE = Recipe(
    274,
    inputs=[ItemStack(COBBLESTONE, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(STONE_PICKAXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of STONE_AXE
R_STONE_AXE = Recipe(
    275,
    inputs=[ItemStack(COBBLESTONE, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(STONE_AXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of STONE_SWORD
R_STONE_SWORD = Recipe(
    272,
    inputs=[ItemStack(COBBLESTONE, 2), ItemStack(STICK, 1)],
    outputs=[ItemStack(STONE_SWORD)],
    needed_properties={"has_crafting": True},
)
R_STONE_TOOLS = [R_STONE_PICKAXE, R_STONE_AXE, R_STONE_SWORD]

# Iron Tools
#: Recipe of IRON_PICKAXE
R_IRON_PICKAXE = Recipe(
    257,
    inputs=[ItemStack(IRON_INGOT, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(IRON_PICKAXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of IRON_AXE
R_IRON_AXE = Recipe(
    258,
    inputs=[ItemStack(IRON_INGOT, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(IRON_AXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of IRON_SWORD
R_IRON_SWORD = Recipe(
    267,
    inputs=[ItemStack(IRON_INGOT, 2), ItemStack(STICK, 1)],
    outputs=[ItemStack(IRON_SWORD)],
    needed_properties={"has_crafting": True},
)
R_IRON_TOOLS = [R_IRON_PICKAXE, R_IRON_AXE, R_IRON_SWORD]

# Gold Tools
#: Recipe of GOLD_PICKAXE
R_GOLD_PICKAXE = Recipe(
    285,
    inputs=[ItemStack(GOLD_INGOT, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(GOLD_PICKAXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of GOLD_AXE
R_GOLD_AXE = Recipe(
    286,
    inputs=[ItemStack(GOLD_INGOT, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(GOLD_AXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of GOLD_SWORD
R_GOLD_SWORD = Recipe(
    283,
    inputs=[ItemStack(GOLD_INGOT, 2), ItemStack(STICK, 1)],
    outputs=[ItemStack(GOLD_SWORD)],
    needed_properties={"has_crafting": True},
)
R_GOLD_TOOLS = [R_GOLD_PICKAXE, R_GOLD_AXE, R_GOLD_SWORD]

# Diamond Tools
#: Recipe of DIAMOND_PICKAXE
R_DIAMOND_PICKAXE = Recipe(
    278,
    inputs=[ItemStack(DIAMOND, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(DIAMOND_PICKAXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of DIAMOND_AXE
R_DIAMOND_AXE = Recipe(
    279,
    inputs=[ItemStack(DIAMOND, 3), ItemStack(STICK, 2)],
    outputs=[ItemStack(DIAMOND_AXE)],
    needed_properties={"has_crafting": True},
)
#: Recipe of DIAMOND_SWORD
R_DIAMOND_SWORD = Recipe(
    276,
    inputs=[ItemStack(DIAMOND, 2), ItemStack(STICK, 1)],
    outputs=[ItemStack(DIAMOND_SWORD)],
    needed_properties={"has_crafting": True},
)
R_DIAMOND_TOOLS = [R_DIAMOND_PICKAXE, R_DIAMOND_AXE, R_DIAMOND_SWORD]

R_TOOLS = R_WOODEN_TOOLS + R_STONE_TOOLS + R_IRON_TOOLS + R_GOLD_TOOLS + R_DIAMOND_TOOLS

# Enchanting recipes
#: Recipe of PAPER
R_PAPER = Recipe(
    339,
    inputs=[ItemStack(REEDS, 3)],
    outputs=[ItemStack(PAPER, 3)],
    needed_properties={"has_crafting": True},
)
#: Recipe of BOOK
R_BOOK = Recipe(
    340,
    inputs=[ItemStack(PAPER, 3), ItemStack(LEATHER, 1)],
    outputs=[ItemStack(BOOK, 1)],
    needed_properties={"has_crafting": True},
)
#: Recipe of ENCHANTING_TABLE
R_ENCHANTING_TABLE = Recipe(
    116,
    inputs=[ItemStack(BOOK, 1), ItemStack(OBSIDIAN, 4), ItemStack(DIAMOND, 2)],
    outputs=[ItemStack(ENCHANTING_TABLE, 1)],
    needed_properties={"has_crafting": True},
)
R_ENCHANT = [R_PAPER, R_BOOK, R_ENCHANTING_TABLE]

# Other recipes
#: Recipe of CLOCK
R_CLOCK = Recipe(
    347,
    inputs=[ItemStack(GOLD_INGOT, 4), ItemStack(REDSTONE, 1)],
    outputs=[ItemStack(CLOCK, 1)],
    needed_properties={"has_crafting": True},
)
R_OTHERS = [R_CLOCK]

MC_RECIPES = R_HAND + R_ZONE + R_SMELTING + R_TOOLS + R_ENCHANT + R_OTHERS

if __name__ == "__main__":
    print(MC_RECIPES)
