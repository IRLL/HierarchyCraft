from typing import List, Optional

import pytest

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone

from tests.envs import classic_env, player_only_env, zone_only_env


def test_render_rgb_array_classic_env():
    named_transformations, start_zone, _, _, _ = classic_env()
    _render_env(
        list(named_transformations.values()),
        start_zone,
        test_with_human=False,
    )


def test_render_rgb_array_player_only_env():
    named_transformations, _, _, _, _ = player_only_env()
    _render_env(
        list(named_transformations.values()),
        test_with_human=False,
    )


def test_render_rgb_array_zone_only_env():
    named_transformations, start_zone, _, _, _ = zone_only_env()
    _render_env(
        list(named_transformations.values()),
        start_zone,
        test_with_human=False,
    )


def _render_env(
    transformations: List[Transformation],
    start_zone: Optional[Zone] = None,
    test_with_human: bool = False,
):
    pytest.importorskip("pygame")
    pytest.importorskip("pygame_menu")
    env = CraftingEnv(transformations, start_zone=start_zone)
    if test_with_human:
        render_env_with_human(env)
    env.render(render_mode="rgb_array")
    env.close()
