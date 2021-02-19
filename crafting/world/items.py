# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Items

Here are defined abstract classes for items, tools and item-stacks

"""


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


class Tool(Item):

    """ Tool are to represent special objects that takes a whole inventory slot.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Item name.
        **params: (Optional) Additional tool attributes.

    """

    def __init__(self, item_id: int, name: str, params: dict=None):
        """ Tool are to represent special objects that takes a whole inventory slot.

        Args:
            item_id: Unique item identification number.
            name: Item name.
            params: (Optional) Additional tool attributes.

        """
        super().__init__(item_id, name, max_stack=1)
        self.params = list(params.keys())
        for param, param_value in params.items():
            setattr(self, param, param_value)

    def __repr__(self):
        params = [getattr(self, param) for param in self.params]
        return f"{self.name.capitalize()}({self.item_id}){params}"


class ItemStack(Item):

    """ ItemStack are to represent stackable objects that could be present in an inventory.

    Attributes:
        item (:obj:`Item`): Item object that will be stacked.
        item_id (int): Unique item identification number.
        name (str): Item name.
        max_stack (int): Maximum number of this item per stack.
        size (int): Number of items in stack.

    """

    def __init__(self, item: Item, size:int):
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
