# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Recipe are to represent transformations of items.

Recipes are initiated using an input-output design
but they can also affect and be affected by the Zone in which the craft is done.

"""

from typing import List
import numpy as np

from crafting.world.items import ItemStack
from crafting.world.map import Zone
from crafting.player.inventory import Inventory

class Recipe():

    """ Recipe are to represent transformations of items.

    Recipes are initiated using an input-output design
    but they can also affect and be affected by the Zone in which the craft is done.

    Attributes:
        recipe_id (int): Unique recipe identification number.
        inputs (list of :obj:`ItemStack`): List of consumed items.
        outputs (list of :obj:`ItemStack`): List of created items.
        needed_properties (dict): Zone properties needed for the craft to be done.
        added_properties (dict): Zone properties modified by the craft if successful.

    """

    def __init__(self,
                 recipe_id: int,
                 inputs: List[ItemStack],
                 outputs: List[ItemStack],
                 needed_properties: dict=None,
                 added_properties: dict=None):

        """ Recipe are to represent transformations of items.

        Recipes are initiated using an input-output design
        but they can also affect and be affected by the Zone in which the craft is done.

        Args:
            recipe_id: Unique recipe identification number.
            inputs: List of consumed items.
            outputs: List of created items.
            needed_properties: Zone properties needed for the craft to be done.
            added_properties: Zone properties modified by the craft if successful.

        """

        self.recipe_id = recipe_id

        self.inputs = inputs
        self.outputs = outputs

        self.needed_properties = needed_properties
        self.added_properties = added_properties

        self._operation = None

    def _build_operation(self, inventory: Inventory):
        """ Build and cache the operation performed by this recipe on the specific inventory """
        operation = np.zeros_like(inventory.content)

        # Inputs consumed if any
        if self.inputs is not None and len(self.inputs) > 0:
            inputs_ids, inputs_sizes = inventory.stacks_ind_and_size(self.inputs)
            operation[inputs_ids] -= inputs_sizes

        # Outputs created if any
        if self.outputs is not None and len(self.outputs) > 0:
            outputs_ids, outputs_sizes = inventory.stacks_ind_and_size(self.outputs)
            operation[outputs_ids] += outputs_sizes

        self._operation =  operation

    def has_enought(self, inventory: Inventory):
        """ Check if the inventory contains the necessary materials

        Args:
            inventory: The inventory to check.

        Return:
            True if the inventory has enough materials, False otherwise.

        """
        if self._operation is None:
            self._build_operation(inventory)
        return np.all(inventory.content + self._operation >= 0)

    def has_properties(self, zone: Zone):
        """ Check if the zone has the necessary propreties

        Args:
            zone: The zone to check.

        Return:
            True if the zone has the necessary propreties, False otherwise.

        """
        if self.needed_properties is None:
            return True
        for property_name, value in self.needed_properties.items():
            if property_name not in zone.properties or \
               not zone.properties[property_name] == value:
                return False
        return True

    def craft(self, inventory: Inventory, zone: Zone) -> bool:
        """ Use the recipe using an inventory in a zone

        Args:
            inventory: Inventory to transform.
            zone: Zone in which the crafting is done.

        Returns:
            True if successful, False otherwise

        """
        if not self.has_enought(inventory):
            return False
        if not self.has_properties(zone):
            return False

        inventory += self._operation

        if self.added_properties is not None:
            for property_name, value in self.added_properties.items():
                zone.properties[property_name] = value

        return True
