import pytest
import pytest_check as check

import os

from unified_planning.io import PDDLWriter
from unified_planning.shortcuts import OneshotPlanner
from unified_planning.plans import SequentialPlan

from crafting.render.human import render_env_with_human
from crafting.examples.minicraft import MINICRAFT_ENVS, MiniCraftBlockedUnlockPickup
from crafting.examples.minicraft.minicraft import MiniCraftEnv
from crafting.planning import world_task_to_planning_problem


@pytest.mark.parametrize("env_class", MINICRAFT_ENVS)
def test_build_env(env_class):
    human_run = False
    env = env_class()
    if human_run:
        render_env_with_human(env)


@pytest.mark.parametrize("env_class", MINICRAFT_ENVS)
def test_pddl_solve(env_class):
    write = False
    env: MiniCraftEnv = env_class()
    problem = world_task_to_planning_problem(env.world, env.name, task=env.task)

    if write:
        writer = PDDLWriter(problem)
        pddl_dir = os.path.join("planning", "pddl", env.name)
        os.makedirs(pddl_dir, exist_ok=True)
        writer.write_domain(os.path.join(pddl_dir, "domain.pddl"))
        writer.write_problem(os.path.join(pddl_dir, "problem.pddl"))

    if isinstance(env, MiniCraftBlockedUnlockPickup):
        return  # Infinite loop for no reason ???

    with OneshotPlanner(problem_kind=problem.kind) as planner:
        results = planner.solve(problem)
        plan: SequentialPlan = results.plan
        assert plan is not None, "Not plan found !"
        actions = plan.actions

    def action_from_plan():
        if not actions:
            raise ValueError("Plan has failed")
        action = int(str(actions.pop(0)).split("_")[0])
        return action

    done = False
    _observation = env.reset()
    while not done:
        action = action_from_plan()
        _observation, _reward, done, _ = env.step(action)
    check.is_true(env.task.terminated)


@pytest.mark.parametrize("env_class", MINICRAFT_ENVS[:-2])
def test_can_solve(env_class):
    env: MiniCraftEnv = env_class(max_step=20)
    solving_behavior = env.solving_behavior(env.task)
    done = False
    observation = env.reset()
    while not done:
        action = solving_behavior(observation)
        observation, _reward, done, _ = env.step(action)
    check.is_true(env.task.terminated)


@pytest.mark.parametrize("env_class", MINICRAFT_ENVS)
def test_requirements_graph(env_class):
    draw = True
    env: MiniCraftEnv = env_class()
    env.world.requirements.graph
    if draw:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        plt.tight_layout()
        fig.set_size_inches(16, 9)
        env.world.requirements.draw(ax)

        requirements_dir = os.path.join("docs", "images", "requirements_graphs")
        os.makedirs(requirements_dir, exist_ok=True)

        filename = os.path.join(requirements_dir, f"{env.name}.png")
        if not os.path.exists(filename):
            fig.savefig(filename, dpi=80, transparent=True)
        plt.close()
