import pytest

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone

from tests.envs import classic_env


def test_render_rgb_array_classic_env():
    named_transformations, start_zone, _, _, _ = classic_env()
    transformations = list(named_transformations.values())
    pytest.importorskip("pygame")
    pytest.importorskip("pygame_menu")
    env = CraftingEnv(transformations, start_zone=start_zone)
    env.render(render_mode="rgb_array")
    env.close()
