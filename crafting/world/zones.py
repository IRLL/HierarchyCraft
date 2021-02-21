# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Map and Zone

Defining Zone and Map to give an abstract way of doing spacialization.
The Zones have special properties for finding or crafting items.
The Map give a graph joinning all Zones.

"""

from typing import List, Dict

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

    def __init__(self, zone_id: int, name: str, items: Dict[int, Item], properties: dict=None):
        """ Zones are to represent abstract places in the world.

        Zone have specific properties that can change how items can be gathered
        and how craftings are done.

        Args:
            zone_id: Unique zone identification number.
            name: Zone name.
            items: Dictionary mapping an item_id to 
                the tools needed to gather it.
            properties: List of all properties names.

        """
        self.zone_id = zone_id
        self.name = name
        self.items = items
        self.properties = properties if properties is not None else {}

    def search_for(self, item:Item, tool:Tool) -> List[ItemStack]:
        """ Searches for the given item using a tool

        Args:
            item: The item to look for.
            tool: The tool to use.

        Return:
            The found item stacks.

        """
        if item.item_id in self.items:
            if tool in self.items[item.item_id]:
                return tool.use(item)
        return []

    def __str__(self):
        return f"{self.name.capitalize()}({self.zone_id})"

    def __repr__(self):
        return f"{self.name.capitalize()}({self.zone_id}){self.properties}"
