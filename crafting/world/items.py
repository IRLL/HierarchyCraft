# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Items

Here are defined abstract classes for items, tools and item-stacks

"""

from typing import List

class Item():

    """ Item are to represent objects that could be present in an inventory

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Item name.
        max_stack (int): Maximum number of this item per stack.

    """

    def __init__(self, item_id: int, name: str, max_stack: int=1):
        """ Item are to represent objects that could be present in an inventory

        Args:
            item_id: Unique item identification number.
            name: Item name.
            max_stack: Maximum number of this item per stack.

        """
        self.item_id = item_id
        self.name = name
        self.max_stack = max_stack

    def __repr__(self):
        return f"{self.name.capitalize()}({self.item_id})"


class ItemStack(Item):

    """ ItemStack are to represent stackable objects that could be present in an inventory.

    Attributes:
        item (:obj:`Item`): Item object that will be stacked.
        item_id (int): Unique item identification number.
        name (str): Item name.
        max_stack (int): Maximum number of this item per stack.
        size (int): Number of items in stack.

    """

    def __init__(self, item: Item, size:int=1):
        """ ItemStack are to represent stackable objects that could be present in an inventory.

        Args:
            item: Item object that will be stacked.
            size: Initial stack value.

        """
        super().__init__(item.item_id, item.name, item.max_stack)
        self.item = item
        self.size = size

    def __repr__(self) -> str:
        return f"{self.name.capitalize()}({self.item_id})[{self.size}]"


class Tool(Item):

    """ Tool are to represent special usable items.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Tool name.
        max_stack (int): Maximum number of tools per stack.

    """

    def use(self, item:Item=None) -> List[ItemStack]:
        """ Use the tool on the (optional) given item.

        Args:
            item: Item to use the tool on.

        Returns:
            The list of found item stacks.

        """
        if item is not None:
            return [ItemStack(item)]
        return []
