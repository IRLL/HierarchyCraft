from typing import List, Optional

import pytest
import pytest_check as check

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.render.render import menus_sizes
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone

from tests.envs import classic_env, player_only_env, zone_only_env


class TestMenusSizes:
    def test_no_zone_no_zone_items(self):
        shapes = menus_sizes(
            n_items=1,
            n_zones_items=0,
            n_zones=0,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (60, 100))
        check.equal(shapes["player"], (140, 78))

    def test_one_zone_no_zone_items(self):
        """No need to show position when only one zone"""
        shapes = menus_sizes(
            n_items=1,
            n_zones_items=0,
            n_zones=1,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (60, 100))
        check.equal(shapes["player"], (140, 78))
        check.equal(shapes["position"], (0, 0))

    def test_two_zone_no_zone_items(self):
        shapes = menus_sizes(
            n_items=1,
            n_zones_items=0,
            n_zones=2,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (60, 100))
        check.equal(shapes["player"], (140, 78))
        check.equal(shapes["position"], (39, 22))

    def test_one_zone_no_player_item(self):
        shapes = menus_sizes(
            n_items=0,
            n_zones_items=10,
            n_zones=1,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (60, 100))
        check.equal(shapes["player"], (0, 0))
        check.equal(shapes["zone"], (200 - 60, 78))
        check.equal(shapes["position"], (0, 0))

    def test_two_zones_no_player_item(self):
        shapes = menus_sizes(
            n_items=0,
            n_zones_items=10,
            n_zones=2,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (60, 100))
        check.equal(shapes["player"], (0, 0))
        check.equal(shapes["zone"], (200 - 60, 78))
        check.equal(shapes["position"], (39, 22))

    def test_all(self):
        shapes = menus_sizes(
            n_items=10,
            n_zones_items=10,
            n_zones=10,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (60, 100))
        check.equal(shapes["player"], (95, 78))
        check.equal(shapes["zone"], (200 - 60 - 95, 78))
        check.equal(shapes["position"], (39, 22))


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
