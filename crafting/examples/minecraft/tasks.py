# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting environement common tasks """

from typing import TYPE_CHECKING

from crafting.task import Task
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *

if TYPE_CHECKING:
    from crafting.world.world import World


class TaskGatherWood(Task):
    """Gather as much wood as possible"""

    def __init__(self, world: "World", use_reward_shaping=True):
        super().__init__("gather_wood", world)
        self.add_item_value(WOOD.item_id, 1)
        self.use_reward_shaping = use_reward_shaping
        if self.use_reward_shaping:
            for axe in AXES:
                self.add_achivement_getitem(axe.item_id, 1)


class TaskGatherStone(Task):
    """Gather as much stone as possible"""

    def __init__(self, world: "World", use_reward_shaping=True):
        super().__init__("gather_stone", world)
        self.add_item_value(COBBLESTONE.item_id, 1)
        self.use_reward_shaping = use_reward_shaping
        if self.use_reward_shaping:
            for pickaxe in PICKAXES:
                self.add_achivement_getitem(pickaxe.item_id, 1)


class TaskObtainBook(Task):
    """Obtaining a Book"""

    def __init__(self, world: "World", use_reward_shaping=True):
        super().__init__("obtain_book", world)
        self.item = BOOK
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(BOOK.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            for item in (
                WOOD,
                WOOD_PLANK,
                REEDS,
                PAPER,
                WOODEN_SWORD,
                LEATHER,
            ):
                self.add_achivement_getitem(item.item_id, 1)


class TaskObtainDiamond(Task):
    """Obtaining a Diamond"""

    def __init__(self, world: "World", use_reward_shaping=True):
        super().__init__("obtain_diamond", world)
        self.item = DIAMOND
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(DIAMOND.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            for item in (
                WOOD,
                WOOD_PLANK,
                WOODEN_PICKAXE,
                COBBLESTONE,
                STONE_PICKAXE,
                IRON_ORE,
                IRON_INGOT,
                IRON_PICKAXE,
            ):
                self.add_achivement_getitem(item.item_id, 1)


class TaskObtainClock(Task):
    """Obtaining an Clock"""

    def __init__(self, world: "World", use_reward_shaping=True):
        super().__init__("obtain_clock", world)
        self.item = CLOCK
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(CLOCK.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            for item in (
                WOOD,
                WOOD_PLANK,
                WOODEN_PICKAXE,
                COBBLESTONE,
                STONE_PICKAXE,
                IRON_ORE,
                IRON_INGOT,
                IRON_PICKAXE,
                GOLD_ORE,
                GOLD_INGOT,
                REDSTONE,
            ):
                self.add_achivement_getitem(item.item_id, 1)


class TaskObtainEnchantingTable(Task):
    """Obtaining an EnchantingTable"""

    def __init__(self, world: "World", use_reward_shaping=True):
        super().__init__("obtain_enchanting_table", world)
        self.item = ENCHANTING_TABLE
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(ENCHANTING_TABLE.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            for item in (
                WOOD,
                WOOD_PLANK,
                WOODEN_PICKAXE,
                COBBLESTONE,
                STONE_PICKAXE,
                IRON_ORE,
                IRON_INGOT,
                IRON_PICKAXE,
                DIAMOND,
                DIAMOND_PICKAXE,
                OBSIDIAN,
                REEDS,
                WOODEN_SWORD,
                LEATHER,
                BOOK,
            ):
                self.add_achivement_getitem(item.item_id, 1)


TASKS = {
    "gather_wood": TaskGatherWood,
    "gather_stone": TaskGatherStone,
    "obtain_book": TaskObtainBook,
    "obtain_diamond": TaskObtainDiamond,
    "obtain_clock": TaskObtainClock,
    "obtain_enchanting_table": TaskObtainEnchantingTable,
}
