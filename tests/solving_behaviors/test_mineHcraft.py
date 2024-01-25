from hcraft.examples.minecraft.env import MineHcraftEnv
from hcraft.task import Task


import pytest
import pytest_check as check

HARD_TASKS = [
    "Place open_ender_portal anywhere",
    "Go to stronghold",
    "Go to end",
    "Get ender_dragon_head",
]


@pytest.mark.slow
@pytest.mark.xfail(reason="Destination items are not taken into account")
def test_solving_behaviors():
    """All tasks should be solved by their solving behavior."""
    env = MineHcraftEnv(purpose="all", max_step=500)
    done = False
    observation = env.reset()
    tasks_left = env.purpose.tasks.copy()
    task = [t for t in tasks_left if t.name == "Place enchanting_table anywhere"][0]
    solving_behavior = env.solving_behavior(task)
    easy_tasks_left = [task]
    while not done and not env.purpose.terminated:
        tasks_left = [t for t in tasks_left if not t.terminated]
        if task is None:
            easy_tasks_left = [t for t in tasks_left if t.name not in HARD_TASKS]
            if len(easy_tasks_left) > 0:
                task = easy_tasks_left[0]
            else:
                task = tasks_left[0]
            print(f"Task started: {task} (step={env.current_step})")
            solving_behavior = env.solving_behavior(task)
        action = solving_behavior(observation)
        observation, _rew, done, _infos = env.step(action)
        if task.terminated:
            print(f"Task finished: {task}, tasks_left: {tasks_left}")
            task = None
    if isinstance(task, Task) and not task.terminated:
        print(f"Last unfinished task: {task}")
    if set(t.name for t in tasks_left) == set(HARD_TASKS):
        pytest.xfail(f"Harder tasks ({HARD_TASKS}) cannot be done for now ...")
    check.is_true(env.purpose.terminated, msg=f"tasks not completed: {tasks_left}")
