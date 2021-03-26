# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import numpy as np

from crafting.world.items import Item, ItemStack
from crafting.player.inventory import Inventory

@pytest.fixture
def items():
    dirt = Item(3, name='dirt')
    plank = Item(5, name='plank')
    stone = Item(12, name='stone')
    return (dirt, plank, stone)

def test_inventory_init(items):
    inv = Inventory(items)

    expected_items_ids = (3, 5, 12)
    if inv.items_ids != expected_items_ids:
        raise ValueError("Unexpected items_ids")

    slot_is_right = [
      inv.item_id_to_slot(item_id) == i for i, item_id in enumerate(expected_items_ids)
    ]

    if not all(slot_is_right):
        raise ValueError("Unexpected id to slot mapping")

    if not np.all(inv.content == np.zeros(3, dtype=np.int32)):
        raise ValueError("Unexpected content")

@pytest.fixture
def inv(items):
    return Inventory(items)

def test_inventory_add_stacks(inv, items):
    stacks = [
        ItemStack(items[0], 15),
        ItemStack(items[2], 33)
    ]
    inv.add_stacks(stacks)
    if not np.all(inv.content == [15, 0, 33]):
        raise ValueError('Unexpected content after add_stacks')

def test_inventory_add_array(inv):
    inv = inv + np.array([15, 0, 33])
    if not np.all(inv.content == [15, 0, 33]):
        raise ValueError('Unexpected content after __add__')

def test_inventory_remove_stacks(inv, items):
    inv.content = np.array([15, 0, 33], dtype=np.int32)

    stacks = [
        ItemStack(items[0], 8),
        ItemStack(items[2], 21)
    ]

    inv.remove_stacks(stacks)
    if not np.all(inv.content == [15-8, 0, 33-21]):
        raise ValueError('Unexpected content after remove_stacks')

def test_inventory_sub_array(inv):
    inv.content = np.array([15, 0, 33], dtype=np.int32)
    inv = inv - np.array([8, 0, 21])
    if not np.all(inv.content == [15-8, 0, 33-21]):
        raise ValueError('Unexpected content after __sub__')
