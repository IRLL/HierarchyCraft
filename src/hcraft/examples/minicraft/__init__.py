from hcraft.examples.minicraft.empty import MiniCraftEmpty
from hcraft.examples.minicraft.fourrooms import MiniCraftFourRooms
from hcraft.examples.minicraft.multiroom import MiniCraftMultiRoom
from hcraft.examples.minicraft.crossing import MiniCraftCrossing
from hcraft.examples.minicraft.doorkey import MiniCraftDoorKey
from hcraft.examples.minicraft.unlock import MiniCraftUnlock
from hcraft.examples.minicraft.unlockpickup import MiniCraftUnlockPickup
from hcraft.examples.minicraft.unlockpickupblocked import MiniCraftBlockedUnlockPickup
from hcraft.examples.minicraft.keycorridor import MiniCraftKeyCorridor


MINICRAFT_ENVS = [
    MiniCraftEmpty,
    MiniCraftFourRooms,
    MiniCraftMultiRoom,
    MiniCraftCrossing,
    MiniCraftDoorKey,
    MiniCraftUnlock,
    MiniCraftUnlockPickup,
    MiniCraftBlockedUnlockPickup,
    MiniCraftKeyCorridor,
]

__all__ = [
    "MiniCraftEmpty",
    "MiniCraftFourRooms",
    "MiniCraftMultiRoom",
    "MiniCraftCrossing",
    "MiniCraftDoorKey",
    "MiniCraftUnlock",
    "MiniCraftUnlockPickup",
    "MiniCraftBlockedUnlockPickup",
    "MiniCraftKeyCorridor",
]
