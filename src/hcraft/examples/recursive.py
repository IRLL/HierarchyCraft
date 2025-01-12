"""# Recursive HierarchyCraft Environments

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

Requirements graph (n_items=6):
<div class="graph">
.. include:: ../../../docs/images/requirements_graphs/RecursiveHcraft-I6.html
</div>
"""

from typing import List

from hcraft.elements import Item
from hcraft.env import HcraftEnv
from hcraft.transformation import Transformation, Use, Yield, PLAYER
from hcraft.task import GetItemTask
from hcraft.world import world_from_transformations

# gym is an optional dependency
try:
    import gymnasium as gym

    gym.register(
        id="RecursiveHcraft-v1",
        entry_point="hcraft.examples.recursive:RecursiveHcraftEnv",
    )

except ImportError:
    pass


class RecursiveHcraftEnv(HcraftEnv):
    """RecursiveHcraft Environment"""

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
