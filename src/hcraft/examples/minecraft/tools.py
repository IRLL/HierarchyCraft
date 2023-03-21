""" Minecraft Tools

All used minecraft tools

"""

from enum import Enum
from typing import Dict, List

from hcraft.elements import Item


class Material(Enum):
    """Minecraft materials"""

    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    GOLD = "gold"
    DIAMOND = "diamond"


class ToolType(Enum):
    """Minecraft tools types"""

    PICKAXE = "pickaxe"
    AXE = "axe"
    SHOVEL = "shovel"
    SWORD = "sword"


MC_TOOLS: List[Item] = []
MC_TOOLS_BY_TYPE_AND_MATERIAL: Dict[ToolType, Dict[Material, Item]] = {}


def build_tools():
    for tool_type in ToolType:
        if tool_type not in MC_TOOLS_BY_TYPE_AND_MATERIAL:
            MC_TOOLS_BY_TYPE_AND_MATERIAL[tool_type] = {}
        for material in Material:
            item = Item(f"{material.value}_{tool_type.value}")
            MC_TOOLS_BY_TYPE_AND_MATERIAL[tool_type][material] = item
            MC_TOOLS.append(item)


build_tools()
