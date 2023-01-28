# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=arguments-differ, inconsistent-return-statements

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

import os

from crafting import CraftingEnv, ItemStack
from crafting.examples.minecraft.transformations import (
    build_minecrafting_transformations,
)
from crafting.examples.minecraft.zones import FOREST, STRONGHOLD, NETHER
from crafting.examples.minecraft.items import CLOSE_ENDER_PORTAL, CLOSE_NETHER_PORTAL


class MineCraftingEnv(CraftingEnv):

    """MineCrafting Environment: A minecraft-like Crafting Environment."""

    def __init__(self, **kwargs):
        mc_dir = os.path.dirname(__file__)
        resources_path = os.path.join(mc_dir, "resources")
        mc_transformations = build_minecrafting_transformations()
        start_zone = kwargs.pop("start_zone", FOREST)
        super().__init__(
            mc_transformations,
            name="MineCrafting",
            start_zone=start_zone,
            start_zones_items={
                NETHER: [ItemStack(CLOSE_NETHER_PORTAL)],
                STRONGHOLD: [ItemStack(CLOSE_ENDER_PORTAL)],
            },
            resources_path=resources_path,
            **kwargs,
        )
        self.metadata["video.frames_per_second"] = kwargs.pop("fps", 10)
