# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Recursive Crafting Environment

Simple environments with recursivity oriented constructor rules.

"""

from typing import List

from crafting.world.items import Item, ItemStack
from crafting.world.recipes import Recipe

from crafting.examples.simple.env import SimpleCraftingEnv


class RecursiveCraftingEnv(SimpleCraftingEnv):

    """Recursive, an exponentially hierarchical Environment.

    Item n requires all previous items (0 to n-1).

    """

    def __init__(self, n_items: int, **kwargs):
        super().__init__(n_items, name="RecursiveCrafting", **kwargs)

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


class LightRecursiveCraftingEnv(SimpleCraftingEnv):

    """LightRecursive, a lighter version of the RecursiveCrafting Environment.

    Item n requires the k previous items (n-k to n-1).

    """

    def __init__(self, n_items: int, n_required_previous: int = 2, **kwargs):
        self.n_required_previous = n_required_previous
        if self.n_required_previous == 1:
            env_name = "LinearRecursiveCrafting"
        else:
            env_name = f"LightRecursiveCrafting-{self.n_required_previous}"
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


class LighterRecursiveCraftingEnv(SimpleCraftingEnv):

    """LighterRecursive, a lighter version of the LightRecursiveCraftingEnv Environment.

    Item n requires the k previous items except the item n-2 (n-k to n-3 and n-1).

    """

    def __init__(self, n_items: int, n_required_previous: int = 3, **kwargs):
        self.n_required_previous = n_required_previous
        if self.n_required_previous <= 2:
            env_name = "LinearRecursiveCrafting"
        else:
            env_name = f"LighterRecursiveCrafting-{self.n_required_previous}"
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
