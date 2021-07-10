# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from typing import List, Dict, Union
from copy import deepcopy

import networkx as nx
import matplotlib.patches as mpatches
from matplotlib.axes import Axes
from matplotlib.legend_handler import HandlerPatch

from crafting.world.items import Item
from crafting.world.zones import Zone
from crafting.graph import compute_levels, option_layout, draw_networkx_nodes_images


class Option():

    """ Abstract class for options """

    def __init__(self, option_id) -> None:
        self.option_id = option_id
        self._graph = None

    def __call__(self, observations, greedy: bool=False):
        """ Use the option to get next actions.

        Args:
            observations: Observations of the environment.
            greedy: If true, the agent should act greedily.

        Returns:
            actions: Actions given by the option with current observations.
            option_done: True if the option is done, False otherwise.

        """
        raise NotImplementedError

    def interest(self, observations) -> float:
        raise NotImplementedError

    def build_graph(self) -> nx.DiGraph:
        raise NotImplementedError
    
    def draw_graph(self, ax):
        return draw_option_graph(self.graph, ax)

    @property
    def graph(self) -> nx.DiGraph:
        if self._graph is None:
            self._graph = self.build_graph()
        return self._graph

def _add_predecessors(graph, prev_checks, node, force_any=False):
    if len(prev_checks) > 1 or (force_any and len(prev_checks) > 0):
        for pred in prev_checks:
            graph.add_edge(pred, node, type='any', color='purple')
    elif len(prev_checks) == 1:
        graph.add_edge(prev_checks[0], node, type='conditional', color='green')

def _add_node_feature_condition(graph, node_name:str, image):
    graph.add_node(node_name, type='feature_check', color='blue', image=image)

def _add_node_option(graph, node_name:str, image):
    graph.add_node(node_name, type='option', color='orange', image=image)

def _add_node_action(graph, node_name:str, image):
    graph.add_node(node_name, type='action', color='red', image=image)

def _add_node_empty(graph, node_name:str):
    graph.add_node(node_name, type='empty', color='purple', image=None)


def draw_option_graph(graph, ax) -> Axes:
    if len(list(graph.nodes())) > 0:
        pos = option_layout(graph)

        draw_networkx_nodes_images(graph, pos, ax=ax, img_zoom=0.4)

        # nx.draw_networkx_labels(
        #     self.graph, pos,
        #     ax=ax,
        #     font_color='black',
        # )

        nx.draw_networkx_edges(
            graph, pos,
            ax=ax,
            arrowsize=20,
            arrowstyle="-|>",
            min_source_margin=30, min_target_margin=30,
            edge_color=[color for _, _, color in graph.edges(data='color')]
        )

        legend_patches = [
            mpatches.Patch(facecolor='none', edgecolor='blue', label='Feature condition'),
            mpatches.Patch(facecolor='none', edgecolor='orange', label='Option'),
            mpatches.Patch(facecolor='none', edgecolor='red', label='Action'),
        ]
        legend_arrows = [
            mpatches.FancyArrow(0, 0, 1, 0,
                facecolor='green', edgecolor='none', label='Condition (True)'),
            mpatches.FancyArrow(0, 0, 1, 0,
                facecolor='red', edgecolor='none', label='Condition (False)'),
            mpatches.FancyArrow(0, 0, 1, 0,
                facecolor='purple', edgecolor='none', label='Any'),
        ]

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

    return ax

class GoToZone(Option):

    """ Generic option for moving to a zone """

    def __init__(self, zone:Zone, world:"crafting.world.World"):
        super().__init__(f"Reach {str(zone)}")
        self.world = world
        self.zone = zone

    def build_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        node_name = f"Go to {self.zone}"
        zone_image = self.world.get_image(self.zone)
        _add_node_action(graph, node_name, zone_image)
        compute_levels(graph)
        return graph

    def __call__(self, observations, greedy: bool=False):
        actual_zone_id = self.world.zone_id_from_observation(observations)
        if actual_zone_id != self.zone.zone_id:
            return self.world.action('move', self.zone.zone_id), True
        return None, True

class GetItem(Option):

    """ Generic option for getting an item """

    def __init__(self, world:"crafting.world.World",
            item:Item,
            all_options: Dict[Union[int, str], Option],
            items_needed:List[List[tuple]],
            last_action: tuple,
            zones_id_needed=None, zones_properties_needed=None):

        super().__init__(f"Get {str(item)}")
        self.world = world
        self.item = item

        self.items_needed = items_needed
        if self.items_needed is None:
            self.items_needed = [[]]

        self.zones_id_needed = zones_id_needed
        if self.zones_id_needed is None:
            self.zones_id_needed = []

        self.zones_properties_needed = zones_properties_needed
        if self.zones_properties_needed is None:
            self.zones_properties_needed = []

        self.last_action = last_action
        self.all_options = all_options

    def gather_items(self, observation, items_id_in_search):
        if len(self.items_needed) == 0:
            return None
        action_for_craft_option = [None for _ in self.items_needed]

        for i, craft_option in enumerate(self.items_needed):
            for item_id, quantity_needed in craft_option:
                if action_for_craft_option[i] is None:
                    item_slot = self.world.item_id_to_slot[item_id]
                    inventory_content = observation[:self.world.n_items]
                    has_enought = inventory_content[item_slot] >= quantity_needed
                    if not has_enought:
                        if item_id not in items_id_in_search:
                            get_item_option = self.all_options[item_id]
                            action_for_craft_option[i], _ = get_item_option(
                                observation, items_id_in_search=items_id_in_search
                            )
                        else:
                            action_for_craft_option[i] = "Not Feasable"
            if action_for_craft_option[i] is None:
                break

        need_an_action = all(action is not None for action in action_for_craft_option)
        any_craft_option = len(self.items_needed[0]) > 0
        if any_craft_option and need_an_action:
            feasable_actions = [
                action for action in action_for_craft_option
                if action is not None and action != "Not Feasable"
            ]
            if len(feasable_actions) > 0:
                return feasable_actions[0]
            return "Not Feasable"
        return None

    def move_to_any_zone_needed(self, observation):
        action_for_zone = [None for _ in self.zones_id_needed]
        for i, zone_id in enumerate(self.zones_id_needed):
            zone = self.world.zone_from_id[zone_id]
            action_for_zone[i], _ = self.all_options[str(zone)](observation)

        need_an_action = all(action is not None for action in action_for_zone)
        if len(self.zones_id_needed) > 0 and need_an_action:
            feasable_actions = [
                action for action in action_for_zone
                if action is not None and action != "Not Feasable"
            ]
            if len(feasable_actions) > 0:
                return feasable_actions[0]
            return "Not Feasable"
        return None

    def get_zone_property(self, zone_property, observation):
        props = self.world.properties_from_observation(observation)
        if zone_property not in props:
            get_property_option = self.all_options[zone_property]
            return get_property_option(observation)[0]

    def __call__(self, observations, greedy: bool=False, items_id_in_search=None):
        if items_id_in_search is None:
            items_id_in_search = []
        else:
            items_id_in_search = deepcopy(items_id_in_search)
        if self.item is not None:
            items_id_in_search.append(self.item.item_id)

        action = self.gather_items(observations, items_id_in_search)
        if action is not None:
            return action, False

        action = self.move_to_any_zone_needed(observations)
        if action is not None:
            return action, False

        for zone_property in self.zones_properties_needed:
            action = self.get_zone_property(zone_property, observations)
            if action is not None:
                return action, False

        return self.world.action(*self.last_action), True

    def build_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        prev_checks = []

        empty_node = None
        if len(self.items_needed) > 1:
            empty_node = ""
            _add_node_empty(graph, empty_node)

        for craft_option in self.items_needed: # Any of Craft options
            prev_check_in_option = None
            for item_id, quantity in craft_option:
                item = self.world.item_from_id[item_id]
                check_item = f"Has {quantity} {item} ?"
                get_item = f"Get {item}"
                item_image = self.world.get_image(item)
                _add_node_feature_condition(graph, check_item, item_image)
                _add_node_option(graph, get_item, item_image)
                if prev_check_in_option is not None:
                    graph.add_edge(prev_check_in_option, check_item,
                        type='conditional', color='green')
                elif empty_node is not None:
                    graph.add_edge(empty_node, check_item, type='any', color='purple')
                graph.add_edge(check_item, get_item, type='conditional', color='red')
                prev_check_in_option = check_item
            if prev_check_in_option is not None:
                prev_checks.append(prev_check_in_option)

        prev_checks_zone = []
        for zone_id in self.zones_id_needed: # Any of the zones possibles
            zone = self.world.zone_from_id[zone_id]
            check_zone = f"Is in {zone} ?"
            option_zone = f"Reach {zone}"
            zone_image = self.world.get_image(zone)
            _add_node_feature_condition(graph, check_zone, zone_image)
            _add_node_option(graph, option_zone, zone_image)
            if len(prev_checks) > 0:
                _add_predecessors(graph, prev_checks, check_zone,
                    force_any=len(self.zones_id_needed) > 1)
            elif len(self.zones_id_needed) > 1:
                empty_node = ""
                _add_node_empty(graph, empty_node)
                graph.add_edge(empty_node, check_zone, type='any', color='purple')
            graph.add_edge(check_zone, option_zone, type='conditional', color='red')
            prev_checks_zone.append(check_zone)

        if len(prev_checks_zone) > 0:
            prev_checks = prev_checks_zone

        for prop in self.zones_properties_needed: # All properties needed
            check_prop = f"Zone {prop} ?"
            get_prop = f"Get {prop}"
            prop_image = self.world.get_image(prop)
            _add_node_feature_condition(graph, check_prop, prop_image)
            _add_node_option(graph, get_prop, prop_image)
            if len(prev_checks) > 0:
                _add_predecessors(graph, prev_checks, check_prop)
            graph.add_edge(check_prop, get_prop, type='conditional', color='red')
            prev_checks = [check_prop]

        # Add last action
        action_type, obj_id = self.last_action
        if action_type == 'get':
            obj = self.world.item_from_id[obj_id]
            last_node = f"Search {obj}"
        elif action_type == 'craft':
            recipe = self.world.recipes_from_id[obj_id]
            if recipe.outputs is not None:
                obj = recipe.outputs[0]
            else:
                obj = list(recipe.added_properties.keys())[0]
            last_node = f"Craft {recipe}"
        elif action_type == 'move':
            obj = self.world.zone_from_id[obj_id]
            last_node = f"Move to {obj}"
        else:
            raise ValueError(f'Unknowed action_type: {action_type}')

        action_image = self.world.get_image(obj)
        _add_node_action(graph, last_node, action_image)
        _add_predecessors(graph, prev_checks, last_node)
        compute_levels(graph)
        return graph

    def __str__(self):

        def _add_text(string, text, do_return=False):
            if do_return:
                string += "\n"
            string += text
            return string

        string = ""
        if self.item is not None:
            string = _add_text(string, f"{self.item}\n")

        do_return = False
        if len(self.items_needed) > 0 and len(self.items_needed[0]) > 0:
            string = _add_text(string, f"  Required {self.items_needed}", do_return)
            do_return = True
        if len(self.zones_id_needed) > 0:
            string = _add_text(string, f"  Zones {self.zones_id_needed}", do_return)
            do_return = True
        if len(self.zones_properties_needed) > 0:
            string = _add_text(string, f"  Properties {self.zones_properties_needed}", do_return)
            do_return = True
        string = _add_text(string, f"  Last action {self.last_action}", do_return)
        return string
