import pytest_check as check


import gym

from crafting.examples.minecraft.env import MineCraftingEnv


def test_gym_make_minecrafting():
    env: MineCraftingEnv = gym.make("MineCrafting-NoReward-v1")
    check.equal(env.fail_penalty, 1)
    check.equal(env.moving_penalty, 0)
    check.equal(env.timestep_penalty, 0)
    check.equal(len(env.tasks), 0)
