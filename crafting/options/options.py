# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for handcrafted Option with OptionGraph in any Crafting environment. """

from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Union

from option_graph import Option, OptionGraph, Action, EmptyNode

from crafting.render.utils import load_image
from crafting.options.actions import SearchItem, MoveToZone, CraftRecipe
from crafting.options.feature_conditions import HasItem, IsInZone, HasProperty

if TYPE_CHECKING:
    from crafting.world.items import Item
    from crafting.world.zones import Zone
    from crafting.world.world import World

class ReachZone(Option):

    """ Option for moving to a Zone """

    def __init__(self, zone:Zone, world:World):
        super().__init__(f"Reach {str(zone)}")
        self.world = world
        self.zone = zone

    def build_graph(self) -> OptionGraph:
        graph = OptionGraph(option=self)

        is_in_zone = IsInZone(self.zone, self.world)
        graph.add_node(is_in_zone)

        go_to_zone = MoveToZone(self.zone, self.world)
        graph.add_node(go_to_zone)
        graph.add_edge(is_in_zone, go_to_zone, index=int(False))

        do_nothing = Action(None)
        graph.add_node(do_nothing)
        graph.add_edge(is_in_zone, do_nothing, index=int(True))
        return graph


class GetItem(Option):

    """ Option for getting an item """

    def __init__(self, world:World,
            item:Item,
            all_options:Dict[Union[int, str], Option],
            items_needed:List[List[tuple]],
            last_action:tuple,
            zones_id_needed:list=None, zones_properties_needed:dict=None):

        super().__init__(name=f"Get {str(item)}")
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
            self.zones_properties_needed = {}

        self.last_action = last_action
        self.all_options = all_options

    def build_graph(self) -> OptionGraph:
        graph = OptionGraph(option=self, all_options=self.all_options)
        prev_checks = []

        # Any of Craft options
        for craft_option in self.items_needed:
            if craft_option is not None:
                prev_check_in_option = None
                for item_id, quantity in craft_option:
                    item = self.world.item_from_id[item_id]

                    has_item = HasItem(item=item, world=self.world, quantity=quantity)
                    graph.add_node(has_item)

                    get_item = Option(f"Get {item}", image=load_image(self.world, item))
                    graph.add_node(get_item)

                    if prev_check_in_option is not None:
                        graph.add_edge(prev_check_in_option, has_item, index=int(True))
                    graph.add_edge(has_item, get_item, index=int(False))

                    prev_check_in_option = has_item
                if prev_check_in_option is not None:
                    prev_checks.append(prev_check_in_option)
            else:
                no_item_required = EmptyNode("No item required")
                graph.add_node(no_item_required)
                prev_checks.append(no_item_required)

        # Any of the zones possibles
        prev_checks_zone = []
        for zone_id in self.zones_id_needed:
            zone = self.world.zone_from_id[zone_id]

            is_in_zone = IsInZone(zone, self.world)
            graph.add_node(is_in_zone)

            reach_zone = Option(f"Reach {zone}", image=load_image(self.world, zone))
            graph.add_node(reach_zone)

            for prev in prev_checks:
                graph.add_edge(prev, is_in_zone, index=int(True))
            graph.add_edge(is_in_zone, reach_zone, index=int(False))

            prev_checks_zone.append(is_in_zone)

        if len(prev_checks_zone) > 0:
            prev_checks = prev_checks_zone

        # All properties needed
        for prop, value in self.zones_properties_needed.items():
            has_prop = HasProperty(prop, world=self.world, value=value)
            graph.add_node(has_prop)

            get_prop = Option(f"Get {prop}", image=load_image(self.world, prop))
            graph.add_node(get_prop)

            for prev in prev_checks:
                graph.add_edge(prev, has_prop, index=int(True))
            graph.add_edge(has_prop, get_prop, index=int(False))

            prev_checks = [has_prop]

        # Add last action
        action_type, obj_id = self.last_action
        if action_type == 'get':
            item = self.world.item_from_id[obj_id]
            action = SearchItem(item, self.world)
        elif action_type == 'craft':
            recipe = self.world.recipes_from_id[obj_id]
            action = CraftRecipe(recipe, self.world)
        elif action_type == 'move':
            zone = self.world.zone_from_id[obj_id]
            action = MoveToZone(zone, self.world)
        else:
            raise ValueError(f'Unknowed action_type: {action_type}')

        graph.add_node(action)
        for prev in prev_checks:
            graph.add_edge(prev, action, index=int(True))
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
