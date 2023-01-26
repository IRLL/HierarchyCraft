from crafting.examples.simple.env import SimpleCraftingEnv
from crafting.examples.simple.recursive import (
    LighterRecursiveCraftingEnv,
    LightRecursiveCraftingEnv,
    RecursiveCraftingEnv,
)
from crafting.examples.simple.tower import TowerCraftingEnv

# gym is an optional dependency
try:
    import gym

    gym.register(
        id="RecursiveCrafting-v1",
        entry_point="crafting.examples.simple.recursive:RecursiveCraftingEnv",
    )

    gym.register(
        id="TowerCrafting-v1",
        entry_point="crafting.examples.simple.tower:TowerCraftingEnv",
    )

except ImportError:
    pass
