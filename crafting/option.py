# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for handcrafted options (with graph) in any Crafting environment. """

from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Union
from copy import deepcopy

from option_graph import Option, OptionGraph

from crafting.world.items import Item
from crafting.render.utils import load_image
if TYPE_CHECKING:
    from crafting.world.zones import Zone
    from crafting.world.world import World


class GoToZone(Option):

    """ Generic option for moving to a zone """

    def __init__(self, zone:Zone, world:World):
        super().__init__(f"Reach {str(zone)}")
        self.world = world
        self.zone = zone

    def build_graph(self) -> OptionGraph:
        graph = OptionGraph()
        node_name = f"Go to {self.zone}"
        zone_image = load_image(self.world, self.zone)
        graph.add_node_action(node_name, zone_image)
        return graph

    def __call__(self, observations, greedy: bool=False):
        actual_zone_id = self.world.zone_id_from_observation(observations)
        if actual_zone_id != self.zone.zone_id:
            return self.world.action('move', self.zone.zone_id), True
        return None, True

class GetItem(Option):

    """ Generic option for getting an item """

    def __init__(self, world:World,
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
            if craft_option is None:
                return None
            for item_id, quantity_needed in craft_option:
                if action_for_craft_option[i] is None:
                    item = self.world.item_from_id[item_id]
                    item_slot = self.world.item_id_to_slot[item_id]
                    inventory_content = observation[:self.world.n_items]
                    has_enought = inventory_content[item_slot] >= quantity_needed
                    if not has_enought:
                        if item_id not in items_id_in_search:
                            get_item_option = self.all_options[f"Get {item}"]
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
            action_for_zone[i], _ = self.all_options[f"Reach {zone}"](observation)

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
            get_property_option = self.all_options[f"Get {zone_property}"]
            return get_property_option(observation)[0]

    def __call__(self, observations, greedy: bool=False, items_id_in_search=None):
        if items_id_in_search is None:
            items_id_in_search = []
        else:
            items_id_in_search = deepcopy(items_id_in_search)
        if self.item is not None:
            if isinstance(self.item, Item):
                items_id_in_search.append(self.item.item_id)
            else:
                items_id_in_search.append(self.item)

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

    def build_graph(self) -> OptionGraph:
        graph = OptionGraph()
        prev_checks = []

        for craft_option in self.items_needed: # Any of Craft options
            if craft_option is not None:
                prev_check_in_option = None
                for item_id, quantity in craft_option:
                    item = self.world.item_from_id[item_id]
                    check_item = f"Has {quantity} {item}?"
                    get_item = f"Get {item}"

                    conditon_text = f"{quantity}" if quantity > 1 else ''
                    item_condition_image = load_image(self.world, item, text=conditon_text)
                    graph.add_node_feature_condition(check_item, item_condition_image)

                    item_option_image = load_image(self.world, item)
                    graph.add_node_option(get_item, item_option_image)

                    if prev_check_in_option is not None:
                        graph.add_edge_conditional(prev_check_in_option, check_item, True)
                    graph.add_edge_conditional(check_item, get_item, False)

                    prev_check_in_option = check_item
                if prev_check_in_option is not None:
                    prev_checks.append(prev_check_in_option)
            else:
                no_item_required = "No item required"
                graph.add_node_empty(no_item_required)
                prev_checks.append(no_item_required)

        prev_checks_zone = []
        for zone_id in self.zones_id_needed: # Any of the zones possibles
            zone = self.world.zone_from_id[zone_id]
            check_zone = f"Is in {zone}?"
            option_zone = f"Reach {zone}"

            zone_image = load_image(self.world, zone)
            graph.add_node_feature_condition(check_zone, zone_image)
            graph.add_node_option(option_zone, zone_image)

            if len(prev_checks) > 0:
                graph.add_predecessors(prev_checks, check_zone,
                    force_any=len(self.zones_id_needed) > 1)
            graph.add_edge_conditional(check_zone, option_zone, False)

            prev_checks_zone.append(check_zone)

        if len(prev_checks_zone) > 0:
            prev_checks = prev_checks_zone

        for prop in self.zones_properties_needed: # All properties needed
            check_prop = f"Zone {prop} ?"
            get_prop = f"Get {prop}"

            prop_image = load_image(self.world, prop)
            graph.add_node_feature_condition(check_prop, prop_image)
            graph.add_node_option(get_prop, prop_image)

            if len(prev_checks) > 0:
                graph.add_predecessors(prev_checks, check_prop)
            graph.add_edge_conditional(check_prop, get_prop, False)

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

        action_image = load_image(self.world, obj)
        graph.add_node_action(last_node, action_image)
        graph.add_predecessors(prev_checks, last_node)
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
