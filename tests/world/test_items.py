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
    ItemStack(stone, 8)

def test_itemstack_add(stone):
    # Simple add
    stone8 = ItemStack(stone, 8)
    stone32 = ItemStack(stone, 32)

    added_stacks = stone8 + stone32
    stacks_sizes = list(map(lambda x: x.size, added_stacks))
    expected_stack_sizes = [40]

    if stacks_sizes != expected_stack_sizes:
        raise ValueError(f"Stack sizes are:\n{stacks_sizes}\nInstead of:\n{expected_stack_sizes}")

    # Overflowed add
    stone32 = ItemStack(stone, 32)
    stone35 = ItemStack(stone, 35)

    added_stacks = stone32 + stone35
    stacks_sizes = list(map(lambda x: x.size, added_stacks))
    expected_stack_sizes = [64, 3]

    if stacks_sizes != expected_stack_sizes:
        raise ValueError(f"Stack sizes are:\n{stacks_sizes}\nInstead of:\n{expected_stack_sizes}")

    # Correcting add
    stone8 = ItemStack(stone, 8)
    stone127 = ItemStack(stone, 127)

    added_stacks = stone8 + stone127
    stacks_sizes = list(map(lambda x: x.size, added_stacks))
    expected_stack_sizes = [64, 64, 7]

    if stacks_sizes != expected_stack_sizes:
        raise ValueError(f"Stack sizes are:\n{stacks_sizes}\nInstead of:\n{expected_stack_sizes}")

def test_itemstack_sub(stone):
    # Simple sub
    stone8 = ItemStack(stone, 8)
    stone32 = ItemStack(stone, 32)

    sub_stacks = stone32 - stone8
    stacks_sizes = list(map(lambda x: x.size, sub_stacks))
    expected_stack_sizes = [24]

    if stacks_sizes != expected_stack_sizes:
        raise ValueError(f"Stack sizes are:\n{stacks_sizes}\nInstead of:\n{expected_stack_sizes}")

    # Zero stack output
    stone32 = ItemStack(stone, 32)
    stone32_2 = ItemStack(stone, 32)

    sub_stacks = stone32 - stone32_2
    stacks_sizes = list(map(lambda x: x.size, sub_stacks))
    expected_stack_sizes = []

    if stacks_sizes != expected_stack_sizes:
        raise ValueError(f"Stack sizes are:\n{stacks_sizes}\nInstead of:\n{expected_stack_sizes}")

    # Not enough Error
    stone32 = ItemStack(stone, 32)
    stone48 = ItemStack(stone, 48)

    with pytest.raises(ValueError, match="Not enough in initial stack to remove"):
        sub_stacks = stone32 - stone48

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
    expected_name = 'Wooden_pickaxe(18)[59, 2]'
    if str(wooden_pickaxe) != expected_name:
        raise ValueError(f"Tool name was: {str(wooden_pickaxe)}\nInstead of: {expected_name}")
