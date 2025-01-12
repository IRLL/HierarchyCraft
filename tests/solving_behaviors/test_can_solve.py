from matplotlib import pyplot as plt
import pytest
import pytest_check as check


from hcraft.examples import EXAMPLE_ENVS
from hcraft.examples.minecraft import MineHcraftEnv
from hcraft.env import HcraftEnv


@pytest.mark.slow
@pytest.mark.parametrize(
    "env_class", [env_class for env_class in EXAMPLE_ENVS if env_class != MineHcraftEnv]
)
def test_can_solve(env_class):
    env: HcraftEnv = env_class(max_step=50)
    draw_call_graph = False

    if draw_call_graph:
        _fig, ax = plt.subplots()

    done = False
    observation, _infos = env.reset()
    for task in env.purpose.best_terminal_group.tasks:
        solving_behavior = env.solving_behavior(task)
        task_done = task.terminated
        while not task_done and not done:
            action = solving_behavior(observation)
            if draw_call_graph:
                plt.cla()
                solving_behavior.graph.call_graph.draw(ax)
                plt.show(block=False)

            if action == "Impossible":
                raise ValueError("Solving behavior could not find a solution.")
            observation, _reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            task_done = task.terminated

    if draw_call_graph:
        plt.show()

    check.is_true(env.purpose.terminated)
