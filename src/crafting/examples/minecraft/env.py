# pylint: disable=arguments-differ, inconsistent-return-statements

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

import os

from crafting.elements import ItemStack
from crafting.env import CraftingEnv
from crafting.examples.minecraft.items import CLOSE_ENDER_PORTAL, OPEN_NETHER_PORTAL
from crafting.examples.minecraft.transformations import (
    build_minecrafting_transformations,
)
from crafting.examples.minecraft.zones import FOREST, NETHER, STRONGHOLD
from crafting.world import world_from_transformations
from crafting.elements import Item
from crafting.purpose import GetItemTask


class MineCraftingEnv(CraftingEnv):

    """MineCrafting Environment: A minecraft-like Crafting Environment.

    Default purpose is to get an iron_ingot.

    """

    def __init__(self, **kwargs):
        mc_dir = os.path.dirname(__file__)
        resources_path = os.path.join(mc_dir, "resources")
        mc_transformations = build_minecrafting_transformations()
        start_zone = kwargs.pop("start_zone", FOREST)
        mc_world = world_from_transformations(
            mc_transformations,
            start_zone=start_zone,
            start_zones_items={
                NETHER: [ItemStack(OPEN_NETHER_PORTAL)],
                STRONGHOLD: [ItemStack(CLOSE_ENDER_PORTAL)],
            },
        )
        mc_world.resources_path = resources_path
        if "purpose" not in kwargs:
            kwargs["purpose"] = GetItemTask(Item("iron_ingot"))
        super().__init__(world=mc_world, name="MineCrafting", **kwargs)
        self.metadata["video.frames_per_second"] = kwargs.pop("fps", 10)
