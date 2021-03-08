# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=unused-argument, no-self-use

""" Task to defines objectives """

from abc import abstractmethod
from typing import List, Union, Dict

class Task():

    """ Abstract class for any task """

    def __init__(self, name, world):
        self.name = name
        self.world = world

    @abstractmethod
    def reward(self, observation, previous_observation, action):
        """ Attribute a reward to the current transition """
        raise NotImplementedError

    @abstractmethod
    def done(self, observation, previous_observation, action):
        """ Return True if the task is done, used for early stopping """
        return False

    def __call__(self, observation, previous_observation, action):
        reward = self.reward(observation, previous_observation, action)
        done = self.done(observation, previous_observation, action)
        return reward, done


class TaskList():

    """ Wrapper for a list of tasks """

    def __init__(self,
            tasks: List[Task],
            tasks_weights: Union[List[float], Dict[str, float]]=None,
            tasks_can_end: Union[List[bool], Dict[str, bool]]=None,
            early_stopping: str='all'
        ):

        if tasks is not None:
            for task in tasks:
                if not isinstance(task, Task):
                    raise TypeError(
                        f'tasks must be subclassed from :class:`crafting.Task` but was {type(task)}'
                    )

        self.tasks = tasks
        self.tasks_weights = tasks_weights
        self.tasks_can_end = tasks_can_end
        self.early_stopping = early_stopping

    def _get_task_weight(self, task, i):
        if isinstance(self.tasks_weights, list):
            return self.tasks_weights[i]
        if isinstance(self.tasks_weights, dict):
            return self.tasks_weights[task.name]
        return 1

    def _get_task_can_end(self, task, i):
        if isinstance(self.tasks_can_end, list):
            return self.tasks_can_end[i]
        if isinstance(self.tasks_can_end, dict):
            return self.tasks_can_end[task.name]
        return True

    def _stack_dones(self, dones):
        if self.early_stopping == "all":
            return all(dones)
        if self.early_stopping == "any":
            return any(dones)
        raise ValueError(f'Unknown value for early_stopping: {self.early_stopping}')

    def __call__(self, observation, previous_observation, action):
        if self.tasks is None:
            return 0, False

        accumulated_reward = 0
        dones = []

        for i, task in enumerate(self.tasks):
            reward, done = task(observation, previous_observation, action)
            accumulated_reward += reward * self._get_task_weight(task, i)
            if self._get_task_can_end(task, i):
                dones.append(done)

        done = self._stack_dones(dones)
        return accumulated_reward, done
