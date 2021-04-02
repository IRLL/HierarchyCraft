# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

import numpy as np

from crafting.env import CraftingEnv
from crafting.world.world import World

from crafting.player.player import Player
from crafting.player.inventory import Inventory

from crafting.world.zones import Zone
from crafting.world.items import Item, Tool
from crafting.world.recipes import Recipe

class MineCraftingEnv(CraftingEnv):

    """ MineCrafting Environment """

    def __init__(self, n_recipes, n_zones=1, n_zones_properties=0, **kwargs):
        tasks = kwargs.pop('tasks', None)

        self.n_tools = 0
        self.tool_prop = kwargs.pop('tool_prop', 0.5)
        n_start_items = kwargs.pop('n_start_items', 3)

        world, initial_zone = self.build_world(
            n_start_items, n_recipes, n_zones, n_zones_properties
        )

        player = Player(Inventory(world.items), initial_zone)
        super().__init__(
            world=world,
            player=player,
            tasks=tasks,
            **kwargs
        )

    def build_world(self, n_start_items, n_recipes, n_zones, n_zones_properties):
        items = [Item(i, f'item_{i}') for i in range(n_start_items)]
        tools = []
        recipes = []
        zones = []

        for _ in range(n_recipes):
            self._add_recipe(items, tools, recipes, zones)

        world = World(zones=zones, items=items, recipes=recipes)
        return world, zones[0]

    def _add_recipe(self, items, tools, recipes, zones):
        raise NotImplementedError

    def _add_zone(self, items, tools, recipes, zones):
        raise NotImplementedError
