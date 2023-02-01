from typing import TYPE_CHECKING, List, Dict, Union, Any, Optional
from enum import Enum

import numpy as np
import networkx as nx

import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
from matplotlib.axes import Axes

from hebg.graph import (
    get_nodes_by_level,
    draw_networkx_nodes_images,
)
from hebg.layouts.metabased import leveled_layout_energy

from crafting.world import Item, Zone
from crafting.transformation import Transformation
from crafting.render.utils import load_or_create_image

if TYPE_CHECKING:
    from crafting.env import CraftingEnv


class ReqNodesTypes(Enum):
    """Node types in the requirements graph."""

    ITEM = "item"
    ZONE = "zone"
    ZONE_ITEM = "zone_item"


NODE_COLOR_BY_TYPE: Dict[ReqNodesTypes, str] = {
    ReqNodesTypes.ITEM: "blue",
    ReqNodesTypes.ZONE: "green",
    ReqNodesTypes.ZONE_ITEM: "cyan",
}


def build_requirements_graph(env: "CraftingEnv") -> nx.MultiDiGraph:
    """Build the world requirements graph.

    Returns:
        The world requirements graph as a networkx DiGraph.

    """
    graph = nx.MultiDiGraph()
    _add_requirements_nodes(env, graph)
    edge_index = _add_start_edges(env, graph)
    for transfo in env.transformations:
        if transfo.zones is not None:
            for zone in transfo.zones:
                _add_transformation_edges(graph, transfo, edge_index, zone)
                edge_index += 1
        else:
            _add_transformation_edges(graph, transfo, edge_index)
            edge_index += 1
    return graph


def _add_requirements_nodes(env: "CraftingEnv", graph: nx.MultiDiGraph):
    resources_path = env.resources_path
    _add_nodes(env.world.items, ReqNodesTypes.ITEM, resources_path, graph)
    _add_nodes(env.world.zones_items, ReqNodesTypes.ZONE_ITEM, resources_path, graph)
    if len(env.world.zones) >= 1:
        _add_nodes(env.world.zones, ReqNodesTypes.ZONE, resources_path, graph)


def _add_nodes(
    objs: List[Union[Item, Zone]],
    node_type: ReqNodesTypes,
    resources_path: str,
    graph: nx.MultiDiGraph,
):
    """Add colored nodes to the graph"""
    for obj in objs:
        name = obj.name
        if node_type == ReqNodesTypes.ZONE_ITEM:
            name = _str_zone_item(name)
        graph.add_node(
            name,
            type=node_type.value,
            color=NODE_COLOR_BY_TYPE[node_type],
            image=np.array(load_or_create_image(obj, resources_path)),
            label=obj.name.capitalize(),
        )


def _add_transformation_edges(
    graph: nx.MultiDiGraph,
    transfo: "Transformation",
    transfo_index: int,
    zone: Optional[Zone] = None,
):
    """Add edges induced by a Crafting recipe."""
    in_items = []
    if transfo.removed_player_items is not None:
        in_items = [stack.item for stack in transfo.removed_player_items]

    out_items = []
    if transfo.added_player_items is not None:
        for stack in transfo.added_player_items:
            # Filter outputs if they require themselves
            if stack.item not in in_items:
                out_items.append(stack.item)

    in_zone_items = []
    if transfo.removed_zone_items is not None:
        in_zone_items = [stack.item for stack in transfo.removed_zone_items]
    if transfo.removed_destination_items is not None:
        in_zone_items += [stack.item for stack in transfo.removed_destination_items]

    _out_zone_items = []
    if transfo.added_zone_items is not None:
        _out_zone_items += transfo.added_zone_items
    if transfo.added_destination_items is not None:
        _out_zone_items += transfo.added_destination_items

    # Filter outputs if they require themselves
    out_zone_items = []
    for stack in _out_zone_items:
        if transfo.removed_zone_items is not None and stack.item in [
            _stack.item for _stack in transfo.removed_zone_items
        ]:
            continue
        if transfo.removed_destination_items is not None and stack.item in [
            _stack.item for _stack in transfo.removed_destination_items
        ]:
            continue
        out_zone_items.append(stack.item)

    destinations = []
    if transfo.destination is not None:
        destinations = [transfo.destination]

    for out_item in out_items:
        _add_crafts(
            graph,
            in_items,
            in_zone_items,
            zone,
            out_item.name,
            transfo,
            transfo_index,
        )

    for out_zone_item in out_zone_items:
        _add_crafts(
            graph,
            in_items,
            in_zone_items,
            zone,
            _str_zone_item(out_zone_item.name),
            transfo,
            transfo_index,
        )

    for destination in destinations:
        _add_crafts(
            graph,
            in_items,
            in_zone_items,
            zone,
            destination.name,
            transfo,
            transfo_index,
        )


def _add_crafts(
    graph: nx.MultiDiGraph,
    in_items: List[Item],
    in_zone_items: List[Item],
    zone: Optional[Zone],
    out_node: Union[Zone, Item],
    transfo: Transformation,
    index: int,
):
    if zone is not None:
        graph.add_edge(
            zone.name,
            out_node,
            type="zone_required",
            color=[0, 1, 0, 1],
            key=index,
        )
    for node in set(in_items):
        graph.add_edge(
            node.name,
            out_node,
            type="item_needed",
            color=[1, 0, 0, 1],
            transformation=transfo,
            key=index,
        )
    for node in set(in_zone_items):
        graph.add_edge(
            _str_zone_item(node.name),
            out_node,
            type="zone_item_needed",
            color=[0.2, 1, 0.2, 1],
            key=index,
        )


def _add_start_edges(env: "CraftingEnv", graph: nx.MultiDiGraph) -> int:
    start_index = 0
    if env.start_zone is not None:
        graph.add_edge(
            "#START",
            env.start_zone.name,
            key=start_index,
            type="start_zone",
            color=[0, 1, 0, 1],
        )
        start_index += 1
    for start_itemstack in env.start_items:
        graph.add_edge(
            "#START",
            _str_zone_item(start_itemstack.item.name),
            key=start_index,
            type="start_item",
            color=[0, 1, 0, 1],
        )
        start_index += 1
    for zone, start_zone_items in env.start_zones_items.items():
        for start_zone_itemstack in start_zone_items:
            graph.add_edge(
                zone.name,
                _str_zone_item(start_zone_itemstack.item.name),
                key=start_index,
                type="start_zone_item",
                color=[0, 1, 0, 1],
            )
            start_index += 1
    return start_index


def _str_zone_item(name: str):
    return f"{name} in zone"


def compute_levels(graph: nx.MultiDiGraph):
    """Compute the hierachical levels of all DiGraph nodes.

    Adds the attribute 'level' to each node in the given graph.
    Adds the attribute 'nodes_by_level' to the given graph.
    Adds the attribute 'depth' to the given graph.

    Args:
        graph: A networkx DiGraph.

    Returns:
        Dictionary of nodes by level.

    """

    def _compute_level_dependencies(graph: nx.MultiDiGraph, node):
        predecessors = list(graph.predecessors(node))
        if len(predecessors) == 0:
            graph.nodes[node]["level"] = 0
            return True

        pred_level_by_key = {}
        for pred, _node, key in graph.in_edges(node, keys=True):
            try:
                pred_level = graph.nodes[pred]["level"]
            except KeyError:
                pred_level = None

            if key in pred_level_by_key:
                pred_level_by_key[key].append(pred_level)
            else:
                pred_level_by_key[key] = [pred_level]

        max_level_by_index = []
        for key, level_list in pred_level_by_key.items():
            if None in level_list:
                continue
            max_level_by_index.append(max(level_list))
        if len(max_level_by_index) == 0:
            return False
        level = 1 + min(max_level_by_index)
        graph.nodes[node]["level"] = level
        return True

    for _ in range(len(graph.nodes())):
        all_nodes_have_level = True
        incomplete_nodes = []
        for node in graph.nodes():
            incomplete = not _compute_level_dependencies(graph, node)
            if incomplete:
                incomplete_nodes.append(node)
                all_nodes_have_level = False
        if all_nodes_have_level:
            break

    if not all_nodes_have_level:
        raise ValueError(
            "Could not attribute levels to all nodes. "
            f"Incomplete nodes: {incomplete_nodes}"
        )

    return get_nodes_by_level(graph)


def compute_edges_color(graph: nx.DiGraph):
    """Compute the edges colors of a leveled graph for readability.

    Requires nodes to have a 'level' attribute.
    Adds the attribute 'color' and 'linestyle' to each edge in the given graph.
    Nodes with a lot of successors will have more transparent edges.
    Edges going from high to low level will be dashed.

    Args:
        graph: A networkx DiGraph.

    """
    alphas = [1, 1, 1, 1, 1, 0.5, 0.5, 0.5]
    for node in graph.nodes():
        successors = list(graph.successors(node))
        for succ in successors:
            alpha = 0.05
            if graph.nodes[node]["level"] < graph.nodes[succ]["level"]:
                if len(successors) < len(alphas):
                    alpha = alphas[len(successors) - 1]
            else:
                graph.edges[node, succ]["linestyle"] = "dashed"
            if isinstance(graph.edges[node, succ]["color"], list):
                graph.edges[node, succ]["color"][-1] = alpha


def collapse_as_digraph(multidigraph: nx.MultiDiGraph) -> nx.DiGraph:
    digraph = nx.DiGraph()
    digraph.graph = multidigraph.graph
    for node, data in multidigraph.nodes(data=True):
        digraph.add_node(node, **data)
    for (pred, node, key, data) in multidigraph.edges(keys=True, data=True):
        if not digraph.has_edge(pred, node):
            digraph.add_edge(pred, node, keys=[], **data)
        digraph.edges[pred, node]["keys"].append(key)
    return digraph


def break_cycles_through_level(multidigraph: nx.MultiDiGraph):
    acyclical_multidigraph = multidigraph.copy()
    nodes_level = acyclical_multidigraph.nodes(data="level", default=0)
    for (pred, node, key) in multidigraph.edges(keys=True):
        if nodes_level[pred] >= nodes_level[node]:
            acyclical_multidigraph.remove_edge(pred, node, key)
    return acyclical_multidigraph


class RequirementsGraphLayout(Enum):
    LEVEL = "level"
    SPRING = "spring"


def draw_requirements_graph(
    ax: Axes,
    requirements_graph: nx.DiGraph,
    layout: RequirementsGraphLayout = RequirementsGraphLayout.LEVEL,
    **kwargs,
):
    """Draw the requirement graph on a given Axes.

    Args:
        ax: Axes to draw on.

    Return:
        The Axes with requirements_graph drawn on it.

    """
    compute_levels(requirements_graph)
    acyclic_requirements_graph = break_cycles_through_level(requirements_graph)
    digraph = collapse_as_digraph(acyclic_requirements_graph)
    compute_edges_color(digraph)

    layout = RequirementsGraphLayout(layout)
    if layout == RequirementsGraphLayout.LEVEL:
        pos = leveled_layout_energy(digraph)
    elif layout == RequirementsGraphLayout.SPRING:
        pos = nx.spring_layout(digraph)

    plain_edges = [
        (u, v)
        for u, v, style in digraph.edges(data="linestyle", default=None)
        if style is None
    ]

    # Plain edges
    nx.draw_networkx_edges(
        digraph,
        pos,
        edgelist=plain_edges,
        ax=ax,
        arrowsize=20,
        arrowstyle="->",
        edge_color=[digraph.edges[u, v]["color"] for u, v in plain_edges],
    )

    draw_networkx_nodes_images(digraph, pos, ax=ax, img_zoom=0.3)

    # nx.draw_networkx_labels(
    #     graph, pos,
    #     ax=ax,
    #     font_color='black',
    #     font_size=6,
    #     labels=dict(graph.nodes(data='label'))
    # )

    # Create the legend patches
    legend_patches = []
    legend_arrows = [
        mpatches.FancyArrow(
            *(0, 0, 1, 0), facecolor="red", edgecolor="none", label="Craft"
        )
    ]

    # Add zone_property legend only if there is any
    for leg_node_type in ReqNodesTypes:
        has_type = [
            node_type == leg_node_type for _, node_type in digraph.nodes(data="type")
        ]
        if any(has_type):
            legend_item = mpatches.Patch(
                facecolor="none",
                edgecolor=NODE_COLOR_BY_TYPE[leg_node_type],
                label=str(leg_node_type.value).capitalize(),
            )
            legend_patches.append(legend_item)

    # Draw the legend
    ax.legend(
        handles=legend_patches + legend_arrows,
        handler_map={
            # Patch arrows with fancy arrows in legend
            mpatches.FancyArrow: HandlerPatch(
                patch_func=lambda width, height, **kwargs: mpatches.FancyArrow(
                    *(0, 0.5 * height, width, 0),
                    width=0.2 * height,
                    length_includes_head=True,
                    head_width=height,
                    overhang=0.5,
                )
            ),
        },
    )

    # Add Hierarchies numbers
    nodes_by_level: Dict[int, Any] = digraph.graph["nodes_by_level"]
    for level, level_nodes in nodes_by_level.items():
        level_poses = np.array([pos[node] for node in level_nodes])
        mean_x = np.mean(level_poses[:, 0])
        if level == 0:
            ax.text(mean_x - 1, -0.07, "Depth", ha="left", va="center")
        ax.text(mean_x, -0.07, str(level), ha="center", va="center")
    return ax
