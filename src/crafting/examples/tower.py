""" Tower Crafting Environment

Simple environment with tower-structured constructor rules.

"""

from typing import List

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack

try:
    import gym

    gym.register(
        id="TowerCrafting-v1",
        entry_point="crafting.examples.tower:TowerCraftingEnv",
    )

except ImportError:
    pass


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
        self.height = height
        self.width = width
        n_items = self.height * self.width + 1
        items = [Item(str(i)) for i in range(n_items)]
        name = f"TowerCrafting-H{self.height}-W{self.width}"
        if "max_step" not in kwargs or not isinstance(kwargs["max_step"], int):
            if self.width == 1:
                kwargs["max_step"] = 1 + int(self.width * (self.height + 1))
            else:
                # 1 + w + w**2 + ... + w**h
                kwargs["max_step"] = 1 + int(
                    (1 - self.width ** (self.height + 1)) / (1 - self.width)
                )
        transformations = self._transformations(items)
        super().__init__(transformations, name=name, **kwargs)

    def _transformations(self, items: List[Item]) -> List[Transformation]:
        """Build recipes to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes as transformations.

        """
        transformations = []

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
                    removed_player_items=inputs,
                    added_player_items=outputs,
                )
                transformations.append(new_recipe)

        # Last item recipe
        last_item = items[-1]
        outputs = [ItemStack(last_item)]
        inputs = []
        last_layer_id = (self.height - 1) * self.width
        for prev_item_id in range(self.width):
            required_item = items[last_layer_id + prev_item_id]
            inputs.append(ItemStack(required_item))

        new_recipe = Transformation(
            removed_player_items=inputs,
            added_player_items=outputs,
        )
        transformations.append(new_recipe)

        return transformations
