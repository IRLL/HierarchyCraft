from crafting.examples.minicraft.empty import MiniCraftEmpty
from crafting.examples.minicraft.fourrooms import MiniCraftFourRooms
from crafting.examples.minicraft.multiroom import MiniCraftMultiRoom
from crafting.examples.minicraft.crossing import MiniCraftCrossing
from crafting.examples.minicraft.doorkey import MiniCraftDoorKey
from crafting.examples.minicraft.unlock import MiniCraftUnlock

MINICRAFT_ENVS = [
    MiniCraftEmpty,
    MiniCraftFourRooms,
    MiniCraftMultiRoom,
    MiniCraftCrossing,
    MiniCraftDoorKey,
    MiniCraftUnlock,
]

__all__ = [
    "MiniCraftEmpty",
    "MiniCraftFourRooms",
    "MiniCraftMultiRoom",
    "MiniCraftCrossing",
    "MiniCraftDoorKey",
    "MiniCraftUnlock",
]
