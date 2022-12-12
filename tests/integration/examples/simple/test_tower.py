# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest_check as check

from hypothesis import given
from hypothesis.strategies import integers

from networkx import is_isomorphic, DiGraph

from crafting.examples.simple import TowerCraftingEnv
from hebg.behavior import Behavior


def test_tower_requirements_graph_1_1():
    """should have expected structure

    #1#
    #0#

    """
    height = 1
    width = 1
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = DiGraph()
    expected_graph.add_edge(0, 1)

    for recipe in env.world.recipes:
        print(recipe)
    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))


def test_tower_requirements_graph_1_2():
    """should have expected structure

    #2#
    #01#

    """
    height = 1
    width = 2
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = DiGraph()
    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(1, 2)

    for recipe in env.world.recipes:
        print(recipe)
    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))


def test_tower_requirements_graph_3_2():
    """should have expected structure

    #6##
    #45#
    #23#
    #01#

    """
    height = 3
    width = 2
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = DiGraph()
    expected_graph.add_edge(5, 6)
    expected_graph.add_edge(4, 6)
    expected_graph.add_edge(2, 5)
    expected_graph.add_edge(3, 5)
    expected_graph.add_edge(2, 4)
    expected_graph.add_edge(3, 4)
    expected_graph.add_edge(0, 3)
    expected_graph.add_edge(1, 3)
    expected_graph.add_edge(0, 2)
    expected_graph.add_edge(1, 2)

    for recipe in env.world.recipes:
        print(recipe)
    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))


def run_solve(env: TowerCraftingEnv, solver: Behavior) -> int:
    """Count how much steps are needed for the solver to finish.

    Args:
        env (CraftingEnv): The Crafting environment containing an finishing task.
        solver (Option): The solver to test the lenght of.

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
    env = TowerCraftingEnv(height=height, width=width, use_old_gym_format=True)
    all_options = env.world.get_all_options()
    solving_option: Behavior = all_options[f"Get {env.tasks[0].goal_item}"]
    n_steps = run_solve(env, solver=solving_option)


def test_tower_accessible_items():
    env = TowerCraftingEnv(height=2, width=3)
    for foundable_item in env.world.items[: env.width]:
        check.is_in(foundable_item, env.world.zones[0].items)
