""" Module for handcrafted Behavior with HEBGraph in any Crafting environment. """

from typing import TYPE_CHECKING, Dict, Union

import numpy as np
from hebg import Behavior, HEBGraph

from crafting.behaviors.actions import DoTransformation
from crafting.behaviors.feature_conditions import HasItemStack, HasZoneItem, IsInZone
from crafting.render.utils import load_or_create_image


if TYPE_CHECKING:
    from crafting.env import CraftingEnv
    from crafting.transformation import Transformation
    from crafting.world import Item, ItemStack, Zone


class GetItem(Behavior):

    """Behavior for getting an item"""

    def __init__(
        self,
        item: "Item",
        env: "CraftingEnv",
        all_behaviors: Dict[Union[int, str], Behavior],
    ):
        super().__init__(name=self.get_name(item))
        self.env = env
        self.item = item
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: "Item"):
        """Get the name of the behavior to reach a zone."""
        return f"Get {item.name}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Any of the Tranformation that gives the item
        for transfo in self.env.transformations:
            item_is_added = transfo.added_player_items is not None and self.item in [
                itemstack.item for itemstack in transfo.added_player_items
            ]
            item_is_not_removed = (
                transfo.removed_player_items is None
                or self.item
                not in [itemstack.item for itemstack in transfo.removed_player_items]
            )
            if item_is_added and item_is_not_removed:
                sub_behavior = Behavior(AbleAndPerformTransformation.get_name(transfo))
                graph.add_node(sub_behavior)
        return graph


class GetZoneItem(Behavior):

    """Behavior for getting an item in the current zone"""

    def __init__(
        self,
        item: "Item",
        env: "CraftingEnv",
        all_behaviors: Dict[Union[int, str], Behavior],
    ):
        super().__init__(name=self.get_name(item))
        self.env = env
        self.item = item
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(item: "Item"):
        """Get the name of the behavior to reach a zone."""
        return f"Get {item.name} in current Zone"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Any of the Tranformation that gives the item
        for transfo in self.env.transformations:
            zone_item_is_added = transfo.added_zone_items is not None and self.item in [
                itemstack.item for itemstack in transfo.added_zone_items
            ]
            zone_item_is_not_removed = (
                transfo.removed_zone_items is None
                or self.item
                not in [itemstack.item for itemstack in transfo.removed_zone_items]
            )
            if zone_item_is_added and zone_item_is_not_removed:
                sub_behavior = Behavior(AbleAndPerformTransformation.get_name(transfo))
                graph.add_node(sub_behavior)

        # Go to any zone where the zone_item is from the start
        for zone, items_stacks in self.env.start_zones_items.items():
            if self.item in [itemstack.item for itemstack in items_stacks]:
                sub_behavior = Behavior(ReachZone.get_name(zone))
                graph.add_node(sub_behavior)

        return graph


class ReachZone(Behavior):

    """Behavior for going into a zone"""

    def __init__(
        self,
        zone: "Zone",
        env: "CraftingEnv",
        all_behaviors: Dict[Union[int, str], Behavior],
    ):
        super().__init__(name=self.get_name(zone))
        self.env = env
        self.zone = zone
        self.all_behaviors = all_behaviors

    @staticmethod
    def get_name(zone: "Zone"):
        """Get the name of the behavior to reach a zone."""
        return f"Reach {zone.name}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)

        # Any of the Tranformation that has the zone as destination
        for transfo in self.env.transformations:
            if transfo.destination is not None and transfo.destination == self.zone:
                sub_behavior = Behavior(AbleAndPerformTransformation.get_name(transfo))
                graph.add_node(sub_behavior)
        return graph


class AbleAndPerformTransformation(Behavior):

    """Behavior for abling then performing any transformation."""

    def __init__(
        self,
        env: "CraftingEnv",
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
        return f"Able and perform: {str(transformation)}"

    def build_graph(self) -> HEBGraph:
        graph = HEBGraph(behavior=self, all_behaviors=self.all_behaviors)
        last_node = None

        # Require all items to be removed from player env
        if self.transformation.removed_player_items is not None:
            for itemstack in self.transformation.removed_player_items:
                has_item = _add_get_item(itemstack, graph, self.env)
                if last_node is not None:
                    graph.add_edge(last_node, has_item, index=int(True))
                last_node = has_item

        # Require to be in any of the zones possibles
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

        # Require all items to be removed from current zone env
        if self.transformation.removed_zone_items is not None:
            for itemstack in self.transformation.removed_zone_items:
                has_prop = _add_get_zone_item(itemstack, graph, self.env)
                for prev in last_nodes:
                    graph.add_edge(prev, has_prop, index=int(True))
                last_nodes = [has_prop]

        # Add last action
        action = DoTransformation(self.transformation, self.env)

        graph.add_node(action)
        for prev in last_nodes:
            graph.add_edge(prev, action, index=int(True))
        return graph


def _add_get_item(
    itemstack: "ItemStack", graph: HEBGraph, env: "CraftingEnv"
) -> HasItemStack:
    has_item = HasItemStack(itemstack, env)
    image = np.array(load_or_create_image(itemstack, env.resources_path))
    get_item = Behavior(f"Get {itemstack.item.name}", image=image)
    graph.add_edge(has_item, get_item, index=int(False))
    return has_item


def _add_zone_behavior(zone: "Zone", graph: HEBGraph, env: "CraftingEnv") -> IsInZone:
    is_in_zone = IsInZone(zone, env)
    image = np.array(load_or_create_image(zone, env.resources_path))
    reach_zone = Behavior(f"Reach {zone.name}", image=image)
    graph.add_edge(is_in_zone, reach_zone, index=int(False))
    return is_in_zone


def _add_get_zone_item(
    itemstack: "ItemStack", graph: HEBGraph, env: "CraftingEnv"
) -> HasZoneItem:
    has_prop = HasZoneItem(itemstack, env)
    image = np.array(load_or_create_image(itemstack, env.resources_path))
    get_prop = Behavior(f"Get {itemstack.item.name} in current Zone", image=image)
    graph.add_edge(has_prop, get_prop, index=int(False))
    return has_prop
