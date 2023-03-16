from crafting.examples.minicraft.empty import MiniCraftEmpty
from crafting.examples.minicraft.fourrooms import MiniCraftFourRooms
from crafting.examples.minicraft.multiroom import MiniCraftMultiRoom
from crafting.examples.minicraft.crossing import MiniCraftCrossing
from crafting.examples.minicraft.doorkey import MiniCraftDoorKey
from crafting.examples.minicraft.unlock import MiniCraftUnlock
from crafting.examples.minicraft.unlockpickup import MiniCraftUnlockPickup
from crafting.examples.minicraft.unlockpickupblocked import MiniCraftBlockedUnlockPickup
from crafting.examples.minicraft.keycorridor import MiniCraftKeyCorridor


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
