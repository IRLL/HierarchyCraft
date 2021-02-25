# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Player """

from crafting.world.items import Item, Tool
from crafting.world.zones import Zone
from crafting.world.recipes import Recipe
from crafting.player.inventory import Inventory

class Player():

    """ Player are entities with an inventory positioned in a zone.

    Attributes:
        inventory (:obj:`Inventory`): Player inventory.
        zone (:obj:`Zone`): Player zone.
        name (str): Player name.

    """

    def __init__(self, inventory: Inventory, zone: Zone, name:str='Player'):
        """ Player are moving inventories that can perform actions.

        Attributes:
            inventory: Initial player inventory.
            zone: Initial player zone.
            name: Initial player name.

        """
        self.inventory = inventory
        self.zone = zone
        self.name = name

    def craft(self, recipe: Recipe) -> bool:
        """ Use a recipe

        Args:
            recipe: The recipe to use.

        Returns:
            True if succeded, False otherwise.

        """
        return recipe(self.inventory, self.zone)

    def choose_tool(self, item: Item) -> Tool:
        """ Choose a tool to search for an item.

        Args:
            item: The item to search for.

        Returns:
            The chosen tool.

        """
        raise NotImplementedError('You must choose how your player choses a tool')

    def search_for(self, item: Item, tool: Tool) -> int:
        """ Search for an item using a tool.

        Args:
            item: The item to look for.
            tool: The tool to use to search.

        Returns:
            Number of items found.

        """
        findings = self.zone.search_for(item, tool)
        if len(findings) > 0:
            self.inventory.add_stacks(findings)
            return sum([stack.size for stack in findings])
        return 0

    def move_to(self, zone: Zone):
        """ Move to a given new zone

        Args:
            zone: The zone to move to.

        Returns:
            True if succeded, False otherwise.

        """
        self.zone = zone
        return True

    def __repr__(self):
        name = self.name.capitalize() + ':'
        position = 'At ' + repr(self.zone)
        return '\n '.join((name, position, str(self.inventory)))
