from typing import TYPE_CHECKING, List

import numpy as np
import networkx as nx

import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
from matplotlib.axes import Axes

from hebg.graph import (
    compute_edges_color,
    compute_levels,
    draw_networkx_nodes_images,
)
from hebg.layouts.metabased import leveled_layout_energy

from crafting.world.items import Tool, Item
from crafting.render.utils import load_or_create_image

if TYPE_CHECKING:
    from crafting.world.recipes import Recipe
    from crafting.world.zones import Zone
    from crafting.world.world import World


def build_requirements_graph(world: "World") -> nx.DiGraph:
    """Build the world requirements graph.

    Returns:
        The world requirements graph as a networkx DiGraph.

    """
    graph = nx.DiGraph()
    _add_requirements_nodes(world, graph)
    _add_recipes_edges(world, graph)
    _add_findable_items_edges(world, graph)
    _add_zones_requirements_edges(world, graph)
    return graph


def _add_requirements_nodes(world: "World", graph: nx.DiGraph):
    _add_items_nodes(world, graph)
    _add_properties_nodes(world, graph)
    _add_zones_nodes(world, graph)


def _add_recipes_edges(world: "World", graph: nx.DiGraph):
    """Add recipes edges"""

    for recipe in world.recipes:
        _add_recipe_edges(graph, recipe)


def _add_findable_items_edges(world: "World", graph: nx.DiGraph):
    """Add required_tools and drops edges"""

    for foundable_item in world.foundable_items:

        need_tool = (
            foundable_item.required_tools is not None
            and None not in foundable_item.required_tools
        )
        if need_tool:
            _add_needed_tools_edges(
                graph, foundable_item, foundable_item.required_tools
            )

        zones_where_item_is = [
            zone for zone in world.zones if foundable_item in zone.items
        ]
        _add_needed_zone_edges(graph, foundable_item, zones_where_item_is, world.zones)

        if hasattr(foundable_item, "items_dropped"):
            _add_drop_item_edges(graph, foundable_item, foundable_item.items_dropped)


def _add_zones_requirements_edges(world: "World", graph: nx.DiGraph):
    """Add required_tools and required_properties edges"""
    for zone in world.zones:
        _add_required_tool_for_zone(graph, zone)
        _add_required_property_for_zone(graph, zone)
        _add_already_present_properties(graph, zone, world.recipes)


def _add_items_nodes(world: "World", graph: nx.DiGraph):
    """Add items nodes"""
    for item in world.items:

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


def _add_properties_nodes(world: "World", graph: nx.DiGraph):
    """Add zones properties nodes"""
    for i, prop in enumerate(world.zone_properties):
        graph.add_node(
            prop,
            type="zone_property",
            color="orange",
            prop_id=i,
            image=np.array(load_or_create_image(world, prop)),
            label=prop.capitalize(),
        )


def _add_zones_nodes(world: "World", graph: nx.DiGraph):
    """Add zones nodes (if more than the start zone)"""
    if len(world.zones) <= 1:
        return
    for zone in world.zones:
        graph.add_node(
            zone.name,
            type="zone",
            color="gray",
            zone_id=zone.zone_id,
            image=np.array(load_or_create_image(world, zone)),
            label=zone.name.capitalize(),
        )


def _add_recipe_edges(graph: nx.DiGraph, recipe: "Recipe"):
    """Add edges induced by a Crafting recipe."""
    in_items_ids = []
    if recipe.inputs is not None:
        in_items_ids = [stack.item_id for stack in recipe.inputs]

    out_items_ids = []
    if recipe.outputs is not None:
        out_items_ids = [stack.item_id for stack in recipe.outputs]

    in_props = []
    if recipe.needed_properties is not None:
        in_props = list(recipe.needed_properties.keys())

    out_props = []
    if recipe.needed_properties is not None:
        for prop, value in recipe.added_properties.items():
            if prop in in_props and recipe.needed_properties[prop] == value:
                continue
            if value:
                out_props.append(prop)

    for out_item in out_items_ids:
        _add_crafts(graph, in_items_ids + in_props, out_item)

    for out_prop in out_props:
        _add_crafts(graph, in_items_ids + in_props, out_prop)


def _add_crafts(graph: nx.DiGraph, in_nodes, out_node):
    for index, node in enumerate(in_nodes):
        graph.add_edge(
            node,
            out_node,
            type="craft",
            color=[1, 0, 0, 1],
            index=index + 1,
        )


def _add_needed_tools_edges(
    graph: nx.DiGraph, item: "Item", required_tools: List["Tool"]
):
    for tool in required_tools:
        graph.add_edge(
            tool.item_id,
            item.item_id,
            type="tool_requirement",
            color=[0, 1, 1, 1],
            index=0,
        )


def _add_needed_zone_edges(
    graph: nx.DiGraph,
    item: "Item",
    zones_where_item_is: List["Zone"],
    world_zones: List["Zone"],
):
    in_every_zone = zones_where_item_is == world_zones
    if not in_every_zone:
        for zone in zones_where_item_is:
            graph.add_edge(
                zone.name,
                item.item_id,
                type="findable_in_zone",
                color=[0.7, 0.7, 0.7, 1],
                index=1,
            )


def _add_drop_item_edges(
    graph: nx.DiGraph, item_searched: "Item", items_dropped: List["Item"]
):
    for dropped_item in items_dropped:
        if dropped_item == item_searched:
            continue
        graph.add_edge(
            item_searched.item_id,
            dropped_item.item_id,
            type="drop",
            color=[0, 1, 0, 1],
            index=0,
        )


def _add_required_tool_for_zone(graph: nx.DiGraph, zone: "Zone"):
    for required_tool in zone.required_tools:
        graph.add_edge(
            required_tool.item_id,
            zone.name,
            type="tool_requirement",
            color=[0, 1, 1, 1],
            index=0,
        )


def _add_required_property_for_zone(graph: nx.DiGraph, zone: "Zone"):
    for i, required_property in enumerate(zone.required_properties.keys()):
        graph.add_edge(
            required_property,
            zone.name,
            type="property_requirement",
            color=[0.7, 0.7, 0.7, 1],
            index=i + 1,
        )


def _add_already_present_properties(
    graph: nx.DiGraph, zone: "Zone", recipes: List["Recipe"]
):
    for present_property in zone.properties.keys():
        # If a property is craftable, we skip this.
        craft_outputs = []
        for recipe in recipes:
            craft_outputs += [
                prop for prop, value in recipe.added_properties.items() if value
            ]
        if present_property in craft_outputs:
            continue
        graph.add_edge(
            zone.name,
            present_property,
            type="present_zone_property",
            color=[0.7, 0.7, 0.7, 1],
            index=0,
        )


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
            *(0, 0, 1, 0),
            facecolor="cyan",
            edgecolor="none",
            label="Tool requirement",
        ),
        mpatches.FancyArrow(
            *(0, 0, 1, 0),
            facecolor="red",
            edgecolor="none",
            label="Craft",
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

    has_zone = [node_type == "zone" for _, node_type in graph.nodes(data="type")]
    if any(has_zone):
        zone_legend = mpatches.Patch(facecolor="none", edgecolor="gray", label="Zone")
        legend_patches.append(zone_legend)

    # Add drop legend only if any edge is a drop
    is_drop = [edge_type == "drop" for _, _, edge_type in graph.edges(data="type")]
    if any(is_drop):
        drop_legend = mpatches.FancyArrow(
            0, 0, 1, 0, facecolor="green", edgecolor="none", label="Drop"
        )
        legend_arrows.append(drop_legend)

    has_findable_in_zone = [
        edge_type == "findable_in_zone" for _, _, edge_type in graph.edges(data="type")
    ]
    if any(has_findable_in_zone):
        findable_in_zone_legend = mpatches.FancyArrow(
            *(0, 0, 1, 0),
            facecolor="gray",
            edgecolor="none",
            label="Item findable in zone",
        )
        legend_arrows.append(findable_in_zone_legend)

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
