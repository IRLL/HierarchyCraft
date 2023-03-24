"""# Requirements

The HierarchyCraft package is meant to able the conception of arbitrary underlying hierarchial
structures in environments.

But of course, it's better to be able to manipulate and visualize those underlying hierarchies !

## Requirements graph

In HierarchyCraft, transformations allow to obtain items, to reach zones or to place items in zones.
Thus transformations are the links between the items and zones.

We can represent all those links in a multi-edged directed graph (or MultiDiGraph), where:

- nodes are either an 'item', a 'zone' or an 'item in zone'.
(See `hcraft.requirements.RequirementNode`)
- edges are indexed per transformation and per available zone
and directed from consumed 'item' or 'item in zone' or necessary 'zone'
to produced 'item' or 'item in zone' or destination 'zone'.
(See `hcraft.requirements.RequirementEdge`)

To represent the initial state of the world, we add a special '#Start' node
and edges with uniquely indexes from this '#Start' node to the start_zone and
to every 'item' in the start_items. Also we add a uniquely indexed edge
from every 'zone' to every 'item in zone' in the corresponding zone in start_zones_items.

## Requirements levels

Hierarchical levels can be computed from a requirements graph.
The 'START#' node is at level 0 then accessible nodes from the 'START#' node are level 1,
then accessible items from level 1 items are level 2, ... until all nodes have a level.

Nodes may be accessible by mutliple options (different transformations),
those options are represented by the indexes of edges.
To be attributed a level, a node needs at least an index where
all the predecessors of this node with this index have a level.
Then the node's level=1+min_over_indexes(max(predecessors_levels_by_index)).

See `hcraft.requirements.compute_levels` for implementation details.


## Collapsed acyclic requirements graph

Once the requirements graph nodes have a level, cycles in the graph can be broken
by removing edges from higher levels to lower levels.

We then obtain the collapsed acyclic requirements graph by removing duplicated edges.
This graph can be used to draw a simpler view of the requirements graph.
This graph is used to find relevant subtasks for any item or zone,
see `hcraft.purpose.RewardShaping.REQUIREMENTS_ACHIVEMENTS`.

# Example

```python
# Obtain the raw Networkx MultiDiGraph
graph = env.world.requirements.graph

# Plot the collapsed acyclic requirements graph
import matplotlib.pyplot as plt
_, ax = plt.subplots()
env.world.requirements.draw(ax)
plt.show()
```

For example, here is the underlying hierarchy of the toy environment MinicraftUnlock:
<img
    src="https://raw.githubusercontent.com/IRLL/HierarchyCraft/master/docs/images/requirements_graphs/MiniCraftUnlock.png"
width="90%"/>

"""

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Union

import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from hebg.graph import draw_networkx_nodes_images, get_nodes_by_level
from hebg.layouts.metabased import leveled_layout_energy
from matplotlib.axes import Axes
from matplotlib.legend_handler import HandlerPatch

from hcraft.render.utils import load_or_create_image

if TYPE_CHECKING:
    from hcraft.elements import Item, Stack, Zone
    from hcraft.transformation import Transformation
    from hcraft.world import World


class RequirementNode(Enum):
    """Node types in the requirements graph."""

    START = "start"
    ZONE = "zone"
    ITEM = "item"
    ZONE_ITEM = "zone_item"


class RequirementEdge(Enum):
    """Edge types in the requirements graph."""

    ZONE_REQUIRED = "zone_required"
    ITEM_REQUIRED = "item_required"
    ITEM_REQUIRED_IN_ZONE = "item_required_in_zone"
    START_ZONE = "start_zone"
    START_ITEM = "start_item"
    START_ITEM_IN_ZONE = "start_item_in_zone"


class RequirementTheme:
    """Defines the colors to draw requirements graph nodes and edges"""

    DEFAULT_COLORS = {
        "item": "red",
        "zone": "green",
        "zone_item": "blue",
        "item_required": "red",
        "zone_required": "green",
        "item_required_in_zone": "blue",
        "start_zone": "black",
        "start_item": "black",
        "start_item_in_zone": "black",
    }
    """Default colors"""

    def __init__(self, default_color: Any = "black", **kwargs) -> None:
        self.colors = self.DEFAULT_COLORS.copy()
        self.colors.update(kwargs)
        self.default_color = default_color

    def color(self, obj: Union[RequirementNode, RequirementEdge]) -> Any:
        """Give the themed color of the given object.

        Args:
            obj: Object to color (node or edge).

        Returns:
            Color of the object using this theme.
        """
        if not obj:
            return self.default_color
        return self.colors.get(obj.value, self.default_color)


class Requirements:
    def __init__(self, world: "World"):
        self.world = world
        self.graph = nx.MultiDiGraph()
        self._digraph: nx.DiGraph = None
        self._acydigraph: nx.DiGraph = None
        self._build()

    def draw(
        self,
        ax: Axes,
        theme: RequirementTheme = RequirementTheme(),
        layout: "RequirementsGraphLayout" = "level",
    ) -> None:
        """Draw the requirements graph on the given Axes.

        Args:
            ax: Matplotlib Axes to draw on.
            layout: Drawing layout. Defaults to "level".
        """
        draw_requirements_graph(
            ax, self, theme, resources_path=self.world.resources_path, layout=layout
        )

    @property
    def digraph(self) -> nx.DiGraph:
        """Collapsed DiGraph of requirements."""
        if self._digraph is not None:
            return self._digraph
        self._digraph = collapse_as_digraph(self.graph)
        return self._digraph

    @property
    def acydigraph(self) -> nx.DiGraph:
        """Collapsed leveled acyclic DiGraph of requirements."""
        if self._acydigraph is not None:
            return self._acydigraph
        self._acydigraph = break_cycles_through_level(self.digraph)
        return self._acydigraph

    @property
    def depth(self) -> int:
        """Depth of the requirements graph."""
        return self.graph.graph.get("depth")

    def _build(self) -> None:
        self._add_requirements_nodes(self.world)
        edge_index = self._add_start_edges(self.world)
        for transfo in self.world.transformations:
            if transfo.zones is not None:
                for zone in transfo.zones:
                    self._add_transformation_edges(transfo, edge_index, zone)
                    edge_index += 1
            else:
                self._add_transformation_edges(transfo, edge_index)
                edge_index += 1
        compute_levels(self.graph)

    def _add_requirements_nodes(self, world: "World") -> None:
        self._add_nodes(world.items, RequirementNode.ITEM)
        self._add_nodes(world.zones_items, RequirementNode.ZONE_ITEM)
        if len(world.zones) >= 1:
            self._add_nodes(world.zones, RequirementNode.ZONE)

    def _add_nodes(
        self, objs: List[Union["Item", "Zone"]], node_type: RequirementNode
    ) -> None:
        """Add colored nodes to the graph"""
        for obj in objs:
            self.graph.add_node(req_node_name(obj, node_type), obj=obj, type=node_type)

    def _add_transformation_edges(
        self,
        transfo: "Transformation",
        transfo_index: int,
        zone: Optional["Zone"] = None,
    ) -> None:
        """Add edges induced by a HierarchyCraft recipe."""
        zones = set() if zone is None else {zone}

        in_items = transfo.min_required("player")
        out_items = [
            item for item in transfo.production("player") if item not in in_items
        ]

        in_zone_items = transfo.min_required_zones_items
        out_zone_items = [
            item for item in transfo.produced_zones_items if item not in in_zone_items
        ]

        other_zones_items = {}
        if transfo.destination is not None:
            required_dest_stacks = transfo.get_changes("destination", "min")
            other_zones_items[transfo.destination] = required_dest_stacks

        required_zones_stacks = transfo.get_changes("zones", "min")
        if required_zones_stacks is not None:
            for other_zone, consumed_stacks in required_zones_stacks.items():
                other_zones_items[other_zone] = consumed_stacks

        for other_zone, other_zone_items in other_zones_items.items():
            # If we require items in other zone that are not here from the start,
            # it means that we have to be able to go there before we can use this transformation
            # or that we can add the items in the other zone from elsewhere.
            if not _available_in_zones_stacks(
                other_zone_items,
                other_zone,
                self.world.start_zones_items,
            ):
                alternative_transformations = [
                    alt_transfo
                    for alt_transfo in self.world.transformations
                    if alt_transfo.get_changes("zones", "add") is not None
                    and _available_in_zones_stacks(
                        other_zone_items,
                        other_zone,
                        alt_transfo.get_changes("zones", "add"),
                    )
                ]
                if len(alternative_transformations) == 1:
                    alt_transfo = alternative_transformations[0]
                    if alt_transfo.zones is None or not (
                        len(alt_transfo.zones) == 1
                        and alt_transfo.zones[0] == other_zone
                    ):
                        in_items |= alt_transfo.min_required("player")
                        in_zone_items |= alt_transfo.min_required_zones_items
                    else:
                        zones.add(other_zone)
                elif not alternative_transformations:
                    zones.add(other_zone)
                else:
                    raise NotImplementedError("A complex case, raise issue if needed")

        transfo_params = {
            "in_items": in_items,
            "in_zone_items": in_zone_items,
            "zones": zones,
            "index": transfo_index,
        }

        for out_item in out_items:
            node_name = req_node_name(out_item, RequirementNode.ITEM)
            self._add_crafts(out_node=node_name, **transfo_params)

        for out_zone_item in out_zone_items:
            node_name = req_node_name(out_zone_item, RequirementNode.ZONE_ITEM)
            self._add_crafts(out_node=node_name, **transfo_params)

        if transfo.destination is not None:
            node_name = req_node_name(transfo.destination, RequirementNode.ZONE)
            self._add_crafts(out_node=node_name, **transfo_params)

    def _add_crafts(
        self,
        in_items: Set["Item"],
        in_zone_items: Set["Item"],
        zones: Set["Zone"],
        out_node: str,
        index: int,
    ) -> None:
        for zone in zones:
            edge_type = RequirementEdge.ZONE_REQUIRED
            node_type = RequirementNode.ZONE
            self._add_obj_edge(out_node, edge_type, index, zone, node_type)
        for item in in_items:
            node_type = RequirementNode.ITEM
            edge_type = RequirementEdge.ITEM_REQUIRED
            self._add_obj_edge(out_node, edge_type, index, item, node_type)
        for item in in_zone_items:
            node_type = RequirementNode.ZONE_ITEM
            edge_type = RequirementEdge.ITEM_REQUIRED_IN_ZONE
            self._add_obj_edge(out_node, edge_type, index, item, node_type)

    def _add_obj_edge(
        self,
        end_node: str,
        edge_type: RequirementEdge,
        index: int,
        start_obj: Optional[Union["Zone", "Item"]] = None,
        start_type: Optional[RequirementNode] = None,
    ):
        start_name = req_node_name(start_obj, start_type)
        self.graph.add_edge(
            start_name,
            end_node,
            type=edge_type,
            key=index,
        )

    def _add_start_edges(self, world: "World") -> int:
        start_index = 0
        if world.start_zone is not None:
            edge_type = RequirementEdge.START_ZONE
            end_node = req_node_name(world.start_zone, RequirementNode.ZONE)
            self._add_obj_edge(
                end_node, edge_type, start_index, start_type=RequirementNode.START
            )
            start_index += 1
        for start_stack in world.start_items:
            edge_type = RequirementEdge.START_ITEM
            end_node = req_node_name(start_stack.item, RequirementNode.ZONE_ITEM)
            self._add_obj_edge(
                end_node, edge_type, start_index, start_type=RequirementNode.START
            )
            start_index += 1
        for zone, start_zone_items in world.start_zones_items.items():
            edge_type = RequirementEdge.START_ITEM_IN_ZONE
            start_type = RequirementNode.ZONE
            for start_zone_stack in start_zone_items:
                end_node = req_node_name(
                    start_zone_stack.item, RequirementNode.ZONE_ITEM
                )
                self._add_obj_edge(end_node, edge_type, start_index, zone, start_type)
                start_index += 1
        return start_index


def req_node_name(obj: Optional[Union["Item", "Zone"]], node_type: RequirementNode):
    """Get a unique node name for the requirements graph"""
    if node_type == RequirementNode.START:
        return "START#"
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

    all_nodes_have_level = True
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


def break_cycles_through_level(digraph: nx.DiGraph):
    """Break cycles in a leveled multidigraph by cutting edges from high to low levels."""
    acygraph = digraph.copy()
    nodes_level = acygraph.nodes(data="level", default=0)
    for pred, node in digraph.edges():
        if nodes_level[pred] >= nodes_level[node]:
            acygraph.remove_edge(pred, node)
    return acygraph


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


def _available_in_zones_stacks(
    stacks: Optional[List["Stack"]],
    zone: "Zone",
    zones_stacks: Dict["Zone", List["Stack"]],
) -> bool:
    """
    Args:
        stacks: List of stacks that should be available.
        zone: Zone where the stacks should be available.
        zones_stacks: Stacks present in each zone.

    Returns:
        True if the given stacks are available from the start. False otherwise.
    """
    if stacks is None:
        return True
    is_available: Dict["Stack", bool] = {}
    for consumed_stack in stacks:
        start_stacks = zones_stacks.get(zone, [])
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
    theme: RequirementTheme,
    resources_path: str,
    layout: RequirementsGraphLayout = "level",
):
    """Draw the requirement graph on a given Axes.

    Args:
        ax: Axes to draw on.

    Return:
        The Axes with requirements_graph drawn on it.

    """
    digraph = requirements.digraph

    layout = RequirementsGraphLayout(layout)
    if layout == RequirementsGraphLayout.LEVEL:
        pos = leveled_layout_energy(digraph)
    elif layout == RequirementsGraphLayout.SPRING:
        pos = nx.spring_layout(digraph)

    edges_colors = [
        theme.color(edge_type) for _, _, edge_type in digraph.edges(data="type")
    ]
    edges_alphas = [_compute_edge_alpha(*edge, digraph) for edge in digraph.edges()]
    # Plain edges
    nx.draw_networkx_edges(
        digraph,
        pos=pos,
        ax=ax,
        arrowsize=20,
        arrowstyle="->",
        edge_color=edges_colors,
        alpha=edges_alphas,
    )

    for node, node_data in digraph.nodes(data=True):
        node_obj = node_data.get("obj", None)
        if node_obj is not None:
            digraph.nodes[node]["color"] = theme.color(node_data["type"])
            image = load_or_create_image(node_obj, resources_path, bg_color=(0, 0, 0))
            digraph.nodes[node]["image"] = np.array(image)
    draw_networkx_nodes_images(digraph, pos, ax=ax, img_zoom=0.3)

    # Add legend for edges (if any for each type)
    legend_arrows = []
    for legend_edge_type in RequirementEdge:
        has_type = [
            edge_type == legend_edge_type.value
            for _, _, edge_type in digraph.edges(data="type")
        ]
        if any(has_type):
            legend_arrows.append(
                mpatches.FancyArrow(
                    *(0, 0, 1, 0),
                    facecolor=theme.color(legend_edge_type),
                    edgecolor="none",
                    label=str(legend_edge_type.value).capitalize(),
                )
            )

    # Add legend for nodes (if any for each type)
    legend_patches = []
    for legend_node_type in RequirementNode:
        has_type = [
            node_type == legend_node_type.value
            for _, node_type in digraph.nodes(data="type")
        ]
        if any(has_type):
            legend_patches.append(
                mpatches.Patch(
                    facecolor="none",
                    edgecolor=theme.color(legend_node_type),
                    label=str(legend_node_type.value).capitalize(),
                )
            )

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

    ax.set_axis_off()
    ax.margins(0, 0)

    # Add Hierarchies numbers
    if layout == "level":
        nodes_by_level: Dict[int, Any] = digraph.graph["nodes_by_level"]
        for level, level_nodes in nodes_by_level.items():
            level_poses = np.array([pos[node] for node in level_nodes])
            mean_x = np.mean(level_poses[:, 0])
            if level == 0:
                ax.text(mean_x - 1, -0.07, "Depth", ha="left", va="center")
            ax.text(mean_x, -0.07, str(level), ha="center", va="center")
    return ax


def _compute_edge_alpha(pred, _succ, graph: nx.DiGraph):
    alphas = [1, 1, 1, 1, 1, 0.5, 0.5, 0.5, 0.2, 0.2, 0.2]
    n_successors = len(list(graph.successors(pred)))
    alpha = 0.1
    if n_successors < len(alphas):
        alpha = alphas[n_successors - 1]
    return alpha
