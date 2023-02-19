import pytest
import pytest_check as check


from crafting.examples import (
    MineCraftingEnv,
    RandomCraftingEnv,
    TowerCraftingEnv,
    RecursiveCraftingEnv,
    LightRecursiveCraftingEnv,
    KeyDoorCraftingEnv,
)

from crafting.cli import crafting_cli

pygame = pytest.importorskip("pygame")


ENV_NAMES = ("minecraft", "tower", "recursive", "light-recursive", "random", "keydoor")


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


@pytest.mark.parametrize("env_name", ENV_NAMES)
def test_maxstep_cli(env_name:str):
    env = crafting_cli(["--max-step", "100", env_name])
    check.equal(env.max_step, 100)


def test_tower_cli():
    env = crafting_cli(["tower", "--height", "4", "--width", "3"])
    check.is_instance(env, TowerCraftingEnv)
    check.equal(env.height, 4)
    check.equal(env.width, 3)


def test_recursive_cli():
    env = crafting_cli(["recursive", "--n-items", "5"])
    check.is_instance(env, RecursiveCraftingEnv)
    check.equal(env.n_items, 5)


def test_light_recursive_cli():
    env = crafting_cli(
        ["light-recursive", "--n-items", "5", "--n-required-previous", "2"]
    )
    check.is_instance(env, LightRecursiveCraftingEnv)
    check.equal(env.n_items, 5)


def test_random_cli():
    env = crafting_cli(
        [
            "random",
            *("--n-items-0", "2"),
            *("--n-items-1", "3"),
            *("--n-items-2", "4"),
            *("--n-items-3", "5"),
        ]
    )
    check.is_instance(env, RandomCraftingEnv)
    check.equal(env.n_items, 14)


def test_key_door_cli():
    env = crafting_cli(["keydoor"])
    check.is_instance(env, KeyDoorCraftingEnv)
