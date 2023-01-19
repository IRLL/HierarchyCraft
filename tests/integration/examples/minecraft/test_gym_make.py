import gym

from crafting.examples.minecraft.env import MineCraftingEnv


def test_gym_make_minecrafting():
    env = gym.make("CraftingEnchantingTable-v1")
