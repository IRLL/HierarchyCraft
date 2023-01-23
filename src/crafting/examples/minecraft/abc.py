# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting Environment ABC's

All redifined specialized objects used for the MineCrafting environment.

"""

from typing import TYPE_CHECKING, List, Optional, Union

import numpy as np

from crafting.player.inventory import Inventory
from crafting.player.player import Player
from crafting.world.items import Item, ItemStack, Tool

if TYPE_CHECKING:
    from crafting.examples.minecraft.world import McWorld


class Block(Item):

    """Blocks are common minecraft items that can be gathered with tools.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Block name.
        hardness (float): How hard is the block to break.
        items_dropped (list of Item): (Optional) Items dropped when the block breaks.
            Blocks drops themselves by default.

    """

    def __init__(
        self,
        item_id: int,
        name: str,
        hardness: float,
        required_tools: list = None,
        drops: List[Item] = None,
    ):
        super().__init__(item_id, name, required_tools)
        self.hardness = hardness
        self.items_dropped = [self] if drops is None else drops


class Loot(Item):

    """Loots are common minecraft items that can be gathered in wilderness.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Loot name.
        stack_size (int): Number of loots dropped at once.

    """

    def __init__(
        self, item_id: int, name: str, required_tools: list = None, stack_size: int = 1
    ):
        super().__init__(item_id, name, required_tools)
        self.stack_size = stack_size


class McTool(Tool):

    """Special tool for minecraft, with durability and speed.

    Attributes:
        item_id (int): Unique item identification number.
        name (str): Tool name.
        durability (int): Tool durability
        speed (int): Tool speed.
        max_stack (int): Maximum number of tool per stack.

    """

    def __init__(self, item_id: int, name: str, durability: int, speed: int):
        super().__init__(item_id, name)
        self.durability = durability
        self._durability = durability
        self.speed = speed

    def use(self, item: Optional[Union[Block, Loot, Item]] = None) -> List[ItemStack]:
        """Use the tool on a given Item.

        Args:
            item: Item to use the tool on.

        Returns:
            List of ItemStack gathered by using the tool on the item.

        """
        if self._durability > 0 and isinstance(item, Block):
            stack_size = min(self.durability, 1 + int(self.speed / item.hardness))
            self._durability -= stack_size
            findings = [
                ItemStack(item_dropped, stack_size)
                for item_dropped in item.items_dropped
            ]
            return findings
        if self._durability > 0 and isinstance(item, Loot):
            self._durability -= 1
            return [ItemStack(item, item.stack_size)]
        return []

    @property
    def is_broken(self):
        """True if the tool is broken, False otherwise."""
        return not self._durability > 0

    def reset(self):
        """Reset the tool durability."""
        self._durability = self.durability


class McPlayer(Player):

    """Player of a MineCrafting environement."""

    def __init__(self, world: "McWorld"):
        """Player of a MineCrafting environement.

        Args:
            world: McWorld of a MineCrafting environment.

        """
        inventory = Inventory(world.items)
        forest_slot = world.zone_id_to_slot[0]
        super().__init__(
            inventory=inventory, zone=world.zones[forest_slot], name="Steve"
        )

    def choose_search_tool(self, item: Item) -> Tool:
        if item in self.zone.items and item.required_tools is not None:
            usable_tools = np.array(
                [tool for tool in item.required_tools if tool is not None]
            )
            tools_id = np.array([tool.item_id for tool in usable_tools])
            tools_slots = self.inventory.item_id_to_slot(tools_id)
            tools_quantities = self.inventory.content[tools_slots]
            usable_tools = usable_tools[tools_quantities > 0]
            if len(usable_tools) > 0:
                usable_tools_speed = np.array([tool.speed for tool in usable_tools])
                return usable_tools[np.argmax(usable_tools_speed)]
        return None

    def search_for(self, item: Item, tool: McTool) -> int:
        n_items_found = super().search_for(item, tool)
        if tool is not None and tool.is_broken:
            self.inventory.remove_stacks([ItemStack(tool)])
            tool.reset()
        return n_items_found
