""" Minecraft Items

All used minecraft items.
They are three kinds of items: Loots and McItems that can be found,
and other items that can only be obtain through hcraft.

"""
from dataclasses import dataclass
from typing import List, Optional, Union

from hcraft.elements import Item, Zone
from hcraft.examples.minecraft.tools import Material, ToolType
from hcraft.examples.minecraft.zones import (
    FOREST,
    SWAMP,
    MEADOW,
    UNDERGROUND,
    BEDROCK,
    NETHER,
    END,
)

#: Items obtainable only with crafts
IRON_INGOT = Item("iron_ingot")
"""IRON_INGOT"""

GOLD_INGOT = Item("gold_ingot")
"""GOLD_INGOT"""

PAPER = Item("paper")
"""PAPER"""

BOOK = Item("book")
"""BOOK"""

CLOCK = Item("clock")
"""CLOCK"""

ENCHANTING_TABLE = Item("enchanting_table")
"""ENCHANTING_TABLE"""

CRAFTING_TABLE = Item("crafting_table")
"""CRAFTING_TABLE"""

FURNACE = Item("furnace")
"""CRAFTING_TABLE"""

STICK = Item("stick")
"""STICK"""

BLAZE_POWDER = Item("blaze_powder")
"""BLAZE_POWDER"""

ENDER_EYE = Item("ender_eye")
"""ENDER_EYE"""

FLINT = Item("flint")
"""FLINT"""

FLINT_AND_STEEL = Item("flint_and_steel")
"""FLINT_AND_STEEL"""

WOOD_PLANK = Item("wood_plank")
"""WOOD_PLANK"""


@dataclass
class McItem:
    """Minecraft item with its specific properties."""

    item: Item
    zones: List[Zone]
    required_tool_types: Optional[List[Union[None, ToolType]]] = None
    required_tool_material: Optional[List[Material]] = None
    hardness: float = 1.0


DIRT = Item("dirt")
MC_DIRT = McItem(
    DIRT,
    zones=[FOREST, SWAMP, MEADOW],
    required_tool_types=[None, ToolType.SHOVEL],
    hardness=0.5,
)
"""DIRT"""

WOOD = Item("wood")
MC_WOOD = McItem(
    WOOD, zones=[FOREST, SWAMP], hardness=2, required_tool_types=[None, ToolType.AXE]
)
"""WOOD"""

GRAVEL = Item("gravel")
MC_GRAVEL = McItem(
    GRAVEL,
    zones=[SWAMP],
    hardness=0.6,
    required_tool_types=[ToolType.SHOVEL],
)
"""GRAVEL"""

COBBLESTONE = Item("cobblestone")
MC_COBBLESTONE = McItem(
    COBBLESTONE,
    zones=[FOREST, SWAMP, MEADOW, UNDERGROUND, BEDROCK],
    hardness=2,
    required_tool_types=[ToolType.PICKAXE],
)
"""COBBLESTONE"""

COAL = Item("coal")
MC_COAL = McItem(
    COAL,
    zones=[UNDERGROUND, BEDROCK],
    hardness=3,
    required_tool_types=[ToolType.PICKAXE],
)
"""COAL"""

IRON_ORE = Item("iron_ore")
MC_IRON_ORE = McItem(
    IRON_ORE,
    zones=[UNDERGROUND, BEDROCK],
    hardness=3,
    required_tool_types=[ToolType.PICKAXE],
    required_tool_material=[Material.STONE, Material.IRON, Material.DIAMOND],
)
"""IRON_ORE"""

GOLD_ORE = Item("gold_ore")
MC_GOLD_ORE = McItem(
    GOLD_ORE,
    zones=[BEDROCK, NETHER],
    hardness=3,
    required_tool_types=[ToolType.PICKAXE],
    required_tool_material=[Material.IRON, Material.DIAMOND],
)
"""GOLD_ORE"""

DIAMOND = Item("diamond")
MC_DIAMOND = McItem(
    DIAMOND,
    zones=[BEDROCK],
    hardness=3,
    required_tool_types=[ToolType.PICKAXE],
    required_tool_material=[Material.IRON, Material.DIAMOND],
)
"""DIAMOND_ORE"""

OBSIDIAN = Item("obsidian")
MC_OBSIDIAN = McItem(
    OBSIDIAN,
    zones=[BEDROCK],
    hardness=50,
    required_tool_types=[ToolType.PICKAXE],
    required_tool_material=[Material.DIAMOND],
)
"""OBSIDIAN"""

REDSTONE = Item("redstone")
MC_REDSTONE = McItem(
    REDSTONE,
    zones=[BEDROCK],
    hardness=3,
    required_tool_types=[ToolType.PICKAXE],
    required_tool_material=[Material.IRON, Material.DIAMOND],
)
"""REDSTONE_ORE"""

NETHERRACK = Item("netherrack")
MC_NETHERRACK = McItem(
    NETHERRACK,
    zones=[NETHER],
    hardness=0.4,
    required_tool_types=[ToolType.PICKAXE],
)
"""NETHERRACK"""


REEDS = Item("reeds")
MC_REEDS = McItem(REEDS, hardness=1 / 3, zones=[SWAMP])
"""REEDS"""

EGG = Item("egg")
MC_EGG = McItem(EGG, zones=[MEADOW])
"""EGG"""

LEATHER = Item("leather")
MC_LEATHER = McItem(
    LEATHER,
    hardness=2,
    zones=[MEADOW],
    required_tool_types=[ToolType.SWORD],
)
"""LEATHER"""

BLAZE_ROD = Item("blaze_rod")
MC_BLAZE_ROD = McItem(
    BLAZE_ROD,
    hardness=4,
    zones=[NETHER],
    required_tool_types=[ToolType.SWORD],
    required_tool_material=[Material.GOLD],
)
"""BLAZE_ROD"""

ENDER_PEARL = Item("ender_pearl")
MC_ENDER_PEARL = McItem(
    ENDER_PEARL,
    hardness=4,
    zones=[UNDERGROUND, END],
    required_tool_types=[ToolType.SWORD],
    required_tool_material=[Material.IRON, Material.DIAMOND],
)
"""ENDER_PEARL"""

ENDER_DRAGON_HEAD = Item("ender_dragon_head")
MC_ENDER_DRAGON_HEAD = McItem(
    ENDER_DRAGON_HEAD,
    hardness=8,
    zones=[END],
    required_tool_types=[ToolType.SWORD],
    required_tool_material=[Material.DIAMOND],
)
"""ENDER_DRAGON_HEAD"""

MC_ITEMS = [
    MC_DIRT,
    MC_WOOD,
    MC_GRAVEL,
    MC_COBBLESTONE,
    MC_COAL,
    MC_IRON_ORE,
    MC_GOLD_ORE,
    MC_DIAMOND,
    MC_OBSIDIAN,
    MC_REDSTONE,
    MC_NETHERRACK,
    MC_REEDS,
    MC_EGG,
    MC_LEATHER,
    MC_BLAZE_ROD,
    MC_ENDER_PEARL,
    MC_ENDER_DRAGON_HEAD,
]

#: Buildings
CLOSE_NETHER_PORTAL = Item("close_nether_portal")
"""NETHER_PORTAL"""

OPEN_NETHER_PORTAL = Item("open_nether_portal")
"""OPEN_NETHER_PORTAL"""

CLOSE_ENDER_PORTAL = Item("close_ender_portal")
"""ENDER_PORTAL"""

OPEN_ENDER_PORTAL = Item("open_ender_portal")
"""OPEN_ENDER_PORTAL"""
