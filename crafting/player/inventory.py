# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Inventory """

from typing import Tuple, List, Union

import numpy as np

from crafting.world.items import ItemStack


class Inventory:

    """Inventory is where Items are stored

    Attributes:
        items (tuple of :obj:`Item`): All items that could be added to this inventory.
        items_ids (tuple of int): All items_ids that could be added to this inventory.
        items_max_stack (tuple of int): Max number of item per stack for each item.
        content (:obj:`np.ndarray`): Array of number of contained items in the inventory.
        item_id_to_slot (func): Function mapping item_ids to slot_index in content.

    """

    def __init__(self, items: Tuple["Item"]):
        """Inventory is where Items are stored

        Args:
            items: All items that could be added to this inventory.

        """
        self.items = items
        self.items_ids = tuple(map(lambda x: x.item_id, items))
        self.items_max_stack = np.array(map(lambda x: x.max_stack, items))
        self.content = np.zeros(len(items), dtype=np.int32)

        self._item_id_to_slot_dict = {
            item.item_id: self.items_ids.index(item.item_id) for item in items
        }

        def item_id_to_slot(item_id):
            return self._item_id_to_slot_dict[item_id]

        self.item_id_to_slot = np.vectorize(item_id_to_slot)

    def stacks_id_and_size(self, stacks: "ItemStack") -> Tuple[np.ndarray]:
        """Gather the item_id and size of a list of stacks."""
        stack_ids = np.array([stack.item_id for stack in stacks])
        stack_ind = self.item_id_to_slot(stack_ids)
        stack_sizes = np.array([stack.size for stack in stacks])
        return stack_ind, stack_sizes

    def add_stacks(self, stacks: List["ItemStack"]) -> bool:
        """Add a list of ItemStack into the inventory content

        Args:
            stacks: ItemStacks to add.

        Returns:
            True if successful, False otherwise.

        """
        stack_ind, stack_sizes = self.stacks_id_and_size(stacks)
        self.content[stack_ind] += stack_sizes
        return True

    def remove_stacks(self, stacks: List["ItemStack"]) -> bool:
        """Remove a list of ItemStack from the inventory content

        Args:
            stacks: ItemStacks to remove.

        Returns:
            True if successful, False otherwise.

        Raise:
            ValueError: If content does not have enough to remove.

        """
        stack_ind, stack_sizes = self.stacks_id_and_size(stacks)

        if np.any(self.content[stack_ind] < stack_sizes):
            raise ValueError("Not enough in content to remove")

        self.content[stack_ind] -= stack_sizes
        return True

    def __add__(self, other):
        self.content += other
        return self

    def __sub__(self, other):
        self.content -= other
        return self

    def __repr__(self):
        non_empty_items = self.content != 0
        items_in_inv = np.array(self.items)[non_empty_items]
        content = self.content[non_empty_items]
        return str(
            [f"{quantity} {name}" for name, quantity in zip(items_in_inv, content)]
        )

    def __contains__(self, item: Union["Item", "ItemStack"]):
        wanted_size = item.size if isinstance(item, ItemStack) else 1

        item_slot = self.item_id_to_slot(item.item_id)
        size = self.content[item_slot]

        return size >= wanted_size
