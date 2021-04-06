# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Minecraft Options

All useful options to get any item

"""

from crafting.option import GetItem

from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *
from crafting.examples.minecraft.zones import *
from crafting.examples.minecraft.recipes import *

MC_WORLD = McWorld()

def _raise_option_not_implemented(*args, **kwargs):
    raise NotImplementedError

ALL_GET_OPTIONS = {
    item.item_id: _raise_option_not_implemented
    for item in MC_FOUDABLE_ITEMS + MC_CRAFT_ITEMS + MC_TOOLS[1:]
}

for item in MC_FOUDABLE_ITEMS:
    zones_id_needed = []
    for zone in MC_ZONES:
        if item.item_id in zone.items:
            zones_id_needed.append(zone.zone_id)

    items_needed = []
    required_tools = item.required_tools if item.required_tools is not None else [AIR]
    for tool in required_tools:
        if tool.item_id == 0:
            crafting_option = []
        else:
            crafting_option = [(tool.item_id, 1)]
        items_needed.append(crafting_option)

    ALL_GET_OPTIONS[item.item_id] =  GetItem(
        world=MC_WORLD,
        items_needed=items_needed,
        last_action=('get', item.item_id),
        zones_id_needed=zones_id_needed
    )

    print(f'{item}')

for recipe in MC_RECIPES:

    items_needed = [
        [
            (itemstack.item_id, itemstack.size)
            for itemstack in recipe.inputs
        ]
    ]

    if recipe.outputs is not None:
        for output in recipe.outputs:
            item = output.item

            ALL_GET_OPTIONS[item.item_id] = GetItem(
                world=MC_WORLD,
                items_needed=items_needed,
                zones_properties_needed=recipe.needed_properties,
                last_action=('craft', recipe.recipe_id)
            )

            print(f'{item}')

    if recipe.added_properties is not None:
        for zone_property in recipe.added_properties:
            ALL_GET_OPTIONS[recipe.recipe_id] = GetItem(
                world=MC_WORLD,
                items_needed=items_needed,
                last_action=('craft', recipe.recipe_id)
            )

            print(f'{zone_property}')

if __name__ == "__main__":
    MC_GETABLE_ITEMS = MC_FOUDABLE_ITEMS + MC_CRAFT_ITEMS + MC_TOOLS[1:]
    for item in MC_GETABLE_ITEMS:
        print(f'{item}:\n{ALL_GET_OPTIONS[item.item_id]}')
