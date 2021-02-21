# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
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
    Tool(18, 'wooden_pickaxe')

@pytest.fixture
def wooden_pickaxe():
    return Tool(18, 'wooden_pickaxe')

def test_tool_use(wooden_pickaxe, stone):
    findings = wooden_pickaxe.use(stone)

    if findings[0].item_id != stone.item_id:
        raise ValueError('Unexpected finding item_id')

    if findings[0].size != 1:
        raise ValueError('Unexpected finding size')

def test_tool_str(wooden_pickaxe):
    expected_name = 'Wooden_pickaxe(18)'
    if str(wooden_pickaxe) != expected_name:
        raise ValueError(f"Tool name was: {str(wooden_pickaxe)}\nInstead of: {expected_name}")
