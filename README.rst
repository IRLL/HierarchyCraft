Crafting - A gym environment for inventory management
=====================================================

.. image:: https://app.codacy.com/project/badge/Grade/b5010ccc46274c0eb1e3ae563934efdd
   :alt: [Codacy - grade]
   :target: https://www.codacy.com/gh/IRLL/Crafting/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/Crafting&amp;utm_campaign=Badge_Grade

.. image:: https://app.codacy.com/project/badge/Coverage/b5010ccc46274c0eb1e3ae563934efdd
   :alt: [Codacy - coverage]
   :target: https://www.codacy.com/gh/IRLL/Crafting/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=IRLL/Crafting&amp;utm_campaign=Badge_Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :alt: [CodeStyle - Black]
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/github/license/MathisFederico/Crafting?style=plastic
   :alt: [Licence - GPLv3]
   :target: https://www.gnu.org/licenses/

Why Crafting ?
--------------

Crafting is a meta-environment allowing to generate 
arbitrarely hierarchical environments for research purpose.

A Crafting environment is a sandbox environment composed of
items, zones, and transformations.


The main example of Crafting environment is the MineCrafting environment 
that mimics the popular game Minecraft.

Installation
------------

Installation can simply be done using pip.

Without optional dependencies:

.. code:: bash

   pip install irll-crafting

With all optional dependencies:

.. code:: bash

   pip install irll-crafting[all]


All crafting environments can use a common graphical user interface.
With gui requirements:

.. code:: bash

   pip install irll-crafting[gui]


Environment can also be obtained throught the gym interface:
With gym requirements:

.. code:: bash

   pip install irll-crafting[gym]


Usage
-----


Run MineCrafting with human
~~~~~~~~~~~~~~~~~~~~~~~~~~~


Using the command line interface:

.. code:: bash

   python -m crafting.examples.minecraft


Using the programmatic interface:

.. code:: python

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



Run MineCrafting with agents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the programmatic interface, any Crafting environment can easily be interfaced with any agent.

.. code:: python

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



.. Run MineCrafting with MaskablePPO from sb3 agent [code]

Other crafting environments examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from crafting import TowerCrafting, RecursiveCrafting, RandomCrafting

    tower_env = TowerCrafting(height=3, width=2)
    # or env = gym.make("TowerCrafting-v1", height=3, width=2)
    recursive_env = RecursiveCrafting(n_items=6)
    # or env = gym.make("RecursiveCrafting-v1", n_items=6)
    random_env = RandomCrafting(n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)
    # or env = gym.make("RandomCrafting-v1", n_items_per_n_inputs={0:2, 1:5, 2:10}, seed=42)



.. ## Custom purposes
.. Single task
.. Reward shaping

.. Multi task (terminal groups)
.. Reward shaping subtasks are optional

.. Custom task

.. ## Rendering options

.. ## Requirements graphs

.. ## Solving behavior
.. Install HEBG [bash]

.. Solve MineCrafting [code]
.. Plot rolled / unrolled [wooden pickaxe]
.. Generated code

.. Solve RandomCrafting [code]
.. Plot rolled / unrolled
.. Generated code

Online documentation
--------------------

.. figure:: docs/_static/images/doc_index.png
   :align: center
   :alt: Online documentation
   :target: https://crafting.readthedocs.io/en/latest/index.html

   Click to see the html documentation!

.. include:: CONTRIBUTING.rst
