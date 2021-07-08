# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from crafting.examples import MineCraftingEnv
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *
from crafting.examples.minecraft.recipes import *
from crafting.examples.minecraft.zones import *

def test_minecrafting_init():
    env = MineCraftingEnv(max_step=500, verbose=1)
    print(env.world.items)
    print(env.world.recipes)
    print(env.world.zones)
    print(env.player)

def test_obtain_getting_wood():
    env = MineCraftingEnv(max_step=100, verbose=1)

    done = False
    while not done:
        _, _, done, _ = env(env.action('get', WOOD.item_id))

    if env.player.inventory.content[5] != 100:
        raise ValueError('Unexpected number of wood got after 100 steps (No tool)')

    print()
    env.reset()
    done = False

    for _ in range(4):
        env(env.action('get', WOOD.item_id))
    for _ in range(4):
        env(env.action('craft', R_WOOD_PLANK.recipe_id))
    for _ in range(2):
        env(env.action('craft', R_STICK.recipe_id))

    env(env.action('craft', R_CRAFTING_TABLE.recipe_id))
    env(env.action('craft', R_WOODEN_PICKAXE.recipe_id))

    for _ in range(2):
        env(env.action('get', STONE.item_id))
    env(env.action('craft', R_STONE_PICKAXE.recipe_id))
    for _ in range(3):
        env(env.action('get', STONE.item_id))

    env(env.action('move', BEDROCK.zone_id))
    for _ in range(2):
        env(env.action('get', IRON_ORE.item_id))

    env(env.action('move', FOREST.zone_id))
    env(env.action('craft', R_FURNACE.recipe_id))
    env(env.action('craft', R_IRON_INGOT_PLANK.recipe_id))
    env(env.action('craft', R_IRON_AXE.recipe_id))
    print(env.player)

    while not done:
        _, _, done, _ = env(env.action('get', WOOD.item_id))

    print(env.player.inventory)
    if env.player.inventory.content[5] != 268:
        raise ValueError('Unexpected number of wood got after 100 steps (IRON AXE)')

def test_obtain_enchant_table():
    env = MineCraftingEnv(max_step=500, verbose=1)
    for _ in range(5):
        env(env.action('get', WOOD.item_id))
    for _ in range(5):
        env(env.action('craft', R_WOOD_PLANK.recipe_id))
    for _ in range(3):
        env(env.action('craft', R_STICK.recipe_id))

    env(env.action('craft', R_CRAFTING_TABLE.recipe_id))
    env(env.action('craft', R_WOODEN_PICKAXE.recipe_id))

    for _ in range(2):
        env(env.action('get', STONE.item_id))
    env(env.action('craft', R_STONE_PICKAXE.recipe_id))
    for _ in range(3):
        env(env.action('get', STONE.item_id))

    env(env.action('craft', R_STONE_SWORD.recipe_id))

    env(env.action('move', MEADOW.zone_id))
    env(env.action('get', LEATHER.item_id))

    env(env.action('move', SWAMP.zone_id))
    for _ in range(3):
        env(env.action('get', REEDS.item_id))

    env(env.action('move', BEDROCK.zone_id))
    for _ in range(2):
        env(env.action('get', IRON_ORE.item_id))

    env(env.action('craft', R_CRAFTING_TABLE.recipe_id))
    env(env.action('craft', R_FURNACE.recipe_id))

    env(env.action('craft', R_IRON_INGOT_PLANK.recipe_id))
    env(env.action('craft', R_IRON_PICKAXE.recipe_id))

    for _ in range(2):
        env(env.action('get', DIAMOND_ORE.item_id))

    env(env.action('craft', R_DIAMOND_PICKAXE.recipe_id))
    for _ in range(4):
        env(env.action('get', OBSIDIAN.item_id))

    env(env.action('craft', R_PAPER.recipe_id))
    env(env.action('craft', R_BOOK.recipe_id))
    env(env.action('craft', R_ENCHANTING_TABLE.recipe_id))

    print(env.player.inventory)

    if env.get_observation()[21] != 1:
        raise ValueError('Enchanting table not built')
