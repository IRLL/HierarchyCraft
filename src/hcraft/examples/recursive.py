r""" # Recursive HierarchyCraft Environments

Simple environments with recursivity oriented constructor rules.





"""

from typing import List

from hcraft.elements import Item
from hcraft.env import HcraftEnv
from hcraft.transformation import Transformation, Use, Yield, PLAYER
from hcraft.task import GetItemTask
from hcraft.world import world_from_transformations

# gym is an optional dependency
try:
    import gym

    ENVS_PATH = "hcraft.examples.recursive:"
    gym.register(
        id="RecursiveHcraft-v1",
        entry_point=ENVS_PATH + "RecursiveHcraftEnv",
    )

    gym.register(
        id="LightRecursiveHcraft-v1",
        entry_point=ENVS_PATH + "LightRecursiveHcraftEnv",
    )

except ImportError:
    pass


class RecursiveHcraftEnv(HcraftEnv):

    """RecursiveHcraft Environment

    The goal of the environment is to get the last item.
    But each item requires all the previous items,
    hence the number of actions required is exponential with the number of items.

    Example:
        >>> env = RecursiveHcraft(n_items=4)
        For example, if there is 4 items, the last item is 3.
        But 3 requires all previous items: {2, 1, 0}.
        And 2 requires all previous items: {1, 0}.
        And 1 requires all previous items: {0}.
        Finally Item 0 can be obtained directly.
        Thus the number of actions required is $1 + 2 + 4 + 1 = 8 = 2^4$.

    """

    def __init__(self, n_items: int = 6, **kwargs):
        items = [Item(str(i)) for i in range(n_items)]
        self.n_items = n_items
        transformations = self.build_transformations(items)
        world = world_from_transformations(transformations)
        if "purpose" not in kwargs:
            kwargs["purpose"] = GetItemTask(items[-1])
        super().__init__(
            world,
            name=f"RecursiveHcraft-I{n_items}",
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
            inventory_changes = [Yield(PLAYER, item)]
            if index > 0:
                inventory_changes += [
                    Use(PLAYER, items[item_id], consume=1) for item_id in range(index)
                ]
            new_recipe = Transformation(inventory_changes=inventory_changes)
            transformation.append(new_recipe)

        return transformation


class LightRecursiveHcraftEnv(HcraftEnv):

    """LightRecursive, a less recursive version of the RecursiveHcraft Environment.

    Item n requires one of each the k previous items (n-k to n-1).

    Example:
        >>> env = LightRecursiveHcraftEnv(n_items=4, n_required_previous=2)
        For example, if there is 5 items, the last item is 4.
        But 4 requires the 2 previous items: {3, 2}.
        And 3 requires the 2 previous items: {2, 1}.
        And 2 requires the 2 previous items: {1, 0}.
        And 1 requires the only previous items: {0}.
        Finally Item 0 can be obtained directly.

    """

    def __init__(self, n_items: int = 6, n_required_previous: int = 2, **kwargs):
        self.n_items = n_items
        self.n_required_previous = n_required_previous
        if n_required_previous == 1:
            env_name = "LinearRecursiveHcraft"
        else:
            env_name = f"LightRecursiveHcraft-K{n_required_previous}-I{n_items}"
        items = [Item(str(i)) for i in range(n_items)]
        transformations = self._transformations(items)
        world = world_from_transformations(transformations)
        if "purpose" not in kwargs:
            kwargs["purpose"] = GetItemTask(items[-1])
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
            inventory_changes = [Yield(PLAYER, item)]
            if index > 0:
                inventory_changes += [
                    Use(PLAYER, items[item_id], consume=1)
                    for item_id in range(low_id, index)
                ]

            new_recipe = Transformation(inventory_changes=inventory_changes)
            transformation.append(new_recipe)

        return transformation
