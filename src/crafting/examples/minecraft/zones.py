# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Zones

Abstract zones to simulate simply a Minecraft environment.

"""

from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *
from crafting.world.zones import Zone

# Zones

#: FOREST
FOREST = Zone(0, "forest", [WOOD, DIRT, STONE])

#: SWAMP
SWAMP = Zone(1, "swamp", [DIRT, GRAVEL, REEDS])

#: MEADOW
MEADOW = Zone(2, "meadow", [DIRT, STONE, LEATHER, EGG])

#: UNDERGROUND
UNDERGROUND = Zone(
    3,
    "underground",
    [GRAVEL, STONE, IRON_ORE, ENDER_PEARL],
    required_tools=PICKAXES,
    properties={"close_ender_portal": True},
)

#: BEDROCK
BEDROCK = Zone(
    4,
    "bedrock",
    [STONE, IRON_ORE, GOLD_ORE, DIAMOND_ORE, REDSTONE_ORE, OBSIDIAN],
    required_tools=[IRON_PICKAXE, DIAMOND_PICKAXE],
)

#: NETHER
NETHER = Zone(
    5,
    "nether",
    items=[NETHERRACK, BLAZE_ROD],
    required_properties={"open_nether_portal": True},
)

#: ENDER
ENDER = Zone(
    6,
    "ender",
    items=[ENDER_PEARL, ENDER_DRAGON_HEAD],
    required_properties={"open_ender_portal": True},
)

MC_ZONES = [
    FOREST,
    SWAMP,
    MEADOW,
    UNDERGROUND,
    BEDROCK,
    NETHER,
    ENDER,
]

if __name__ == "__main__":
    print("Zones:", str(MC_ZONES))
