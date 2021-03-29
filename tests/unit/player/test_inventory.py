# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=no-self-use

""" Inventory tests """

import pytest
import pytest_check as check
import numpy as np

from crafting.world.items import Item, ItemStack
from crafting.player.inventory import Inventory


@pytest.fixture
def items(mocker):
    """ Dummy items for testing """
    item_ids = [3, 5, 12]
    mocker.patch('crafting.world.items.Item')
    return [Item(item_id, 'Item_' + str(item_id)) for item_id in item_ids]

class TestInventory:

    """ Inventory """

    def test_inventory_init(self, items):
        """ should instanciate correctly. """
        inv = Inventory(items)

        expected_items_ids = (3, 5, 12)
        check.equal(inv.items_ids, expected_items_ids)

        slot_is_right = [
            inv.item_id_to_slot(item_id) == i
            for i, item_id in enumerate(expected_items_ids)
        ]

        check.is_true(all(slot_is_right), "should match id to slots correctly")
        check.is_true(np.all(inv.content == np.zeros(3, dtype=np.int32)), "should be empty")

    def test_inventory_add_stacks(self, items):
        """ should be able to add a list of ItemStack. """
        inv = Inventory(items)

        stacks = [
            ItemStack(items[0], 15),
            ItemStack(items[2], 33)
        ]

        inv.add_stacks(stacks)
        check.is_true(np.all(inv.content == [15, 0, 33]))

    def test_inventory_add_array(self, items):
        """ should be able to add an array. """
        inv = Inventory(items)
        inv += np.array([15, 0, 33])
        check.is_true(np.all(inv.content == [15, 0, 33]))

    def test_inventory_remove_stacks(self, items):
        """ should be able to remove a list of ItemStack. """
        inv = Inventory(items)
        inv.content = np.array([15, 0, 33], dtype=np.int32)

        stacks = [
            ItemStack(items[0], 8),
            ItemStack(items[2], 21)
        ]

        inv.remove_stacks(stacks)
        check.is_true(np.all(inv.content == [15-8, 0, 33-21]))

    def test_inventory_sub_array(self, items):
        """ should be able to substract an array. """
        inv = Inventory(items)
        inv.content = np.array([15, 0, 33], dtype=np.int32)
        inv = inv - np.array([8, 0, 21])
        check.is_true(np.all(inv.content == [15-8, 0, 33-21]))
