from hcraft.examples import EXAMPLE_ENVS
from hcraft.render.human import render_env_with_human


import pytest


@pytest.mark.slow
@pytest.mark.parametrize("env_class", EXAMPLE_ENVS)
def test_build_env(env_class):
    human_run = False
    env = env_class()
    if human_run:
        render_env_with_human(env)
