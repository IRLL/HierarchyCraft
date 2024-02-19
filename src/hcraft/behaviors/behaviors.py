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
from hcraft.task import _zones_str

if TYPE_CHECKING:
    from hcraft.env import HcraftEnv
    from hcraft.transformation import Transformation


class GetItem(Behavior):

    """Behavior for getting an item"""

    def __init__(
        self,
        item: Item,
        env: "HcraftEnv",
        all_behaviors: Dict[str, Behavior],
    ):
        super().__init__(name=self.get_name(item))
        self.env = env
        self.item = item
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: Item) -> str:
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
        all_behaviors: Dict[str, Behavior],
    ):
        super().__init__(name=self.get_name(item))
        self.env = env
        self.item = item
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: Item) -> str:
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
        all_behaviors: Dict[str, Behavior],
        zone: Optional[Zone] = None,
    ):
        self.item = item
        self.zone = zone
        super().__init__(name=self.get_name(self.item, self.zone))
        self.env = env
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: Item, zone: Optional[Zone] = None) -> str:
        """Get the name of the behavior to reach a zone."""
        return f"Place {item.name}{_zones_str(zone)}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Go to any zone where the zone_item is from the start
        for zone, items_stacks in self.env.world.start_zones_items.items():
            if self.zone is not None and zone != self.zone:
                continue
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
            transformation.zone,
            transformation.destination,
        )

    def _zone_item_is_required(self, transformation: "Transformation") -> bool:
        return self._zone_item_is_in(
            transformation.get_changes("current_zone", "min"),
            transformation.get_changes("destination", "min"),
            transformation.get_changes("zones", "min"),
            transformation.zone,
            transformation.destination,
        )

    def _zone_item_is_in(
        self,
        zone_items: Optional[List[Stack]],
        destination_items: Optional[List[Stack]],
        zones_items: Optional[Dict[Zone, List[Stack]]],
        zone: Optional[Zone],
        destination: Optional[Zone],
    ) -> bool:
        zone_is_valid = self.zone is None or zone is None or zone == self.zone
        if zone_is_valid and self._item_is_in_stack(zone_items):
            return True

        destination_is_valid = self.zone is None or (
            destination is not None and destination == self.zone
        )
        if destination_is_valid and self._item_is_in_stack(destination_items):
            return True
        if self._zone_item_in_dict_of_stacks(zones_items):
            return True
        return False

    def _zone_item_in_dict_of_stacks(
        self, dict_of_stack: Optional[Dict["Zone", List["Stack"]]]
    ) -> bool:
        if dict_of_stack is None:
            return False
        valid_zones = list(dict_of_stack.keys()) if self.zone is None else [self.zone]
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
        all_behaviors: Dict[str, Behavior],
    ):
        super().__init__(name=self.get_name(zone))
        self.env = env
        self.zone = zone
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(zone: Zone) -> str:
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
        all_behaviors: Dict[str, Behavior],
    ):
        super().__init__(name=self.get_name(transformation))
        self.env = env
        self.transformation = transformation
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(transformation: "Transformation") -> str:
        """Name of the behavior to able the transformation."""
        return f"Able and do {transformation.name}"

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

        # Required items from destination
        for stack in self.transformation.get_changes("destination", "min", []):
            has_item_in_dest = _add_place_item(
                graph, self.env, stack, zone=self.transformation.destination
            )
            if last_node is not None:
                graph.add_edge(last_node, has_item_in_dest, index=int(True))
            last_node = has_item_in_dest

        # Required items from current zone (or required zone)
        for stack in self.transformation.get_changes("current_zone", "min", []):
            has_item_in_zone = _add_place_item(
                graph, self.env, stack, zone=self.transformation.zone
            )
            if last_node is not None:
                graph.add_edge(last_node, has_item_in_zone, index=int(True))
            last_node = has_item_in_zone

        # Be in required zone
        if self.env.world.n_zones > 1 and self.transformation.zone is not None:
            is_in_zone = _add_zone_behavior(self.transformation.zone, graph, self.env)
            if last_node is not None:
                graph.add_edge(last_node, is_in_zone, index=int(True))
            last_node = is_in_zone

        # Drop all items that would go be over maximum in player inventory
        for stack in self.transformation.get_changes("player", "max", []):
            has_not_item = _add_drop_item(stack, graph, self.env)
            if last_node is not None:
                graph.add_edge(last_node, has_not_item, index=int(True))
            last_node = has_not_item

        # Add last action
        action = DoTransformation(self.transformation, self.env)

        graph.add_node(action)
        if last_node is not None:
            graph.add_edge(last_node, action, index=int(True))
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
