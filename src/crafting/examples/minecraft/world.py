# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for the MineCrafting World. """

import os

import crafting
from crafting.world.world import World

from crafting.examples.minecraft.items import MC_ITEMS, MC_SEARCHABLE_ITEMS
from crafting.examples.minecraft.tools import MC_TOOLS
from crafting.examples.minecraft.zones import MC_ZONES
from crafting.examples.minecraft.recipes import MC_RECIPES


class McWorld(World):

    """Minecraft world"""

    def __init__(self):
        mc_dir = os.path.dirname(crafting.examples.minecraft.__file__)
        resources_path = os.path.join(mc_dir, "resources")
        super().__init__(
            zones=MC_ZONES,
            items=MC_ITEMS + MC_TOOLS,
            searchable_items=MC_SEARCHABLE_ITEMS,
            recipes=MC_RECIPES,
            resources_path=resources_path,
            font_path=os.path.join(resources_path, "minecraft_font.ttf"),
        )
