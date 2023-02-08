import collections
import os
from typing import Dict, List, Optional, Set, Tuple, Union

import networkx as nx
import numpy as np

import crafting
from crafting.behaviors.solving_behaviors import Behavior, build_all_solving_behaviors
from crafting.purpose import Purpose
from crafting.render.render import CraftingWindow
from crafting.render.utils import surface_to_rgb_array
from crafting.requirement_graph import build_requirements_graph, draw_requirements_graph
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, World, Zone

# Gym is an optional dependency.
try:
    import gym

    DiscreteSpace = gym.spaces.Discrete
    BoxSpace = gym.spaces.Box
    TupleSpace = gym.spaces.Tuple
    MultiBinarySpace = gym.spaces.MultiBinary
    Env = gym.Env
except ImportError:
    DiscreteSpace = collections.namedtuple("DiscreteSpace", "n")
    BoxSpace = collections.namedtuple("BoxSpace", "low, high, shape, dtype")
    TupleSpace = collections.namedtuple("TupleSpace", "spaces")
    MultiBinarySpace = collections.namedtuple("MultiBinary", "n")
    Env = object


class CraftingEnv(Env):
    """A gym-like environment built from a list of `Transformation`."""

    def __init__(
        self,
        transformations: List[Transformation],
        start_zone: Optional[Zone] = None,
        start_items: Optional[List[ItemStack]] = None,
        start_zones_items: Optional[Dict[Zone, List[ItemStack]]] = None,
        purpose: Optional[Purpose] = None,
        invalid_reward: float = -10.0,
        render_mode="rgb_array",
        resources_path: Optional[str] = None,
        name: str = "Crafting",
        max_step: Optional[int] = None,
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
        self.discovered_transformations = np.array([], dtype=np.ubyte)

        self.player_inventory = np.array([], dtype=np.uint16)
        self.discovered_items = np.array([], dtype=np.ubyte)
        self.position = np.array([], dtype=np.uint16)
        self.discovered_zones = np.array([], dtype=np.ubyte)
        self.zones_inventories = np.array([], dtype=np.uint16)
        self.discovered_zones_items = np.array([], dtype=np.ubyte)
        self.current_step = 0
        self.reset()

        if purpose is None:
            purpose = Purpose(None)
        if not isinstance(purpose, Purpose):
            purpose = Purpose(tasks=purpose)
        self.purpose = purpose
        self.purpose.build(self)

        self.render_mode = render_mode
        self.render_window = None
        if resources_path is None:
            render_dir = os.path.dirname(crafting.render.__file__)
            resources_path = os.path.join(render_dir, "default_resources")
        self.resources_path = resources_path

        self.max_step = max_step

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
        if self.position.shape[0] == 0:
            return np.array([])  # No Zone
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
        if self.max_step is None:
            return False
        return self.current_step >= self.max_step

    @property
    def terminated(self) -> bool:
        """Whether the environment tasks are all done (if any)"""
        return self.purpose.is_terminal(*self.state)

    @property
    def observation_space(self) -> Union[BoxSpace, TupleSpace]:
        """Observation space for the Agent in the Crafting environment."""
        obs_space = BoxSpace(
            low=np.array(
                [0 for _ in range(self.world.n_items)]
                + [0 for _ in range(self.world.n_zones)]
                + [0 for _ in range(self.world.n_zones_items)]
            ),
            high=np.array(
                [np.inf for _ in range(self.world.n_items)]
                + [1 for _ in range(self.world.n_zones)]
                + [np.inf for _ in range(self.world.n_zones_items)]
            ),
        )

        return obs_space

    @property
    def action_space(self) -> DiscreteSpace:
        """Action space for the Agent in the Crafting environment.

        Actions are expected to often be invalid.
        """
        return DiscreteSpace(len(self.transformations))

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
        self.current_step += 1
        choosen_transformation = self.transformations[action]
        if not choosen_transformation.is_valid(*self.state):
            return self._step_output(self.invalid_reward)
        choosen_transformation.apply(
            self.player_inventory,
            self.position,
            self.zones_inventories,
        )
        self._update_discoveries(action)
        reward = self.purpose.reward(*self.state)
        return self._step_output(reward)

    def render(self, mode: Optional[str] = None, **kwargs) -> Union[str, np.ndarray]:
        """Render the observation of the agent in a format depending on `render_mode`."""
        if mode is not None:
            self.render_mode = mode

        if self.render_mode in ("human", "rgb_array"):  # for human interaction
            return self._render_rgb_array()
        if self.render_mode == "console":  # for console print
            raise NotImplementedError
        raise NotImplementedError

    def reset(self, seed: int = 0):
        """Resets the state of the environement."""
        self.current_step = 0
        self._reset_discoveries()
        self._reset_state()
        self._update_discoveries()

    def close(self):
        """Closes the environment."""
        if self.render_window is not None:
            self.render_window.close()

    def get_all_behaviors(self) -> Dict[str, "Behavior"]:
        """Build all solving behaviors using hebg."""
        return build_all_solving_behaviors(self)

    def draw_requirements_graph(self, ax, **kwargs):
        return draw_requirements_graph(ax, self.requirements_graph, **kwargs)

    @property
    def requirements_graph(self) -> nx.DiGraph:
        if self._requirements_graph is None:
            self._requirements_graph = build_requirements_graph(self)
        return self._requirements_graph

    def _update_discoveries(self, action: Optional[int] = None) -> None:
        self.discovered_items = np.bitwise_or(
            self.discovered_items, self.player_inventory > 0
        )
        self.discovered_zones_items = np.bitwise_or(
            self.discovered_zones_items, np.sum(self.zones_inventories, axis=0) > 0
        )
        self.discovered_zones = np.bitwise_or(self.discovered_zones, self.position > 0)
        if action is not None:
            self.discovered_transformations[action] = 1

    def _reset_discoveries(self) -> None:
        self.discovered_items = np.zeros(self.world.n_items, dtype=np.ubyte)
        self.discovered_zones_items = np.zeros(self.world.n_zones_items, dtype=np.ubyte)
        self.discovered_zones = np.zeros(self.world.n_zones, dtype=np.ubyte)
        self.discovered_transformations = np.zeros(
            len(self.transformations), dtype=np.ubyte
        )

    def _step_output(self, reward: float):
        infos = {"action_is_legal": self.actions_mask}
        return (self.observation, reward, self.terminated or self.truncated, infos)

    def _build_world(self) -> World:
        """Reads the transformation to build the list of items, zones and zones_items
        composing the world."""

        # Start elements
        zones = set()
        if self.start_zone is not None:
            zones.add(self.start_zone)

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
        if self.position.shape[0] > 0:
            self.position[start_slot] = 1

        self.zones_inventories = np.zeros(
            (self.world.n_zones, self.world.n_zones_items), dtype=np.uint16
        )
        for zone, zone_itemstacks in self.start_zones_items.items():
            zone_slot = self.world.zones.index(zone)
            for itemstack in zone_itemstacks:
                item_slot = self.world.zones_items.index(itemstack.item)
                self.zones_inventories[zone_slot, item_slot] = itemstack.quantity

        self.current_step = 0

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
