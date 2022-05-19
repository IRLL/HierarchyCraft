# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=no-self-use, missing-function-docstring

""" Module testing that each of the built-in tasks can be done succesfully. """


import pytest
import pytest_check as check

from crafting.examples import MineCraftingEnv
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *
from crafting.examples.minecraft.recipes import *
from crafting.examples.minecraft.zones import *

from crafting.task import TaskObtainItem, get_task_from_name


class TestTasks:

    """Tasks of the MineCrafting environment"""

    @pytest.mark.parametrize(
        "task_name",
        [f"obtain_{item}" for item in MineCraftingEnv().world.getable_items],
    )
    def test_completion_of_(self, task_name):
        env = MineCraftingEnv()
        task: TaskObtainItem = get_task_from_name(env.world, task_name)
        env.add_task(task, can_end=True)

        all_options = env.world.get_all_options()
        option_solving_task = all_options[f"Get {task.goal_item}"]

        observation = env.reset()
        done = False
        while not done:
            action = option_solving_task(observation)
            observation, _, done, _ = env.step(action)

        item_slot = env.world.item_id_to_slot[task.goal_item.item_id]
        check.greater_equal(
            env.player.inventory.content[item_slot], 1, f"{task_name} completed."
        )


def test_obtain_getting_wood():
    """should obtain the correct amount of wood using tool or not."""
    env = MineCraftingEnv(max_step=100, verbose=1)

    done = False
    while not done:
        _, _, done, _ = env(env.action("get", WOOD.item_id))

    if env.player.inventory.content[5] != 100:
        raise ValueError("Unexpected number of wood got after 100 steps (No tool)")

    print()
    env.reset()
    done = False

    for _ in range(4):
        env(env.action("get", WOOD.item_id))
    for _ in range(4):
        env(env.action("craft", R_WOOD_PLANK.recipe_id))
    for _ in range(2):
        env(env.action("craft", R_STICK.recipe_id))

    env(env.action("craft", R_CRAFTING_TABLE.recipe_id))
    env(env.action("craft", R_WOODEN_PICKAXE.recipe_id))

    for _ in range(2):
        env(env.action("get", STONE.item_id))
    env(env.action("craft", R_STONE_PICKAXE.recipe_id))
    for _ in range(3):
        env(env.action("get", STONE.item_id))

    env(env.action("move", BEDROCK.zone_id))
    for _ in range(2):
        env(env.action("get", IRON_ORE.item_id))

    env(env.action("move", FOREST.zone_id))
    env(env.action("craft", R_FURNACE.recipe_id))
    env(env.action("craft", R_IRON_INGOT_PLANK.recipe_id))
    env(env.action("craft", R_IRON_AXE.recipe_id))
    print(env.player)

    while not done:
        _, _, done, _ = env(env.action("get", WOOD.item_id))

    print(env.player.inventory)
    if env.player.inventory.content[5] != 268:
        raise ValueError("Unexpected number of wood got after 100 steps (IRON AXE)")


def test_obtain_enchant_table():
    """should be able to build an enchanting table."""
    env = MineCraftingEnv(max_step=500, verbose=1)
    for _ in range(5):
        env(env.action("get", WOOD.item_id))
    for _ in range(5):
        env(env.action("craft", R_WOOD_PLANK.recipe_id))
    for _ in range(3):
        env(env.action("craft", R_STICK.recipe_id))

    env(env.action("craft", R_CRAFTING_TABLE.recipe_id))
    env(env.action("craft", R_WOODEN_PICKAXE.recipe_id))

    for _ in range(2):
        env(env.action("get", STONE.item_id))
    env(env.action("craft", R_STONE_PICKAXE.recipe_id))
    for _ in range(3):
        env(env.action("get", STONE.item_id))

    env(env.action("craft", R_STONE_SWORD.recipe_id))

    env(env.action("move", MEADOW.zone_id))
    env(env.action("get", LEATHER.item_id))

    env(env.action("move", SWAMP.zone_id))
    for _ in range(3):
        env(env.action("get", REEDS.item_id))

    env(env.action("move", BEDROCK.zone_id))
    for _ in range(2):
        env(env.action("get", IRON_ORE.item_id))

    env(env.action("craft", R_CRAFTING_TABLE.recipe_id))
    env(env.action("craft", R_FURNACE.recipe_id))

    env(env.action("craft", R_IRON_INGOT_PLANK.recipe_id))
    env(env.action("craft", R_IRON_PICKAXE.recipe_id))

    for _ in range(2):
        env(env.action("get", DIAMOND_ORE.item_id))

    env(env.action("craft", R_DIAMOND_PICKAXE.recipe_id))
    for _ in range(4):
        env(env.action("get", OBSIDIAN.item_id))

    env(env.action("craft", R_PAPER.recipe_id))
    env(env.action("craft", R_BOOK.recipe_id))
    env(env.action("craft", R_ENCHANTING_TABLE.recipe_id))

    print(env.player.inventory)

    if env.get_observation()[21] != 1:
        raise ValueError("Enchanting table not built")
