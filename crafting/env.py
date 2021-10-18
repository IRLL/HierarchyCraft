# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from typing import Tuple, List, Union
from copy import deepcopy

import gym
import numpy as np
from gym import spaces

from crafting.world.world import World
from crafting.player.player import Player
from crafting.task import Task, TaskList
from crafting.render.render import update_rendering, surface_to_rgb_array, create_window

class CraftingEnv(gym.Env):

    """ Generic Crafting Environment """

    metadata = {
        'render.modes': ['rgb_array'],
        'video.frames_per_second': 10
    }

    def __init__(self, world: World, player: Player, name:str='Crafting',
        max_step: int=500, verbose: int=0, observe_legal_actions: bool=False,
        tasks: List[Union[str, Task]]=None, tasks_weights: Union[list, dict]=None,
        tasks_can_end: Union[list, dict]=None, tasks_early_stopping: str='all',
        fail_penalty: float=0.09, timestep_penalty: float=0.01, moving_penalty: float=0.09):
        """ Generic Crafting Environment.

        Args:
            world: The world containing items, crafts and zones.
            player: The player containing an inventory and a position.
            max_step: The maximum number of steps until done.
            verbose: Verbosity level. {0: quiet, 1: print actions results}.
            observe_legal_actions: If True, add legal actions to observations.
            tasks: List of tasks.
            tasks_weights: Weight of tasks used for reward.
            tasks_can_end: Whether task can end the environment.
            tasks_early_stopping: If 'all', all task that can end have to be done to stop the
                environment. If 'any', any task that can end will stop the environment when done.
            fail_penalty: Reward penalty for each non-successful action.
            timestep_penalty: Reward penalty for each timestep.
            moving_penalty: Reward penalty for moving to an other zone.

        """
        self.name = name

        self.world = deepcopy(world)
        self.initial_world = deepcopy(world)

        self.player = deepcopy(player)
        self.initial_player = deepcopy(player)

        self.tasks = TaskList(
            tasks=tasks,
            tasks_weights=tasks_weights,
            tasks_can_end=tasks_can_end,
            early_stopping=tasks_early_stopping
        )

        self.fail_penalty = fail_penalty
        self.timestep_penalty = timestep_penalty
        self.moving_penalty = moving_penalty

        self.max_step = max_step
        self.steps = 1
        self.verbose = verbose
        self.observe_legal_actions = observe_legal_actions

        # Action space
        # (get_item or use_recipe or move_to_zone)
        self.action_space = spaces.Discrete(
            self.world.n_foundable_items +\
            self.world.n_recipes +\
            self.world.n_zones
        )

        # Observation space
        # (n_stacks_per_item, inv_filled_proportion, one_hot_zone)
        self.observation_space = spaces.Box(
            low=np.array(
                [0 for _ in range(self.world.n_items)] +\
                [0 for _ in range(self.world.n_zones)] +\
                [0 for _ in range(self.world.n_zone_properties)]
            ),
            high=np.array(
                [np.inf for _ in range(self.world.n_items)] +\
                [1 for _ in range(self.world.n_zones)] +\
                [1 for _ in range(self.world.n_zone_properties)]
            ),
            dtype=np.float32
        )

        if self.observe_legal_actions:
            self.legal_actions_space = spaces.MultiBinary(self.action_space.n)
            self.observation_space = spaces.Tuple(
                (self.observation_space, self.legal_actions_space)
            )

        self.observation_legend = np.concatenate((
            [str(item) for item in self.world.items],
            [str(zone) for zone in self.world.zones],
            [str(prop) for prop in self.world.zone_properties]
        ))

    def action(self, action_type:str, identification:int) -> int:
        """ Return action_id from action type and identifier.

        Args:
            action_type: One of {'get', 'craft', 'move'}.
            identification: Id of the item, recipe or zone.

        Returns:
            The corresponding discrete action ID.

        """
        return self.world.action(action_type, identification)

    def action_from_id(self, action_id:int) -> str:
        """ Return action_id from action type and identifier.

        Args:
            action_id: A discrete action ID.

        Return:
            The action type and object concerned by the action.

        """
        return self.world.action_from_id(action_id)

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        previous_observation = self.get_observation()
        reward = 0

        # Get an item
        if action < self.world.n_foundable_items:
            item_slot = action
            item = self.world.foundable_items[item_slot]
            tool = self.player.choose_tool(item)
            n_found = self.player.search_for(item, tool)
            success = n_found > 0
            if self.verbose > 0:
                status_msg = 'SUCCEDED' if success else 'FAILED'
                print(f'{status_msg} at getting {item}[{n_found}] with {tool}')

        # Craft a recipe
        start_index = self.world.n_foundable_items
        if 0 <= action - start_index < self.world.n_recipes:
            recipe_slot = action - start_index
            recipe = self.world.recipes[recipe_slot]
            success = self.player.craft(recipe)
            if self.verbose > 0:
                status_msg = 'SUCCEDED' if success else 'FAILED'
                print(f'{status_msg} at crafting {recipe}')

        # Change zone
        start_index = self.world.n_foundable_items + self.world.n_recipes
        if 0 <= action - start_index < self.world.n_zones:
            zone_slot = action - start_index
            zone = self.world.zones[zone_slot]
            success = self.player.move_to(zone)
            reward -= self.moving_penalty
            if self.verbose > 0:
                status_msg = 'SUCCEDED' if success else 'FAILED'
                print(f'{status_msg} at moving to {zone}')

        # Synchronise world zone with player zone
        zone_slot = self.world.zone_id_to_slot[self.player.zone.zone_id]
        self.world.zones[zone_slot] = self.player.zone

        # Obtain new observation
        observation = self.get_observation()

        # Tasks
        task_reward, task_done = self.tasks(observation, previous_observation, action)
        reward += task_reward
        reward -= self.timestep_penalty
        if not success:
            reward -= self.fail_penalty

        self.player.score += int(100 * reward)

        # Termination
        done = self.steps >= self.max_step or task_done

        # Infos
        action_is_legal = self.action_masks()
        infos = {
            'env_step': self.steps,
            'action_is_legal': action_is_legal
        }

        self.steps += 1

        if self.observe_legal_actions:
            observation = (observation, action_is_legal)

        return observation, reward, done, infos

    def action_masks(self) -> np.ndarray:
        """ Return the legal actions """
        can_get = np.array([
            self.player.can_get(item, self.player.choose_tool(item))
            for item in self.world.foundable_items
        ])
        can_craft = np.array([self.player.can_craft(recipe) for recipe in self.world.recipes])
        can_move = np.array([self.player.can_move_to(zone) for zone in self.world.zones])
        return np.concatenate((can_get, can_craft, can_move))

    def get_observation(self) -> np.ndarray:
        """ Return the current observation """
        one_hot_zone = np.zeros(self.world.n_zones, np.float32)
        zone_slot = self.world.zone_id_to_slot[self.player.zone.zone_id]
        one_hot_zone[zone_slot] = 1

        inventory_content = self.player.inventory.content

        zone_properties = np.zeros(self.world.n_zone_properties)
        for i, prop in enumerate(self.world.zone_properties):
            if prop in self.player.zone.properties:
                zone_properties[i] = self.player.zone.properties[prop]

        observation = np.concatenate(
            (inventory_content, one_hot_zone, zone_properties),
            axis=-1
        )

        return observation

    def reset(self) -> np.ndarray:
        self.steps = 0
        self.player = deepcopy(self.initial_player)
        self.world = deepcopy(self.initial_world)
        self.tasks.reset()

        observation = self.get_observation()
        if self.observe_legal_actions:
            observation = (observation, self.action_masks())

        return observation

    def render(self, mode='human'):
        if mode == 'human': # for human interaction
            raise NotImplementedError
        if mode == 'console': # for console print
            return str(self.player)
        if mode == 'rgb_array':
            if self.render_variables is None:
                self.render_variables = create_window(self)
            update_rendering(env=self, fps=self.frame_per_sec, **self.render_variables)
            rgb_array = surface_to_rgb_array(self.render_variables['screen'])
            return rgb_array
        return super().render(mode=mode) # just raise an exception

    def __call__(self, action):
        return self.step(action)
