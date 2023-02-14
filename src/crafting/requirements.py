"""# Requirements

The crafting package is meant to able the conception of arbitrary underlying hierarchial
structures in environments.

But of course, it's better to be able to manipulate and visualize those underlying hierachies !

## Requirements graph

In Crafting, transformations allow to obtain items, to reach zones or to place items in zones.
Thus transformations are the links between the items and zones.

We can represent all those links in a multi-edged directed graph (or MultiDiGraph), where:

- nodes are either an 'item', a 'zone' or an 'item in zone'.
(See `crafting.requirements.RequirementNode`)
- edges have are indexed per transformation and per available zone
and directed from consumed 'item' or 'item in zone' or necessary 'zone'
to produced 'item' or 'item in zone' or destination 'zone'.

To represent the initial state of the world, we add a special '#Start' node
and edges with unique negative indexes from this '#Start' node to the start_zone,
to every 'item' in the start_items
and to every 'item in zone' in the start_zones_items.

## Requirements levels



## Collapsed acyclic requirements graph 



# Example

```python
from crafting.examples import MineCraftingEnv
env = MineCraftingEnv()

# Obtain the raw Networkx MultiDiGraph
graph = env.requirements.graph 

# Plot the simplified requirements graph
import matplotlib.pyplot as plt
_, ax = plt.subplots()
env.requirements.draw(ax)
plt.show()
```

![MineCrafting hierarchy](../../docs/images/minecrafting_crafts_hierarchy.png)

"""

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from hebg.graph import draw_networkx_nodes_images, get_nodes_by_level
from hebg.layouts.metabased import leveled_layout_energy
from matplotlib.axes import Axes
from matplotlib.legend_handler import HandlerPatch

from crafting.render.utils import load_or_create_image
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone, World


class RequirementNode(Enum):
    """Node types in the requirements graph."""

    ITEM = "item"
    ZONE = "zone"
    ZONE_ITEM = "zone_item"


NODE_COLOR_BY_TYPE: Dict[RequirementNode, str] = {
    RequirementNode.ITEM: "blue",
    RequirementNode.ZONE: "green",
    RequirementNode.ZONE_ITEM: "cyan",
}


class Requirements:
    def __init__(self, world: World, resources_path: str):
        self.world = world
        self.graph = nx.MultiDiGraph()
        self._digraph: nx.DiGraph = None
        self._build(resources_path)

    def draw(self, ax: Axes, layout: "RequirementsGraphLayout" = "level") -> None:
        """Draw the requirements graph on the given Axes.

        Args:
            ax: Matplotlib Axes to draw on.
            layout: Drawing layout. Defaults to "level".
        """
        draw_requirements_graph(ax, self, layout=layout)

    @property
    def digraph(self) -> nx.DiGraph:
        """Collapsed leveleld acyclic DiGraph of requirements."""
        if self._digraph is not None:
            return self._digraph
        compute_levels(self.graph)
        acyclic_graph = break_cycles_through_level(self.graph)
        self._digraph = collapse_as_digraph(acyclic_graph)
        return self._digraph

    def _build(self, resources_path: str) -> None:
        self._add_requirements_nodes(self.world, resources_path)
        edge_index = self._add_start_edges(self.world)
        for transfo in self.world.transformations:
            if transfo.zones is not None:
                for zone in transfo.zones:
                    self._add_transformation_edges(transfo, edge_index, zone)
                    edge_index += 1
            else:
                self._add_transformation_edges(transfo, edge_index)
                edge_index += 1

    def _add_requirements_nodes(
        self,
        world: "World",
        resources_path: str,
    ) -> None:
        self._add_nodes(world.items, RequirementNode.ITEM, resources_path)
        self._add_nodes(world.zones_items, RequirementNode.ZONE_ITEM, resources_path)
        if len(world.zones) >= 1:
            self._add_nodes(world.zones, RequirementNode.ZONE, resources_path)

    def _add_nodes(
        self,
        objs: List[Union[Item, Zone]],
        node_type: RequirementNode,
        resources_path: str,
    ) -> None:
        """Add colored nodes to the graph"""
        for obj in objs:
            self.graph.add_node(
                req_node_name(obj, node_type),
                obj=obj,
                type=node_type.value,
                color=NODE_COLOR_BY_TYPE[node_type],
                image=np.array(load_or_create_image(obj, resources_path)),
                label=obj.name.capitalize(),
            )

    def _add_transformation_edges(
        self,
        transfo: "Transformation",
        transfo_index: int,
        zone: Optional[Zone] = None,
    ) -> None:
        """Add edges induced by a Crafting recipe."""
        zones = [] if zone is None else [zone]

        in_items = transfo.consumed_items
        out_items = [item for item in transfo.produced_items if item not in in_items]

        in_zone_items = (
            transfo.consumed_zones_items + transfo.consumed_destination_items
        )
        out_zone_items = [
            item for item in transfo.produced_zones_items if item not in in_zone_items
        ]

        destinations = []
        if transfo.destination is not None:
            destinations = [transfo.destination]
            # If we require items in destination that are not here from the start,
            # it means that we have to be able to go there before we can use this transformation.
            if not _available_from_start(
                transfo.removed_destination_items,
                transfo.destination,
                self.world.start_zones_items,
            ):
                zones.append(transfo.destination)

        transfo_params = {
            "in_items": in_items,
            "in_zone_items": in_zone_items,
            "zones": zones,
            "transfo": transfo,
            "index": transfo_index,
        }

        for out_item in out_items:
            node_name = req_node_name(out_item, RequirementNode.ITEM)
            self._add_crafts(out_node=node_name, **transfo_params)

        for out_zone_item in out_zone_items:
            node_name = req_node_name(out_zone_item, RequirementNode.ZONE_ITEM)
            self._add_crafts(out_node=node_name, **transfo_params)

        for destination in destinations:
            node_name = req_node_name(destination, RequirementNode.ZONE)
            self._add_crafts(out_node=node_name, **transfo_params)

    def _add_crafts(
        self,
        in_items: List[Item],
        in_zone_items: List[Item],
        zones: List[Zone],
        out_node: str,
        transfo: Transformation,
        index: int,
    ) -> None:
        for zone in zones:
            self.graph.add_edge(
                req_node_name(zone, RequirementNode.ZONE),
                out_node,
                type="zone_required",
                color=[0, 1, 0, 1],
                key=index,
            )
        for node in set(in_items):
            self.graph.add_edge(
                req_node_name(node, RequirementNode.ITEM),
                out_node,
                type="item_needed",
                color=[1, 0, 0, 1],
                transformation=transfo,
                key=index,
            )
        for node in set(in_zone_items):
            self.graph.add_edge(
                req_node_name(node, RequirementNode.ZONE_ITEM),
                out_node,
                type="zone_item_needed",
                color=[0.2, 1, 0.2, 1],
                key=index,
            )

    def _add_start_edges(self, world: "World") -> int:
        start_index = 0
        if world.start_zone is not None:
            self.graph.add_edge(
                "#START",
                req_node_name(world.start_zone, RequirementNode.ZONE),
                key=start_index,
                type="start_zone",
                color=[0, 1, 0, 1],
            )
            start_index += 1
        for start_itemstack in world.start_items:
            self.graph.add_edge(
                "#START",
                req_node_name(start_itemstack.item, RequirementNode.ZONE_ITEM),
                key=start_index,
                type="start_item",
                color=[0, 1, 0, 1],
            )
            start_index += 1
        for zone, start_zone_items in world.start_zones_items.items():
            for start_zone_itemstack in start_zone_items:
                self.graph.add_edge(
                    req_node_name(zone, RequirementNode.ZONE),
                    req_node_name(start_zone_itemstack.item, RequirementNode.ZONE_ITEM),
                    key=start_index,
                    type="start_zone_item",
                    color=[0, 1, 0, 1],
                )
                start_index += 1
        return start_index


def req_node_name(obj: Union[Item, Zone], node_type: RequirementNode):
    """Get a unique node name for the requirements graph"""
    name = obj.name
    if node_type == RequirementNode.ZONE_ITEM:
        name = f"{name} in zone"
    return node_type.value + "#" + name


def compute_levels(graph: Requirements):
    """Compute the hierachical levels of a RequirementsGraph.

    Adds the attribute 'level' to each node in the given graph.
    Adds the attribute 'nodes_by_level' to the given graph.
    Adds the attribute 'depth' to the given graph.

    Args:
        graph: A RequirementsGraph.

    Returns:
        Dictionary of nodes by level.

    """

    def _compute_level_dependencies(graph: nx.MultiDiGraph, node):
        predecessors = list(graph.predecessors(node))
        if len(predecessors) == 0:
            graph.nodes[node]["level"] = 0
            return True
        if "level" in graph.nodes[node]:
            return True

        pred_level_by_key = {}
        for pred, _node, key in graph.in_edges(node, keys=True):
            pred_level = graph.nodes[pred].get("level", None)
            if key not in pred_level_by_key:
                pred_level_by_key[key] = []
            pred_level_by_key[key].append(pred_level)

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


def break_cycles_through_level(multidigraph: nx.MultiDiGraph):
    """Break cycles in a leveled multidigraph by cutting edges from high to low levels."""
    acyclical_multidigraph = multidigraph.copy()
    nodes_level = acyclical_multidigraph.nodes(data="level", default=0)
    for pred, node, key in multidigraph.edges(keys=True):
        if nodes_level[pred] >= nodes_level[node]:
            acyclical_multidigraph.remove_edge(pred, node, key)
    return acyclical_multidigraph


def collapse_as_digraph(multidigraph: nx.MultiDiGraph) -> nx.DiGraph:
    """Create a collapsed DiGraph from a MultiDiGraph by removing duplicated edges."""
    digraph = nx.DiGraph()
    digraph.graph = multidigraph.graph
    for node, data in multidigraph.nodes(data=True):
        digraph.add_node(node, **data)
    for pred, node, key, data in multidigraph.edges(keys=True, data=True):
        if not digraph.has_edge(pred, node):
            digraph.add_edge(pred, node, keys=[], **data)
        digraph.edges[pred, node]["keys"].append(key)
    return digraph


def _available_from_start(
    stacks: Optional[List[ItemStack]],
    zone: Zone,
    start_zones_stacks: Dict[Zone, List[ItemStack]],
) -> bool:
    """
    Args:
        stacks: List of stacks that should be available.
        zone: Zone where the stacks should be available.
        start_zones_stacks: Stacks present in each zone from the start.

    Returns:
        True if the given stacks are available from the start. False otherwise.
    """
    if stacks is None:
        return True
    is_available: Dict[ItemStack, bool] = {}
    for consumed_stack in stacks:
        start_stacks = start_zones_stacks.get(zone, [])
        for start_stack in start_stacks:
            if start_stack.item != consumed_stack.item:
                continue
            if start_stack.quantity >= consumed_stack.quantity:
                is_available[consumed_stack] = True
        if consumed_stack not in is_available:
            is_available[consumed_stack] = False
    return all(is_available.values())


class RequirementsGraphLayout(Enum):
    LEVEL = "level"
    """Layout using requirement level and a metaheuristic."""
    SPRING = "spring"
    """Classic spring layout."""


def draw_requirements_graph(
    ax: Axes,
    requirements: Requirements,
    layout: RequirementsGraphLayout = "level",
):
    """Draw the requirement graph on a given Axes.

    Args:
        ax: Axes to draw on.

    Return:
        The Axes with requirements_graph drawn on it.

    """
    digraph = requirements.digraph
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
    for leg_node_type in RequirementNode:
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
