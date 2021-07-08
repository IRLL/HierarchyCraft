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
        self.score = 0

    def craft(self, recipe: Recipe) -> bool:
        """ Use a recipe

        Args:
            recipe: The recipe to use.

        Returns:
            True if succeded, False otherwise.

        """
        if self.can_craft(recipe):
            return recipe(self.inventory, self.zone)
        return False

    def can_craft(self, recipe: Recipe) -> bool:
        """ Check if the recipe can be performed

        Args:
            recipe: Recipe to be tested.

        Return:
            True if the recipe can be used, False otherwise.

        """
        return recipe.can_craft(self.inventory, self.zone)

    def choose_tool(self, item: Item) -> Tool:
        """ Choose a tool to search for an item.

        Args:
            item: The item to search for.

        Returns:
            The chosen tool.

        """
        raise NotImplementedError('You must choose how your player choses a tool')

    def search_for(self, item: Item, tool: Tool) -> int:
        """ Search for an item using a tool and add them to inventory.

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
        """ Check if the item can be found

        Args:
            item: The item to look for.

        Returns:
            True if the item can be found, False otherwise.

        """
        return self.zone.can_search_for(item, tool)

    def move_to(self, zone: Zone) -> bool:
        """ Move to a given new zone

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
        """ Check if the player can move to the zone

        Args:
            zone: The zone we want to access.

        Returns:
            True if the zone can be accessed, False otherwise.

        """
        return zone.zone_id != self.zone.zone_id

    def __repr__(self):
        name = self.name.capitalize() + ':'
        position = 'At ' + repr(self.zone)
        return '\n '.join((name, position, str(self.inventory)))
