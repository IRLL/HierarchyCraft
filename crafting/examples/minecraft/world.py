# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from crafting.world.world import World

from crafting.examples.minecraft.items import MC_ITEMS
from crafting.examples.minecraft.tools import MC_TOOLS
from crafting.examples.minecraft.zones import MC_ZONES
from crafting.examples.minecraft.recipes import MC_RECIPES

class McWorld(World):

    """ Minecraft world """

    def __init__(self):
        super().__init__(zones=MC_ZONES, items=MC_ITEMS + MC_TOOLS, recipes=MC_RECIPES)
