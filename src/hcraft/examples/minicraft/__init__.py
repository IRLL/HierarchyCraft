import inspect
from pathlib import Path

from hcraft.examples.minicraft.empty import MiniHCraftEmpty
from hcraft.examples.minicraft.fourrooms import MiniHCraftFourRooms
from hcraft.examples.minicraft.multiroom import MiniHCraftMultiRoom
from hcraft.examples.minicraft.crossing import MiniHCraftCrossing
from hcraft.examples.minicraft.doorkey import MiniHCraftDoorKey
from hcraft.examples.minicraft.unlock import MiniHCraftUnlock
from hcraft.examples.minicraft.unlockpickup import MiniHCraftUnlockPickup
from hcraft.examples.minicraft.unlockpickupblocked import MiniHCraftBlockedUnlockPickup
from hcraft.examples.minicraft.keycorridor import MiniHCraftKeyCorridor


MINICRAFT_ENVS = [
    MiniHCraftEmpty,
    MiniHCraftFourRooms,
    MiniHCraftMultiRoom,
    MiniHCraftCrossing,
    MiniHCraftDoorKey,
    MiniHCraftUnlock,
    MiniHCraftUnlockPickup,
    MiniHCraftBlockedUnlockPickup,
    MiniHCraftKeyCorridor,
]

__all__ = [
    "MiniHCraftEmpty",
    "MiniHCraftFourRooms",
    "MiniHCraftMultiRoom",
    "MiniHCraftCrossing",
    "MiniHCraftDoorKey",
    "MiniHCraftUnlock",
    "MiniHCraftUnlockPickup",
    "MiniHCraftBlockedUnlockPickup",
    "MiniHCraftKeyCorridor",
]

MINICRAFT_GYM_ENVS = []

try:
    import gym

    ENV_PATH = "hcraft.examples.minicraft"

    for env_class in MINICRAFT_ENVS:
        env_name = env_class().name
        submodule = Path(inspect.getfile(env_class)).name.split(".")[0]
        env_path = f"{ENV_PATH}.{submodule}:{env_class.__name__}"
        gym_name = f"{env_name}-v1"
        gym.register(id=gym_name, entry_point=env_path)
        MINICRAFT_GYM_ENVS.append(gym_name)


except ImportError:
    pass
