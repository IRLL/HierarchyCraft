# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" A World stiches together every non-player parts of the environment.

"""

from typing import List

import numpy as np
import networkx as nx

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch

from crafting.world.zones import Zone
from crafting.world.items import Item, Tool
from crafting.world.recipes import Recipe


class World():

    """ A crafting World containing items, recipes and zones. """

    def __init__(self, items:List[Item], recipes:List[Recipe], zones:List[Zone]):
        """ A crafting World containing items, recipes and zones.

        Args:
            items: List of world items.
            recipes: List of world recipes.
            zones: List of world zones.

        """
        # Zones
        self.zones = zones
        self.zone_from_id = {zone.zone_id: zone for zone in zones}
        self.zone_id_to_slot = {
            zone.zone_id: i for i, zone in enumerate(zones)
        }
        self.n_zones = len(zones)

        # Items
        self.items = items
        self.item_from_id = {item.item_id: item for item in items}
        self.item_id_to_slot = {
            item.item_id: i for i, item in enumerate(items)
        }
        self.n_items = len(items)

        self.tools = [item for item in self.items if isinstance(item, Tool)]

        # Foundable items
        self.foundable_items_ids = set()
        for zone in zones:
            for item in zone.items:
                self.foundable_items_ids.add(item.item_id)

        self.foundable_items = [
            self.item_from_id[item_id]
            for item_id in self.foundable_items_ids
        ]
        self.foundable_items_id_to_slot = {
            item.item_id: i
            for i, item in enumerate(self.foundable_items)
        }
        self.n_foundable_items = len(self.foundable_items)

        # Recipes
        self.recipes = recipes
        self.recipes_from_id = {recipe.recipe_id: recipe for recipe in recipes}
        self.recipes_id_to_slot = {
            recipe.recipe_id: i for i, recipe in enumerate(recipes)
        }
        self.n_recipes = len(recipes)

        # Zone properties
        self.zone_properties = set()
        for zone in zones:
            for prop in zone.properties:
                self.zone_properties.add(prop)

        for recipe in recipes:
            for prop in recipe.added_properties:
                self.zone_properties.add(prop)

        self.zone_properties = list(self.zone_properties)
        self.n_zone_properties = len(self.zone_properties)

        self.n_actions = self.n_foundable_items + self.n_recipes + self.n_zones

    def action(self, action_type:str, identification:int) -> int:
        """ Return the action_id from action_type and identification. """
        action_id = 0
        if action_type == 'get':
            action_id += self.foundable_items_id_to_slot[identification]
        elif action_type == 'craft':
            action_id = self.n_foundable_items
            action_id += self.recipes_id_to_slot[identification]
        elif action_type == 'move':
            action_id = self.n_foundable_items + self.n_recipes
            action_id += self.zone_id_to_slot[identification]
        return action_id

    def zone_id_from_observation(self, observation):
        """ Return the player zone from an observation. """
        n_items = self.n_items
        n_zones = self.n_zones
        one_hot_zones = observation[n_items:n_items + n_zones]
        zone_slot = np.where(one_hot_zones)[0][0]
        return self.zones[zone_slot].zone_id

    def get_requirements_graph(self) -> nx.DiGraph:
        """ Build the world requirements graph.

        Returns:
            The world requirements graph as a networkx DiGraph.

        """
        graph = nx.DiGraph()

        # Add items nodes
        for i, item in enumerate(self.items):
            color = "blue"
            if item in self.foundable_items:
                color = "green"
            elif isinstance(item, Tool):
                color = "cyan"
            graph.add_node(
                item.item_id,
                type="item",
                color=color,
                item_id=item.item_id,
                label=f"{item.name.capitalize()}({item.item_id})"
            )

        # Add properties nodes
        for i, prop in enumerate(self.zone_properties):
            graph.add_node(
                prop,
                type="zone_property",
                color="orange",
                prop_id=i,
                label=prop.capitalize()
            )

        # Add recipes edges
        def _add_crafts(in_nodes, out_node):
            for node in in_nodes:
                graph.add_edge(node, out_node, type="craft", color="red")

        for recipe in self.recipes:

            in_items_ids = []
            if recipe.inputs is not None:
                in_items_ids = [stack.item_id for stack in recipe.inputs]

            out_items_ids = []
            if recipe.outputs is not None:
                out_items_ids = [stack.item_id for stack in recipe.outputs]

            in_props = recipe.needed_properties if recipe.needed_properties is not None else []
            out_props = recipe.added_properties if recipe.needed_properties is not None else []

            for out_item in out_items_ids:
                _add_crafts(in_items_ids, out_item)
                _add_crafts(in_props, out_item)

            for out_prop in out_props:
                _add_crafts(in_items_ids, out_prop)
                _add_crafts(in_props, out_prop)

        # Add required_tools and drops edges
        for foundable_item in self.foundable_items:

            if foundable_item.required_tools is not None:
                for tool in foundable_item.required_tools:
                    graph.add_edge(
                        tool.item_id, foundable_item.item_id,
                        type="tool_requirement", color="cyan"
                    )

            if hasattr(foundable_item, "items_dropped"):
                for dropped_item in foundable_item.items_dropped:
                    if dropped_item != foundable_item:
                        graph.add_edge(
                            foundable_item.item_id, dropped_item.item_id,
                            type="drop", color="green"
                        )

        compute_levels(graph)
        return graph

    # pylint: disable=invalid-name
    def draw_requirements_graph(self, ax:plt.Axes):
        """ Draw the requirement graph on a given Axes.

        Args:
            ax: Axes to draw on.

        Return:
            The Axes with requirements_graph drawn on it.

        """
        graph = self.get_requirements_graph()
        pos, nodes_by_level = leveled_layout(graph)

        nx.draw_networkx_edges(
            graph, pos,
            ax=ax,
            arrowsize=40,
            alpha=0.6,
            arrowstyle="->",
            connectionstyle=None,
            edge_color=[color for _, _, color in graph.edges(data='color')]
        )

        nx.draw_networkx_nodes(
            graph, pos,
            ax=ax,
            alpha=0.3,
            node_color=[color for _, color in graph.nodes(data='color')],
            node_shape="H",
        )

        nx.draw_networkx_labels(
            graph, pos,
            ax=ax,
            labels=dict(graph.nodes(data='label'))
        )

        # Create the legend patches
        legend_patches = [
            mpatches.Patch(facecolor='none', edgecolor='cyan', label='Tool'),
            mpatches.Patch(facecolor='none', edgecolor='green', label='Item (foundable)'),
            mpatches.Patch(facecolor='none', edgecolor='blue', label='Item'),
        ]
        legend_arrows = [
            mpatches.FancyArrow(0, 0, 1, 0,
                facecolor='cyan', edgecolor='none', label='Tool requirement'),
            mpatches.FancyArrow(0, 0, 1, 0,
                facecolor='red', edgecolor='none', label='Craft'),
        ]

        # Add zone_property legend only if there is any
        is_prop = [node_type == 'zone_property' for _, node_type in graph.nodes(data='type')]
        if any(is_prop):
            prop_legend = mpatches.Patch(
                facecolor='none', edgecolor='orange',label='Zone property')
            legend_patches.append(prop_legend)

        # Add drop legend only if any edge is a drop
        is_drop = [edge_type == 'drop' for _, _, edge_type in graph.edges(data='type')]
        if any(is_drop):
            drop_legend = mpatches.FancyArrow(0, 0, 1, 0,
                facecolor='green', edgecolor='none', label='Drop')
            legend_arrows.append(drop_legend)

        # Draw the legend
        ax.legend(
            handles=legend_patches + legend_arrows,
            handler_map={
                # Patch arrows with fancy arrows in legend
                mpatches.FancyArrow : HandlerPatch(
                    patch_func=lambda width, height, **kwargs:mpatches.FancyArrow(
                        0, 0.5*height, width, 0, width=0.2*height,
                        length_includes_head=True, head_width=height, overhang=0.5
                    )
                ),

            }
        )

        # Add Hierarchies numbers
        for level in nodes_by_level:
            level_poses = np.array([pos[node] for node in nodes_by_level[level]])
            min_x = np.min(level_poses[:, 0])
            mean_y = np.mean(level_poses[:, 1])
            ax.text(min_x-0.75, mean_y, str(level), ha='right', va='center')
        return ax

    def __str__(self):
        world_str = "\nItems"
        for item in self.items:
            requitements_txt = ""
            if item.required_tools is not None:
                requitements_txt = f"<- {item.required_tools}"
            world_str += f"\n  {item}{requitements_txt}"

        world_str += "\nZones"
        for zone in self.zones:
            world_str += "\n  " + repr(zone)

        world_str += "\nRecipes"
        for recipe in self.recipes:
            world_str += "\n  " + str(recipe)

        return world_str


def compute_levels(graph:nx.DiGraph, weak_edges_type:List[str]=("tool_requirement",)):
    """ Compute the hierachical levels of all DiGraph nodes given some weak_edges.

    Adds the attribute 'level' for each node in the given graph.

    Args:
        graph: A networkx DiGraph.
        weak_edges_type: List of weak edges types (only the min level of those will be considered).
            Require edges to have the attribute 'type'.

    """

    def _compute_level_dependencies(graph, node, predecessors):
        strong_dependencies = [0]
        weak_dependencies = []
        incomplete = False
        for pred in predecessors:
            try:
                pred_level = graph.nodes[pred]['level']
                if graph.edges[pred, node]['type'] in weak_edges_type:
                    weak_dependencies.append(pred_level)
                else:
                    strong_dependencies.append(pred_level)
            except KeyError:
                if graph.edges[pred, node]['type'] not in weak_edges_type:
                    incomplete = True
        dependencies = strong_dependencies
        if len(weak_dependencies) > 0:
            dependencies += [min(weak_dependencies)]
        return 1 + max(dependencies), incomplete

    all_nodes_have_level = False
    while not all_nodes_have_level:
        all_nodes_have_level = True
        for node in graph.nodes():
            predecessors = list(graph.predecessors(node))
            if len(predecessors) == 0:
                level = 0
            else:
                level, incomplete = _compute_level_dependencies(graph, node, predecessors)
                if incomplete:
                    all_nodes_have_level = False
            if 'level' in graph.nodes[node] and graph.nodes[node]['level'] != level:
                all_nodes_have_level = False

            graph.nodes[node]['level'] = level

# pylint: disable=protected-access
def leveled_layout(graph:nx.DiGraph, center=None):
    """ Compute positions for a levelled DiGraph.

    Requires each node to have a 'level' attribute.

    Args:
        graph: A networkx DiGraph.
        center: Center of the graph layout.

    """
    graph, center = nx.drawing.layout._process_params(graph, center, dim=2)

    nodes_by_level = {}
    for node, node_data in graph.nodes(data=True):
        level = node_data['level']
        try:
            nodes_by_level[level].append(node)
        except KeyError:
            nodes_by_level[level] = [node]

    pos = {}
    for level in nodes_by_level:
        for i, node in enumerate(nodes_by_level[level]):
            pos[node] = [i, -level]

    return pos, nodes_by_level
