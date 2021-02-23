# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting Environment ABC's

All redifined specialized objects used for the MineCrafting environment.

"""

from typing import List, Union
import numpy as np

from crafting.world.items import Item, Tool, ItemStack
from crafting.world.world import World
from crafting.player.player import Player
from crafting.player.inventory import Inventory

class Block(Item):

    """ Blocks are common minecraft items that can be gathered with tools.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Block name.
        hardness (float): How hard is the block to break.
        items_dropped (list of Item): (Optional) Items dropped when the block breaks.
            Blocks drops themselves by default.

    """

    def __init__(self, item_id: int, name: str, hardness:float, drops:List[Item]=None):
        super().__init__(item_id, name, max_stack=64)
        self.hardness = hardness
        self.items_dropped = [self] if drops is None else drops

class Loot(Item):

    """ Loots are common minecraft items that can be gathered in wilderness.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Loot name.
        stack_size (int): Number of loots dropped at once.

    """

    def __init__(self, item_id: int, name: str, stack_size: int=1):
        super().__init__(item_id, name, max_stack=64)
        self.stack_size = stack_size

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

    def use(self, item:Union[Block, Loot, Item]=None):
        if self.durability > 0 and isinstance(item, Block):
            stack_size = min(self.durability, 1+int(self.speed / item.hardness))
            self.durability -= stack_size
            findings = [
                ItemStack(item_dropped, stack_size)
                for item_dropped in item.items_dropped
            ]
            return findings
        if self.durability > 0 and isinstance(item, Loot):
            self.durability -= 1
            return [ItemStack(item, item.stack_size)]
        return []

class McPlayer(Player):

    def __init__(self, world: World):
        inventory = Inventory(world.items)
        self.hand = world.item_from_id[0]
        inventory.add_stacks([ItemStack(self.hand)])
        forest_slot = world.zone_id_to_slot[0]
        super().__init__(
            inventory=inventory,
            zone=world.zones[forest_slot],
            name='Steve'
        )

    def choose_tool(self, item:Item) -> Tool:
        if item.item_id in self.zone.items:
            usable_tools = np.array(self.zone.items[item.item_id])
            tools_id = np.array([tool.item_id for tool in usable_tools])
            tools_slots = self.inventory.item_id_to_slot(tools_id)
            tools_quantities = self.inventory.content[tools_slots]
            usable_tools = usable_tools[tools_quantities > 0]
            if len(usable_tools) > 0:
                usable_tools_speed = np.array([tool.speed for tool in usable_tools])
                return usable_tools[np.argmax(usable_tools_speed)]
        return self.hand
