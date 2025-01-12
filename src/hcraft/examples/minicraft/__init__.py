"""# MiniHCraft environments

List of environments representing abstractions from
[minigrid environments](https://minigrid.farama.org/environments/minigrid/).

See submodules for each individual environement:

| Minigrid name       | Hcraft reference                                |
|:--------------------|:------------------------------------------------|
| Empty               | `hcraft.examples.minicraft.empty`               |
| FourRooms           | `hcraft.examples.minicraft.fourrooms`           |
| MultiRoom           | `hcraft.examples.minicraft.multiroom`           |
| Crossing            | `hcraft.examples.minicraft.crossing`            |
| KeyCorridor         | `hcraft.examples.minicraft.keycorridor`         |
| DoorKey             | `hcraft.examples.minicraft.doorkey`             |
| Unlock              | `hcraft.examples.minicraft.unlock`              |
| UnlockPickup        | `hcraft.examples.minicraft.unlockpickup`        |
| BlockedUnlockPickup | `hcraft.examples.minicraft.unlockpickupblocked` |


"""

import inspect
from pathlib import Path
from typing import List, Type


from hcraft.examples.minicraft.minicraft import MiniCraftEnv

import hcraft.examples.minicraft.empty as empty
import hcraft.examples.minicraft.fourrooms as fourrooms
import hcraft.examples.minicraft.multiroom as multiroom
import hcraft.examples.minicraft.crossing as crossing
import hcraft.examples.minicraft.doorkey as doorkey
import hcraft.examples.minicraft.unlock as unlock
import hcraft.examples.minicraft.unlockpickup as unlockpickup
import hcraft.examples.minicraft.unlockpickupblocked as unlockpickupblocked
import hcraft.examples.minicraft.keycorridor as keycorridor

from hcraft.examples.minicraft.empty import MiniHCraftEmpty
from hcraft.examples.minicraft.fourrooms import MiniHCraftFourRooms
from hcraft.examples.minicraft.multiroom import MiniHCraftMultiRoom
from hcraft.examples.minicraft.crossing import MiniHCraftCrossing
from hcraft.examples.minicraft.doorkey import MiniHCraftDoorKey
from hcraft.examples.minicraft.unlock import MiniHCraftUnlock
from hcraft.examples.minicraft.unlockpickup import MiniHCraftUnlockPickup
from hcraft.examples.minicraft.unlockpickupblocked import MiniHCraftBlockedUnlockPickup
from hcraft.examples.minicraft.keycorridor import MiniHCraftKeyCorridor


MINICRAFT_ENVS: List[Type[MiniCraftEnv]] = [
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

MINICRAFT_NAME_TO_ENV = {env.MINICRAFT_NAME: env for env in MINICRAFT_ENVS}

__all__ = [
    "empty",
    "fourrooms",
    "multiroom",
    "crossing",
    "doorkey",
    "unlock",
    "unlockpickup",
    "unlockpickupblocked",
    "keycorridor",
]

MINICRAFT_GYM_ENVS = []

try:
    import gymnasium as gym

    ENV_PATH = "hcraft.examples.minicraft"

    for env_name, env_class in MINICRAFT_NAME_TO_ENV.items():
        submodule = Path(inspect.getfile(env_class)).name.split(".")[0]
        env_path = f"{ENV_PATH}.{submodule}:{env_class.__name__}"
        gym_name = f"{env_name}-v1"
        gym.register(id=gym_name, entry_point=env_path)
        MINICRAFT_GYM_ENVS.append(gym_name)


except ImportError:
    pass
