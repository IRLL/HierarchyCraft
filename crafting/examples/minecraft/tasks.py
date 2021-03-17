# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting environement common tasks """

from crafting import Task
from crafting.world.world import World
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import *

class TaskObtainDiamond(Task):
    """ Obtaining a diamond """

    def __init__(self, world:World, use_reward_shaping=True):
        super().__init__('obtain_diamond', world)
        self.use_reward_shaping = use_reward_shaping
        self.add_achivement_getitem(DIAMOND.item_id, 100, end_task=True)

        if self.use_reward_shaping:
            self.add_achivement_getitem(WOOD.item_id, 1.01)
            self.add_achivement_getitem(WOOD_PLANK.item_id, 1)
            self.add_achivement_getitem(WOODEN_PICKAXE.item_id, 1)
            self.add_achivement_getitem(STONE_PICKAXE.item_id, 3)
            self.add_achivement_getitem(IRON_INGOT.item_id, 3)
            self.add_achivement_getitem(IRON_PICKAXE.item_id, 5)

TASKS = {
    'obtain_diamond': TaskObtainDiamond
}
