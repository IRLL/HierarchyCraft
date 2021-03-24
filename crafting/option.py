# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

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

    def __init__(self, world: World, items_needed, last_action, zones_id_needed=None):
        self.world = world
        self.items_needed = items_needed
        self.zones_id_needed = zones_id_needed
        self.last_action = last_action

    def gather_items(self, observation):
        for item_id, quantity_needed, get_item_option in self.items_needed:
            item_slot = self.world.item_id_to_slot[item_id]
            inventory_content = observation[:self.world.n_items]
            if inventory_content[item_slot] < quantity_needed:
                if isinstance(get_item_option, tuple):
                    return self.action(*get_item_option)
                if isinstance(get_item_option, int):
                    return get_item_option
                if isinstance(get_item_option, Option):
                    return get_item_option(observation)
                raise TypeError(
                    'items_needed tuples must contain a int, tuple or Option in last position'
                )

    def move_to_zone(self, observation):
        if self.zones_id_needed is not None:
            zone_id = self.world.zone_id_from_observation(observation)
            if zone_id not in self.zones_id_needed:
                return self.world.action('move', zone_id)

    def __call__(self, observations, greedy: bool=False):
        ## TODO Vectorize
        action = self.gather_items(observations)
        if action is not None:
            return action, False

        action = self.move_to_zone(observations)
        if action is not None:
            return action, False

        return self.world.action(*self.last_action), True
