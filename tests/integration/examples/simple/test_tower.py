# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest_check as check

from hypothesis import given
from hypothesis.strategies import integers

from networkx import is_isomorphic, DiGraph

from crafting.examples.simple import TowerCraftingEnv


@given(integers(1, 3), integers(1, 3))
def test_tower_requirements_graph(height: int, width: int):
    env = TowerCraftingEnv(height=height, width=width)
    expected_graph = DiGraph()
    for layer in range(1, height):
        layer_id = layer * width
        prev_layer_id = (layer - 1) * width
        for item_layer_id in range(width):
            for required_id in range(width):
                expected_graph.add_edge(
                    prev_layer_id + required_id,
                    layer_id + item_layer_id,
                )

    last_layer_id = (height - 1) * width
    last_item_id = height * width + 1
    for required_id in range(width):
        expected_graph.add_edge(last_layer_id + required_id, last_item_id)

    for recipe in env.world.recipes:
        print(recipe)
    check.is_true(is_isomorphic(env.world.get_requirements_graph(), expected_graph))
