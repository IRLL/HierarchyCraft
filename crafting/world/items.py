# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Items

Here are defined abstract classes for items, tools and item-stacks

"""

from typing import List


class Item():

    """ Item are to represent objects that could be present in an inventory

    Args:
        item_id (int): Unique item identification number.
        name (str): Item name.
        max_stack (int): Maximum number of this item per stack.

    """

    def __init__(self, item_id: int, name: str, max_stack: int=1):
        self.item_id = item_id
        self.name = name
        self.max_stack = max_stack

    def __repr__(self):
        return f"{self.name.capitalize()}({self.item_id})"


class Tool(Item):

    """ Tool are to represent special objects that takes a whole inventory slot.

    Tool are special objects with additional proprieties taking a whole inventory slot.

    Args:
        item_id (int): Unique item identification number.
        name (str): Item name.
        params (dict): (Optional) Additional tool attributes.

    """

    def __init__(self, item_id: int, name: str, params: dict=None):
        super().__init__(item_id, name, max_stack=1)
        self.params = list(params.keys())
        for param, param_value in params.items():
            setattr(self, param, param_value)

    def __repr__(self):
        params = [getattr(self, param) for param in self.params]
        return f"{self.name.capitalize()}({self.item_id}){params}"


class ItemStack(Item):

    """ ItemStack are to represent stackable objects that could be present in an inventory.

    Args:
        item (Item): Item object that will be stacked.
        size (int): Initial stack value.

    """

    def __init__(self, item: Item, size:int):
        super().__init__(item.item_id, item.name, item.max_stack)
        self.item = item
        self.size = size

    def add(self, size: int) -> List[Item]:
        """ Add new elements to the stack

        If the total is more that the stack capability,
        multiple stacks will be resulted.

        Args:
            size (int): Number of elemets to add to the stack.

        Return:
            (list): List of resulted stacks.

        """
        new_size = self.size + size
        if new_size <= self.max_stack:
            new_stacks = [ItemStack(self.item, new_size)]
        else:
            new_stack = ItemStack(self.item, 0)
            new_stacks = new_stack.add(new_size - self.max_stack)
            new_stacks = [ItemStack(self.item, self.max_stack)] + new_stacks
        return new_stacks

    def sub(self, size: int) -> List[Item]:
        """ Remove elements from the stack

        If the removed size is exactly that the stack size,
        no stacks will be resulted.

        Args:
            size (int): Number of elements to add to the stack.

        Return:
            (list): List of resulted stacks.

        """
        if self.size == size:
            return []
        elif self.size > size:
            return [ItemStack(self.item, self.size - size)]
        else:
            raise ValueError("Not enough in initial stack to remove")

    def __add__(self, other: Item) -> List[Item]:
        assert isinstance(other, ItemStack)
        assert self.item_id == other.item_id
        return self.add(other.size)

    def __sub__(self, other: Item) -> List[Item]:
        assert isinstance(other, ItemStack)
        assert self.item_id == other.item_id
        return self.sub(other.size)

    def __repr__(self) -> str:
        return f"{self.size} {self.name.capitalize()}({self.item_id})"
