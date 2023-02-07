import networkx as nx
import numpy as np
import pytest_check as check
from networkx import is_isomorphic


def check_np_equal(array: np.ndarray, expected_array: np.ndarray):
    check.is_true(
        np.all(array == expected_array),
        msg=f"Got:\n{array}\nExpected:\n{expected_array}\nDiff:{array-expected_array}",
    )


def check_isomorphic(actual_graph: nx.Graph, expected_graph: nx.Graph):
    check.is_true(
        is_isomorphic(actual_graph, expected_graph),
        msg="Graphs are not isomorphic:"
        f"\n{list(actual_graph.edges())}"
        f"\n{list(expected_graph.edges())}",
    )


def check_not_isomorphic(actual_graph: nx.Graph, expected_graph: nx.Graph):
    check.is_false(
        is_isomorphic(actual_graph, expected_graph),
        msg="Graphs are isomorphic, yet they shouldn't:"
        f"\n{list(actual_graph.edges())}"
        f"\n{list(expected_graph.edges())}",
    )
