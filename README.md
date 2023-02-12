# **Crafting - A gym environment for inventory management**

[![Codacy - grade](https://app.codacy.com/project/badge/Grade/b5010ccc46274c0eb1e3ae563934efdd)](https://www.codacy.com/gh/IRLL/Crafting/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/Crafting&amp;utm_campaign=Badge_Grade)
[![Codacy - coverage](https://app.codacy.com/project/badge/Coverage/b5010ccc46274c0eb1e3ae563934efdd)](https://www.codacy.com/gh/IRLL/Crafting/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/Crafting&amp;utm_campaign=Badge_Coverage)
[![CodeStyle - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Licence - GPLv3](https://img.shields.io/github/license/MathisFederico/Crafting?style=plastic)](https://www.gnu.org/licenses/)

# Why Crafting ?

Crafting is a meta-environment allowing to generate 
arbitrarely hierarchical environments for research purpose.

A Crafting environment is a sandbox environment composed of
items, zones, and transformations.


The main example of Crafting environment is the MineCrafting environment 
that mimics the (complex) hierarchies of the popular game Minecraft.

![MineCrafting craft hierarchy](docs/_static/images/minecrafting_crafts_hierarchy.png)

# Installation

Installation can simply be done using pip.

Without optional dependencies:

```bash
pip install irll-crafting
```

With all optional dependencies:

```bash
pip install irll-crafting[all]
```


All crafting environments can use a common graphical user interface.
With gui requirements:

```bash
pip install irll-crafting[gui]
```

Environment can also be obtained throught the gym interface:
With gym requirements:

```bash
pip install irll-crafting[gym]
```

# Quickstart


## Run MineCrafting with human

Using the command line interface:

```bash
crafting minecraft
```

See more options with:

```bash
crafting --help
```

Using the programmatic interface:

```python
from crafting import MineCraftingEnv, get_human_action

env = MineCraftingEnv()
# or env: MineCraftingEnv = gym.make("MineCrafting-NoReward-v1")
n_episodes = 2
for _ in range(n_episodes):
    env.reset()
    done = False
    total_reward = 0
    while not done:
        env.render()
        action = get_human_action(env)
        print(f"Human pressed: {env.transformations[action]}")

        _observation, reward, done, _info = env.step(action)
        total_reward += reward

    print(f"SCORE: {total_reward}")
```


## Run MineCrafting with agents

Using the programmatic interface, any Crafting environment can easily be interfaced with any agent.

```python
import numpy as np
from crafting import MineCraftingEnv

def random_legal_agent(observation, action_is_legal):
    action = np.random.choice(np.nonzero(action_is_legal)[0])
    return action

env = MineCraftingEnv(max_step=10)
done = False
observation = env.reset()
while not done:
    action_is_legal = env.actions_mask
    action = random_legal_agent(observation, action_is_legal)
    _observation, _reward, done, _info = env.step(action)
```
<!-- Run MineCrafting with MaskablePPO from sb3 agent [code] -->

## Other crafting environments

See `crafting.examples`.

``` python
from crafting import TowerCrafting, RecursiveCrafting, RandomCrafting

tower_env = TowerCrafting(height=3, width=2)
# or tower_env = gym.make("TowerCrafting-v1", height=3, width=2)
recursive_env = RecursiveCrafting(n_items=6)
# or recursive_env = gym.make("RecursiveCrafting-v1", n_items=6)
random_env = RandomCrafting(n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)
# or random_env = gym.make("RandomCrafting-v1", n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)
```

# Online documentation

There is much more to discover in crafting:

- Add a Purpose to the player: `crafting.purpose`
- Get a solving behavior for any given task: `crafting.solving_behaviors`
- Plot the underlying requirements graph: `crafting.requirement_graph`
- Create your own customize environment: `crafting.env`

Find everything in the [documentation](https://irll.github.io/Crafting/crafting.html):

[![DOCUMENTATION](docs/images/doc_index.png)](https://irll.github.io/Crafting/crafting.html)


<!-- Rendering options -->

<!-- Requirements graphs -->

<!-- Solving behavior
Install HEBG [bash] -->

<!-- Solve MineCrafting [code]
Plot rolled / unrolled [wooden pickaxe]
Generated code -->

<!-- Solve RandomCrafting [code]
Plot rolled / unrolled
Generated code -->

