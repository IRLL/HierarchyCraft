from typing import Dict, List, Set, Tuple, Optional, Union

import os
import numpy as np
import networkx as nx

import crafting
from crafting.world import Item, ItemStack, Zone, World
from crafting.transformation import Transformation
from crafting.purpose import Purpose
from crafting.behaviors.solving_behaviors import Behavior, build_all_solving_behaviors

from crafting.render.render import CraftingWindow
from crafting.render.utils import surface_to_rgb_array


class CraftingEnv:
    """A gym-like environment built from a list of `Transformation`."""

    def __init__(
        self,
        transformations: List[Transformation],
        start_zone: Optional[Zone],
        start_items: Optional[List[ItemStack]] = None,
        start_zones_items: Optional[Dict[Zone, List[ItemStack]]] = None,
        purpose: Optional[Purpose] = None,
        invalid_reward: float = -10.0,
        render_mode="rgb_array",
        resources_path: Optional[str] = None,
        name: str = "Crafting",
    ) -> None:
        """Initialize a Crafting environement.

        Args:
            transformations (List[Transformation]): The list of transformations
                defining the environment.
            start_zone (Optional[Zone], optional): The Zone in which the player starts.
                If not given, start in the first indexed zone.
            purpose (Optional[Purpose], optional): Purpose of the player,
                defining rewards and termination. Defaults to None, hence a sandbox environment.
            invalid_reward (float, optional): Reward given to the agent for invalid actions.
                Defaults to -10.0.
            render_mode (str, optional): Render mode. Defaults to "rgb_array".
            name (str): Name of the environement.
        """
        self.transformations = transformations
        self.start_zone = start_zone
        self.start_items = start_items if start_items is not None else []
        self.start_zones_items = (
            start_zones_items if start_zones_items is not None else {}
        )
        self.invalid_reward = invalid_reward
        self.world = self._build_world()
        self._build_transformations()

        self.player_inventory = np.array([], dtype=np.uint16)
        self.position = np.array([], dtype=np.uint16)
        self.zones_inventories = np.array([], dtype=np.uint16)
        self._reset_state()

        if purpose is None:
            purpose = Purpose(None)
        if not isinstance(purpose, Purpose):
            purpose = Purpose(tasks=purpose)
        self.purpose = purpose
        self.purpose.build(self.world)

        self.render_mode = render_mode
        self.render_window = None
        if resources_path is None:
            render_dir = os.path.dirname(crafting.render.__file__)
            resources_path = os.path.join(render_dir, "default_resources")
        self.resources_path = resources_path

        self.metadata = {}
        self.name = name

        self._requirements_graph = None

    @property
    def state(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Current state of the environment."""
        return self.player_inventory, self.position, self.zones_inventories

    @property
    def current_zone_inventory(self) -> np.ndarray:
        """Current zone inventory."""
        current_zone_slot = self.position.nonzero()[0]
        return self.zones_inventories[current_zone_slot, :][0]

    @property
    def observation(self) -> np.ndarray:
        """Observation given to the player."""
        return np.concatenate(
            (self.player_inventory, self.position, self.current_zone_inventory)
        )

    @property
    def truncated(self) -> bool:
        """Whether the time limit has been exceeded."""
        return False

    @property
    def terminated(self) -> bool:
        """Whether the environment tasks are all done (if any)"""
        return self.purpose.is_terminal(*self.state)

    @property
    def actions_mask(self) -> np.ndarray:
        """Boolean mask of valid actions."""
        return np.array([t.is_valid(*self.state) for t in self.transformations])

    def step(self, action: int):
        """Perform one step in the environment given the index of a wanted transformation.

        If the selected transformation can be performed, the state is updated and
        a reward is given depending of the environment tasks.
        Else the state is left unchanged and the `invalid_reward` is given to the player.

        """
        choosen_transformation = self.transformations[action]
        if not choosen_transformation.is_valid(*self.state):
            return self._step_output(self.invalid_reward)
        choosen_transformation.apply(
            self.player_inventory,
            self.position,
            self.zones_inventories,
        )
        reward = self.purpose.reward(*self.state)
        return self._step_output(reward)

    def reset(self, seed: int = 0):
        """Resets the state of the environement."""
        self._reset_state()

    def close(self):
        """Closes the environment."""
        if self.render_window is not None:
            self.render_window.close()

    def get_all_behaviors(self) -> Dict[str, "Behavior"]:
        """Build all solving behaviors using hebg."""
        return build_all_solving_behaviors(self)

    @property
    def requirements_graph(self) -> nx.DiGraph:
        return self._requirements_graph

    def _step_output(self, reward: float):
        infos = {"action_is_legal": self.actions_mask}
        return (self.observation, reward, self.terminated or self.truncated, infos)

    def _build_world(self) -> World:
        """Reads the transformation to build the list of items, zones and zones_items
        composing the world."""

        # Start elements
        zones = set([self.start_zone])
        items = set(itemstack.item for itemstack in self.start_items)
        zones_items = set()
        for zone, zone_items in self.start_zones_items.items():
            zones.add(zone)
            zones_items |= set(itemstack.item for itemstack in zone_items)

        # Elements by transformations
        for transfo in self.transformations:
            if transfo.destination is not None:
                zones.add(transfo.destination)
            if transfo.zones is not None:
                zones |= set(transfo.zones)
            items = _add_items_to(transfo.removed_player_items, items)
            items = _add_items_to(transfo.added_player_items, items)
            zones_items = _add_items_to(transfo.removed_destination_items, zones_items)
            zones_items = _add_items_to(transfo.added_destination_items, zones_items)
            zones_items = _add_items_to(transfo.removed_zone_items, zones_items)
            zones_items = _add_items_to(transfo.added_zone_items, zones_items)

        return World(list(items), list(zones), list(zones_items))

    def _build_transformations(self):
        for transformation in self.transformations:
            transformation.build(self.world)

    def _reset_state(self) -> None:
        self.player_inventory = np.zeros(self.world.n_items, dtype=np.uint16)
        for itemstack in self.start_items:
            item_slot = self.world.items.index(itemstack.item)
            self.player_inventory[item_slot] = itemstack.quantity

        self.position = np.zeros(self.world.n_zones, dtype=np.uint16)
        start_slot = 0  # Start in first Zone by default
        if self.start_zone is not None:
            start_slot = self.world.slot_from_zone(self.start_zone)
        self.position[start_slot] = 1

        self.zones_inventories = np.zeros(
            (self.world.n_zones, self.world.n_zones_items), dtype=np.uint16
        )
        for zone, zone_itemstacks in self.start_zones_items.items():
            zone_slot = self.world.zones.index(zone)
            for itemstack in zone_itemstacks:
                item_slot = self.world.zones_items.index(itemstack.item)
                self.zones_inventories[zone_slot, item_slot] = itemstack.quantity

    def render(self, mode: Optional[str] = None, **kwargs) -> Union[str, np.ndarray]:
        """Render the observation of the agent in a format depending on `render_mode`."""
        if mode is not None:
            self.render_mode = mode

        if self.render_mode in ("human", "rgb_array"):  # for human interaction
            return self._render_rgb_array()
        if self.render_mode == "console":  # for console print
            raise NotImplementedError
        raise NotImplementedError

    def _render_rgb_array(self) -> np.ndarray:
        """Render an image of the game.

        Create the rendering window if not existing yet.
        """
        if self.render_window is None:
            self.render_window = CraftingWindow(self)
        fps = self.metadata.get("video.frames_per_second")
        self.render_window.update_rendering(fps=fps)
        return surface_to_rgb_array(self.render_window.screen)


def _add_items_to(itemstacks: Optional[List[ItemStack]], items_set: Set[Item]):
    if itemstacks is not None:
        for itemstack in itemstacks:
            items_set.add(itemstack.item)
    return items_set
