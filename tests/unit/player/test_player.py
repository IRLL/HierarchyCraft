# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest

from crafting.world.items import Item, Tool
from crafting.world.zones import Zone
from crafting.player.player import Player
from crafting.player.inventory import Inventory

@pytest.fixture
def items():
    dirt = Item(3, name='dirt')
    plank = Item(5, name='plank')
    stone = Item(12, name='stone')
    air = Tool(0, 'air')
    wooden_pickaxe = Tool(270, 'wooden_pickaxe')
    return (dirt, plank, stone, wooden_pickaxe, air)

@pytest.fixture
def forest(items):
    dirt = items[0]
    stone = items[2]
    air = items[3]
    wooden_pickaxe = items[4]
    return Zone(0, 'forest', {
        stone.item_id: [wooden_pickaxe],
        dirt.item_id: [air]
    })

@pytest.fixture
def inv(items):
    return Inventory(items)

def test_player_init(inv, forest):
    Player(inv, forest)
