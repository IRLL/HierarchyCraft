# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" A World stiches together every non-player parts of the environment.

"""

from typing import List
from copy import deepcopy

import numpy as np
import networkx as nx

import matplotlib.pyplot as plt
plt.style.use('dark_background')
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch

from crafting.world.zones import Zone
from crafting.world.items import Item, Tool
from crafting.world.recipes import Recipe
from crafting.option import GetItem, GoToZone


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

        self.zone_properties = np.array(list(self.zone_properties))
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

    def action_from_id(self, action_id:int) -> str:
        """ Describe the action_id effects. """
        offset = 0
        if action_id < self.n_foundable_items:
            action_type = 'get'
            object_concerned = self.foundable_items[action_id]
        elif 0 <= action_id - self.n_foundable_items < self.n_recipes:
            offset = self.n_foundable_items
            action_type = 'craft'
            object_concerned = self.recipes[action_id - offset]
        elif action_id >= self.n_foundable_items + self.n_recipes:
            action_type = 'move'
            offset = self.n_foundable_items + self.n_recipes
            object_concerned = self.zones[action_id - offset]
        return f"{action_type.capitalize()} {object_concerned}"

    def zone_id_from_observation(self, observation):
        """ Return the player zone from an observation. """
        one_hot_zones = observation[self.n_items:self.n_items + self.n_zones]
        zone_slot = np.where(one_hot_zones)[0][0]
        return self.zones[zone_slot].zone_id

    def properties_from_observation(self, observation):
        """ Return the zone proprietes from an observation. """
        one_hot_props = observation[self.n_items + self.n_zones:]
        props_slot = np.where(one_hot_props)
        return self.zone_properties[props_slot]

    def get_all_options(self):
        all_options = {}

        for zone in self.zones:
            all_options[str(zone)] = GoToZone(zone, self)

        for item in self.foundable_items:
            zones_id_needed = []
            for zone in self.zones:
                if item.item_id in zone.items:
                    zones_id_needed.append(zone.zone_id)

            items_needed = []
            if item.required_tools is not None:
                for tool in item.required_tools:
                    if tool.item_id == 0:
                        crafting_option = []
                    else:
                        crafting_option = [(tool.item_id, 1)]
                    items_needed.append(crafting_option)

            if hasattr(item, 'items_dropped'):
                for dropped_item in item.items_dropped:
                    all_options[dropped_item.item_id] = GetItem(
                        world=self,
                        item=dropped_item,
                        all_options=all_options,
                        items_needed=items_needed,
                        last_action=('get', item.item_id),
                        zones_id_needed=zones_id_needed,
                    )
            else:
                all_options[item.item_id] = GetItem(
                    world=self,
                    item=item,
                    all_options=all_options,
                    items_needed=items_needed,
                    last_action=('get', item.item_id),
                    zones_id_needed=zones_id_needed,
                )

        for recipe in self.recipes:

            items_needed = [
                [
                    (itemstack.item_id, itemstack.size)
                    for itemstack in recipe.inputs
                ]
            ]

            if recipe.outputs is not None:
                for output in recipe.outputs:
                    all_options[output.item.item_id] = GetItem(
                        world=self,
                        item=output.item,
                        all_options=all_options,
                        items_needed=items_needed,
                        zones_properties_needed=recipe.needed_properties,
                        last_action=('craft', recipe.recipe_id),
                    )

            if recipe.added_properties is not None:
                for zone_property in recipe.added_properties:
                    all_options[zone_property] = GetItem(
                        world=self,
                        item=None,
                        all_options=all_options,
                        items_needed=items_needed,
                        zones_properties_needed=recipe.needed_properties,
                        last_action=('craft', recipe.recipe_id),
                    )

        return all_options

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
                graph.add_edge(node, out_node, type="craft", color=[1, 0, 0, 1])

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
                        type="tool_requirement", color=[0, 1, 1, 1]
                    )

            if hasattr(foundable_item, "items_dropped"):
                for dropped_item in foundable_item.items_dropped:
                    if dropped_item != foundable_item:
                        graph.add_edge(
                            foundable_item.item_id, dropped_item.item_id,
                            type="drop", color=[0, 1, 0, 1]
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
        compute_color(graph)

        dashed_edges = [
            (u, v)
            for u, v, style in graph.edges(data='linestyle', default=None)
            if style == 'dashed'
        ]

        # Dashed edges
        nx.draw_networkx_edges(
            graph, pos,
            edgelist=dashed_edges,
            ax=ax,
            arrowsize=40,
            arrowstyle="->",
            style=(0, (8, 4)),
            edge_color=[graph.edges[u, v]['color'] for u, v in dashed_edges]
        )

        plain_edges = [
            (u, v)
            for u, v, style in graph.edges(data='linestyle', default=None)
            if style is None
        ]

        # Plain edges
        nx.draw_networkx_edges(
            graph, pos,
            edgelist=plain_edges,
            ax=ax,
            arrowsize=40,
            arrowstyle="->",
            edge_color=[graph.edges[u, v]['color'] for u, v in plain_edges]
        )

        nx.draw_networkx_nodes(
            graph, pos,
            ax=ax,
            alpha=0.8,
            node_color=[color for _, color in graph.nodes(data='color')],
            node_shape="H",
        )

        nx.draw_networkx_labels(
            graph, pos,
            ax=ax,
            font_color='white',
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
            mean_y = np.mean(level_poses[:, 1])
            ax.text(-0.15, mean_y, str(level), ha='right', va='center')
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


def compute_color(graph:nx.DiGraph):
    alphas = [1, 1, 0.9, 0.8, 0.7, 0.5, 0.4, 0.3]
    for node in graph.nodes():
        successors = list(graph.successors(node))
        for succ in successors:
            alpha = 0.2
            if graph.nodes[node]['level'] < graph.nodes[succ]['level']:
                if len(successors) < len(alphas):
                    alpha = alphas[len(successors)-1]
            else:
                graph.edges[node, succ]['linestyle'] = "dashed"
            if isinstance(graph.edges[node, succ]['color'], list):
                graph.edges[node, succ]['color'][3] = alpha

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
    step_size = 1 / max(len(nodes_by_level[level]) for level in nodes_by_level)
    spacing = np.arange(0, 1, step=step_size)
    for level in nodes_by_level:
        n_nodes_in_level = len(nodes_by_level[level])
        if n_nodes_in_level > 1:
            positions = np.linspace(0, len(spacing)-1, n_nodes_in_level,
                endpoint=True, dtype=np.int32)
            positions = spacing[positions]
        else:
            positions = [spacing[(len(spacing)-1)//2]]

        for i, node in enumerate(nodes_by_level[level]):
            pos[node] = [positions[i], -level]

    def energy(pos, nodes_by_level, nodes_strenght=1, edges_strenght=2):

        def dist(x, y):
            x_arr, y_arr = np.array(x), np.array(y)
            return np.linalg.norm(x_arr-y_arr)

        energy = 0
        for level in nodes_by_level:
            for node in nodes_by_level[level]:  
                energy += nodes_strenght * sum(
                    np.square(dist(pos[node], pos[n]))
                    for n in nodes_by_level[level] if n != node
                )
                energy -= sum(
                    edges_strenght \
                        # *graph.edges[pred, node]['color'][3]\
                        /abs(graph.nodes[node]['level'] - graph.nodes[pred]['level'])\
                        /max(1e-6, dist(pos[node], pos[pred]))
                    for pred in graph.predecessors(node)
                )
                energy -= sum(
                    edges_strenght \
                        # *graph.edges[node, succ]['color'][3]\
                        /abs(graph.nodes[node]['level'] - graph.nodes[succ]['level'])\
                        /max(1e-6, dist(pos[node], pos[succ]))
                    for succ in graph.successors(node)
                )
        return energy

    def neighbor(pos, step_size):
        pos_copy = deepcopy(pos)
        choosen_node = np.random.choice(list(pos_copy.keys()))
        try:
            choosen_node = int(choosen_node)
        except ValueError:
            pass
        x, y = pos_copy[choosen_node][0], pos_copy[choosen_node][1]

        if x <= 0:
            sign = 1
        elif x >= 1:
            sign = -1
        else:
            sign = np.random.choice((-1, 1))

        new_pos = [x + sign * step_size, y]

        for n in pos:
            if n != choosen_node and np.all(np.isclose(new_pos, pos_copy[n])):
                pos_copy[choosen_node], pos_copy[n] = pos_copy[n], pos_copy[choosen_node]
                return pos_copy

        pos_copy[choosen_node] = new_pos
        return pos_copy

    def prob_keep(temperature, delta_e, kb=1):
        return min(1, np.exp(delta_e/kb/temperature))

    max_iterations = 1000
    max_iters_without_new = 100
    iters_without_new = 0
    boltzmann_factor = 50
    initial_temperature = 0.1
    energy_pos = energy(pos, nodes_by_level)
    for k in range(max_iterations):
        new_pos = neighbor(pos, step_size)
        new_e = energy(new_pos, nodes_by_level)
        temperature = initial_temperature/(k+1)
        iters_without_new += 1
        prob = prob_keep(temperature, energy_pos - new_e, boltzmann_factor)
        if np.random.random() < prob:
            print(f"{k}\t({prob:.0%})\t{energy_pos:.2f}->{new_e:.2f}", end='\r')
            pos, energy_pos = new_pos, new_e
            iters_without_new = 0

        if iters_without_new >= max_iters_without_new:
            break

    return pos, nodes_by_level
