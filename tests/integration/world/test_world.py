# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest

from crafting.world.zones import Zone
from crafting.world.world import World
from crafting.world.recipes import Recipe
from crafting.world.items import Item, Tool, ItemStack


@pytest.fixture
def air():
    return Tool(0, "air")


@pytest.fixture
def wooden_pickaxe():
    return Tool(18, "wooden_pickaxe")


@pytest.fixture
def dirt():
    return Item(3, "dirt")


@pytest.fixture
def wood(air, wooden_pickaxe):
    return Item(14, "wood", required_tools=[air, wooden_pickaxe])


@pytest.fixture
def stick():
    return Item(280, name="stick")


@pytest.fixture
def plank():
    return Item(5, name="plank")


@pytest.fixture
def stone(wooden_pickaxe):
    return Item(1, "stone", required_tools=[wooden_pickaxe])


@pytest.fixture
def forest(wood):
    return Zone(0, "forest", items=[wood])


@pytest.fixture
def underground(stone, dirt):
    return Zone(1, "underground", items=[stone, dirt])


@pytest.fixture
def recipe_wooden_pickaxe(plank, stick, wooden_pickaxe):
    return Recipe(
        recipe_id=3,
        inputs=[ItemStack(plank, 3), ItemStack(stick, 2)],
        outputs=[ItemStack(wooden_pickaxe)],
        needed_properties={"has_crafting": True},
        added_properties=None,
    )


@pytest.fixture
def recipe_crafting_table(plank):
    return Recipe(
        recipe_id=3,
        inputs=[ItemStack(plank, 4)],
        added_properties={"has_crafting": True},
    )


@pytest.fixture
def items(dirt, wood, stone, plank, stick, air, wooden_pickaxe):
    return [dirt, wood, stone, plank, stick, air, wooden_pickaxe]


@pytest.fixture
def world(items, forest, underground, recipe_wooden_pickaxe, recipe_crafting_table):
    return World(
        items, [recipe_wooden_pickaxe, recipe_crafting_table], [forest, underground]
    )


def test_init(world, underground):
    print("Items:", world.items)
    if world.n_items != 7:
        raise ValueError("Unexpected n_items")

    print("Recipes:", world.recipes)
    if world.n_recipes != 2:
        raise ValueError("Unexpected n_recipes")

    print("Foundable items:", world.foundable_items)
    if world.n_foundable_items != 3:
        raise ValueError("Unexpected n_foundable_items")

    if world.zone_id_to_slot[underground.zone_id] != 1:
        raise ValueError("Unexpected zone_slot for given zone_id")

    if world.n_zone_properties != 1:
        raise ValueError("Unexpected n_zone_properties")
