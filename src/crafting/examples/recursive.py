# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Recursive Crafting Environment

Simple environments with recursivity oriented constructor rules.

"""

from typing import List

from crafting.env import CraftingEnv
from crafting.world import Item, ItemStack
from crafting.transformation import Transformation

# gym is an optional dependency
try:
    import gym

    ENVS_PATH = "crafting.examples.recursive:"
    gym.register(
        id="RecursiveCrafting-v1",
        entry_point=ENVS_PATH + "RecursiveCraftingEnv",
    )

    # gym.register(
    #     id="RecursiveCrafting",
    #     entry_point=ENVS_PATH + "RecursiveCraftingEnv",
    # )

    # gym.register(
    #     id="RecursiveCrafting",
    #     entry_point=ENVS_PATH + "RecursiveCraftingEnv",
    # )

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

        for index, item in enumerate(items[1:]):
            inputs = [ItemStack(items[item_id]) for item_id in range(index)]
            outputs = [ItemStack(item)]

            # Build recipe
            new_recipe = Transformation(
                removed_player_items=inputs,
                added_player_items=outputs,
            )
            transformation.append(new_recipe)

        return transformation


# class LightRecursiveCraftingEnv(CraftingEnv):

#     """LightRecursive, a less recursive version of the RecursiveCrafting Environment.

#     Item n requires one of the k previous items (n-k to n-1).

#     """

#     def __init__(self, n_items: int, n_required_previous: int = 2, **kwargs):
#         self.n_required_previous = n_required_previous
#         if self.n_required_previous == 1:
#             env_name = "LinearRecursiveCrafting"
#         else:
#             env_name = f"LightRecursiveCrafting-{self.n_required_previous}"
#         super().__init__(n_items, name=env_name, **kwargs)

#     def _build_recipes(self, items: List[Item]) -> List[Transformation]:
#         """Build recipes to make every item accessible.

#         Args:
#             items: List of items.

#         Returns:
#             List of craft recipes.

#         """
#         recipes = []

#         for item in items[1:]:
#             low_id = max(0, item.item_id - self.n_required_previous)
#             inputs = [
#                 ItemStack(items[item_id]) for item_id in range(low_id, item.item_id)
#             ]
#             outputs = [ItemStack(items[item.item_id])]

#             # Build recipe
#             new_recipe = Transformation(len(recipes), inputs=inputs, outputs=outputs)
#             recipes.append(new_recipe)

#         return recipes


# class LighterRecursiveCraftingEnv(CraftingEnv):

#     """LighterRecursive, a lighter version of the LightRecursiveCraftingEnv Environment.

#     Item n requires the k previous items except the item n-2 (n-k to n-3 and n-1).

#     """

#     def __init__(self, n_items: int, n_required_previous: int = 3, **kwargs):
#         self.n_required_previous = n_required_previous
#         if self.n_required_previous <= 2:
#             env_name = "LinearRecursiveCrafting"
#         else:
#             env_name = f"LighterRecursiveCrafting-{self.n_required_previous}"
#         super().__init__(n_items, name=env_name, **kwargs)

#     def _build_recipes(self, items: List[Item]) -> List[Transformation]:
#         """Build recipes to make every item accessible.

#         Args:
#             items: List of items.

#         Returns:
#             List of craft recipes.

#         """
#         recipes = []

#         for item in items[1:]:
#             inputs = [ItemStack(items[item.item_id - 1])]
#             if item.item_id >= 3:
#                 low_id = max(0, item.item_id - self.n_required_previous)
#                 inputs += [
#                     ItemStack(items[item_id])
#                     for item_id in range(low_id, item.item_id - 2)
#                 ]
#             outputs = [ItemStack(items[item.item_id])]

#             # Build recipe
#             new_recipe = Transformation(inputs=inputs, outputs=outputs)
#             recipes.append(new_recipe)

#         return recipes


if __name__ == "__main__":
    import gym
    from crafting.render.human import render_env_with_human

    env = gym.make("RecursiveCrafting-v1", n_items=7, max_step="auto")
    render_env_with_human(env)
