# pylint: disable=arguments-differ, inconsistent-return-statements

""" MineHcraft Environment

HierarchyCraft environment adapted to the Minecraft inventory

"""

from pathlib import Path

from hcraft.elements import Stack
from hcraft.env import HcraftEnv
from hcraft.examples.minecraft.items import CLOSE_ENDER_PORTAL, OPEN_NETHER_PORTAL
from hcraft.examples.minecraft.transformations import (
    build_minehcraft_transformations,
)
from hcraft.examples.minecraft.zones import FOREST, NETHER, STRONGHOLD
from hcraft.world import world_from_transformations


class MineHcraftEnv(HcraftEnv):

    """MineHcraft Environment: A minecraft-like HierarchyCraft Environment.

    Default purpose is None (sandbox).

    """

    def __init__(self, **kwargs):
        mc_transformations = build_minehcraft_transformations()
        start_zone = kwargs.pop("start_zone", FOREST)
        mc_world = world_from_transformations(
            mc_transformations,
            start_zone=start_zone,
            start_zones_items={
                NETHER: [Stack(OPEN_NETHER_PORTAL)],
                STRONGHOLD: [Stack(CLOSE_ENDER_PORTAL)],
            },
        )
        mc_world.resources_path = Path(__file__).parent / "resources"
        super().__init__(world=mc_world, name="MineHcraft", **kwargs)
        self.metadata["video.frames_per_second"] = kwargs.pop("fps", 10)
