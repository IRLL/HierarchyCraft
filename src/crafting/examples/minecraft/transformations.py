""" Minecraft Recipes

All used Minecraft recipies.

"""

from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *
from crafting.examples.minecraft.zones import *
from crafting.transformation import Transformation
from crafting.elements import ItemStack


def build_minecrafting_transformations() -> List[Transformation]:
    transformations = []
    transformations += _move_to_zones()
    transformations += _zones_search()
    transformations += _building()
    transformations += _crafting_recipes()
    transformations += _tools_recipes()
    return transformations


def _move_to_zones() -> List[Transformation]:
    walk = [
        #: Move to FOREST
        Transformation(
            destination=FOREST,
            zones=[zone for zone in OVERWORLD if zone != FOREST] + [END],
        ),
        #: Move to SWAMP
        Transformation(
            destination=SWAMP, zones=[zone for zone in OVERWORLD if zone != SWAMP]
        ),
        #: Move to MEADOW
        Transformation(
            destination=MEADOW, zones=[zone for zone in OVERWORLD if zone != MEADOW]
        ),
    ]

    required_pickaxe_materials = {
        UNDERGROUND: [Material.STONE, Material.IRON, Material.DIAMOND],
        BEDROCK: [Material.IRON, Material.DIAMOND],
    }

    #: Dig to UNDERGROUND or BEDROCK
    dig = []
    for zone, materials in required_pickaxe_materials.items():
        for material in materials:
            pickaxe = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][material]
            other_zones = [other_zone for other_zone in OVERWORLD if other_zone != zone]
            dig.append(
                Transformation(
                    destination=zone,
                    zones=other_zones,
                    removed_player_items=[ItemStack(pickaxe)],
                )
            )

    nether = [
        #: Move to NETHER
        Transformation(
            destination=NETHER,
            removed_zone_items=[ItemStack(OPEN_NETHER_PORTAL)],
            added_zone_items=[ItemStack(OPEN_NETHER_PORTAL)],
        )
    ]
    #: Move back to OVERWORLD
    for zone in OVERWORLD:
        nether.append(
            Transformation(
                destination=zone,
                zones=[NETHER],
                removed_zone_items=[ItemStack(OPEN_NETHER_PORTAL)],
                added_zone_items=[ItemStack(OPEN_NETHER_PORTAL)],
                removed_destination_items=[ItemStack(OPEN_NETHER_PORTAL)],
                added_destination_items=[ItemStack(OPEN_NETHER_PORTAL)],
            )
        )

    end = [
        #: Move to STRONGHOLD
        Transformation(
            destination=STRONGHOLD,
            zones=OVERWORLD,
            removed_player_items=[ItemStack(ENDER_EYE, 2)],
        ),
        #: Move to END
        Transformation(
            destination=END,
            removed_zone_items=[ItemStack(OPEN_ENDER_PORTAL)],
            added_zone_items=[ItemStack(OPEN_ENDER_PORTAL)],
        ),
    ]

    return walk + dig + nether + end


def _zones_search() -> List[Transformation]:
    """Build the transformations to search for items in zones using tools or not."""
    material_speed = {
        None: 1,
        Material.WOOD: 2,
        Material.STONE: 4,
        Material.IRON: 6,
        Material.GOLD: 12,
        Material.DIAMOND: 8,
    }

    search_item = []
    for mc_item in MC_ITEMS:
        item = mc_item.item

        if mc_item.required_tool_types is None:
            quantity = max(1, round(1 / mc_item.hardness))
            search_item.append(
                Transformation(
                    zones=mc_item.zones, added_player_items=[ItemStack(item, quantity)]
                )
            )
            continue

        for tool_type in mc_item.required_tool_types:
            if tool_type is None:
                # Can still be gather by hand
                quantity = max(1, round(1 / mc_item.hardness))
                search_item.append(
                    Transformation(
                        zones=mc_item.zones,
                        added_player_items=[ItemStack(item, quantity)],
                    )
                )
            else:
                allowed_materials = mc_item.required_tool_material
                if allowed_materials is None:
                    allowed_materials = list(Material)
                for material in allowed_materials:
                    quantity = max(
                        1, round(material_speed[material] / mc_item.hardness)
                    )
                    tools = None
                    if material is not None:
                        tool_stack = ItemStack(
                            MC_TOOLS_BY_TYPE_AND_MATERIAL[tool_type][material]
                        )
                        tools = [tool_stack]
                    search_item.append(
                        Transformation(
                            zones=mc_item.zones,
                            added_player_items=[ItemStack(item, quantity)],
                            removed_player_items=tools,
                        )
                    )

    return search_item


def _crafting_recipes() -> List[Transformation]:
    """Build the item only based crafting recipes."""
    return [
        #: Recipe of WOOD_PLANK
        Transformation(
            removed_player_items=[ItemStack(WOOD)],
            added_player_items=[ItemStack(WOOD_PLANK, 4)],
        ),
        #: Recipe of STICK
        Transformation(
            removed_player_items=[ItemStack(WOOD_PLANK, 2)],
            added_player_items=[ItemStack(STICK, 4)],
        ),
        #: Recipe of CRAFTING_TABLE
        Transformation(
            removed_player_items=[ItemStack(WOOD_PLANK, 4)],
            added_player_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Recipe of FURNACE
        Transformation(
            removed_player_items=[ItemStack(COBBLESTONE, 8)],
            added_player_items=[ItemStack(FURNACE)],
            removed_zone_items=[ItemStack(CRAFTING_TABLE)],
            added_zone_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Recipe of PAPER
        Transformation(
            removed_player_items=[ItemStack(REEDS, 3)],
            added_player_items=[ItemStack(PAPER, 3)],
            removed_zone_items=[ItemStack(CRAFTING_TABLE)],
            added_zone_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Recipe of BOOK
        Transformation(
            removed_player_items=[ItemStack(PAPER, 3), ItemStack(LEATHER)],
            added_player_items=[ItemStack(BOOK)],
            removed_zone_items=[ItemStack(CRAFTING_TABLE)],
            added_zone_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Recipe of ENCHANTING_TABLE
        Transformation(
            removed_player_items=[
                ItemStack(BOOK),
                ItemStack(OBSIDIAN, 4),
                ItemStack(DIAMOND, 2),
            ],
            added_player_items=[ItemStack(ENCHANTING_TABLE)],
            removed_zone_items=[ItemStack(CRAFTING_TABLE)],
            added_zone_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Recipe of CLOCK
        Transformation(
            removed_player_items=[ItemStack(GOLD_INGOT, 4), ItemStack(REDSTONE)],
            added_player_items=[ItemStack(CLOCK)],
            removed_zone_items=[ItemStack(CRAFTING_TABLE)],
            added_zone_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Recipe of FLINT
        Transformation(
            removed_player_items=[ItemStack(GRAVEL, 10)],
            added_player_items=[ItemStack(FLINT)],
        ),
        #: Recipe of FLINT_AND_STEEL
        Transformation(
            removed_player_items=[ItemStack(IRON_INGOT), ItemStack(FLINT)],
            added_player_items=[ItemStack(FLINT_AND_STEEL, 4)],
        ),
        #: Recipe of BLAZE_POWDER
        Transformation(
            removed_player_items=[ItemStack(BLAZE_ROD)],
            added_player_items=[ItemStack(BLAZE_POWDER, 2)],
        ),
        #: Recipe of BLAZE_POWDER
        Transformation(
            removed_player_items=[
                ItemStack(BLAZE_POWDER),
                ItemStack(ENDER_PEARL),
            ],
            added_player_items=[ItemStack(ENDER_EYE)],
        ),
    ]


def _building() -> List[Transformation]:
    """Build building based transformations"""
    building_creation = [
        #: Build a CRAFTING_TABLE
        Transformation(
            removed_player_items=[ItemStack(CRAFTING_TABLE)],
            added_zone_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Collect a CRAFTING_TABLE
        Transformation(
            added_player_items=[ItemStack(CRAFTING_TABLE)],
            removed_zone_items=[ItemStack(CRAFTING_TABLE)],
        ),
        #: Build a FURNACE
        Transformation(
            removed_player_items=[ItemStack(FURNACE)],
            added_zone_items=[ItemStack(FURNACE)],
        ),
        #: Collect a FURNACE
        Transformation(
            added_player_items=[ItemStack(FURNACE)],
            removed_zone_items=[ItemStack(FURNACE)],
        ),
        #: Build an ENCHANTING_TABLE
        Transformation(
            removed_player_items=[ItemStack(ENCHANTING_TABLE)],
            added_zone_items=[ItemStack(ENCHANTING_TABLE)],
        ),
        #: Collect a ENCHANTING_TABLE
        Transformation(
            added_player_items=[ItemStack(ENCHANTING_TABLE)],
            removed_zone_items=[ItemStack(ENCHANTING_TABLE)],
        ),
        #: Build NETHER_PORTAL
        Transformation(
            removed_player_items=[ItemStack(OBSIDIAN, 10)],
            added_zone_items=[ItemStack(CLOSE_NETHER_PORTAL)],
        ),
        #: Open NETHER_PORTAL
        Transformation(
            removed_player_items=[ItemStack(FLINT_AND_STEEL)],
            removed_zone_items=[ItemStack(CLOSE_NETHER_PORTAL)],
            added_zone_items=[ItemStack(OPEN_NETHER_PORTAL)],
        ),
        #: Open END_PORTAL
        Transformation(
            removed_player_items=[ItemStack(ENDER_EYE, 9)],
            removed_zone_items=[ItemStack(CLOSE_ENDER_PORTAL)],
            added_zone_items=[ItemStack(OPEN_ENDER_PORTAL)],
        ),
    ]

    smelting = [
        #: Recipe of IRON_INGOT using PLANK at FURNACE
        Transformation(
            removed_player_items=[ItemStack(IRON_ORE, 3), ItemStack(WOOD_PLANK, 2)],
            added_player_items=[ItemStack(IRON_INGOT, 3)],
            removed_zone_items=[ItemStack(FURNACE)],
            added_zone_items=[ItemStack(FURNACE)],
        ),
        #: Recipe of GOLD_INGOT using PLANK at FURNACE
        Transformation(
            removed_player_items=[ItemStack(GOLD_ORE, 3), ItemStack(WOOD_PLANK, 2)],
            added_player_items=[ItemStack(GOLD_INGOT, 3)],
            removed_zone_items=[ItemStack(FURNACE)],
            added_zone_items=[ItemStack(FURNACE)],
        ),
        #: Recipe of IRON_INGOT using COAL at FURNACE
        Transformation(
            removed_player_items=[ItemStack(IRON_ORE, 8), ItemStack(COAL, 1)],
            added_player_items=[ItemStack(IRON_INGOT, 8)],
            removed_zone_items=[ItemStack(FURNACE)],
            added_zone_items=[ItemStack(FURNACE)],
        ),
        #: Recipe of GOLD_INGOT using COAL at FURNACE
        Transformation(
            removed_player_items=[ItemStack(GOLD_ORE, 8), ItemStack(COAL, 1)],
            added_player_items=[ItemStack(GOLD_INGOT, 8)],
            removed_zone_items=[ItemStack(FURNACE)],
            added_zone_items=[ItemStack(FURNACE)],
        ),
    ]

    return building_creation + smelting


def _tools_recipes() -> List[Transformation]:
    """Builds the list of transformations for the tools recipes"""
    tools_recipes = []

    material_items_per_type = {
        ToolType.PICKAXE: 3,
        ToolType.AXE: 3,
        ToolType.SHOVEL: 1,
        ToolType.SWORD: 2,
    }

    sticks_per_type = {
        ToolType.PICKAXE: 2,
        ToolType.AXE: 2,
        ToolType.SHOVEL: 2,
        ToolType.SWORD: 1,
    }

    material_item = {
        Material.WOOD: WOOD_PLANK,
        Material.STONE: COBBLESTONE,
        Material.IRON: IRON_INGOT,
        Material.GOLD: GOLD_INGOT,
        Material.DIAMOND: DIAMOND,
    }

    durability_by_material = {
        Material.WOOD: 10,
        Material.STONE: 20,
        Material.IRON: 40,
        Material.GOLD: 10,
        Material.DIAMOND: 100,
    }

    for material in Material:
        for tool_type in ToolType:
            tool_recipe = Transformation(
                removed_player_items=[
                    ItemStack(
                        material_item[material], material_items_per_type[tool_type]
                    ),
                    ItemStack(STICK, sticks_per_type[tool_type]),
                ],
                added_player_items=[
                    ItemStack(
                        MC_TOOLS_BY_TYPE_AND_MATERIAL[tool_type][material],
                        durability_by_material[material],
                    )
                ],
                removed_zone_items=[ItemStack(CRAFTING_TABLE)],
                added_zone_items=[ItemStack(CRAFTING_TABLE)],
            )
            tools_recipes.append(tool_recipe)

    return tools_recipes


if __name__ == "__main__":
    all_tranformations = build_minecrafting_transformations()
    print(f"Total of {len(all_tranformations)} transformations in MineCrafting.")

    print("\nMOVE TO ZONES: ")
    for transfo in _move_to_zones():
        print(transfo)
    print("\nSEARCH: ")
    for transfo in _zones_search():
        print(transfo)
    print("\nCRAFTS: ")
    for transfo in _crafting_recipes():
        print(transfo)
    print("\nBUILDINGS: ")
    for transfo in _building():
        print(transfo)
    print("\nTOOLS: ")
    for transfo in _tools_recipes():
        print(transfo)
