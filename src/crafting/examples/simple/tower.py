# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Tower Crafting Environment

Simple environment with tower-structured constructor rules.

"""

from typing import List

from crafting.world.items import Item, ItemStack
from crafting.world.recipes import Recipe

from crafting.examples.simple.env import SimpleCraftingEnv


class TowerCraftingEnv(SimpleCraftingEnv):

    """Tower, a tower-structured hierarchical Environment.

    Item of layer l requires all items of the previous layer l-1.
    The goal is to obtain the last item on top of the tower.

    For example, a tower of height 3 and width 2:
        #6##
        #45#
        #23#
        #01#

    """

    def __init__(self, height: int, width: int, **kwargs):
        """Tower, a tower-structured hierarchical Environment.

        Args:
            height (int): Number of layers of the tower (ignoring goal item).
            width (int): Number of items per layer.
        """
        self.height = int(height)
        self.width = int(width)
        assert self.height > 0
        assert self.width > 0
        n_items = self.height * self.width + 1
        name = f"TowerCrafting-v1-H{self.height}-W{self.width}"
        if "max_step" not in kwargs:
            kwargs["max_step"] = (
                sum(self.width**h for h in range(self.height + 1)) + 1
            )
        super().__init__(n_items, name=name, **kwargs)

    def _build_recipes(self, items: List[Item]) -> List[Recipe]:
        """Build recipes to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes.

        """
        recipes = []

        # Tower recipes
        for layer in range(1, self.height):
            for item_layer_id in range(self.width):
                item_id = layer * self.width + item_layer_id
                item = items[item_id]

                outputs = [ItemStack(item)]
                inputs = []
                prev_layer_id = (layer - 1) * self.width
                for prev_item_id in range(self.width):
                    required_item = items[prev_layer_id + prev_item_id]
                    inputs.append(ItemStack(required_item))

                new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
                recipes.append(new_recipe)

        # Last item recipe
        last_item = items[-1]
        outputs = [ItemStack(last_item)]
        inputs = []
        last_layer_id = (self.height - 1) * self.width
        for prev_item_id in range(self.width):
            required_item = items[last_layer_id + prev_item_id]
            inputs.append(ItemStack(required_item))

        new_recipe = Recipe(len(recipes), inputs=inputs, outputs=outputs)
        recipes.append(new_recipe)

        return recipes
