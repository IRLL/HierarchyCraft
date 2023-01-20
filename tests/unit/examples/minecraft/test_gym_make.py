import pytest
import pytest_check as check

gym = pytest.importorskip("gym")

from crafting.examples.minecraft.env import MineCraftingEnv


def test_no_reward_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-NoReward-v1")
    check.equal(env.fail_penalty, 1)
    check.equal(env.moving_penalty, 0)
    check.equal(env.timestep_penalty, 0)
    check.equal(len(env.tasks), 0)


def test_enchanting_table_gym_make():
    env: MineCraftingEnv = gym.make("MineCrafting-EnchantingTable-v1")
    check.equal(env.fail_penalty, 1)
    check.equal(env.moving_penalty, 0.4)
    check.equal(env.timestep_penalty, 0.1)
    check.equal(len(env.tasks), 1)
    task = env.tasks[0]
    check.equal(task.name, "obtain_Enchanting_table(116)")
