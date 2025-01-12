from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Type, TypeVar
import pytest
import pytest_check as check


from hcraft.env import HcraftEnv
from hcraft.examples import HCRAFT_GYM_ENVS
from hcraft.examples.light_recursive import LightRecursiveHcraftEnv
from hcraft.examples.minecraft.env import MineHcraftEnv
from hcraft.examples.random_simple.env import RandomHcraftEnv
from hcraft.examples.recursive import RecursiveHcraftEnv
from hcraft.examples.tower import TowerHcraftEnv
from hcraft.task import GetItemTask, GoToZoneTask, PlaceItemTask, Task

if TYPE_CHECKING:
    import gymnasium as gym

gym_module: "gym" = pytest.importorskip("gymnasium")


@pytest.mark.parametrize("env_gym_id", HCRAFT_GYM_ENVS)
def test_gym_make(env_gym_id: str):
    """Ensure all hcraft envs follow the gymnasium interface."""
    env: HcraftEnv = gym_module.make(env_gym_id)
    observation, infos = env.reset()
    observation, reward, terminated, truncated, infos = env.step(0)


def test_gym_make_TowerHcraft():
    env = _given_env_from_gym_make(TowerHcraftEnv, "TowerHcraft-v1", height=3, width=2)
    check.equal(env.height, 3)
    check.equal(env.width, 2)
    check.equal(env.world.n_items, 3 * 2 + 1)
    check.is_in("TowerHcraft", env.name)


def test_gym_make_RandomHcraftEnv():
    n_items_per_n_inputs = {0: 1, 1: 5, 2: 10, 4: 1}
    env = _given_env_from_gym_make(
        RandomHcraftEnv,
        "RandomHcraft-v1",
        n_items_per_n_inputs=n_items_per_n_inputs,
        seed=42,
    )
    check.equal(len(env.world.items), sum(n_items_per_n_inputs.values()))
    check.equal(env.seed, 42)


def test_gym_make_light_recursive():
    n_items = 10
    n_required_previous = 3
    env = _given_env_from_gym_make(
        LightRecursiveHcraftEnv,
        "LightRecursiveHcraft-v1",
        n_items=n_items,
        n_required_previous=n_required_previous,
    )
    check.equal(len(env.world.items), n_items)
    check.equal(env.name, "LightRecursiveHcraft-K3-I10")


def test_gym_make_recursive():
    n_items = 10
    env = _given_env_from_gym_make(
        RecursiveHcraftEnv, "RecursiveHcraft-v1", n_items=n_items
    )
    check.equal(len(env.world.items), n_items)
    check.equal(env.name, "RecursiveHcraft-I10")


class TestGymMakeMineHcraft:
    def test_no_reward_gym_make(self):
        env = _given_env_from_gym_make(MineHcraftEnv, "MineHcraft-NoReward-v1")
        check.equal(env.purpose.tasks, [])

    def test_stone_gym_make(self):
        env = _given_env_from_gym_make(MineHcraftEnv, "MineHcraft-Stone-v1")
        check.equal(len(env.purpose.tasks), 1)
        task = env.purpose.tasks[0]
        check.equal(task.name, "Get cobblestone")

    def test_iron_gym_make(self):
        env = _given_env_from_gym_make(MineHcraftEnv, "MineHcraft-Iron-v1")
        check.equal(len(env.purpose.tasks), 1)
        task = env.purpose.tasks[0]
        check.equal(task.name, "Get iron_ingot")

    def test_diamond_gym_make(self):
        env = _given_env_from_gym_make(MineHcraftEnv, "MineHcraft-Diamond-v1")
        check.equal(len(env.purpose.tasks), 1)
        task = env.purpose.tasks[0]
        check.equal(task.name, "Get diamond")

    def test_enchanting_table_gym_make(self):
        env = _given_env_from_gym_make(MineHcraftEnv, "MineHcraft-EnchantingTable-v1")
        check.equal(len(env.purpose.tasks), 1)
        task = env.purpose.tasks[0]
        check.equal(task.name, "Get enchanting_table")

    def test_all_items_gym_make(self):
        env = _given_env_from_gym_make(MineHcraftEnv, "MineHcraft-v1")

        TaskOfType = TypeVar("TaskOfType")

        def _task_names_of_type(
            tasks: List[Task], task_type: Type[TaskOfType]
        ) -> List[TaskOfType]:
            return [task for task in tasks if isinstance(task, task_type)]

        check.assert_equal(
            set(
                task.item_stack.item.name
                for task in _task_names_of_type(env.purpose.tasks, GetItemTask)
            ),
            set(item.name for item in env.world.items),
        )
        check.assert_equal(
            set(
                task.zone.name
                for task in _task_names_of_type(env.purpose.tasks, GoToZoneTask)
            ),
            set(zone.name for zone in env.world.zones),
        )
        check.assert_equal(
            set(
                task.item_stack.item.name
                for task in _task_names_of_type(env.purpose.tasks, PlaceItemTask)
            ),
            set(item.name for item in env.world.zones_items),
        )

    def test_dragon_gym_make(self):
        env = _given_env_from_gym_make(MineHcraftEnv, "MineHcraft-Dragon-v1")
        env.reset()
        expected_tasknames = {
            "Go to meadow",
            "Go to swamp",
            "Go to forest",
            "Get wood",
            "Get wood_plank",
            "Get stick",
            "Get crafting_table",
            "Place crafting_table anywhere",
            "Get wood_shovel",
            "Get wood_pickaxe",
            "Get cobblestone",
            "Get stone_pickaxe",
            "Go to underground",
            "Get iron_ore",
            "Get furnace",
            "Place furnace anywhere",
            "Get coal",
            "Get iron_ingot",
            "Get iron_pickaxe",
            "Get iron_sword",
            "Go to bedrock",
            "Get diamond",
            "Get diamond_pickaxe",
            "Get diamond_sword",
            "Get gold_ore",
            "Get gold_ingot",
            "Get gold_sword",
            "Get obsidian",
            "Place close_nether_portal anywhere",
            "Place open_nether_portal anywhere",
            "Get gravel",
            "Get flint",
            "Get flint_and_steel",
            "Go to nether",
            "Get blaze_rod",
            "Get blaze_powder",
            "Get ender_pearl",
            "Get ender_eye",
            "Go to stronghold",
            "Place close_ender_portal anywhere",
            "Place open_ender_portal anywhere",
            "Go to end",
            "Get ender_dragon_head",
        }
        tasks_names = set(task.name for task in env.purpose.tasks)
        check.equal(
            tasks_names,
            expected_tasknames,
            f"Diff:\n{expected_tasknames.difference(tasks_names)}",
        )


EnvType = TypeVar("EnvType", bound=HcraftEnv)


def _given_env_from_gym_make(
    env_type: type[EnvType], env_id: str, **env_kwargs: Any
) -> EnvType:
    env = _unwrap_env(gym_module.make(env_id, **env_kwargs))
    assert isinstance(env, env_type)
    return env


def _unwrap_env(env: "gym.Env") -> HcraftEnv:
    """Unwrap the underlying Hcraft env from a gymnasium composite."""
    while not isinstance(env, HcraftEnv):
        env = env.env
    return env
