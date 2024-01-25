from typing import TYPE_CHECKING

import pytest
import pytest_check as check


from hcraft.examples import EXAMPLE_ENVS
from hcraft.examples.minecraft import MineHcraftEnv
from hcraft.examples.minicraft import (
    MiniHCraftKeyCorridor,
    MiniHCraftBlockedUnlockPickup,
    MiniHCraftUnlockPickup,
)
from hcraft.env import HcraftEnv

if TYPE_CHECKING:
    pass


KNOWN_TO_FAIL_HEBG = [
    MineHcraftEnv,
    MiniHCraftBlockedUnlockPickup,
    MiniHCraftUnlockPickup,
    MiniHCraftKeyCorridor,
]


@pytest.mark.slow
@pytest.mark.parametrize("env_class", EXAMPLE_ENVS)
def test_can_solve(env_class):
    env: HcraftEnv = env_class(max_step=50)
    if env_class in KNOWN_TO_FAIL_HEBG:
        pytest.xfail("Hebg is known to fail on this environment")
    done = False
    observation = env.reset()
    for task in env.purpose.best_terminal_group.tasks:
        solving_behavior = env.solving_behavior(task)
        task_done = task.terminated
        while not task_done and not done:
            action = solving_behavior(observation)
            if action == "Impossible":
                raise ValueError("Solving behavior could not find a solution.")
            observation, _reward, done, _ = env.step(action)
            task_done = task.terminated
    check.is_true(env.purpose.terminated)
