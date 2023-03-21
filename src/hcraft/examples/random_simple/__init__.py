from hcraft.examples.random_simple.env import RandomHcraftEnv

__all__ = ["RandomHcraftEnv"]

# gym is an optional dependency
try:
    import gym

    gym.register(
        id="RandomHcraft-v1",
        entry_point="hcraft.examples.random_simple.env:RandomHcraftEnv",
    )
except ImportError:
    pass
