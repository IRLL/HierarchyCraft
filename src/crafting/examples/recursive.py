""" Recursive Crafting Environment

Simple environments with recursivity oriented constructor rules.

"""

from typing import List

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack

# gym is an optional dependency
try:
    import gym

    ENVS_PATH = "crafting.examples.recursive:"
    gym.register(
        id="RecursiveCrafting-v1",
        entry_point=ENVS_PATH + "RecursiveCraftingEnv",
    )

    gym.register(
        id="LightRecursiveCrafting-v1",
        entry_point=ENVS_PATH + "LightRecursiveCraftingEnv",
    )

except ImportError:
    pass


class RecursiveCraftingEnv(CraftingEnv):

    """Recursive, an exponentially hierarchical Environment.

    Item n requires one of all previous items (0 to n-1).

    """

    def __init__(self, n_items: int, **kwargs):
        items = [Item(str(i)) for i in range(n_items)]
        transformations = self._transformations(items)
        super().__init__(
            transformations,
            name=f"RecursiveCrafting-I{n_items}",
            **kwargs,
        )

    def _transformations(self, items: List[Item]) -> List[Transformation]:
        """Build recipes to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes as transformations.

        """
        transformation = []

        for index, item in enumerate(items):
            if index == 0:
                inputs = []
            else:
                inputs = [ItemStack(items[item_id]) for item_id in range(index)]
            outputs = [ItemStack(item)]

            # Build recipe
            new_recipe = Transformation(
                removed_player_items=inputs,
                added_player_items=outputs,
            )
            transformation.append(new_recipe)

        return transformation


class LightRecursiveCraftingEnv(CraftingEnv):

    """LightRecursive, a less recursive version of the RecursiveCrafting Environment.

    Item n requires one of the k previous items (n-k to n-1).

    """

    def __init__(self, n_items: int, n_required_previous: int = 2, **kwargs):
        self.n_required_previous = n_required_previous
        if n_required_previous == 1:
            env_name = "LinearRecursiveCrafting"
        else:
            env_name = f"LightRecursiveCrafting-K{n_required_previous}-I{n_items}"
        items = [Item(str(i)) for i in range(n_items)]
        transformations = self._transformations(items)
        super().__init__(transformations, name=env_name, **kwargs)

    def _transformations(self, items: List[Item]) -> List[Transformation]:
        """Build recipes to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes.

        """
        transformation = []

        for index, item in enumerate(items):
            low_id = max(0, index - self.n_required_previous)
            if index == 0:
                inputs = []
            else:
                inputs = [ItemStack(items[item_id]) for item_id in range(low_id, index)]
            outputs = [ItemStack(item)]

            # Build recipe
            new_recipe = Transformation(
                removed_player_items=inputs,
                added_player_items=outputs,
            )
            transformation.append(new_recipe)

        return transformation
