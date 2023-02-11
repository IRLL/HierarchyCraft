import pytest
import pytest_check as check

gym = pytest.importorskip("gym")

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.task import Task


def test_no_reward_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-NoReward-v1")
    check.equal(env.purpose.tasks, [])


def test_stone_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-Stone-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get cobblestone")


def test_iron_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-Iron-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get iron_ingot")


def test_diamond_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-Diamond-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get diamond")


def test_enchanting_table_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-EnchantingTable-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get enchanting_table")


def test_the_end_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-End-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Go to end")


def test_the_end_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-Dragon-v1")
    check.equal(len(env.purpose.tasks), 1)
    task = env.purpose.tasks[0]
    check.equal(task.name, "Get ender_dragon_head")
