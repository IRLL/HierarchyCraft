from typing import TYPE_CHECKING, List, Type, TypeVar
import pytest
import pytest_check as check


from hcraft.examples.minecraft.env import MineHcraftEnv
from hcraft.task import GetItemTask, GoToZoneTask, PlaceItemTask, Task

if TYPE_CHECKING:
    import gym

gym_module: "gym" = pytest.importorskip("gym")


def test_no_reward_gym_make():
    env: MineHcraftEnv = gym_module.make("MineHcraft-NoReward-v1")
    check.equal(env.purpose.tasks, [])


def test_stone_gym_make():
    env: MineHcraftEnv = gym_module.make("MineHcraft-Stone-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get cobblestone")


def test_iron_gym_make():
    env: MineHcraftEnv = gym_module.make("MineHcraft-Iron-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get iron_ingot")


def test_diamond_gym_make():
    env: MineHcraftEnv = gym_module.make("MineHcraft-Diamond-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get diamond")


def test_enchanting_table_gym_make():
    env: MineHcraftEnv = gym_module.make("MineHcraft-EnchantingTable-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get enchanting_table")


def test_all_items_gym_make():
    env: MineHcraftEnv = gym_module.make("MineHcraft-v1")

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


def test_dragon_gym_make():
    env: MineHcraftEnv = gym_module.make("MineHcraft-Dragon-v1")
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
