# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Simple Crafting Environment

A collection of simple environments using basic constructor rules.

"""

from typing import List, Tuple


from crafting.env import CraftingEnv
from crafting.world.world import World

from crafting.player.player import Player
from crafting.player.inventory import Inventory

from crafting.task import TaskList, TaskObtainItem

from crafting.world.zones import Zone
from crafting.world.items import Item, ItemStack
from crafting.world.recipes import Recipe


class SimpleCraftingEnv(CraftingEnv):

    """Base for simple handcrafted environments."""

    def __init__(
        self,
        n_items: int,
        **kwargs,
    ):
        """Base for simple handcrafted environments.

        No zones, or tools dynamics.

        Args:
            n_items: Total number of items to generate.

        Kwargs:
            max_step: The maximum number of steps until done.
            verbose: Verbosity level. {0: quiet, 1: print actions results}.
            observe_legal_actions: If True, add legal actions to observations.
            fail_penalty: Reward penalty for each non-successful action.
            timestep_penalty: Reward penalty for each timestep.

        """

        world, initial_zone = self.build_world(n_items=n_items)
        if "max_step" not in kwargs:
            kwargs["max_step"] = 2**n_items
        player = Player(Inventory(world.items), initial_zone)
        reward_shaping = kwargs.pop("reward_shaping", 0)
        task = TaskObtainItem(
            world,
            world.items[-1],
            goal_reward=2**n_items,
            reward_shaping=reward_shaping,
        )
        super().__init__(
            world=world,
            player=player,
            seed=0,
            tasks=TaskList([task], can_end=[True]),
            **kwargs,
        )

    def build_world(self, n_items: int) -> Tuple[World, Zone]:
        """Initialise a linerarly stacked World.

        Args:
            n_items: Total number of items to generate.

        Returns:
            A linerarly stacked World.

        """
        items = [Item(i, f"{i}") for i in range(n_items)]
        recipes = self._build_recipes(items)
        zone = self._build_zone(items, recipes)

        world = World(zones=[zone], items=items, recipes=recipes)
        return world, zone

    @staticmethod
    def _build_zone(items: List[Item], recipes: List[Recipe]):
        # Search for items that should be foundable
        available_items = set()
        needed_items = set()
        for item in items:
            for recipe in recipes:
                items_produced = [stack.item for stack in recipe.outputs]
                if item in items_produced:
                    available_items.add(item)
                items_needed = [stack.item for stack in recipe.inputs]
                if item in items_needed:
                    needed_items.add(item)

        foundable_items = [item for item in needed_items if item not in available_items]
        return Zone(0, "zone", items=foundable_items)

    def _build_recipes(self, items: List[Item]) -> List[Recipe]:
        raise NotImplementedError
