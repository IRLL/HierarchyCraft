""" Module for handcrafted Behavior with HEBGraph in any HierarchyCraft environment. """

from typing import TYPE_CHECKING, Dict, List, Optional, Union

import numpy as np
from hebg import Behavior, HEBGraph

from hcraft.behaviors.actions import DoTransformation
from hcraft.behaviors.feature_conditions import (
    HasStack,
    HasLessStack,
    HasZoneItem,
    IsInZone,
)
from hcraft.elements import Item, Stack, Zone
from hcraft.render.utils import load_or_create_image
from hcraft.task import _ensure_zone_list, _zones_str

if TYPE_CHECKING:
    from hcraft.env import HcraftEnv
    from hcraft.transformation import Transformation


class GetItem(Behavior):

    """Behavior for getting an item"""

    def __init__(
        self,
        item: Item,
        env: "HcraftEnv",
        all_behaviors: Dict[Union[int, str], Behavior],
    ):
        super().__init__(name=self.get_name(item))
        self.env = env
        self.item = item
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: Item):
        """Get the name of the behavior."""
        return f"Get {item.name}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Any of the Tranformation that gives the item
        for transfo in self.env.world.transformations:
            produced_items = transfo.production("player")
            item_is_added = self.item in produced_items
            required_items = transfo.min_required("player")
            item_is_not_required = self.item not in required_items
            if item_is_added and item_is_not_required:
                sub_behavior = Behavior(AbleAndPerformTransformation.get_name(transfo))
                graph.add_node(sub_behavior)

        _ensure_has_node(graph, self)
        return graph


class DropItem(Behavior):

    """Behavior for dropping an item"""

    def __init__(
        self,
        item: Item,
        env: "HcraftEnv",
        all_behaviors: Dict[Union[int, str], Behavior],
    ):
        super().__init__(name=self.get_name(item))
        self.env = env
        self.item = item
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: Item):
        """Get the name of the behavior."""
        return f"Drop {item.name}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Any of the Tranformation that drops the item
        for transfo in self.env.world.transformations:
            produced_items = transfo.production("player")
            consumed_items = transfo.consumption("player")
            item_is_not_added = not produced_items and self.item not in produced_items
            item_is_removed = consumed_items or self.item in consumed_items
            if item_is_removed and item_is_not_added:
                sub_behavior = Behavior(AbleAndPerformTransformation.get_name(transfo))
                graph.add_node(sub_behavior)

        _ensure_has_node(graph, self)
        return graph


class PlaceItem(Behavior):

    """Behavior for getting an item in any of the given zones.

    If no zones are given, places in any of the zones were the item can be placed.

    """

    def __init__(
        self,
        item: Item,
        env: "HcraftEnv",
        all_behaviors: Dict[Union[int, str], Behavior],
        zones: Optional[Union[Zone, List[Zone]]] = None,
    ):
        self.item = item
        self.zones = _ensure_zone_list(zones)
        super().__init__(name=self.get_name(self.item, self.zones))
        self.env = env
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: Item, zones: Optional[List[Zone]] = None):
        """Get the name of the behavior to reach a zone."""
        zones_str = _zones_str(_ensure_zone_list(zones))
        return f"Place {item.name}{zones_str}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Go to any zone where the zone_item is from the start
        for zone, items_stacks in self.env.world.start_zones_items.items():
            if self.item in [stack.item for stack in items_stacks]:
                sub_behavior = Behavior(ReachZone.get_name(zone))
                graph.add_node(sub_behavior)

        # Any of the Tranformation that places the item in the given zone
        for transfo in self.env.world.transformations:
            is_added = self._zone_item_is_added(transfo)
            is_required = self._zone_item_is_required(transfo)
            if is_added and not is_required:
                sub_behavior = Behavior(AbleAndPerformTransformation.get_name(transfo))
                graph.add_node(sub_behavior)

        _ensure_has_node(graph, self)
        return graph

    def _zone_item_is_added(self, transformation: "Transformation") -> bool:
        return self._zone_item_is_in(
            transformation.get_changes("current_zone", "add"),
            transformation.get_changes("destination", "add"),
            transformation.get_changes("zones", "add"),
            transformation.zones,
            transformation.destination,
        )

    def _zone_item_is_required(self, transformation: "Transformation") -> bool:
        return self._zone_item_is_in(
            transformation.get_changes("current_zone", "min"),
            transformation.get_changes("destination", "min"),
            transformation.get_changes("zones", "min"),
            transformation.zones,
            transformation.destination,
        )

    def _zone_item_is_in(
        self,
        zone_items: Optional[List[Stack]],
        destination_items: Optional[List[Stack]],
        zones_items: Optional[Dict[Zone, List[Stack]]],
        zones: Optional[List[Zone]],
        destination: Optional[Zone],
    ):
        zone_is_valid = (
            self.zones is None or zones is None or (set(self.zones) - set(zones))
        )
        destination_is_valid = self.zones is None or (
            destination is not None and destination in self.zones
        )
        if self._item_is_in_stack(zone_items) and zone_is_valid:
            return True
        if self._item_is_in_stack(destination_items) and destination_is_valid:
            return True
        if self._zone_item_in_dict_of_stacks(zones_items):
            return True
        return False

    def _zone_item_in_dict_of_stacks(
        self, dict_of_stack: Optional[Dict["Zone", List["Stack"]]]
    ):
        if dict_of_stack is None:
            return False
        valid_zones = list(dict_of_stack.keys()) if self.zones is None else self.zones
        stacks = []
        for zone in valid_zones:
            zone_stacks = dict_of_stack.get(zone, [])
            stacks.extend(zone_stacks)
        return self._item_is_in_stack(stacks)

    def _item_is_in_stack(self, stacks: Optional[List["Stack"]]) -> bool:
        return stacks is not None and self.item in [stack.item for stack in stacks]


class ReachZone(Behavior):

    """Behavior for going into a zone"""

    def __init__(
        self,
        zone: Zone,
        env: "HcraftEnv",
        all_behaviors: Dict[Union[int, str], Behavior],
    ):
        super().__init__(name=self.get_name(zone))
        self.env = env
        self.zone = zone
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(zone: Zone):
        """Get the name of the behavior to reach a zone."""
        return f"Reach {zone.name}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Any of the Tranformation that has the zone as destination
        for transfo in self.env.world.transformations:
            if transfo.destination is not None and transfo.destination == self.zone:
                sub_behavior = Behavior(AbleAndPerformTransformation.get_name(transfo))
                graph.add_node(sub_behavior)

        _ensure_has_node(graph, self)
        return graph


class AbleAndPerformTransformation(Behavior):

    """Behavior for abling then performing any transformation."""

    def __init__(
        self,
        env: "HcraftEnv",
        transformation: "Transformation",
        all_behaviors: Dict[Union[int, str], Behavior],
    ):
        super().__init__(name=self.get_name(transformation))
        self.env = env
        self.transformation = transformation
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(transformation: "Transformation"):
        """Name of the behavior to able the transformation."""
        return f"Able and perform: {transformation.name}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)
        last_node = None

        # Required items from specific zones
        for zone, stacks in self.transformation.get_changes("zones", "min", {}).items():
            for stack in stacks:
                has_item_in_zone = _add_place_item(graph, self.env, stack, zone)
                if last_node is not None:
                    graph.add_edge(last_node, has_item_in_zone, index=int(True))
                last_node = has_item_in_zone

        # Required items
        for stack in self.transformation.get_changes("player", "min", []):
            has_item = _add_get_item(stack, graph, self.env)
            if last_node is not None:
                graph.add_edge(last_node, has_item, index=int(True))
            last_node = has_item

        # Be in any of the possible zones
        prev_checks_zone = []
        if self.env.world.n_zones > 1 and self.transformation.zones is not None:
            for zone in self.transformation.zones:
                is_in_zone = _add_zone_behavior(zone, graph, self.env)
                prev_checks_zone.append(is_in_zone)
                if last_node is not None:
                    graph.add_edge(last_node, is_in_zone, index=int(True))

        if len(prev_checks_zone) > 0:  # Required zones
            last_nodes = prev_checks_zone
        elif last_node is not None:  # No required zone, but required craft
            last_nodes = [last_node]
        else:  # Require nothing yet
            last_nodes = []

        # Required items from current zone
        for stack in self.transformation.get_changes("current_zone", "min", []):
            has_item_in_zone = _add_place_item(graph, self.env, stack)
            for prev in last_nodes:
                graph.add_edge(prev, has_item_in_zone, index=int(True))
            last_nodes = [has_item_in_zone]

        # Drop all items that would go be over maximum in player inventory
        for stack in self.transformation.get_changes("player", "max", []):
            has_not_item = _add_drop_item(stack, graph, self.env)
            for prev in last_nodes:
                graph.add_edge(prev, has_not_item, index=int(True))
            last_nodes = [has_not_item]

        # Add last action
        action = DoTransformation(self.transformation, self.env)

        graph.add_node(action)
        for prev in last_nodes:
            graph.add_edge(prev, action, index=int(True))
        return graph


def _add_get_item(stack: Stack, graph: HEBGraph, env: "HcraftEnv") -> HasStack:
    has_item = HasStack(env, stack)
    image = np.array(load_or_create_image(stack, env.world.resources_path))
    get_item = Behavior(GetItem.get_name(stack.item), image=image)
    graph.add_edge(has_item, get_item, index=int(False))
    return has_item


def _add_drop_item(stack: Stack, graph: HEBGraph, env: "HcraftEnv") -> HasLessStack:
    has_not_item = HasLessStack(env, stack)
    image = np.array(load_or_create_image(stack, env.world.resources_path))
    drop_item = Behavior(DropItem.get_name(stack.item), image=image)
    graph.add_edge(has_not_item, drop_item, index=int(False))
    return has_not_item


def _add_zone_behavior(zone: Zone, graph: HEBGraph, env: "HcraftEnv") -> IsInZone:
    is_in_zone = IsInZone(env, zone)
    image = np.array(load_or_create_image(zone, env.world.resources_path))
    reach_zone = Behavior(ReachZone.get_name(zone), image=image)
    graph.add_edge(is_in_zone, reach_zone, index=int(False))
    return is_in_zone


def _add_place_item(
    graph: HEBGraph,
    env: "HcraftEnv",
    stack: Stack,
    zone: Optional[Zone] = None,
) -> HasZoneItem:
    has_item_in_zone = HasZoneItem(env, stack, zone)
    image = np.array(load_or_create_image(stack, env.world.resources_path))
    place_item = Behavior(PlaceItem.get_name(stack.item, zone), image=image)
    graph.add_edge(has_item_in_zone, place_item, index=int(False))
    return has_item_in_zone


def _ensure_has_node(graph: HEBGraph, behavior: Behavior) -> None:
    if len(list(graph.nodes())) == 0:
        raise ValueError(
            f"No node was build while trying to build HEBGraph for behavior: {behavior}."
        )
