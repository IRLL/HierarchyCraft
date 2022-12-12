# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Random Crafting Environment

Generate a random Crafting environment using basic constructor rules.

"""

from typing import List, Tuple


from crafting.env import CraftingEnv
from crafting.world.world import World

from crafting.player.player import Player
from crafting.player.inventory import Inventory

from crafting.task import TaskList, TaskObtainItem, RewardShaping

from crafting.world.zones import Zone
from crafting.world.items import Item, ItemStack
from crafting.world.recipes import Recipe


class BaseSimpleCraftingEnv(CraftingEnv):

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
        zone = Zone(0, "zone", items=[items[0]])

        recipes = self._build_recipes(items)

        world = World(zones=[zone], items=items, recipes=recipes)
        return world, zone

    def _build_recipes(self, items: List[Item]) -> List[Recipe]:
        raise NotImplementedError


class StackedCraftingEnv(BaseSimpleCraftingEnv):

    """Stacked, an exponentially hierarchical Environment.

    Item n requires all previous items (0 to n-1).

    """

    def __init__(self, n_items: int, **kwargs):
        super().__init__(n_items, name="StackedCrafting", **kwargs)

    def _build_recipes(self, items: List[Item]) -> List[Recipe]:
        """Build recipes to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes.

        """
        recipes = []

        for item in items[1:]:
            inputs = [ItemStack(items[item_id]) for item_id in range(item.item_id)]
            outputs = [ItemStack(items[item.item_id])]

            # Build recipe
            new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
            recipes.append(new_recipe)

        return recipes


class LightStackedCraftingEnv(BaseSimpleCraftingEnv):

    """LightStacked, a lighter version of the StackedCrafting Environment.

    Item n requires the k previous items (n-k to n-1).

    """

    def __init__(self, n_items: int, n_required_previous: int = 2, **kwargs):
        self.n_required_previous = n_required_previous
        if self.n_required_previous == 1:
            env_name = "LinearStackedCrafting"
        else:
            env_name = f"LightStackedCrafting-{self.n_required_previous}"
        super().__init__(n_items, name=env_name, **kwargs)

    def _build_recipes(self, items: List[Item]) -> List[Recipe]:
        """Build recipes to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes.

        """
        recipes = []

        for item in items[1:]:
            low_id = max(0, item.item_id - self.n_required_previous)
            inputs = [
                ItemStack(items[item_id]) for item_id in range(low_id, item.item_id)
            ]
            outputs = [ItemStack(items[item.item_id])]

            # Build recipe
            new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
            recipes.append(new_recipe)

        return recipes


class LighterStackedCraftingEnv(BaseSimpleCraftingEnv):

    """LighterStacked, a lighter version of the LightStackedCraftingEnv Environment.

    Item n requires the k previous items except the item n-2 (n-k to n-3 and n-1).

    """

    def __init__(self, n_items: int, n_required_previous: int = 3, **kwargs):
        self.n_required_previous = n_required_previous
        if self.n_required_previous <= 2:
            env_name = "LinearStackedCrafting"
        else:
            env_name = f"LighterStackedCrafting-{self.n_required_previous}"
        super().__init__(n_items, name=env_name, **kwargs)

    def _build_recipes(self, items: List[Item]) -> List[Recipe]:
        """Build recipes to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes.

        """
        recipes = []

        for item in items[1:]:
            inputs = [ItemStack(items[item.item_id - 1])]
            if item.item_id >= 3:
                low_id = max(0, item.item_id - self.n_required_previous)
                inputs += [
                    ItemStack(items[item_id])
                    for item_id in range(low_id, item.item_id - 2)
                ]
            outputs = [ItemStack(items[item.item_id])]

            # Build recipe
            new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
            recipes.append(new_recipe)

        return recipes
