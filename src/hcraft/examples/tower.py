"""# TowerHcraft Environment

Simple environment with tower-structured constructor rules
to evaluate polynomial sub-behaviors reusability.

The goal of the environment is to get the item on top of the tower.

The tower has 'height' layers and 'width' items per layer,
plus the final item on top of the last layer.

Each item in the tower requires all the items of the previous layer to be built.
Items of the floor layer require nothing and can be built from the start.

## Example

For example here is a tower of height 2 and width 3:

|   | 6 |   |
|:-:|:-:|:-:|
| 3 | 4 | 5 |
| 0 | 1 | 2 |

The goal here is to get the item 6.
Item 6 requires the items {3, 4, 5}.
Each of the items 3, 4 and 5 requires items {0, 1, 2}.
Each of the items 0, 1 and 2 requires nothing and can be crafted from the start.


"""

from typing import List

from hcraft.elements import Item
from hcraft.env import HcraftEnv
from hcraft.transformation import Transformation, Use, Yield, PLAYER
from hcraft.world import world_from_transformations
from hcraft.task import GetItemTask

try:
    import gym

    gym.register(
        id="TowerHcraft-v1",
        entry_point="hcraft.examples.tower:TowerHcraftEnv",
    )

except ImportError:
    pass


class TowerHcraftEnv(HcraftEnv):

    """Tower, a tower-structured hierarchical Environment.

    Item of given layer requires all items of the previous.
    The goal is to obtain the last item on top of the tower.

    """

    def __init__(self, height: int = 2, width: int = 3, **kwargs):
        """
        Args:
            height (int): Number of layers of the tower (ignoring goal item).
            width (int): Number of items per layer.
        """
        self.height = height
        self.width = width
        n_items = self.height * self.width + 1
        self.items = [Item(str(i)) for i in range(n_items)]
        name = f"TowerHcraft-H{self.height}-W{self.width}"
        if not isinstance(kwargs.get("max_step"), int):
            if self.width == 1:
                kwargs["max_step"] = 1 + int(self.width * (self.height + 1))
            else:
                # 1 + w + w**2 + ... + w**h
                kwargs["max_step"] = 1 + int(
                    (1 - self.width ** (self.height + 1)) / (1 - self.width)
                )
        transformations = self.build_transformations(self.items)
        world = world_from_transformations(transformations)
        if "purpose" not in kwargs:
            kwargs["purpose"] = GetItemTask(self.items[-1])
        super().__init__(world, name=name, **kwargs)

    def build_transformations(self, items: List[Item]) -> List[Transformation]:
        """Build transformations to make every item accessible.

        Args:
            items: List of items.

        Returns:
            List of craft recipes as transformations.

        """
        transformations = []

        # First layer recipes
        for first_layer_id in range(self.width):
            item = items[first_layer_id]
            new_recipe = Transformation(inventory_changes=[Yield(PLAYER, item)])
            transformations.append(new_recipe)

        # Tower recipes
        for layer in range(1, self.height):
            for item_layer_id in range(self.width):
                item_id = layer * self.width + item_layer_id
                item = items[item_id]

                inventory_changes = [Yield(PLAYER, item)]

                prev_layer_id = (layer - 1) * self.width
                for prev_item_id in range(self.width):
                    required_item = items[prev_layer_id + prev_item_id]
                    inventory_changes.append(Use(PLAYER, required_item, consume=1))

                new_recipe = Transformation(inventory_changes=inventory_changes)
                transformations.append(new_recipe)

        # Last item recipe
        last_item = items[-1]
        inventory_changes = [Yield(PLAYER, last_item)]
        last_layer_id = (self.height - 1) * self.width
        for prev_item_id in range(self.width):
            required_item = items[last_layer_id + prev_item_id]
            inventory_changes.append(Use(PLAYER, required_item, consume=1))

        new_recipe = Transformation(inventory_changes=inventory_changes)
        transformations.append(new_recipe)

        return transformations
