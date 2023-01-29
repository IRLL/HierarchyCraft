# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Tower Crafting Environment

Simple environment with tower-structured constructor rules.

"""

from typing import List

from crafting.env import CraftingEnv
from crafting.world import Item, ItemStack
from crafting.transformation import Transformation


class TowerCraftingEnv(CraftingEnv):

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
        items = self._items()
        name = f"TowerCrafting-v1-H{self.height}-W{self.width}"
        if "max_step" not in kwargs or not isinstance(kwargs["max_step"], int):
            if self.width == 1:
                kwargs["max_step"] = 1 + int(self.width * (self.height + 1))
            else:
                # 1 + w + w**2 + ... + w**h
                kwargs["max_step"] = 1 + int(
                    (1 - self.width ** (self.height + 1)) / (1 - self.width)
                )
        super().__init__(n_items, name=name, **kwargs)

    def _items(self) -> List[Item]:
        """"""

    def _transformations(self, items: List[Item]) -> List[Transformation]:
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

                new_recipe = Transformation(
                    added_player_items=inputs, removed_player_items=outputs
                )
                recipes.append(new_recipe)

        # Last item recipe
        last_item = items[-1]
        outputs = [ItemStack(last_item)]
        inputs = []
        last_layer_id = (self.height - 1) * self.width
        for prev_item_id in range(self.width):
            required_item = items[last_layer_id + prev_item_id]
            inputs.append(ItemStack(required_item))

        new_recipe = Transformation(
            added_player_items=inputs, removed_player_items=outputs
        )
        recipes.append(new_recipe)

        return recipes


if __name__ == "__main__":
    import gym
    from crafting.render.human import render_env_with_human

    env = gym.make("TowerCrafting-v1", height=4, width=2, max_step="auto")
    render_env_with_human(env)