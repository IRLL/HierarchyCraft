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

GET_WOOD = GetItem(
    world=MC_WORLD,
    items_needed=[],
    last_action=('get', WOOD.item_id),
    zones_id_needed=(FOREST.zone_id,)
)

GET_WOOD_PLANK = GetItem(
    world=MC_WORLD,
    items_needed=[
        (WOOD.item_id, 1, GET_WOOD)
    ],
    last_action=('craft', R_WOOD_PLANK.recipe_id)
)

GET_STICK = GetItem(
    world=MC_WORLD,
    items_needed=[
        (WOOD_PLANK.item_id, 2, GET_WOOD_PLANK)
    ],
    last_action=('craft', R_STICK.recipe_id),
)

ALL_GET_OPTIONS = {
    WOOD.item_id: GET_WOOD,
    WOOD_PLANK.item_id: GET_WOOD_PLANK,
    STICK.item_id: GET_STICK,
}
