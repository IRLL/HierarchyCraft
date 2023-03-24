# pylint: disable=no-member

""" Random HierarchyCraft Environment

Generate a random HierarchyCraft environment using basic constructor rules.

"""

from typing import Dict, List, Optional

import numpy as np

from hcraft.elements import Item
from hcraft.env import HcraftEnv
from hcraft.transformation import Transformation, Use, Yield, PLAYER
from hcraft.world import world_from_transformations
from hcraft.purpose import GetItemTask, Purpose


class RandomHcraftEnv(HcraftEnv):

    """Random HierarchyCraft Environment"""

    def __init__(
        self,
        n_items_per_n_inputs: Optional[Dict[int, int]] = None,
        seed: int = None,
        **kwargs,
    ):
        """Random HierarchyCraft Environment.

        Args:
            n_items_per_n_inputs: Mapping from the number of inputs to the number of items
                with this number of inputs.
        Kwargs:
            max_step: The maximum number of steps until done.
        """
        if n_items_per_n_inputs is None:
            n_items_per_n_inputs = {0: 5, 1: 5, 2: 10, 3: 5}

        self.seed = seed
        self.np_random = np.random.RandomState(seed)
        self.n_items = sum(n_items_per_n_inputs.values())
        env_characteristics = "".join(
            [
                f"{n_inputs}I{n_items}"
                for n_inputs, n_items in n_items_per_n_inputs.items()
            ]
        )
        name = f"RandomCrafing-{env_characteristics}-S{seed}"
        self.items: List[Item] = []
        transformations = self._transformations(n_items_per_n_inputs)
        world = world_from_transformations(transformations)
        if "purpose" not in kwargs:
            purpose = Purpose()
            for item in self.items:
                purpose.add_task(GetItemTask(item))
            kwargs["purpose"] = purpose
        super().__init__(world, name=name, **kwargs)

    def _transformations(
        self,
        n_items_per_n_inputs: Dict[int, int],
    ) -> List[Transformation]:
        """Build transformations for a RandomHcraft environement.

        Args:
            n_items_per_n_inputs: Mapping from the number of inputs to the number of items
                with this number of inputs.
        Returns:
            A list of random (but accessible) transformations.

        """

        for n_inputs, n_items in n_items_per_n_inputs.items():
            self.items += [Item(f"{n_inputs}_{i}") for i in range(n_items)]

        transformations = []

        # Items with 0 inputs are accessible from the start
        accessible_items = []
        for item in self.items:
            if item.name.startswith("0"):
                search_item = Transformation(inventory_changes=[Yield(PLAYER, item)])
                transformations.append(search_item)
                accessible_items.append(item)

        # Other items are built with inputs
        unaccessible_items = [
            item for item in self.items if item not in accessible_items
        ]
        self.np_random.shuffle(unaccessible_items)

        while len(accessible_items) < len(self.items):
            new_accessible_item = unaccessible_items.pop()
            inventory_changes = [Yield(PLAYER, new_accessible_item)]

            n_inputs = int(new_accessible_item.name.split("_")[0])
            n_inputs = min(n_inputs, len(accessible_items))

            # Chooses randomly accessible items
            input_items = list(
                self.np_random.choice(accessible_items, size=n_inputs, replace=False)
            )
            inventory_changes += [Use(PLAYER, item, consume=1) for item in input_items]

            # Build recipe
            new_recipe = Transformation(inventory_changes=inventory_changes)
            transformations.append(new_recipe)
            accessible_items.append(new_accessible_item)

        return transformations
