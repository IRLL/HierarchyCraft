from typing import TYPE_CHECKING

import numpy as np
import networkx as nx

import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
from matplotlib.axes import Axes

# HEBG is an optional dependency
try:
    from hebg.graph import (
        compute_edges_color,
        compute_levels,
        draw_networkx_nodes_images,
    )
    from hebg.layouts.metabased import leveled_layout_energy
except ImportError:

    def _should_install_hebg(*args, **kwargs):
        raise ImportError(
            "Missing dependency for graph visualizations: hebg."
            "Install using 'pip install hebg'."
        )

    compute_edges_color = _should_install_hebg
    compute_levels = _should_install_hebg
    draw_networkx_nodes_images = _should_install_hebg
    leveled_layout_energy = _should_install_hebg

from crafting.world.items import Tool
from crafting.render.utils import load_or_create_image

if TYPE_CHECKING:
    from crafting.world.world import World


def build_requirements_graph(world: "World") -> nx.DiGraph:
    """Build the world requirements graph.

    Returns:
        The world requirements graph as a networkx DiGraph.

    """
    graph = nx.DiGraph()

    # Add items nodes
    for i, item in enumerate(world.items):

        color = "blue"
        if item in world.foundable_items:
            color = "green"
        elif isinstance(item, Tool):
            color = "cyan"

        graph.add_node(
            item.item_id,
            type="item",
            color=color,
            image=np.array(load_or_create_image(world, item)),
            item_id=item.item_id,
            label=item.name.capitalize(),
        )

    # Add properties nodes
    for i, prop in enumerate(world.zone_properties):
        graph.add_node(
            prop,
            type="zone_property",
            color="orange",
            prop_id=i,
            image=np.array(load_or_create_image(world, prop)),
            label=prop.capitalize(),
        )

    # Add recipes edges
    def _add_crafts(in_nodes, out_node):
        for index, node in enumerate(in_nodes):
            graph.add_edge(
                node,
                out_node,
                type="craft",
                color=[1, 0, 0, 1],
                index=index + 1,
            )

    for recipe in world.recipes:

        in_items_ids = []
        if recipe.inputs is not None:
            in_items_ids = [stack.item_id for stack in recipe.inputs]

        out_items_ids = []
        if recipe.outputs is not None:
            out_items_ids = [stack.item_id for stack in recipe.outputs]

        in_props = (
            list(recipe.needed_properties.keys())
            if recipe.needed_properties is not None
            else []
        )
        out_props = (
            list(recipe.added_properties.keys())
            if recipe.needed_properties is not None
            else []
        )

        for out_item in out_items_ids:
            _add_crafts(in_items_ids + in_props, out_item)

        for out_prop in out_props:
            _add_crafts(in_items_ids + in_props, out_prop)

    # Add required_tools and drops edges
    for foundable_item in world.foundable_items:

        need_tool = (
            foundable_item.required_tools is not None
            and None not in foundable_item.required_tools
        )
        if need_tool:
            for tool in foundable_item.required_tools:
                graph.add_edge(
                    tool.item_id,
                    foundable_item.item_id,
                    type="tool_requirement",
                    color=[0, 1, 1, 1],
                    index=0,
                )

        if hasattr(foundable_item, "items_dropped"):
            for dropped_item in foundable_item.items_dropped:
                if dropped_item != foundable_item:
                    graph.add_edge(
                        foundable_item.item_id,
                        dropped_item.item_id,
                        type="drop",
                        color=[0, 1, 0, 1],
                        index=0,
                    )
    return graph


def draw_requirements_graph(ax: Axes, graph: nx.DiGraph):
    """Draw the requirement graph on a given Axes.

    Args:
        ax: Axes to draw on.

    Return:
        The Axes with requirements_graph drawn on it.

    """
    compute_levels(graph)
    nodes_by_level = graph.graph["nodes_by_level"]
    pos = leveled_layout_energy(graph)
    compute_edges_color(graph)

    dashed_edges = [
        (u, v)
        for u, v, style in graph.edges(data="linestyle", default=None)
        if style == "dashed"
    ]

    # Dashed edges
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=dashed_edges,
        ax=ax,
        arrowsize=40,
        arrowstyle="->",
        style=(0, (8, 4)),
        edge_color=[graph.edges[u, v]["color"] for u, v in dashed_edges],
    )

    plain_edges = [
        (u, v)
        for u, v, style in graph.edges(data="linestyle", default=None)
        if style is None
    ]

    # Plain edges
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=plain_edges,
        ax=ax,
        arrowsize=20,
        arrowstyle="->",
        edge_color=[graph.edges[u, v]["color"] for u, v in plain_edges],
    )

    draw_networkx_nodes_images(graph, pos, ax=ax, img_zoom=0.3)

    # nx.draw_networkx_labels(
    #     graph, pos,
    #     ax=ax,
    #     font_color='black',
    #     font_size=6,
    #     labels=dict(graph.nodes(data='label'))
    # )

    # Create the legend patches
    legend_patches = [
        mpatches.Patch(facecolor="none", edgecolor="cyan", label="Tool"),
        mpatches.Patch(facecolor="none", edgecolor="green", label="Item (foundable)"),
        mpatches.Patch(facecolor="none", edgecolor="blue", label="Item"),
    ]
    legend_arrows = [
        mpatches.FancyArrow(
            0, 0, 1, 0, facecolor="cyan", edgecolor="none", label="Tool requirement"
        ),
        mpatches.FancyArrow(
            0, 0, 1, 0, facecolor="red", edgecolor="none", label="Craft"
        ),
    ]

    # Add zone_property legend only if there is any
    is_prop = [
        node_type == "zone_property" for _, node_type in graph.nodes(data="type")
    ]
    if any(is_prop):
        prop_legend = mpatches.Patch(
            facecolor="none", edgecolor="orange", label="Zone property"
        )
        legend_patches.append(prop_legend)

    # Add drop legend only if any edge is a drop
    is_drop = [edge_type == "drop" for _, _, edge_type in graph.edges(data="type")]
    if any(is_drop):
        drop_legend = mpatches.FancyArrow(
            0, 0, 1, 0, facecolor="green", edgecolor="none", label="Drop"
        )
        legend_arrows.append(drop_legend)

    # Draw the legend
    ax.legend(
        handles=legend_patches + legend_arrows,
        handler_map={
            # Patch arrows with fancy arrows in legend
            mpatches.FancyArrow: HandlerPatch(
                patch_func=lambda width, height, **kwargs: mpatches.FancyArrow(
                    0,
                    0.5 * height,
                    width,
                    0,
                    width=0.2 * height,
                    length_includes_head=True,
                    head_width=height,
                    overhang=0.5,
                )
            ),
        },
    )

    # Add Hierarchies numbers
    for level in nodes_by_level:
        level_poses = np.array([pos[node] for node in nodes_by_level[level]])
        mean_x = np.mean(level_poses[:, 0])
        if level == 0:
            ax.text(mean_x - 1, -0.07, "Depth", ha="left", va="center")
        ax.text(mean_x, -0.07, str(level), ha="center", va="center")
    return ax
