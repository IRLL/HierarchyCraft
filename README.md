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

## Create your own tailored HierarchyCraft environments

You can use HierarchyCraft to create various custom hierarchical environments. As an example, here is a replica of the underlying hierarchy of the popular game Minecraft without the computationaly intensive 3D:

![A player knowing Minecraft will find MineHcraft easy.](docs/images/minehcraft_human_demo.gif)

### Play yourself!

```bash
pip install hcraft[gui]
hcraft minecraft
```


For more examples, see [examples](https://irll.github.io/HierarchyCraft/hcraft/examples.html).

To create a HierarchyCraft environment, one need to understand **transformations** fully.

Each **transformation** is composed of three optional elements:

-   The first element is a **destination** zone, which specifies the zone to which the agent will move if the transformation changes the player position. This element is only necessary if the transformation changes the agent's position in the environment.

-   The second element is a list of **zones** to which the transformation is restricted. This element allows users to define which zones the agent can perform the transformation in, restricting the agent's actions to certain areas of the environment. If not specified, the transformation can be done anywhere.

-   The third element is a dictionary of **inventory changes** for the player, the current zone, the destination zone, or any specific zones. Inventory changes are defined as a dictionary mapping operations such as 'add', 'remove', 'min', 'max' on lists of stacks of items. This element allows users to define changes to any inventory that may result from the transformation, it also restricts the transformation to only be possible if the amount of the specified item is more that min and less than max. If unspecified, no changes are done, and 'min' will default to 0, 'max' to +inf.

For examples, see [`hcraft.transformation`](https://irll.github.io/HierarchyCraft/hcraft/transformation.html)


Each HierarchyCraft environment is defined by a list of transformations and an initial state. The initial state defines the starting state of the environment, including the agent's position, inventory, and zones inventories. By combining transformations and an initial state, users can simply create complex hierarchical environments with a high degree of flexibility and control.

See [`hcraft.env`](https://irll.github.io/HierarchyCraft/hcraft/env.html) for a complete tutorial on creating custom environments.

See [`hcraft.state`](https://irll.github.io/HierarchyCraft/hcraft/state.html) for more details on the HierarchyCraft environements state.

## Custom purposes for agents in HierarchyCraft environments

HierarchyCraft allows users to specify custom purposes for agents in their environments, composed of one or multiple tasks. This feature provides a high degree of flexibility and allows users to design environments that are tailored to specific applications or scenarios. This feature enables to study mutli-task or lifelong learning settings.

See [`hcraft.purpose`](https://irll.github.io/HierarchyCraft/hcraft/purpose.html) for more details.

## Solving behavior for all tasks of most HierarchyCraft environments

HierarchyCraft also includes solving behaviors that can be used to generate actions from observations that will complete most tasks in any HierarchyCraft environment, including those designed by the user.

Solving behaviors are handcrafted, and may not work in some edge cases when transformations require items in specific zones. This feature makes it easy for users to obtain a strong baseline in their custom environments.

See [`hcraft.solving_behaviors`](https://irll.github.io/HierarchyCraft/hcraft/solving_behaviors.html) for more details.

## Visualizing the underlying hierarchy of the environment (requirements graph)

HierarchyCraft gives the ability to visualize the hierarchy of the environment as a requirements graph. This graph provides a potentialy complex but complete representation of what is required to obtain each item or to go in each zone, allowing users to easily understand the structure of the environment and identify key items of the environment.

For example, here is the graph of the 'MiniCraftUnlock' environment where the goal is to open a door using a key:
![Unlock requirements graph](https://raw.githubusercontent.com/IRLL/HierarchyCraft/master/docs/images/requirements_graphs/MiniCraftUnlock.png)


And here is much more complex graph of the 'MineHcraft' environment shown previously:
![Minehcraft requirements graph](https://raw.githubusercontent.com/IRLL/HierarchyCraft/master/docs/images/requirements_graphs/MineHcraft.png)


See [`hcraft.requirements`](https://irll.github.io/HierarchyCraft/hcraft/requirements.html) for more details.


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

Environment can also be obtained throught the gym interface:
With gym requirements:

```bash
pip install hcraft[gym]
```

# Quickstart

See command line interface (CLI) options with:

```bash
hcraft --help
```

Using the programmatic interface:

```python
from hcraft import MineHcraftEnv, get_human_action

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


## Run MineHcraft with autonomous agents

Using the programmatic interface, any HierarchyCraft environment can easily be interfaced with any agent.

```python
import numpy as np
from hcraft import MineHcraftEnv

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
<!-- Run MineHcraft with MaskablePPO from sb3 agent [code] -->

## Other hcraft environments

See [`hcraft.examples`](https://irll.github.io/HierarchyCraft/hcraft/examples.html).

``` python
from hcraft import TowerHcraft, RecursiveHcraft, RandomHcraft

tower_env = TowerHcraft(height=3, width=2)
# or tower_env = gym.make("TowerHcraft-v1", height=3, width=2)
recursive_env = RecursiveHcraft(n_items=6)
# or recursive_env = gym.make("RecursiveHcraft-v1", n_items=6)
random_env = RandomHcraft(n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)
# or random_env = gym.make("RandomHcraft-v1", n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)
```

Learn more in the [documentation](https://irll.github.io/HierarchyCraft/hcraft.html)
