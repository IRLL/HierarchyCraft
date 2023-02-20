r""" # Recursive Crafting Environments

Simple environments with recursivity oriented constructor rules.

## RecursiveCrafting

The goal of the environment is to get the last item.
But each item requires all the previous items,
hence the number of actions required is exponential with the number of items.

### *Proof*

Let $u_n$ be the number of transitions needed for item $n$.

Then $u_0 = 1$ and $\forall n \in N, u_n = 1 + \sum_{k=1}^{n} u_{n-k}$.

Thus $\forall n \in N, u_n = u_{n-1} + 1 + \sum_{k=1}^{n-1} u_{n-k}$.

Thus $\forall n \in N, u_n = 2 * u_{n-1}$.

We recognize a geometrical sequence of common ratio 2.

Thus $\forall n \in N, u_n = u_0*2^n = 2^n$.

### Example

For example, if there is $n=4$ items, the last item is 3.

But 3 requires all previous items: {2, 1, 0}.

And 2 requires all previous items: {1, 0}.

And 1 requires all previous items: {0}.

Item 0 can be obtained directly.

Thus the number of actions required is $1 + 2 + 4 + 1 = 8 = 2^4$.



"""

from typing import List

from crafting.env import CraftingEnv
from crafting.transformation import Transformation

from crafting.elements import Item, ItemStack
from crafting.world import world_from_transformations

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
        self.n_items = n_items
        transformations = self.build_transformations(items)
        world = world_from_transformations(transformations)
        super().__init__(
            world,
            name=f"RecursiveCrafting-I{n_items}",
            **kwargs,
        )

    def build_transformations(self, items: List[Item]) -> List[Transformation]:
        """Build transformations to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of transformations.

        """
        transformation = []

        for index, item in enumerate(items):
            if index == 0:
                inputs = []
            else:
                inputs = [ItemStack(items[item_id]) for item_id in range(index)]
            outputs = [ItemStack(item)]

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
        self.n_items = n_items
        self.n_required_previous = n_required_previous
        if n_required_previous == 1:
            env_name = "LinearRecursiveCrafting"
        else:
            env_name = f"LightRecursiveCrafting-K{n_required_previous}-I{n_items}"
        items = [Item(str(i)) for i in range(n_items)]
        transformations = self._transformations(items)
        world = world_from_transformations(transformations)
        super().__init__(world, name=env_name, **kwargs)

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
