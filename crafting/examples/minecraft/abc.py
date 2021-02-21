# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting Environment ABC's

All redifined specialized objects used for the MineCrafting environment.

"""

from typing import List, Union
from crafting.world.items import Item, Tool, ItemStack


class Block(Item):

    """ Blocks are common minecraft items that can be gathered with tools.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Block name.
        hardness (float): How hard is the block to break.

    """

    def __init__(self, item_id: int, name: str, hardness:float, drops:List[Item]=None):
        super().__init__(item_id, name, max_stack=64)
        self.hardness = hardness
        self.items_dropped = [self] if drops is None else drops

class McTool(Tool):

    """ Special tool for minecraft, with durability and speed.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Tool name.
        durability (int): Tool durability
        speed (int): Tool speed.
        max_stack (int): Maximum number of tool per stack.

    """

    def __init__(self, item_id:int, name:str, durability:int, speed:int, max_stack:int=1):
        super().__init__(item_id, name, max_stack)
        self.durability = durability
        self.speed = speed

    def use(self, item:Union[Block, Item]=None):
        if self.durability > 0 and isinstance(item, Block):
            stack_size = min(self.durability, int(self.speed / item.hardness))
            self.durability -= stack_size
            findings = [
                ItemStack(item_dropped, stack_size)
                for item_dropped in item.items_dropped
            ]
            return findings
        return []
