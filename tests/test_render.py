import pytest

from hcraft.env import HcraftEnv
from hcraft.render.human import render_env_with_human
from tests.envs import classic_env, player_only_env, zone_only_env


def test_render_rgb_array_classic_env():
    env = classic_env()[0]
    _render_env(env, test_with_human=False)


def test_render_rgb_array_player_only_env():
    env = player_only_env()[0]
    _render_env(env, test_with_human=False)


def test_render_rgb_array_zone_only_env():
    env = zone_only_env()[0]
    _render_env(env, test_with_human=False)


def _render_env(env: HcraftEnv, test_with_human: bool = False):
    pytest.importorskip("pygame")
    pytest.importorskip("pygame_menu")
    if test_with_human:
        render_env_with_human(env)
    env.render(render_mode="rgb_array")
    env.close()
