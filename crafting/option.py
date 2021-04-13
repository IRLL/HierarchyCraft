# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from typing import List, Dict
from copy import deepcopy
from crafting.world.items import Item

class Option():

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

class GetItem(Option):

    def __init__(self, world:"crafting.world.World",
            item:Item,
            all_get_options: Dict[int, Option],
            items_needed:List[List[tuple]],
            last_action: tuple,
            zones_id_needed=None, zones_properties_needed=None):
        self.world = world
        self.item = item
        self.items_needed = items_needed
        self.zones_id_needed = zones_id_needed
        self.zones_properties_needed = zones_properties_needed
        self.last_action = last_action
        self.all_get_options = all_get_options

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
                            get_item_option = self.all_get_options[item_id]
                            action_for_craft_option[i], _ = get_item_option(
                                observation, items_id_in_search=items_id_in_search
                            )
                        else:
                            action_for_craft_option[i] = "Not Feasable"
            if action_for_craft_option[i] is None:
                break

        # print(self.item, self.items_needed, action_for_craft_option)
        if all(action is not None for action in action_for_craft_option):
            feasable_actions = [
                action for action in action_for_craft_option
                if action is not None and action != "Not Feasable"
            ]
            if len(feasable_actions) > 0:
                return feasable_actions[0]
            return "Not Feasable"

    def move_to_zone(self, observation):
        zone_id = self.world.zone_id_from_observation(observation)
        if len(self.zones_id_needed) > 0 and zone_id not in self.zones_id_needed:
            return self.world.action('move', self.zones_id_needed[0])

    def get_zone_property(self, zone_property, observation):
        props = self.world.properties_from_observation(observation)
        print(zone_property, props, observation[self.world.n_items + self.world.n_zones:])
        if zone_property not in props:
            get_property_option = self.all_get_options[zone_property]
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

        if self.zones_id_needed is not None:
            action = self.move_to_zone(observations)
            if action is not None:
                return action, False

        if self.zones_properties_needed is not None:
            for zone_property in self.zones_properties_needed:
                action = self.get_zone_property(zone_property, observations)
                if action is not None:
                    return action, False

        return self.world.action(*self.last_action), True

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
        if self.zones_id_needed is not None and len(self.zones_id_needed) > 0:
            string = _add_text(string, f"  Zones {self.zones_id_needed}", do_return)
            do_return = True
        if self.zones_properties_needed is not None:
            string = _add_text(string, f"  Properties {self.zones_properties_needed}", do_return)
            do_return = True
        string = _add_text(string, f"  Last action {self.last_action}", do_return)
        return string
