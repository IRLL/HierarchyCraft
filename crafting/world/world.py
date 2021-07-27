# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" A World stiches together every non-player parts of the environment.

"""

from __future__ import annotations

from typing import List, Dict

import numpy as np
import networkx as nx

import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch

from option_graph.graph import compute_color, compute_levels, \
    leveled_layout, draw_networkx_nodes_images

from crafting.world.zones import Zone
from crafting.world.recipes import Recipe
from crafting.world.items import Item, Tool
from crafting.options.options import GetItem, ReachZone, Option

class World():

    """ A crafting World containing items, recipes and zones. """

    def __init__(self, items:List[Item], recipes:List[Recipe], zones:List[Zone],
            searchable_items:List[Item]=None, resources_path:str=None, font_path:str=None
        ):
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
        self.searchable_items = searchable_items if searchable_items is not None else items
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
        self.property_to_slot = {
            prop: i + self.n_items + self.n_zones
            for i, prop in enumerate(self.zone_properties)
        }
        self.n_zone_properties = len(self.zone_properties)

        self.n_actions = self.n_foundable_items + self.n_recipes + self.n_zones
        self.observation_size = self.n_items + self.n_zones + self.n_zone_properties

        self.resources_path = resources_path
        self.font_path = font_path

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

    def get_all_options(self)-> Dict[str, Option]:
        """ Return a dictionary of handcrafted options to get each item, zone and property. """
        all_options = {}

        for zone in self.zones:
            zone_option = ReachZone(zone, self)
            all_options[str(zone_option)] = zone_option

        for item in self.foundable_items:
            zones_id_needed = []
            for zone in self.zones:
                if item.item_id in zone.items:
                    zones_id_needed.append(zone.zone_id)

            items_needed = []
            if item.required_tools is not None :
                for tool in item.required_tools:
                    crafting_option = [(tool.item_id, 1)] if tool is not None else None
                    items_needed.append(crafting_option)

            if hasattr(item, 'items_dropped'):
                for dropped_item in item.items_dropped:
                    item_option = GetItem(
                        world=self,
                        item=dropped_item,
                        all_options=all_options,
                        items_needed=items_needed,
                        last_action=('get', item.item_id),
                        zones_id_needed=zones_id_needed,
                    )
            else:
                item_option = GetItem(
                    world=self,
                    item=item,
                    all_options=all_options,
                    items_needed=items_needed,
                    last_action=('get', item.item_id),
                    zones_id_needed=zones_id_needed,
                )
            all_options[str(item_option)] = item_option

        for recipe in self.recipes:

            items_needed = [
                [
                    (itemstack.item_id, itemstack.size)
                    for itemstack in recipe.inputs
                ]
            ]

            if recipe.outputs is not None:
                for output in recipe.outputs:
                    recipe_option = GetItem(
                        world=self,
                        item=output.item,
                        all_options=all_options,
                        items_needed=items_needed,
                        zones_properties_needed=recipe.needed_properties,
                        last_action=('craft', recipe.recipe_id),
                    )
                    all_options[str(recipe_option)] = recipe_option

            if recipe.added_properties is not None:
                for zone_property in recipe.added_properties:
                    zone_property_option = GetItem(
                        world=self,
                        item=zone_property,
                        all_options=all_options,
                        items_needed=items_needed,
                        zones_properties_needed=recipe.needed_properties,
                        last_action=('craft', recipe.recipe_id),
                    )
                    all_options[str(zone_property_option)] = zone_property_option

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
                image=self.get_image(item),
                item_id=item.item_id,
                label=item.name.capitalize()
            )

        # Add properties nodes
        for i, prop in enumerate(self.zone_properties):
            graph.add_node(
                prop,
                type="zone_property",
                color="orange",
                prop_id=i,
                image=self.get_image(prop),
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

            need_tool = foundable_item.required_tools is not None and \
                None not in foundable_item.required_tools
            if need_tool:
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

        compute_levels(graph, weak_edges_type=["tool_requirement"])
        return graph

    # pylint: disable=invalid-name
    def draw_requirements_graph(self, ax):
        """ Draw the requirement graph on a given Axes.

        Args:
            ax: Axes to draw on.

        Return:
            The Axes with requirements_graph drawn on it.

        """
        graph = self.get_requirements_graph()
        pos = leveled_layout(graph, max_iterations=2000, initial_temperature=10)
        nodes_by_level = graph.graph['nodes_by_level']
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
            arrowsize=20,
            arrowstyle="->",
            edge_color=[graph.edges[u, v]['color'] for u, v in plain_edges]
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
            mean_x = np.mean(level_poses[:, 0])
            if level == 0:
                ax.text(mean_x-1, -0.07, "Depth", ha='left', va='center')
            ax.text(mean_x, -0.07, str(level), ha='center', va='center')
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
