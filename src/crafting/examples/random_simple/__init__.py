# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

# gym is an optional dependency
try:
    import gym

    gym.register(
        id="RandomCrafting-v1",
        entry_point="crafting.examples.random_simple.env:RandomCraftingEnv",
    )
except ImportError:
    pass
