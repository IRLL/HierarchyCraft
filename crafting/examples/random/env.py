# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

from typing import List, Tuple, Dict

import numpy as np

from crafting.env import CraftingEnv
from crafting.world.world import World

from crafting.player.player import Player
from crafting.player.inventory import Inventory

from crafting.world.zones import Zone
from crafting.world.items import Item, Tool, ItemStack
from crafting.world.recipes import Recipe


class RandomCraftingEnv(CraftingEnv):

    """Random Crafting Environment"""

    def __init__(
        self,
        n_items: int,
        n_tools: int,
        n_foundables: int,
        n_required_tools: List[float],
        n_inputs_per_craft: List[float],
        n_zones: int = 1,
        **kwargs,
    ):
        """Random Crafting Environment.

        Args:
            n_items: Total number of items to generate.
            n_tools: Number of random tools to generate.
            n_foundables: Number of random foundable items to generate.
            n_required_tools: List of probabilities of having x requirements where x is the index.
            n_inputs_per_craft: List of probabilities of having x+1 inputs where x is the index.
            n_zones: Number of random zones to generate.

        Kwargs:
            max_step: The maximum number of steps until done.
            verbose: Verbosity level. {0: quiet, 1: print actions results}.
            observe_legal_actions: If True, add legal actions to observations.
            tasks: List of tasks.
            tasks_weights: Weight of tasks used for reward.
            tasks_can_end: Whether task can end the environment.
            tasks_early_stopping: If 'all', all task that can end have to be done to stop the
                environment. If 'any', any task that can end will stop the environment when done.
            fail_penalty: Reward penalty for each non-successful action.
            timestep_penalty: Reward penalty for each timestep.
            moving_penalty: Reward penalty for moving to an other zone.

        """

        world, initial_zone = self.build_world(
            n_items=n_items,
            n_tools=n_tools,
            n_foundables=n_foundables,
            n_zones=n_zones,
            n_required_tools=n_required_tools,
            n_inputs_per_craft=n_inputs_per_craft,
        )

        tasks = kwargs.pop("tasks", None)
        player = Player(Inventory(world.items), initial_zone)
        super().__init__(world=world, player=player, tasks=tasks, **kwargs)

    def build_world(
        self,
        n_items: int,
        n_tools: int,
        n_foundables: int,
        n_zones: int,
        n_required_tools: List[float],
        n_inputs_per_craft: List[float],
    ) -> World:
        """Build a random world.

        Args:
            n_items: Total number of items to generate.
            n_tools: Number of random tools to generate.
            n_foundables: Number of random foundable items to generate.
            n_zones: Number of random zones to generate.
            n_required_tools: List of probabilities of having x requirements where x is the index.
            n_inputs_per_craft: List of probabilities of having x+1 inputs where x is the index.

        Returns:
            A randomly built World.

        """

        if n_items < n_tools + n_foundables:
            raise ValueError(
                f"n_items must be >= n_tools + n_foundables"
                f"\nGot {n_items} < {n_tools} + {n_foundables}"
            )

        tools = [Tool(i, "tool") for i in range(n_tools)]
        craftables = [
            Item(n_tools + i, "item") for i in range(n_items - n_foundables - n_tools)
        ]

        foundables, items_per_zones, items_per_tool = self._build_foundables(
            n_foundables,
            n_required_tools,
            tools,
            n_zones,
            offset_id=n_items - n_foundables,
        )
        zones = self._build_zones(n_zones, items_per_zones)

        items = tools + craftables + foundables
        recipes = self._build_recipes(
            items, foundables, n_inputs_per_craft, items_per_tool
        )

        world = World(zones=zones, items=items, recipes=recipes)
        return world, zones[0]

    @staticmethod
    def _build_foundables(
        n_foundables: int,
        n_required_tools: List[float],
        tools: List[Tool],
        n_zones: int,
        offset_id: int = 0,
    ) -> Tuple[List[Item], Dict[int, List[Item]]]:
        """Build a random list of foundable items scattered accross potential zones.

        Args:
            n_foundables: Number of random foundable items to generate.
            n_required_tools: List of probabilities of having x requirements where x is the index.
            tools: List of tools that can be requirements.
            n_zones: Number of zones to scatter items into.
            offset_id: Offset added to each item_id of generated foundable items.

        Returns:
            foundables: List of generated Items.
            items_per_zones: List of attributed zones for each Item generated.
            items_per_tool: Dictionary mapping tool.item_id to all foundable items that requires it.

        """
        original_item = Item(offset_id, "found")
        foundables = [original_item]
        items_per_zones = [[] for _ in range(n_zones)]
        items_per_zones[0].append(original_item)
        items_per_tool = {tool.item_id: [] for tool in tools}

        for _ in range(1, n_foundables):
            # Get required tools
            n_req_probs = np.array(n_required_tools) / np.sum(n_required_tools)
            n_req_tools = np.random.choice(range(len(n_required_tools)), p=n_req_probs)
            required_tools = list(
                np.random.choice(tools, size=n_req_tools, replace=False)
            )

            # Build item
            item_id = offset_id + len(foundables)
            new_foundable = Item(item_id, "found", required_tools=required_tools)
            foundables.append(new_foundable)

            # Assign item to each required_tool
            for tool in required_tools:
                items_per_tool[tool.item_id].append(new_foundable)

            # Place item in (futur?) zones
            n_zones_probs = np.array([1 / (n + 1) for n in range(1, n_zones)])
            n_zones_probs /= np.sum(n_zones_probs)
            n_foundable_zones = np.random.choice(range(1, n_zones), p=n_zones_probs)

            foundable_zones = np.random.choice(
                range(n_zones), size=n_foundable_zones, replace=False
            )

            for foundable_zone in foundable_zones:
                items_per_zones[foundable_zone].append(new_foundable)

        return foundables, items_per_zones, items_per_tool

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

    @staticmethod
    def _build_recipes(
        items: List[Item],
        foundables: List[Item],
        n_inputs_per_craft: List[float],
        items_per_tool: Dict[int, List[Item]],
    ) -> List[Recipe]:
        """Build random recipes to make every item accessible.

        Args:
            items: List of items.
            foundables: List of foundable items.
            n_inputs_per_craft: List of probabilities of having x+1 inputs where x is the index.
            items_per_tool: Dictionary mapping tool item_id to all foundable items that requires it.

        Returns:
            List of random recipes.

        """
        recipes = []
        accessible_items = [
            foundable for foundable in foundables if foundable.required_tools is None
        ]

        unaccessible_items = [item for item in items if item not in foundables]

        while len(unaccessible_items) > 0:
            new_accessible_item = unaccessible_items.pop(
                np.random.randint(len(unaccessible_items))
            )
            outputs = [ItemStack(new_accessible_item)]

            n_inputs_probs = np.array(n_inputs_per_craft) / np.sum(n_inputs_per_craft)
            n_inputs = 1 + np.random.choice(
                range(len(n_inputs_probs)), p=n_inputs_probs
            )
            n_inputs = min(n_inputs, len(accessible_items))
            input_items = list(
                np.random.choice(accessible_items, size=n_inputs, replace=False)
            )
            inputs = [ItemStack(item) for item in input_items]

            new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
            recipes.append(new_recipe)

            if isinstance(new_accessible_item, Tool):
                for new_accessible_item_by_tool in items_per_tool[
                    new_accessible_item.item_id
                ]:
                    accessible_items.append(new_accessible_item_by_tool)
            else:
                accessible_items.append(new_accessible_item)

        return recipes


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    env = RandomCraftingEnv(
        n_items=30,
        n_tools=10,
        n_foundables=10,
        n_required_tools=[0.25, 0.4, 0.2, 0.1, 0.05],
        n_inputs_per_craft=[0.1, 0.6, 0.3],
        n_zones=5,
    )

    fig, ax = plt.subplots()
    env.world.draw_requirements_graph(ax)
    plt.show()
