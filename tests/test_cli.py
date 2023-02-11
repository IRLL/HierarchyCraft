import pytest_check as check


from crafting.examples import (
    MineCraftingEnv,
    RandomCraftingEnv,
    TowerCraftingEnv,
    RecursiveCraftingEnv,
    LightRecursiveCraftingEnv,
)

from crafting.cli import crafting_cli


def test_purposeless_minecrafting_cli():
    env = crafting_cli(["minecraft"])
    check.is_instance(env, MineCraftingEnv)


def test_purposed_minecrafting_cli():
    env = crafting_cli(
        ["--get-items", "diamond", "wood", "--goal-reward", "100", "minecraft"]
    )
    check.is_instance(env, MineCraftingEnv)

    task_names = set(task.name for task in env.purpose.tasks)
    check.equal(task_names, {"Get diamond", "Get wood"})

    for task in env.purpose.tasks:
        check.equal(task._reward, 100)


def test_tower_cli():
    env = crafting_cli(["tower", "--height", "4", "--width", "3"])
    check.is_instance(env, TowerCraftingEnv)
    check.equal(env.height, 4)
    check.equal(env.width, 3)


def test_recursive_cli():
    env = crafting_cli(["recursive", "--n-items", "5"])
    check.is_instance(env, RecursiveCraftingEnv)
    check.equal(env.n_items, 5)
