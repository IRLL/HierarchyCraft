# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
from crafting.world.zones import Zone

def test_zone_init():
    forest = Zone(
        zone_id=0,
        name='forest',
        properties={'has_crafting': False, 'has_furnace': False},
        items={}
    )

    if forest.zone_id != 0:
        raise ValueError("Unexpected zone_id")

    if forest.name != "forest":
        raise ValueError("Unexpected name")

    if forest.properties['has_crafting'] is not False:
        raise ValueError("Unexpected has_crafting")

@pytest.fixture
def forest():
    return Zone(
        zone_id=0,
        name='forest',
        properties={'has_crafting': False, 'has_furnace': False},
        items={}
    )

def test_zone_str(forest):
    print(str(forest))
    if str(forest) != "Forest(0)":
        raise ValueError("Unexpected str")

def test_zone_repr(forest):
    print(repr(forest))
    if repr(forest) != "Forest(0){'has_crafting': False, 'has_furnace': False}":
        raise ValueError("Unexpected repr")
