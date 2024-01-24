from typing import TYPE_CHECKING

import pytest
import pytest_check as check

import os


from hcraft.examples import EXAMPLE_ENVS
from hcraft.examples.minecraft import MineHcraftEnv
from hcraft.examples.minicraft import (
    MiniHCraftBlockedUnlockPickup,
)
from hcraft.env import HcraftEnv

if TYPE_CHECKING:
    from unified_planning.io import PDDLWriter


KNOWN_TO_FAIL_ENHSP = [
    MineHcraftEnv,
    MiniHCraftBlockedUnlockPickup,
]


@pytest.mark.slow
@pytest.mark.parametrize("env_class", EXAMPLE_ENVS)
def test_pddl_solve(env_class):
    up = pytest.importorskip("unified_planning")
    write = False
    env: HcraftEnv = env_class(max_step=200)
    problem = env.planning_problem(timeout=5)

    if env_class in KNOWN_TO_FAIL_ENHSP:
        pytest.xfail("ENHSP planner is known to fail on this environment")

    if write:
        writer: "PDDLWriter" = up.io.PDDLWriter(problem.upf_problem)
        pddl_dir = os.path.join("planning", "pddl", env.name)
        os.makedirs(pddl_dir, exist_ok=True)
        writer.write_domain(os.path.join(pddl_dir, "domain.pddl"))
        writer.write_problem(os.path.join(pddl_dir, "problem.pddl"))

    done = False
    _observation = env.reset()
    while not done:
        action = problem.action_from_plan(env.state)
        _observation, _reward, done, _ = env.step(action)
    check.is_true(env.purpose.terminated, msg=f"Plan was :{problem.plans}")
    check.equal(env.current_step, problem.stats[0]["Plan-Length"])
