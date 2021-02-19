# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Map

Abstract zones to simulate simply a Minecraft environment.

"""

from crafting.world.map import Zone
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *

# Zones
FOREST = Zone(0, 'forest',
    {
        WOOD.item_id: [AIR] + AXES,
        DIRT.item_id: [AIR],
        COBBLESTONE.item_id: PICKAXES
    }
)

RIVER = Zone(1, 'river',
    {
        DIRT.item_id: [AIR],
        REEDS.item_id: [AIR]
    }
)

MEADOW = Zone(2, 'meadow',
    {
        DIRT.item_id: [AIR],
        LEATHER.item_id: SWORDS,
        EGG.item_id: [AIR]
    }
)

UNDERGROUND = Zone(3, 'underground',
    {
        DIRT.item_id: [AIR],
        COBBLESTONE.item_id: PICKAXES,
        IRON_ORE.item_id: PICKAXES[1:],
        GOLD_ORE.item_id: PICKAXES[2:],
    }
)

BEDROCK = Zone(4, 'bedrock',
    {
        DIRT.item_id: [AIR],
        COBBLESTONE.item_id: PICKAXES,
        IRON_ORE.item_id: PICKAXES[1:],
        GOLD_ORE.item_id: PICKAXES[2:],
        DIAMOND.item_id: PICKAXES[2:],
        REDSTONE.item_id: PICKAXES[2:],
        OBSIDIAN.item_id: [DIAMOND_PICKAXE],
    }
)

MC_ZONES = [
    FOREST,
    RIVER,
    MEADOW,
    UNDERGROUND,
    BEDROCK,
]

if __name__ == "__main__":
    print('Zones:', str(MC_ZONES))
