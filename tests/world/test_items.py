# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
from copy import copy
from crafting.world.items import Item, Tool, ItemStack

### Item ###

def test_item_init():
    Item(12, name='stone', max_stack=64)

@pytest.fixture
def stone():
    return Item(12, name='stone', max_stack=64)

def test_item_str(stone):
    expected_item_name = 'Stone(12)'
    if str(stone) != expected_item_name:
        raise ValueError(f"\nName is {str(stone)}\nInstead of {expected_item_name}")


### ItemStack ###

def test_itemstack_init(stone):
    stack = ItemStack(stone, 8)

    if stack.item_id != stone.item_id:
        raise ValueError("Wrong item_id")

    if stack.size != 8:
        raise ValueError("Wrong size")

### Tool ###

def test_tool_init():
    Tool(18, 'wooden_pickaxe', {'durability': 59, 'speed':2})

@pytest.fixture
def wooden_pickaxe():
    return Tool(18, 'wooden_pickaxe', {'durability': 59, 'speed':2})

def test_tool_change(wooden_pickaxe):
    initial_durability = copy(wooden_pickaxe.durability)
    wooden_pickaxe.durability -= 1
    if wooden_pickaxe.durability != initial_durability - 1:
        raise ValueError("Durability parameter was not changed effectively")

def test_tool_str(wooden_pickaxe):
    expected_name = 'Wooden_pickaxe(18)'
    if str(wooden_pickaxe) != expected_name:
        raise ValueError(f"Tool name was: {str(wooden_pickaxe)}\nInstead of: {expected_name}")

def test_tool_repr(wooden_pickaxe):
    expected_name = 'Wooden_pickaxe(18)[59, 2]'
    if repr(wooden_pickaxe) != expected_name:
        raise ValueError(f"Tool name was: {repr(wooden_pickaxe)}\nInstead of: {expected_name}")

