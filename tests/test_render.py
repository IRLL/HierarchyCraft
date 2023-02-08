from typing import List, Optional

import pytest

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone

from tests.envs import classic_env, player_only_env


def test_render_rgb_array_classic_env():
    named_transformations, start_zone, _, _, _ = classic_env()
    _render_env(list(named_transformations.values()))


def test_render_rgb_array_player_only_env():
    named_transformations, start_zone, _, _, _ = player_only_env()
    _render_env(list(named_transformations.values()))


def _render_env(
    transformations: List[Transformation],
    start_zone: Optional[Zone] = None,
    test_with_human: bool = False,
):
    pytest.importorskip("pygame")
    pytest.importorskip("pygame_menu")
    env = CraftingEnv(transformations, start_zone=start_zone)
    if test_with_human:
        render_env_with_human()
    env.render(render_mode="rgb_array")
    env.close()
