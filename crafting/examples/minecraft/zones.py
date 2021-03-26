# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Zones

Abstract zones to simulate simply a Minecraft environment.

"""

from crafting.world.zones import Zone
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *

# Zones

FOREST = Zone(0, 'forest', [WOOD, DIRT, STONE]) #: FOREST
SWAMP = Zone(1, 'swamp', [DIRT, REEDS]) #: SWAMP
MEADOW = Zone(2, 'meadow', [DIRT, STONE, LEATHER, EGG]) #: MEADOW
UNDERGROUND = Zone(3, 'underground',
    [DIRT, STONE, IRON_ORE, GOLD_ORE]) #: UNDERGROUND
BEDROCK = Zone(4, 'bedrock',
    [DIRT, STONE, IRON_ORE, GOLD_ORE,
     DIAMOND_ORE, REDSTONE_ORE, OBSIDIAN]) #: BEDROCK

MC_ZONES = [
    FOREST,
    SWAMP,
    MEADOW,
    UNDERGROUND,
    BEDROCK,
]

if __name__ == "__main__":
    print('Zones:', str(MC_ZONES))
