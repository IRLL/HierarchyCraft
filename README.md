# **HierarchyCraft - Environements builder for hierarchical ML research**

[![Fury - PyPi stable version](https://badge.fury.io/py/hcraft.svg)](https://badge.fury.io/py/hcraft)
[![PePy - Downloads](https://static.pepy.tech/badge/hcraft)](https://pepy.tech/project/hcraft)
[![PePy - Downloads per week](https://static.pepy.tech/badge/hcraft/week)](https://pepy.tech/project/hcraft)
[![Licence - GPLv3](https://img.shields.io/github/license/IRLL/HierarchyCraft?style=plastic)](https://www.gnu.org/licenses/)

[![Codacy - grade](https://app.codacy.com/project/badge/Grade/b5010ccc46274c0eb1e3ae563934efdd)](https://www.codacy.com/gh/IRLL/HierarchyCraft/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/HierarchyCraft&amp;utm_campaign=Badge_Grade)
[![Codacy - coverage](https://app.codacy.com/project/badge/Coverage/b5010ccc46274c0eb1e3ae563934efdd)](https://www.codacy.com/gh/IRLL/HierarchyCraft/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/HierarchyCraft&amp;utm_campaign=Badge_Coverage)
[![CodeStyle - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CodeStyle - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)


# HierarchyCraft

HierarchyCraft (hcraft for short) is a Python library designed to create arbitrary hierarchical environments that are compatible with both the [OpenAI Gym Reinforcement Learning Framework](https://github.com/openai/gym) and [AIPlan4EU Unified Planning Framework](https://github.com/aiplan4eu/unified-planning). This library enables users to easily create complex hierarchical structures that can be used to test and develop various reinforcement learning or planning algorithms.

In environments built with HierarchyCraft the agent (player) has an inventory and can navigate into abstract zones that themselves have inventories.

Available actions of the agent are defined by **transformations**.
**Transformations** are the core element of every HierarchyCraft environment, they define the actions that an agent can perform in the environment. At their core, transformations are simply changes to the state of the environment that can be triggered by the agent if the transformation is allowed in the current state.

## No feature extraction for fast research even with low compute

HierarchyCraft returns vectorized state information, which plainly and directly describes the player's inventory, current positions, and the inventory of the current zone. Compared to benchmarks that return grids, pixel arrays, text or sound, we directly return a low-dimensional latent representation that doesn't need to be learned.
Therefore saving compute time and allowing researchers to focus only the the hierarchical reasoning part.

![](docs/images/hcraft_observation.png)

See [`hcraft.state`](https://irll.github.io/HierarchyCraft/hcraft/state.html) for more details.

## Create your own tailored HierarchyCraft environments

You can use HierarchyCraft to create various custom hierarchical environments. As a showcase of the complexe possibilities, here is a replica of the underlying hierarchy of the popular game Minecraft, without the computationaly intensive 3D and without being a 2D grid version either.

![A player knowing Minecraft will find MineHcraft easy.](./docs/images/minehcraft_human_demo.gif)

See [`hcraft.env`](https://irll.github.io/HierarchyCraft/hcraft/env.html) for a complete tutorial on creating custom environments.


# Installation

## Using pip

Without optional dependencies:

```bash
pip install hcraft
```

With all optional dependencies:

```bash
pip install hcraft[all]
```

All hcraft environments can use a common graphical user interface.
With gui requirements:

```bash
pip install hcraft[gui]
```

Gym environment can be obtained throught the with gym requirements:

```bash
pip install hcraft[gym]
```

Planning problems can be obtained throught the upf interface:

```bash
pip install hcraft[planning]
```

# Quickstart

## Play yourself!

Don't forget to install the GUI:
```bash
pip install hcraft[gui]
```

### Using the command line interface

You can directly try to play yourself with the GUI available for any HierarchyCraft environments, for example:
```bash
hcraft minecraft
```

For more examples:
```bash
hcraft --help
```
###  Using the programmatic interface:

```python
from hcraft import get_human_action
from hcraft.examples import MineHcraftEnv

env = MineHcraftEnv()
# or env: MineHcraftEnv = gym.make("MineHcraft-NoReward-v1")
n_episodes = 2
for _ in range(n_episodes):
    env.reset()
    done = False
    total_reward = 0
    while not done:
        env.render()
        action = get_human_action(env)
        print(f"Human pressed: {env.world.transformations[action]}")

        _observation, reward, done, _info = env.step(action)
        total_reward += reward

    print(f"SCORE: {total_reward}")
```

## As a Gym RL environment

Using the programmatic interface, any HierarchyCraft environment can easily be interfaced with classic reinforcement learning agents.

```python
import numpy as np
from hcraft.examples import MineHcraftEnv

def random_legal_agent(observation, action_is_legal):
    action = np.random.choice(np.nonzero(action_is_legal)[0])
    return int(action)

env = MineHcraftEnv(max_step=10)
done = False
observation = env.reset()
while not done:
    action_is_legal = env.action_masks()
    action = random_legal_agent(observation, action_is_legal)
    _observation, _reward, done, _info = env.step(action)
```


```python
# Other examples of HierarchyCraft environments
from hcraft.examples import TowerHcraft, RecursiveHcraft, RandomHcraft

tower_env = TowerHcraft(height=3, width=2)
# or tower_env = gym.make("TowerHcraft-v1", height=3, width=2)
recursive_env = RecursiveHcraft(n_items=6)
# or recursive_env = gym.make("RecursiveHcraft-v1", n_items=6)
random_env = RandomHcraft(n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)
# or random_env = gym.make("RandomHcraft-v1", n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)
```
<!-- Run MineHcraft with MaskablePPO from sb3 agent [code] -->

See [`hcraft.env`](https://irll.github.io/HierarchyCraft/hcraft/env.html) for a more complete description.

## As a UPF problem for planning

HierarchyCraft environments can be converted to planning problem in one line
thanks to the Unified Planning Framework (UPF):

```python
problem = env.planning_problem()
print(problem.upf_problem)
```

Then they can be solved with any compatible planner (default is enhsp):

```python
problem.solve()
print(problem.plan)
```

See [`hcraft.planning`](https://irll.github.io/HierarchyCraft/hcraft/planning.html) for a more complete description.


# More about HierarchyCraft

## Online documentation

Learn more in the [DOCUMENTATION](https://irll.github.io/HierarchyCraft/hcraft.html)
