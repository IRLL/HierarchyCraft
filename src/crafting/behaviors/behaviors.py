# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for handcrafted Behavior with HEBGraph in any Crafting environment. """

from typing import TYPE_CHECKING, Dict, List, Union, Tuple

import numpy as np
from hebg import HEBGraph, Behavior

from crafting.constants import ActionTypes
from crafting.behaviors.actions import CraftRecipe, MoveToZone, SearchItem
from crafting.behaviors.feature_conditions import HasItem, HasProperty, IsInZone
from crafting.render.utils import load_or_create_image

if TYPE_CHECKING:
    from crafting.world.items import Item, Tool
    from crafting.world.world import World
    from crafting.world.zones import Zone


class ReachZone(Behavior):

    """Behavior for moving to a Zone"""

    def __init__(
        self, zone: "Zone", world: "World", all_behaviors: Dict[str, Behavior]
    ):
        super().__init__(f"Reach {str(zone)}")
        self.world = world
        self.zone = zone
        self.all_behaviors = all_behaviors

    def build_graph(self) -> HEBGraph:
        """Build the HEBGraph of this Behavior.

        Returns:
            The built HEBGraph.

        """
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        prev_checks = []

        # Any of Tool needed
        for tool in self.zone.required_tools:
            has_item = _add_required_tool(self.world, graph, tool)
            prev_checks.append(has_item)

        # All properties needed
        for prop, _ in self.zone.required_properties.items():
            has_prop = _add_property_needed(self.world, graph, prop)
            for prev in prev_checks:
                graph.add_edge(prev, has_prop, index=int(True))
            prev_checks = [has_prop]

        go_to_zone = MoveToZone(self.zone, self.world)
        graph.add_node(go_to_zone)
        for prev in prev_checks:
            graph.add_edge(prev, go_to_zone, index=int(True))

        return graph


class GetItem(Behavior):

    """Behavior for getting an item"""

    def __init__(
        self,
        world: "World",
        item: "Item",
        all_behaviors: Dict[Union[int, str], Behavior],
        items_needed: List[List[tuple]],
        last_action: Tuple[ActionTypes, int],
        zones_id_needed: list = None,
        zones_properties_needed: dict = None,
    ):

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
        self.all_behaviors = all_behaviors

    def build_graph(self) -> HEBGraph:
        """Build the HEBGraph of this Behavior.

        Returns:
            The built HEBGraph.

        """
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)
        prev_checks = []

        # Any of Craft behaviors
        if None not in self.items_needed:
            for craft_behavior in self.items_needed:
                prev_check = None
                for item_id, quantity in craft_behavior:
                    has_item = _add_crafting_behavior(
                        self.world, graph, item_id, quantity
                    )
                    if prev_check is not None:
                        graph.add_edge(prev_check, has_item, index=int(True))
                    prev_check = has_item
                if prev_check is not None:
                    prev_checks.append(prev_check)

        # Any of the zones possibles
        prev_checks_zone = []
        if self.world.n_zones > 1:
            for zone_id in self.zones_id_needed:
                is_in_zone = _add_zone_behavior(self.world, graph, zone_id)
                prev_checks_zone.append(is_in_zone)
                for prev in prev_checks:
                    graph.add_edge(prev, is_in_zone, index=int(True))
        if len(prev_checks_zone) > 0:
            prev_checks = prev_checks_zone

        # All properties needed
        for prop, _ in self.zones_properties_needed.items():
            has_prop = _add_property_needed(self.world, graph, prop)
            for prev in prev_checks:
                graph.add_edge(prev, has_prop, index=int(True))
            prev_checks = [has_prop]

        # Add last action
        action_type, obj_id = self.last_action
        if action_type == ActionTypes.SEARCH:
            item = self.world.item_from_id[obj_id]
            action = SearchItem(item, self.world)
        elif action_type == ActionTypes.CRAFT:
            recipe = self.world.recipes_from_id[obj_id]
            action = CraftRecipe(recipe, self.world)
        elif action_type == ActionTypes.MOVE:
            zone = self.world.zone_from_id[obj_id]
            action = MoveToZone(zone, self.world)
        else:
            raise ValueError(f"Unknowed action_type: {action_type}")

        graph.add_node(action)
        for prev in prev_checks:
            graph.add_edge(prev, action, index=int(True))
        return graph


def _add_crafting_behavior(
    world: "World", graph: HEBGraph, item_id: int, quantity: int
) -> HasItem:
    item = world.item_from_id[item_id]
    has_item = HasItem(item=item, world=world, quantity=quantity)
    image = np.array(load_or_create_image(world, item))
    get_item = Behavior(f"Get {item}", image=image)
    graph.add_edge(has_item, get_item, index=int(False))
    return has_item


def _add_required_tool(world: "World", graph: HEBGraph, tool: "Tool") -> HasItem:
    item = world.item_from_id[tool.item_id]
    has_item = HasItem(item=item, world=world, quantity=1)
    image = np.array(load_or_create_image(world, item))
    get_item = Behavior(f"Get {item}", image=image)
    graph.add_edge(has_item, get_item, index=int(False))
    return has_item


def _add_zone_behavior(world: "World", graph: HEBGraph, zone_id: int) -> IsInZone:
    zone = world.zone_from_id[zone_id]
    is_in_zone = IsInZone(zone, world)
    image = np.array(load_or_create_image(world, zone))
    reach_zone = Behavior(f"Reach {zone}", image=image)
    graph.add_edge(is_in_zone, reach_zone, index=int(False))
    return is_in_zone


def _add_property_needed(world: "World", graph: HEBGraph, prop: str) -> HasProperty:
    has_prop = HasProperty(prop, world=world)
    image = np.array(load_or_create_image(world, prop))
    get_prop = Behavior(f"Get {prop}", image=image)
    graph.add_edge(has_prop, get_prop, index=int(False))
    return has_prop
