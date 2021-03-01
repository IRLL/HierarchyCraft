# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Zones

Abstract zones to simulate simply a Minecraft environment.

"""

from crafting.world.zones import Zone
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *

# Zones
#: FOREST
FOREST = Zone(0, 'forest',
    {
        WOOD.item_id: [AIR] + AXES,
        DIRT.item_id: [AIR],
        STONE.item_id: PICKAXES,
    }
)

#: SWAMP
SWAMP = Zone(1, 'swamp',
    {
        DIRT.item_id: [AIR],
        REEDS.item_id: [AIR]
    }
)

#: MEADOW
MEADOW = Zone(2, 'meadow',
    {
        DIRT.item_id: [AIR],
        STONE.item_id: PICKAXES,
        LEATHER.item_id: SWORDS,
        EGG.item_id: [AIR]
    }
)

#: UNDERGROUND
UNDERGROUND = Zone(3, 'underground',
    {
        DIRT.item_id: [AIR],
        STONE.item_id: PICKAXES,
        IRON_ORE.item_id: PICKAXES[1:],
        GOLD_ORE.item_id: PICKAXES[2:],
    }
)

#: BEDROCK
BEDROCK = Zone(4, 'bedrock',
    {
        DIRT.item_id: [AIR],
        STONE.item_id: PICKAXES,
        IRON_ORE.item_id: PICKAXES[1:],
        GOLD_ORE.item_id: PICKAXES[2:],
        DIAMOND_ORE.item_id: PICKAXES[2:],
        REDSTONE_ORE.item_id: PICKAXES[2:],
        OBSIDIAN.item_id: [DIAMOND_PICKAXE],
    }
)

MC_ZONES = [
    FOREST,
    SWAMP,
    MEADOW,
    UNDERGROUND,
    BEDROCK,
]

if __name__ == "__main__":
    print('Zones:', str(MC_ZONES))
