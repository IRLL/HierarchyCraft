# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Random Crafting Environment

Generate a random Crafting environment using basic constructor rules.

"""

from typing import List, Tuple, Dict

import numpy as np
from numpy import random

from crafting.env import CraftingEnv
from crafting.render.render import get_human_action
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

        assert n_zones > 0, "Must have at lease one zone."
        assert (
            n_items >= n_tools + n_foundables
        ), "Number of items must be greater than number of tools and foundables."

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
            raise ValueError("n_items must be >= n_tools + n_foundables")

        tools = [Tool(i, "tool") for i in range(n_tools)]
        foundables, items_per_zones, items_per_tool = self._build_foundables(
            n_foundables,
            n_required_tools,
            tools,
            n_zones,
            offset_id=n_items - n_foundables,
        )
        zones = self._build_zones(n_zones, items_per_zones)

        craftables = [
            Item(n_tools + i, "item") for i in range(n_items - n_foundables - n_tools)
        ]
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
            n_req_tools = min(n_req_tools, len(tools))
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
            if n_zones > 1:
                n_zones_probs = np.array([1 / (n + 1) for n in range(1, n_zones)])
                n_zones_probs /= np.sum(n_zones_probs)
                n_foundable_zones = 1 + np.random.choice(
                    range(1, n_zones), p=n_zones_probs
                )
                foundable_zones = np.random.choice(
                    range(n_zones), size=n_foundable_zones, replace=False
                )
            else:
                foundable_zones = [0]

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
        accessible_items = set(
            foundable for foundable in foundables if foundable.required_tools is None
        )

        unaccessible_items = [item for item in items if item not in foundables]
        random.shuffle(unaccessible_items)

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
            n_inputs = 1 + np.random.choice(
                range(len(n_inputs_probs)), p=n_inputs_probs
            )
            n_inputs = min(n_inputs, len(accessible_notool_items))

            # Chooses randomly accessible items and build ItemStacks of size 1 (default).
            input_items = list(
                np.random.choice(accessible_notool_items, size=n_inputs, replace=False)
            )
            inputs = [ItemStack(item) for item in input_items]

            # Build recipe
            new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
            recipes.append(new_recipe)

            # If new accessible item is a tool,
            #   add foundables that can be gathered with it in accessible items
            if new_is_tool:
                for new_accessible_item_by_tool in items_per_tool[
                    new_accessible_item.item_id
                ]:
                    accessible_items.add(new_accessible_item_by_tool)
            accessible_items.add(new_accessible_item)

        return recipes


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    env = RandomCraftingEnv(
        n_items=12,
        n_tools=2,
        n_foundables=5,
        n_required_tools=[0.25, 0.4, 0.2, 0.1, 0.05],
        n_inputs_per_craft=[0.1, 0.6, 0.3],
        n_zones=1,
    )

    plot_requirement_graph = True
    if plot_requirement_graph:
        fig, ax = plt.subplots()
        env.world.draw_requirements_graph(ax)
        plt.show(block=False)
        plt.pause(0.001)

    for _ in range(1):
        observation = env.reset()
        done = False
        total_reward = 0
        while not done:
            rgb_array = env.render(mode="rgb_array")

            action = get_human_action(env, **env.render_variables)
            action_id = env.action(*action)
            print(f"Human did: {env.action_from_id(action_id)}")

            observation, reward, done, infos = env(action_id)
            total_reward += reward

        print("SCORE: ", total_reward)
