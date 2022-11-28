# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest_check as check

from hypothesis import given
from hypothesis.strategies import integers

from networkx import is_isomorphic, DiGraph

from crafting.examples.simple.env import (
    StackedCraftingEnv,
    LightStackedCraftingEnv,
    LighterStackedCraftingEnv,
)


def test_stacked_requirements_graph():
    env = StackedCraftingEnv(n_items=4)
    expected_graph = DiGraph()
    for item in env.world.items:
        for required_id in range(item.item_id):
            expected_graph.add_edge(required_id, item.item_id)

    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))


@given(integers(2, 6))
def test_lightstacked_requirements_graph(n_required_previous: int):
    env = LightStackedCraftingEnv(n_items=4, n_required_previous=n_required_previous)
    expected_graph = DiGraph()
    for item in env.world.items:
        min_idx = max(0, item.item_id - n_required_previous)
        for required_id in range(min_idx, item.item_id):
            expected_graph.add_edge(required_id, item.item_id)

    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))


@given(integers(3, 6))
def test_lighterstacked_requirements_graph(n_required_previous: int):
    env = LighterStackedCraftingEnv(n_items=4, n_required_previous=n_required_previous)
    expected_graph = DiGraph()
    for item in env.world.items:
        if item.item_id > 0:
            expected_graph.add_edge(item.item_id - 1, item.item_id)
        min_idx = max(0, item.item_id - n_required_previous)
        for required_id in range(min_idx, item.item_id - 2):
            expected_graph.add_edge(required_id, item.item_id)

    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))
