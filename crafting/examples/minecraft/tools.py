# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Tools

All used minecraft tools

"""

import numpy as np
from crafting.world.items import Tool

AIR = Tool(0, 'air', {'durability':np.inf, 'speed': 1})
WOODEN_PICKAXE = Tool(270, 'wooden_pickaxe', {'durability': 59, 'speed': 2})
WOODEN_AXE = Tool(271, 'wooden_axe', {'durability': 59, 'speed': 2})
WOODEN_SWORD = Tool(268, 'wooden_sword', {'durability': 59, 'speed': 2})
STONE_PICKAXE = Tool(274, 'stone_pickaxe', {'durability': 131, 'speed': 4})
STONE_AXE = Tool(275, 'stone_axe', {'durability': 131, 'speed': 4})
STONE_SWORD = Tool(272, 'stone_sword', {'durability': 131, 'speed': 4})
IRON_PICKAXE = Tool(257, 'iron_pickaxe', {'durability': 256, 'speed': 6})
IRON_AXE = Tool(258, 'iron_axe', {'durability': 256, 'speed': 6})
IRON_SWORD = Tool(267, 'iron_sword', {'durability': 256, 'speed': 6})
GOLD_PICKAXE = Tool(285, 'gold_pickaxe', {'durability': 32, 'speed': 12})
GOLD_AXE = Tool(286, 'gold_axe', {'durability': 32, 'speed': 12})
GOLD_SWORD = Tool(283, 'gold_sword', {'durability': 32, 'speed': 12})
DIAMOND_PICKAXE = Tool(278, 'diamond_pickaxe', {'durability': 1561, 'speed': 8})
DIAMOND_AXE = Tool(279, 'diamond_axe', {'durability': 1561, 'speed': 8})
DIAMOND_SWORD = Tool(276, 'diamond_sword', {'durability': 1561, 'speed': 8})

# Tools groups
PICKAXES = [
    WOODEN_PICKAXE, STONE_PICKAXE, IRON_PICKAXE,
    GOLD_PICKAXE, DIAMOND_PICKAXE
]

AXES = [
    WOODEN_AXE, STONE_AXE,
    IRON_AXE, GOLD_AXE, DIAMOND_AXE
]

SWORDS = [
    WOODEN_SWORD, STONE_SWORD, IRON_SWORD,
    GOLD_SWORD, DIAMOND_SWORD
]

MC_TOOLS = [
    WOODEN_PICKAXE,
    WOODEN_AXE,
    WOODEN_SWORD,
    STONE_PICKAXE,
    STONE_AXE,
    STONE_SWORD,
    IRON_PICKAXE,
    IRON_AXE,
    IRON_SWORD,
    GOLD_PICKAXE,
    GOLD_AXE,
    GOLD_SWORD,
    DIAMOND_PICKAXE,
    DIAMOND_AXE,
    DIAMOND_SWORD,
]

if __name__ == "__main__":
    print('Tools:', str(MC_TOOLS))
