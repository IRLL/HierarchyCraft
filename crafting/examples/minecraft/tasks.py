# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting environement common tasks """

from crafting import Task
from crafting.world.world import World
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *


class TaskGatherWood(Task):
    """ Gather as much wood as possible """

    def __init__(self, world:World, use_reward_shaping=True):
        super().__init__('gather_wood', world)
        self.add_item_value(WOOD.item_id, 1)
        self.use_reward_shaping = use_reward_shaping
        if self.use_reward_shaping:
            for axe in AXES:
                self.add_achivement_getitem(axe.item_id, 1)


class TaskGatherStone(Task):
    """ Gather as much stone as possible """

    def __init__(self, world:World, use_reward_shaping=True):
        super().__init__('gather_stone', world)
        self.add_item_value(COBBLESTONE.item_id, 1)
        self.use_reward_shaping = use_reward_shaping
        if self.use_reward_shaping:
            for pickaxe in PICKAXES:
                self.add_achivement_getitem(pickaxe.item_id, 1)



class TaskObtainBook(Task):
    """ Obtaining a Book """

    def __init__(self, world:World, use_reward_shaping=True):
        super().__init__('obtain_book', world)
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(BOOK.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            self.add_achivement_getitem(WOOD.item_id, 1)
            self.add_achivement_getitem(WOOD_PLANK.item_id, 1)
            self.add_achivement_getitem(REEDS.item_id, 1)
            self.add_achivement_getitem(PAPER.item_id, 1)
            self.add_achivement_getitem(WOODEN_SWORD.item_id, 1)
            self.add_achivement_getitem(LEATHER.item_id, 1)


class TaskObtainDiamond(Task):
    """ Obtaining a Diamond """

    def __init__(self, world:World, use_reward_shaping=True):
        super().__init__('obtain_diamond', world)
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(DIAMOND.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            self.add_achivement_getitem(WOOD.item_id, 1)
            self.add_achivement_getitem(WOOD_PLANK.item_id, 1)
            self.add_achivement_getitem(WOODEN_PICKAXE.item_id, 1)
            self.add_achivement_getitem(COBBLESTONE.item_id, 1)
            self.add_achivement_getitem(STONE_PICKAXE.item_id, 1)
            self.add_achivement_getitem(IRON_INGOT.item_id, 1)
            self.add_achivement_getitem(IRON_PICKAXE.item_id, 1)


class TaskObtainClock(Task):
    """ Obtaining an Clock """

    def __init__(self, world:World, use_reward_shaping=True):
        super().__init__('obtain_clock', world)
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(CLOCK.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            self.add_achivement_getitem(WOOD.item_id, 1)
            self.add_achivement_getitem(WOOD_PLANK.item_id, 1)
            self.add_achivement_getitem(WOODEN_PICKAXE.item_id, 1)
            self.add_achivement_getitem(COBBLESTONE.item_id, 1)
            self.add_achivement_getitem(STONE_PICKAXE.item_id, 1)
            self.add_achivement_getitem(IRON_ORE.item_id, 1)
            self.add_achivement_getitem(IRON_INGOT.item_id, 1)
            self.add_achivement_getitem(IRON_PICKAXE.item_id, 1)
            self.add_achivement_getitem(GOLD_ORE.item_id, 1)
            self.add_achivement_getitem(GOLD_INGOT.item_id, 1)
            self.add_achivement_getitem(REDSTONE.item_id, 1)


class TaskObtainEnchantingTable(Task):
    """ Obtaining an EnchantingTable """

    def __init__(self, world:World, use_reward_shaping=True):
        super().__init__('obtain_enchanting_table', world)
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(ENCHANTING_TABLE.item_id, 10, end_task=True)

        if self.use_reward_shaping:
            self.add_achivement_getitem(WOOD.item_id, 1)
            self.add_achivement_getitem(WOOD_PLANK.item_id, 1)
            self.add_achivement_getitem(WOODEN_PICKAXE.item_id, 1)
            self.add_achivement_getitem(COBBLESTONE.item_id, 1)
            self.add_achivement_getitem(STONE_PICKAXE.item_id, 1)
            self.add_achivement_getitem(IRON_INGOT.item_id, 1)
            self.add_achivement_getitem(IRON_PICKAXE.item_id, 1)
            self.add_achivement_getitem(DIAMOND.item_id, 1)
            self.add_achivement_getitem(DIAMOND_PICKAXE.item_id, 1)
            self.add_achivement_getitem(OBSIDIAN.item_id, 1)

            self.add_achivement_getitem(REEDS.item_id, 1)
            self.add_achivement_getitem(PAPER.item_id, 1)
            self.add_achivement_getitem(WOODEN_SWORD.item_id, 1)
            self.add_achivement_getitem(LEATHER.item_id, 1)
            self.add_achivement_getitem(BOOK.item_id, 1)


TASKS = {
    'gather_wood': TaskGatherWood,
    'gather_stone': TaskGatherStone,
    'obtain_book': TaskObtainBook,
    'obtain_diamond': TaskObtainDiamond,
    'obtain_clock': TaskObtainClock,
    'obtain_enchanting_table': TaskObtainEnchantingTable,
}
