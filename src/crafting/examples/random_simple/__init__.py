from crafting.examples.random_simple.env import RandomCraftingEnv

# gym is an optional dependency
try:
    import gym

    gym.register(
        id="RandomCrafting-v1",
        entry_point="crafting.examples.random_simple.env:RandomCraftingEnv",
    )
except ImportError:
    pass
