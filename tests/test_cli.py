import pytest
import pytest_check as check

from hcraft.cli import hcraft_cli
from hcraft.examples import (
    LightRecursiveHcraftEnv,
    MineHcraftEnv,
    RandomHcraftEnv,
    RecursiveHcraftEnv,
    TowerHcraftEnv,
)

pygame = pytest.importorskip("pygame")


ENV_NAMES = ("minecraft", "tower", "recursive", "light-recursive", "random")


def test_purposeless_minehcraft_cli():
    env = hcraft_cli(["minecraft"])
    check.is_instance(env, MineHcraftEnv)


def test_purposed_minehcraft_cli():
    env = hcraft_cli(
        [
            "--goal-reward",
            "100",
            "--get-item",
            "diamond",
            "--get-item",
            "wood",
            "minecraft",
        ]
    )
    check.is_instance(env, MineHcraftEnv)

    task_names = set(task.name for task in env.purpose.tasks)
    check.equal(task_names, {"Get diamond", "Get wood"})

    for task in env.purpose.tasks:
        check.equal(task._reward, 100)


@pytest.mark.parametrize("env_name", ENV_NAMES)
def test_maxstep_cli(env_name: str):
    env = hcraft_cli(["--max-step", "100", env_name])
    check.equal(env.max_step, 100)


def test_tower_cli():
    env = hcraft_cli(["tower", "--height", "4", "--width", "3"])
    check.is_instance(env, TowerHcraftEnv)
    check.equal(env.height, 4)
    check.equal(env.width, 3)


def test_recursive_cli():
    env = hcraft_cli(["recursive", "--n-items", "5"])
    check.is_instance(env, RecursiveHcraftEnv)
    check.equal(env.n_items, 5)


def test_light_recursive_cli():
    env = hcraft_cli(
        ["light-recursive", "--n-items", "5", "--n-required-previous", "2"]
    )
    check.is_instance(env, LightRecursiveHcraftEnv)
    check.equal(env.n_items, 5)


def test_random_cli():
    env = hcraft_cli(
        [
            "random",
            *("--n-items-0", "2"),
            *("--n-items-1", "3"),
            *("--n-items-2", "4"),
            *("--n-items-3", "5"),
        ]
    )
    check.is_instance(env, RandomHcraftEnv)
    check.equal(env.n_items, 14)
