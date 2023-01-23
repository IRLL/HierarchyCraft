# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Items

Here are defined abstract classes for items, tools and item-stacks

"""

from operator import index
from typing import List


class Item:

    """Item are to represent objects that could be present in an inventory

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Item name.
        max_stack (int): Maximum number of this item per stack.

    """

    def __init__(self, item_id: int, name: str, required_tools: List["Tool"] = None):
        """Item are to represent objects that could be present in an inventory

        Args:
            item_id: Unique item identification number.
            name: Item name.
            required_tools: List of tools that can be used to gather the item.
                If None (Default), the item can be gathered without requirement.

        """
        self.item_id = item_id
        self.name = name
        self.required_tools = required_tools
        if (
            isinstance(self.required_tools, (list, tuple))
            and len(self.required_tools) == 0
        ):
            self.required_tools = None

    def __eq__(self, item):
        if isinstance(item, Item):
            return self.item_id == item.item_id
        try:
            # Accept any int-like thing
            return self.item_id == index(item)
        except TypeError:
            return NotImplemented

    def __hash__(self):
        return self.item_id

    def __repr__(self):
        if self.name.capitalize() == str(self.item_id):
            return f"Item({self.item_id})"

        return f"{self.name.capitalize()}({self.item_id})"


class ItemStack(Item):

    """ItemStack are to represent stackable objects that could be present in an inventory.

    Attributes:
        item (:obj:`Item`): Item object that will be stacked.
        item_id (int): Unique item identification number.
        name (str): Item name.
        required_tools: List of tools that can be used to gather the item.
            If None (Default), the item can be gathered without requirement.
        size (int): Number of items in stack.

    """

    def __init__(self, item: Item, size: int = 1):
        """ItemStack are to represent stackable objects that could be present in an inventory.

        Args:
            item: Item object that will be stacked.
            size: Initial stack value.

        """
        super().__init__(item.item_id, item.name, item.required_tools)
        self.item = item
        self.size = size

    def __repr__(self) -> str:
        item_name = repr(self.item)
        if self.size == 1:
            return item_name
        return f"{item_name}[{self.size}]"


class Tool(Item):

    """Tool are to represent special usable items.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Tool name.
        max_stack (int): Maximum number of tools per stack.

    """

    def use(self, item: Item = None) -> List[ItemStack]:
        """Use the tool on the (optional) given item.

        Args:
            item: Item to use the tool on.

        Returns:
            The list of found item stacks.

        """
        if item is not None:
            return [ItemStack(item)]
        return []
