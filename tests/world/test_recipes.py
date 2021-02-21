# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import numpy as np

from crafting.world.items import Item, Tool, ItemStack
from crafting.world.zones import Zone
from crafting.player.inventory import Inventory
from crafting.world.recipes import Recipe

@pytest.fixture
def forest():
    return Zone(
        zone_id=0,
        name='forest',
        items={}
    )

@pytest.fixture
def dirt():
    return Item(3, name='dirt', max_stack=64)

@pytest.fixture
def plank():
    return Item(5, name='plank', max_stack=64)

@pytest.fixture
def stone():
    return Item(12, name='stone', max_stack=64)

@pytest.fixture
def stick():
    return Item(280, name='stick', max_stack=64)

@pytest.fixture
def wooden_pickaxe():
    return Tool(18, 'wooden_pickaxe', {'durability': 59, 'speed':2})

@pytest.fixture
def stone_pickaxe():
    return Tool(274, 'stone_pickaxe', {'durability': 131, 'speed': 4})

@pytest.fixture
def all_items(dirt, plank, stone, stick, wooden_pickaxe, stone_pickaxe):
    return [dirt, plank, stone, stick, wooden_pickaxe, stone_pickaxe]

def test_recipe_init(plank, stick, wooden_pickaxe):
    Recipe(
        recipe_id=3,
        inputs=[ItemStack(plank, 3), ItemStack(stick, 2)],
        outputs=[ItemStack(wooden_pickaxe)],
        needed_properties={'has_crafting': True},
        added_properties=None
    )

@pytest.fixture
def recipe_wooden_pickaxe(plank, stick, wooden_pickaxe):
    return Recipe(
        recipe_id=3,
        inputs=[ItemStack(plank, 3), ItemStack(stick, 2)],
        outputs=[ItemStack(wooden_pickaxe)],
        needed_properties={'has_crafting': True},
        added_properties=None
    )

def test_recipe_craft_inv(forest, all_items, plank, stick, recipe_wooden_pickaxe):
    inv = Inventory(all_items)
    inv.add_stacks([ItemStack(stick, 10), ItemStack(plank, 7)])

    forest.properties['has_crafting'] = True

    success = recipe_wooden_pickaxe.craft(inv, forest)
    if not success or not np.all(inv.content == [0, 4, 0, 8, 1, 0]):
        raise ValueError("First craft failed unexpectedly")

    success = recipe_wooden_pickaxe.craft(inv, forest)
    if not success or not np.all(inv.content == [0, 1, 0, 6, 2, 0]):
        raise ValueError("Second craft failed unexpectedly")

    success = recipe_wooden_pickaxe.craft(inv, forest)
    if success or not np.all(inv.content == [0, 1, 0, 6, 2, 0]):
        raise ValueError("Third craft succeded unexpectedly")

@pytest.fixture
def recipe_crafting_table(plank):
    return Recipe(
        recipe_id=3,
        inputs=[ItemStack(plank, 4)],
        outputs=[],
        needed_properties=None,
        added_properties={'has_crafting': True}
    )

def test_recipe_craft_zone(forest, all_items, plank, recipe_crafting_table):
    inv = Inventory(all_items)
    inv.add_stacks([ItemStack(plank, 9)])

    assert 'has_crafting' not in forest.properties

    success = recipe_crafting_table.craft(inv, forest)
    print(inv, success, forest.properties['has_crafting'])
    if not success or not forest.properties['has_crafting']:
        raise ValueError("First craft failed unexpectedly")

    success = recipe_crafting_table.craft(inv, forest)
    print(inv, success, forest.properties['has_crafting'])
    if not success or not forest.properties['has_crafting']:
        raise ValueError("Second craft failed unexpectedly")

    success = recipe_crafting_table.craft(inv, forest)
    print(inv, success, forest.properties['has_crafting'])
    if success:
        raise ValueError("Third craft succeded unexpectedly")
