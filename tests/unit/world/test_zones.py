# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
from crafting.world.zones import Zone
from crafting.world.items import Tool, Item

@pytest.fixture
def stone():
    return Item(1, 'stone', 64)

@pytest.fixture
def air():
    return Tool(0, 'air')

@pytest.fixture
def wooden_pickaxe():
    return Tool(18, 'wooden_pickaxe')

@pytest.fixture
def forest(stone, wooden_pickaxe):
    return Zone(
        zone_id=0,
        name='forest',
        properties={'has_crafting': False, 'has_furnace': False},
        items={stone.item_id: [wooden_pickaxe]}
    )

def test_zone_str(forest):
    print(str(forest))
    if str(forest) != "Forest(0)":
        raise ValueError("Unexpected str")

def test_zone_repr(forest):
    print(repr(forest))
    if repr(forest) != "Forest(0){'has_crafting': False, 'has_furnace': False}[1]":
        raise ValueError("Unexpected repr")

def test_zone_search_for(forest, air, stone, wooden_pickaxe):
    findings_with_pick = forest.search_for(stone, wooden_pickaxe)
    if findings_with_pick[0].item_id != stone.item_id:
        raise ValueError('Unexpected findings with wooden_pickaxe')

    findings_with_air = forest.search_for(stone, air)
    if len(findings_with_air) > 0:
        raise ValueError(f'Unexpected findings with air: {findings_with_air}')
