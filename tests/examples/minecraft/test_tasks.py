# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
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
        [f"obtain_{item.name}" for item in MineCraftingEnv().world.getable_items],
    )
    def test_completion_of_(self, task_name):
        env = MineCraftingEnv()
        task: TaskObtainItem = get_task_from_name(env.world, task_name)
        env.add_task(task, can_end=True)

        all_behaviors = env.world.get_all_behaviors()
        behavior_solving_task = all_behaviors[f"Get {task.goal_item}"]

        observation = env.reset()
        done = False
        while not done:
            action = behavior_solving_task(observation)
            observation, _, done, _ = env.step(action)

        item_slot = env.world.item_id_to_slot[task.goal_item.item_id]
        check.greater_equal(
            env.player.inventory.content[item_slot], 1, f"{task_name} completed."
        )


def test_obtain_getting_wood_no_tool():
    """should obtain the correct amount of wood using no tool."""
    env = MineCraftingEnv(max_step=100, verbose=1)
    wood_slot = env.player.inventory.item_id_to_slot(WOOD.item_id)

    done = False
    while not done:
        _, _, done, _ = env(env.action("search", WOOD.item_id))

    wood_gathered = env.player.inventory.content[wood_slot]
    expected_wood_gathered = 100
    check.equal(
        wood_gathered,
        expected_wood_gathered,
        "Unexpected number of wood got after 100 steps (No tool)"
        f": {wood_gathered} instead of {expected_wood_gathered}",
    )


def test_obtain_getting_wood_axe():
    """should obtain the correct amount of wood using an axe."""
    env = MineCraftingEnv(max_step=100, verbose=1)
    wood_slot = env.player.inventory.item_id_to_slot(WOOD.item_id)
    env.reset()
    done = False

    for _ in range(4):
        env(env.action("search", WOOD.item_id))
    for _ in range(4):
        env(env.action("craft", R_WOOD_PLANK.recipe_id))
    for _ in range(2):
        env(env.action("craft", R_STICK.recipe_id))

    env(env.action("craft", R_CRAFTING_TABLE.recipe_id))
    env(env.action("craft", R_WOODEN_PICKAXE.recipe_id))

    for _ in range(2):
        env(env.action("search", STONE.item_id))
    env(env.action("craft", R_STONE_PICKAXE.recipe_id))
    for _ in range(3):
        env(env.action("search", STONE.item_id))

    env(env.action("move", UNDERGROUND.zone_id))
    for _ in range(2):
        env(env.action("search", IRON_ORE.item_id))

    env(env.action("move", FOREST.zone_id))
    env(env.action("craft", R_FURNACE.recipe_id))
    env(env.action("craft", R_IRON_INGOT_PLANK.recipe_id))
    env(env.action("craft", R_IRON_AXE.recipe_id))
    print(env.player)

    while not done:
        _, _, done, _ = env(env.action("search", WOOD.item_id))

    wood_gathered = env.player.inventory.content[wood_slot]
    expected_wood_gathered = 268
    check.equal(
        wood_gathered,
        expected_wood_gathered,
        "Unexpected number of wood got after 100 steps (No tool)"
        f": {wood_gathered} instead of {expected_wood_gathered}",
    )
