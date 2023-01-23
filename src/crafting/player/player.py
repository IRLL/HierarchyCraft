# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Player """

from typing import Optional

from crafting.player.inventory import Inventory
from crafting.world.items import Item, Tool
from crafting.world.recipes import Recipe
from crafting.world.zones import Zone


class Player:

    """Player are entities with an inventory positioned in a zone.

    Attributes:
        inventory (:obj:`Inventory`): Player inventory.
        zone (:obj:`Zone`): Player zone.
        name (str): Player name.

    """

    def __init__(self, inventory: Inventory, zone: Zone, name: str = "Player"):
        """Player are moving inventories that can perform actions.

        Attributes:
            inventory: Initial player inventory.
            zone: Initial player zone.
            name: Initial player name.

        """
        self.inventory = inventory
        self.zone = zone
        self.name = name
        self.score = 0

    def craft(self, recipe: Recipe) -> bool:
        """Use a recipe

        Args:
            recipe: The recipe to use.

        Returns:
            True if succeded, False otherwise.

        """
        if self.can_craft(recipe):
            return recipe(self.inventory, self.zone)
        return False

    def can_craft(self, recipe: Recipe) -> bool:
        """Check if the recipe can be performed

        Args:
            recipe: Recipe to be tested.

        Return:
            True if the recipe can be used, False otherwise.

        """
        return recipe.can_craft(self.inventory, self.zone)

    def choose_search_tool(self, item: Item) -> Optional[Tool]:
        """Choose a tool to search for an item.

        Args:
            item (Item): The item to search for.

        Returns:
            The chosen tool.

        """
        if item in self.zone.items and item.required_tools is not None:
            usable_tools = [
                tool
                for tool in item.required_tools
                if tool is not None and tool in self.inventory
            ]
            if len(usable_tools) > 0:
                return usable_tools[0]
        return None

    def choose_access_tool(self, zone: Zone) -> Optional[Tool]:
        """Choose a tool to search for access a zone.

        Args:
            zone (Zone): The Zone to access.

        Returns:
            The chosen tool.

        """
        if zone.required_tools is None:
            return None
        usable_tools = [tool for tool in zone.required_tools if tool in self.inventory]
        if len(usable_tools) > 0:
            return usable_tools[0]
        return None

    def search_for(self, item: Item, tool: Tool) -> int:
        """Search for an item using a tool and add them to inventory.

        Args:
            item: The item to look for.
            tool: The tool to use to search.

        Returns:
            Number of items found.

        """
        if self.can_get(item, tool):
            findings = self.zone.search_for(item, tool)
            if len(findings) > 0:
                self.inventory.add_stacks(findings)
                return sum([stack.size for stack in findings])
        return 0

    def can_get(self, item: Item, tool: Tool) -> bool:
        """Check if the item can be found

        Args:
            item: The item to look for.

        Returns:
            True if the item can be found, False otherwise.

        """
        return self.zone.can_search_for(item, tool)

    def move_to(self, zone: Zone) -> bool:
        """Move to a given new zone

        Args:
            zone: The zone to move to.

        Returns:
            True if succeded, False otherwise.

        """
        if self.can_move_to(zone):
            self.zone = zone
            return True
        return False

    def can_move_to(self, zone: Zone) -> bool:
        """Check if the player can move to the zone

        Args:
            zone: The zone we want to access.

        Returns:
            True if the zone can be accessed, False otherwise.

        """
        tool_choosen = self.choose_access_tool(zone)
        return zone.can_access_with(tool_choosen) and zone.can_be_reach_from(self.zone)

    def __repr__(self):
        name = self.name.capitalize() + ":"
        position = "At " + repr(self.zone)
        return "\n ".join((name, position, str(self.inventory)))
