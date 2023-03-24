import numpy as np
import pytest_check as check

from hcraft.env import HcraftEnv
from tests.envs import classic_env


def random_legal_agent(observation, action_is_legal):
    action = np.random.choice(np.nonzero(action_is_legal)[0])
    return int(action)


def test_random_legal_agent():
    world = classic_env()[1]
    env = HcraftEnv(world, max_step=10)
    done = False
    observation = env.reset()
    total_reward = 0
    while not done:
        action_is_legal = env.action_masks()
        action = random_legal_agent(observation, action_is_legal)
        _observation, reward, done, _info = env.step(action)
        total_reward += reward

    check.greater_equal(total_reward, 0)
