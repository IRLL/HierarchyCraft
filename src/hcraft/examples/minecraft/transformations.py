""" Minecraft Recipes

All used Minecraft recipies.

"""

from typing import List

import hcraft.examples.minecraft.items as items
from hcraft.examples.minecraft.tools import (
    ToolType,
    Material,
    MC_TOOLS_BY_TYPE_AND_MATERIAL,
)
import hcraft.examples.minecraft.zones as zones
from hcraft.transformation import (
    Transformation,
    Use,
    Yield,
    PLAYER,
    CURRENT_ZONE,
    DESTINATION,
)


def build_minehcraft_transformations() -> List[Transformation]:
    transformations = []
    transformations += _move_to_zones()
    transformations += _zones_search()
    transformations += _building()
    transformations += _recipes()
    transformations += _tools_recipes()
    return transformations


def _move_to_zones() -> List[Transformation]:
    name_prefix = "move-to-"
    walk = [
        #: Move to FOREST
        Transformation(
            name_prefix + zones.FOREST.name,
            destination=zones.FOREST,
            zones=[zone for zone in zones.OVERWORLD if zone != zones.FOREST]
            + [zones.END],
        ),
        #: Move to SWAMP
        Transformation(
            name_prefix + zones.SWAMP.name,
            destination=zones.SWAMP,
            zones=[zone for zone in zones.OVERWORLD if zone != zones.SWAMP],
        ),
        #: Move to zones.MEADOW
        Transformation(
            name_prefix + zones.MEADOW.name,
            destination=zones.MEADOW,
            zones=[zone for zone in zones.OVERWORLD if zone != zones.MEADOW],
        ),
    ]

    required_pickaxe_materials = {
        zones.UNDERGROUND: [Material.STONE, Material.IRON, Material.DIAMOND],
        zones.BEDROCK: [Material.IRON, Material.DIAMOND],
    }

    #: Dig to zones.UNDERGROUND or zones.BEDROCK
    dig = []
    for zone, materials in required_pickaxe_materials.items():
        for material in materials:
            pickaxe = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][material]
            other_zones = [
                other_zone for other_zone in zones.OVERWORLD if other_zone != zone
            ]
            dig.append(
                Transformation(
                    name_prefix + f"{zone.name}-with-{pickaxe.name}",
                    destination=zone,
                    zones=other_zones,
                    inventory_changes=[Use(PLAYER, pickaxe, consume=1)],
                )
            )

    nether = [
        #: Move to NETHER
        Transformation(
            name_prefix + zones.NETHER.name,
            destination=zones.NETHER,
            inventory_changes=[Use(CURRENT_ZONE, items.OPEN_NETHER_PORTAL)],
        )
    ]
    #: Move back to OVERWORLD
    for zone in [
        zones.FOREST,
        zones.MEADOW,
        zones.SWAMP,
        zones.UNDERGROUND,
        zones.BEDROCK,
    ]:
        nether.append(
            Transformation(
                name_prefix + zone.name + f"-from-{zones.NETHER.name}",
                destination=zone,
                zones=[zones.NETHER],
                inventory_changes=[
                    Use(CURRENT_ZONE, items.OPEN_NETHER_PORTAL),
                    Use(DESTINATION, items.OPEN_NETHER_PORTAL),
                ],
            )
        )

    end = [
        #: Move to STRONGHOLD
        Transformation(
            name_prefix + zones.STRONGHOLD.name,
            destination=zones.STRONGHOLD,
            zones=zones.OVERWORLD,
            inventory_changes=[Use(CURRENT_ZONE, items.OPEN_NETHER_PORTAL, consume=2)],
        ),
        #: Move to zones.END
        Transformation(
            name_prefix + zones.END.name,
            destination=zones.END,
            inventory_changes=[Use(CURRENT_ZONE, items.OPEN_ENDER_PORTAL)],
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

    name_prefix = "search-for-"
    search_item = []
    for mc_item in items.MC_ITEMS:
        item = mc_item.item

        if mc_item.required_tool_types is None:
            quantity = max(1, round(1 / mc_item.hardness))
            search_item.append(
                Transformation(
                    name_prefix + item.name,
                    zones=mc_item.zones,
                    inventory_changes=[Yield(PLAYER, item, quantity)],
                )
            )
            continue

        for tool_type in mc_item.required_tool_types:
            if tool_type is None:
                # Can still be gather by hand
                quantity = max(1, round(1 / mc_item.hardness))
                search_item.append(
                    Transformation(
                        name_prefix + item.name,
                        zones=mc_item.zones,
                        inventory_changes=[Yield(PLAYER, item, quantity)],
                    )
                )
            else:
                allowed_materials = mc_item.required_tool_material
                if allowed_materials is None:
                    allowed_materials = list(Material)
                for material in allowed_materials[::-1]:
                    quantity = max(
                        1, round(material_speed[material] / mc_item.hardness)
                    )
                    inventory_changes = [Yield(PLAYER, item, quantity)]
                    if material is not None:
                        tool = MC_TOOLS_BY_TYPE_AND_MATERIAL[tool_type][material]
                        inventory_changes.append(Use(PLAYER, tool, consume=1))
                    search_item.append(
                        Transformation(
                            name_prefix + item.name + f"-with-{tool.name}",
                            zones=mc_item.zones,
                            inventory_changes=inventory_changes,
                        )
                    )

    return search_item


def _recipes() -> List[Transformation]:
    """Build the item based on recipes."""
    name_prefix = "craft-"
    return [
        #: Recipe of WOOD_PLANK
        Transformation(
            name_prefix + items.WOOD_PLANK.name,
            inventory_changes=[
                Use(PLAYER, items.WOOD, consume=1),
                Yield(PLAYER, items.WOOD_PLANK, create=4),
            ],
        ),
        #: Recipe of STICK
        Transformation(
            name_prefix + items.STICK.name,
            inventory_changes=[
                Use(PLAYER, items.WOOD_PLANK, consume=2),
                Yield(PLAYER, items.STICK, create=4),
            ],
        ),
        #: Recipe of CRAFTING_TABLE
        Transformation(
            name_prefix + items.CRAFTING_TABLE.name,
            inventory_changes=[
                Use(PLAYER, items.WOOD_PLANK, consume=4),
                Yield(PLAYER, items.CRAFTING_TABLE),
            ],
        ),
        #: Recipe of FURNACE
        Transformation(
            name_prefix + items.FURNACE.name,
            inventory_changes=[
                Use(PLAYER, items.COBBLESTONE, consume=8),
                Yield(PLAYER, items.FURNACE),
                Use(CURRENT_ZONE, items.CRAFTING_TABLE),
            ],
        ),
        #: Recipe of PAPER
        Transformation(
            name_prefix + items.PAPER.name,
            inventory_changes=[
                Use(PLAYER, items.REEDS, consume=3),
                Yield(PLAYER, items.PAPER, create=3),
                Use(CURRENT_ZONE, items.CRAFTING_TABLE),
            ],
        ),
        #: Recipe of BOOK
        Transformation(
            name_prefix + items.BOOK.name,
            inventory_changes=[
                Use(PLAYER, items.PAPER, consume=3),
                Use(PLAYER, items.LEATHER, consume=1),
                Yield(PLAYER, items.BOOK),
                Use(CURRENT_ZONE, items.CRAFTING_TABLE),
            ],
        ),
        #: Recipe of ENCHANTING_TABLE
        Transformation(
            name_prefix + items.ENCHANTING_TABLE.name,
            inventory_changes=[
                Use(PLAYER, items.BOOK, consume=1),
                Use(PLAYER, items.OBSIDIAN, consume=4),
                Use(PLAYER, items.DIAMOND, consume=2),
                Yield(PLAYER, items.ENCHANTING_TABLE),
                Use(CURRENT_ZONE, items.CRAFTING_TABLE),
            ],
        ),
        #: Recipe of CLOCK
        Transformation(
            name_prefix + items.CLOCK.name,
            inventory_changes=[
                Use(PLAYER, items.GOLD_INGOT, consume=4),
                Use(PLAYER, items.REDSTONE, consume=1),
                Yield(PLAYER, items.CLOCK),
                Use(CURRENT_ZONE, items.CRAFTING_TABLE),
            ],
        ),
        #: Recipe of FLINT
        Transformation(
            name_prefix + items.FLINT.name,
            inventory_changes=[
                Use(PLAYER, items.GRAVEL, consume=10),
                Yield(PLAYER, items.FLINT),
            ],
        ),
        #: Recipe of FLINT_AND_STEEL
        Transformation(
            name_prefix + items.FLINT_AND_STEEL.name,
            inventory_changes=[
                Use(PLAYER, items.IRON_INGOT, consume=1),
                Use(PLAYER, items.FLINT, consume=1),
                Yield(PLAYER, items.FLINT_AND_STEEL, create=4),
            ],
        ),
        #: Recipe of BLAZE_POWDER
        Transformation(
            name_prefix + items.BLAZE_POWDER.name,
            inventory_changes=[
                Use(PLAYER, items.BLAZE_ROD, consume=1),
                Yield(PLAYER, items.BLAZE_POWDER, create=2),
            ],
        ),
        #: Recipe of ENDER_EYE
        Transformation(
            name_prefix + items.ENDER_EYE.name,
            inventory_changes=[
                Use(PLAYER, items.BLAZE_POWDER, consume=1),
                Use(PLAYER, items.ENDER_PEARL, consume=1),
                Yield(PLAYER, items.ENDER_EYE),
            ],
        ),
    ]


def _building() -> List[Transformation]:
    """Build building based transformations"""

    placable_items = (items.CRAFTING_TABLE, items.FURNACE, items.ENCHANTING_TABLE)
    place_items = [
        Transformation(
            "place-" + item.name,
            inventory_changes=[
                Use(PLAYER, item, consume=1),
                Yield(CURRENT_ZONE, item, create=1),
            ],
        )
        for item in placable_items
    ]

    pickup_items = [
        Transformation(
            "pickup-" + item.name,
            inventory_changes=[
                Use(CURRENT_ZONE, item, consume=1),
                Yield(PLAYER, item, create=1),
            ],
        )
        for item in placable_items
    ]

    building_creation = [
        #: Build NETHER_PORTAL
        Transformation(
            "build-" + items.CLOSE_NETHER_PORTAL.name,
            inventory_changes=[
                Use(PLAYER, items.OBSIDIAN, consume=10),
                Yield(CURRENT_ZONE, items.CLOSE_NETHER_PORTAL, create=1),
            ],
        ),
        #: Open NETHER_PORTAL
        Transformation(
            "open-nether-portal",
            inventory_changes=[
                Use(PLAYER, items.FLINT_AND_STEEL, consume=1),
                Use(CURRENT_ZONE, items.CLOSE_NETHER_PORTAL, consume=1),
                Yield(CURRENT_ZONE, items.OPEN_NETHER_PORTAL),
            ],
        ),
        #: Open END_PORTAL
        Transformation(
            "open-end-portal",
            inventory_changes=[
                Use(PLAYER, items.ENDER_EYE, consume=9),
                Use(CURRENT_ZONE, items.CLOSE_ENDER_PORTAL, consume=1),
                Yield(CURRENT_ZONE, items.OPEN_ENDER_PORTAL),
            ],
        ),
    ]

    ores_ingots = [
        (items.IRON_ORE, items.IRON_INGOT),
        (items.GOLD_ORE, items.GOLD_INGOT),
    ]

    smelt_with_wood = [
        Transformation(
            f"smelt-{ore.name}-with-{items.WOOD_PLANK.name}",
            inventory_changes=[
                Use(PLAYER, ore, consume=3),
                Use(PLAYER, items.WOOD_PLANK, consume=2),
                Use(CURRENT_ZONE, items.FURNACE),
                Yield(PLAYER, ingot, create=3),
            ],
        )
        for ore, ingot in ores_ingots
    ]

    smelt_with_coal = [
        Transformation(
            f"smelt-{ore.name}-with-{items.COAL.name}",
            inventory_changes=[
                Use(PLAYER, ore, consume=8),
                Use(PLAYER, items.COAL, consume=1),
                Use(CURRENT_ZONE, items.FURNACE),
                Yield(PLAYER, ingot, create=8),
            ],
        )
        for ore, ingot in ores_ingots
    ]

    smelting = smelt_with_wood + smelt_with_coal

    return place_items + pickup_items + building_creation + smelting


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
        Material.WOOD: items.WOOD_PLANK,
        Material.STONE: items.COBBLESTONE,
        Material.IRON: items.IRON_INGOT,
        Material.GOLD: items.GOLD_INGOT,
        Material.DIAMOND: items.DIAMOND,
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
            tool = MC_TOOLS_BY_TYPE_AND_MATERIAL[tool_type][material]
            durability = durability_by_material[material]
            tool_recipe = Transformation(
                f"craft-{tool.name}",
                inventory_changes=[
                    Use(
                        PLAYER,
                        material_item[material],
                        consume=material_items_per_type[tool_type],
                    ),
                    Use(PLAYER, items.STICK, consume=sticks_per_type[tool_type]),
                    Use(CURRENT_ZONE, items.CRAFTING_TABLE),
                    Yield(PLAYER, tool, create=durability),
                ],
            )

            tools_recipes.append(tool_recipe)

    return tools_recipes


if __name__ == "__main__":
    all_tranformations = build_minehcraft_transformations()
    print(f"Total of {len(all_tranformations)} transformations in MineHcraft.")

    print("\nMOVE TO ZONES: ")
    for transfo in _move_to_zones():
        print(transfo)
        print("\t", repr(transfo))
    print("\nSEARCH: ")
    for transfo in _zones_search():
        print(transfo)
        print("\t", repr(transfo))
    print("\nCRAFTS: ")
    for transfo in _recipes():
        print(transfo)
        print("\t", repr(transfo))
    print("\nBUILDINGS: ")
    for transfo in _building():
        print(transfo)
        print("\t", repr(transfo))
    print("\nTOOLS: ")
    for transfo in _tools_recipes():
        print(transfo)
        print("\t", repr(transfo))
