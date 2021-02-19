# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Inventory """

from typing import Tuple, List

import numpy as np

from crafting.world.items import Item, ItemStack

class Inventory():

    """ Inventory is where Items are stored """

    def __init__(self, items: Tuple[Item]):
        self.items = items
        self.items_ids = tuple(map(lambda x: x.item_id, items))
        self.items_max_stack = np.array(map(lambda x: x.max_stack, items))
        self.content = np.zeros(len(items), dtype=np.int32)

        self.item_id_to_slot_dict = {
            item.item_id: self.items_ids.index(item.item_id) for item in items
        }

        def item_id_to_slot(item_id):
            return self.item_id_to_slot_dict[item_id]

        self.item_id_to_slot = np.vectorize(item_id_to_slot)

    def _stacks_ind_size(self, stacks):
        stack_ids = np.array([stack.item_id for stack in stacks])
        stack_ind = self.item_id_to_slot(stack_ids)
        stack_sizes = np.array([stack.size for stack in stacks])
        print(stack_ind, stack_sizes)
        return stack_ind, stack_sizes

    def add_stacks(self, stacks: List[ItemStack]):
        stack_ind, stack_sizes = self._stacks_ind_size(stacks)
        self.content[stack_ind] += stack_sizes

    def remove_stacks(self, stacks: List[ItemStack]):
        stack_ind, stack_sizes = self._stacks_ind_size(stacks)
        self.content[stack_ind] -= stack_sizes

    def __add__(self, other):
        self.content += other
        return self

    def __sub__(self, other):
        self.content -= other
        return self

    def __repr__(self):
        non_empty_items = self.content != 0
        items_in_inv = np.array(self.items)[non_empty_items]
        return f'Inventory{items_in_inv}{self.content[non_empty_items]}'
