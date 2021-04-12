# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from typing import List, Dict

from crafting.world.world import World

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

    def __init__(self, world: World, all_get_options: Dict[int, Option],
            items_needed:List[List[tuple]],
            last_action: tuple,
            zones_id_needed=None, zones_properties_needed=None):
        self.world = world
        self.items_needed = items_needed
        self.zones_id_needed = zones_id_needed
        self.zones_properties_needed = zones_properties_needed
        self.last_action = last_action
        self.all_get_options = all_get_options

    def gather_items(self, observation):
        if len(self.items_needed) == 0:
            return None
        action_for_craft_option = [None for _ in self.items_needed]
        for i, craft_option in enumerate(self.items_needed):
            for item_id, quantity_needed in craft_option:
                if action_for_craft_option[i] is None:
                    item_slot = self.world.item_id_to_slot[item_id]
                    inventory_content = observation[:self.world.n_items]
                    if inventory_content[item_slot] < quantity_needed:
                        get_item_option = self.all_get_options[item_id]
                        action_for_craft_option[i] = get_item_option(observation)[0]
            if action_for_craft_option[i] is None:
                break

        if all(action is not None for action in action_for_craft_option):
            return action_for_craft_option[0]

    def move_to_zone(self, observation):
        zone_id = self.world.zone_id_from_observation(observation)
        if zone_id not in self.zones_id_needed:
            return self.world.action('move', zone_id)

    def get_zone_property(self, observation):
        raise NotImplementedError

    def __call__(self, observations, greedy: bool=False):
        ## TODO Vectorize
        action = self.gather_items(observations)
        if action is not None:
            return action, False

        if self.zones_id_needed is not None:
            action = self.move_to_zone(observations)
            if action is not None:
                return action, False

        if self.zones_properties_needed is not None:
            action = self.get_zone_property(observations)
            if action is not None:
                return action, False

        return self.world.action(*self.last_action), True

    def __str__(self):
        string = ""
        if len(self.items_needed) > 0 and len(self.items_needed[0]) > 0:
            string += f"  Required {self.items_needed}"
        if self.zones_id_needed is not None and len(self.zones_id_needed) > 0:
            if len(string) > 0:
                string += "\n"
            string += f"  Zones {self.zones_id_needed}"
        if self.zones_properties_needed is not None:
            if len(string) > 0:
                string += "\n"
            string += f"  Properties {self.zones_properties_needed}"
        if len(string) > 0:
            string += "\n"
        string += f"  Last action {self.last_action}"
        return string
