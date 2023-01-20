from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis.strategies import integers

from crafting.examples.simple import TowerCraftingEnv

if TYPE_CHECKING:
    from hebg.behavior import Behavior


def run_solve(env: TowerCraftingEnv, solver: "Behavior") -> int:
    """Count how much steps are needed for the solver to finish.

    Args:
        env (CraftingEnv): The Crafting environment containing an finishing task.
        solver (Behavior): The solver to test the lenght of.

    Returns:
        int: Number of steps needed for the solver to complete the task.
    """
    step = 0
    done = False
    observation = env.reset()
    while not done:
        action = solver(observation)
        observation, _, done, _ = env.step(action)
        step += 1

    assert step < env.max_step
    return step


@given(integers(1, 3), integers(1, 3))
def test_tower_can_solve(height: int, width: int):
    env = TowerCraftingEnv(height=height, width=width)
    all_behaviors = env.world.get_all_behaviors()
    solving_behavior: "Behavior" = all_behaviors[f"Get {env.tasks[0].goal_item}"]
    n_steps = run_solve(env, solver=solving_behavior)
