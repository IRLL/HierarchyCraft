from typing import TYPE_CHECKING

import pytest

from hcraft.examples import HCRAFT_GYM_ENVS

if TYPE_CHECKING:
    import gym


@pytest.mark.slow
@pytest.mark.parametrize("env_gym_id", HCRAFT_GYM_ENVS)
def test_gym_make(env_gym_id):
    gym: "gym" = pytest.importorskip("gym")
    gym.make(env_gym_id)
