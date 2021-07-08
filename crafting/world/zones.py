# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Zone

Gives an abstract way of doing spacialization.
The Zones have special properties for finding or crafting items.

"""

from typing import List

from crafting.world.items import Item, Tool, ItemStack

class Zone():

    """ Zones are to represent abstract places in the world.

    Zone have specific properties that can change how items can be gathered
    and how craftings are done.

    By default

    Attributes:
        zone_id (int): Unique zone identification number.
        name (str): Zone name.
        items (dict): Dictionary associating an item_id
            with the tools needed to gather it and how efficient it is.
        properties (dict): Dictionary of properties.

    """

    def __init__(self, zone_id: int, name: str, items: List[Item], properties: dict=None):
        """ Zones are to represent abstract places in the world.

        Zone have specific properties that can change how items can be gathered
        and how craftings are done.

        Args:
            zone_id: Unique zone identification number.
            name: Zone name.
            items: List of all available items.
            properties: List of all properties names.

        """
        self.zone_id = zone_id
        self.name = name
        self.items = items
        self.properties = properties if properties is not None else {}

    def can_search_for(self, item:Item, tool:Tool=None) -> bool:
        """ Check if the item can be found using a tool

        Args:
            item: The item to look for.
            tool: The tool to use in search.

        Returns:
            True if the item can be found, False otherwise.

        """
        if not item in self.items:
            return False
        required_tools = item.required_tools
        no_tool_is_required = required_tools is None or None in required_tools
        tool_in_required = tool is not None and tool in required_tools
        return no_tool_is_required or tool_in_required

    def search_for(self, item:Item, tool:Tool=None) -> List[ItemStack]:
        """ Searches for the given item using a tool

        Args:
            item: The item to look for.
            tool: The tool to use.

        Return:
            The found item stacks.

        """
        if item in self.items:
            required_tools = item.required_tools

            # If no tool is usable, just gather item
            if required_tools is None:
                return [ItemStack(item)]
            # If a tool is needed, gather items relative to used tool
            if tool is not None and tool in required_tools:
                return tool.use(item)
            # If no tool is needed anyway, just gather item
            elif None in required_tools:
                return [ItemStack(item)]
        return []

    def __str__(self):
        return f"{self.name.capitalize()}({self.zone_id})"

    def __repr__(self):
        name = f"{self.name.capitalize()}({self.zone_id})"
        if len(self.properties) > 0:
            name += str(self.properties)
        if len(self.items) > 0:
            name += str(list(self.items))
        return name
