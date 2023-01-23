# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Random Crafting Environment

Generate a random Crafting environment using basic constructor rules.

"""

from typing import Dict, List, Tuple

import numpy as np

from crafting.env import CraftingEnv
from crafting.player.inventory import Inventory
from crafting.player.player import Player
from crafting.world.items import Item, ItemStack, Tool
from crafting.world.recipes import Recipe
from crafting.world.world import World
from crafting.world.zones import Zone


class RandomCraftingEnv(CraftingEnv):

    """Random Crafting Environment"""

    def __init__(
        self,
        n_items: int,
        n_tools: int,
        n_findables: int,
        n_required_tools: List[float],
        n_inputs_per_craft: List[float],
        n_zones: int = 1,
        seed: int = None,
        **kwargs,
    ):
        """Random Crafting Environment.

        Args:
            n_items: Total number of items to generate.
            n_tools: Number of random tools to generate.
            n_findables: Number of random findable items to generate.
            n_required_tools: List of probabilities of having x requirements where x is the index.
            n_inputs_per_craft: List of probabilities of having x+1 inputs where x is the index.
            n_zones: Number of random zones to generate.

        Kwargs:
            max_step: The maximum number of steps until done.
            verbose: Verbosity level. {0: quiet, 1: print actions results}.
            observe_legal_actions: If True, add legal actions to observations.
            tasks: List of tasks.
            fail_penalty: Reward penalty for each non-successful action.
            timestep_penalty: Reward penalty for each timestep.
            moving_penalty: Reward penalty for moving to an other zone.

        """

        assert n_zones > 0, "Must have at lease one zone."
        assert (
            n_items >= n_tools + n_findables
        ), "Number of items must be greater than number of tools and findables."

        (seed,) = super().seed(seed)

        world, initial_zone = self.build_world(
            n_items=n_items,
            n_tools=n_tools,
            n_findables=n_findables,
            n_zones=n_zones,
            n_required_tools=n_required_tools,
            n_inputs_per_craft=n_inputs_per_craft,
        )

        player = Player(Inventory(world.items), initial_zone)
        super().__init__(world=world, player=player, seed=seed, **kwargs)

    def build_world(
        self,
        n_items: int,
        n_tools: int,
        n_findables: int,
        n_zones: int,
        n_required_tools: List[float],
        n_inputs_per_craft: List[float],
    ) -> Tuple[World, Zone]:
        """Build a random world.

        Args:
            n_items: Total number of items to generate.
            n_tools: Number of random tools to generate.
            n_findables: Number of random findable items to generate.
            n_zones: Number of random zones to generate.
            n_required_tools: List of probabilities of having x requirements where x is the index.
            n_inputs_per_craft: List of probabilities of having x+1 inputs where x is the index.

        Returns:
            A randomly built World.

        """

        if n_items < n_tools + n_findables:
            raise ValueError("n_items must be >= n_tools + n_findables")

        tools = [Tool(i, "tool") for i in range(n_tools)]
        findables, items_per_zones, items_per_tool = self._build_findables(
            n_findables,
            n_required_tools,
            tools,
            n_zones,
            offset_id=n_items - n_findables,
        )
        zones = self._build_zones(n_zones, items_per_zones)

        craftables = [
            Item(n_tools + i, "item") for i in range(n_items - n_findables - n_tools)
        ]
        items = tools + craftables + findables
        recipes = self._build_recipes(
            items, findables, n_inputs_per_craft, items_per_tool
        )

        world = World(zones=zones, items=items, recipes=recipes)
        return world, zones[0]

    def _build_findables(
        self,
        n_findables: int,
        n_required_tools: List[float],
        tools: List[Tool],
        n_zones: int,
        offset_id: int = 0,
    ) -> Tuple[List[Item], Dict[int, List[Item]]]:
        """Build a random list of findable items scattered accross potential zones.

        Args:
            n_findables: Number of random findable items to generate.
            n_required_tools: List of probabilities of having x requirements where x is the index.
            tools: List of tools that can be requirements.
            n_zones: Number of zones to scatter items into.
            offset_id: Offset added to each item_id of generated findable items.

        Returns:
            findables: List of generated Items.
            items_per_zones: List of attributed zones for each Item generated.
            items_per_tool: Dictionary mapping tool.item_id to all findable items that requires it.

        """
        original_item = Item(offset_id, "find")
        findables = [original_item]
        items_per_zones = [[] for _ in range(n_zones)]
        items_per_zones[0].append(original_item)
        items_per_tool = {tool.item_id: [] for tool in tools}

        for _ in range(1, n_findables):
            # Get required tools
            n_req_probs = np.array(n_required_tools) / np.sum(n_required_tools)
            n_req_tools = self.np_random.choice(
                range(len(n_required_tools)), p=n_req_probs
            )
            n_req_tools = min(n_req_tools, len(tools))
            required_tools = list(
                self.np_random.choice(tools, size=n_req_tools, replace=False)
            )

            # Build item
            item_id = offset_id + len(findables)
            new_findable = Item(item_id, "find", required_tools=required_tools)
            findables.append(new_findable)

            # Assign item to each required_tool
            for tool in required_tools:
                items_per_tool[tool.item_id].append(new_findable)

            # Place item in (futur?) zones
            if n_zones > 1:
                n_zones_probs = np.array([1 / (n + 1) for n in range(1, n_zones)])
                n_zones_probs /= np.sum(n_zones_probs)
                n_findable_zones = 1 + self.np_random.choice(
                    range(1, n_zones), p=n_zones_probs
                )
                findable_zones = self.np_random.choice(
                    range(n_zones), size=n_findable_zones, replace=False
                )
            else:
                findable_zones = [0]

            for findable_zone in findable_zones:
                items_per_zones[findable_zone].append(new_findable)

        return findables, items_per_zones, items_per_tool

    @staticmethod
    def _build_zones(n_zones: int, items_per_zones: List[List[Item]]) -> List[Zone]:
        """Build random zones filled with given items

        Args:
            n_zones: Number of zones.
            items_per_zones: Items to fill each zones with.

        Returns:
            List of random zones.

        """
        zones = []
        for zone_id in range(n_zones):
            zone_items = items_per_zones[zone_id]
            new_zone = Zone(zone_id, "zone", items=zone_items)
            zones.append(new_zone)
        return zones

    def _build_recipes(
        self,
        items: List[Item],
        findables: List[Item],
        n_inputs_per_craft: List[float],
        items_per_tool: Dict[int, List[Item]],
    ) -> List[Recipe]:
        """Build random recipes to make every item accessible.

        Args:
            items: List of items.
            findables: List of findable items.
            n_inputs_per_craft: List of probabilities of having x+1 inputs where x is the index.
            items_per_tool: Dictionary mapping tool item_id to all findable items that requires it.

        Returns:
            List of random recipes.

        """
        recipes = []
        accessible_items = set(
            findable for findable in findables if findable.required_tools is None
        )

        unaccessible_items = [item for item in items if item not in findables]
        self.np_random.shuffle(unaccessible_items)

        while len(accessible_items) < len(items):
            new_accessible_item = unaccessible_items.pop()
            new_is_tool = isinstance(new_accessible_item, Tool)

            # Don't build recipes from tools or unaccesible items
            accessible_notool_items = [
                item
                for item in items
                if item in accessible_items and not isinstance(item, Tool)
            ]

            outputs = [ItemStack(new_accessible_item)]

            # Chooses randomly the number of input items (>=1)
            n_inputs_probs = np.array(n_inputs_per_craft) / np.sum(n_inputs_per_craft)
            n_inputs = 1 + self.np_random.choice(
                range(len(n_inputs_probs)), p=n_inputs_probs
            )
            n_inputs = min(n_inputs, len(accessible_notool_items))

            # Chooses randomly accessible items and build ItemStacks of size 1 (default).
            input_items = list(
                self.np_random.choice(
                    accessible_notool_items, size=n_inputs, replace=False
                )
            )
            inputs = [ItemStack(item) for item in input_items]

            # Build recipe
            new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
            recipes.append(new_recipe)

            # If new accessible item is a tool,
            #   add findables that can be gathered with it in accessible items
            if new_is_tool:
                for new_accessible_item_by_tool in items_per_tool[
                    new_accessible_item.item_id
                ]:
                    accessible_items.add(new_accessible_item_by_tool)
            accessible_items.add(new_accessible_item)

        return recipes
