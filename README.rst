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

Using pip:

.. code:: bash

   pip install irll-crafting


Usage
-----


Run MineCrafting with human
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install optional gui requirements:

.. code:: bash

   pip install irll-crafting[gui]


Using the command line interface:

.. code:: bash

   python -m crafting.examples.minecraft


Using the programmatic interface:

.. code:: python

    from crafting import MineCraftingEnv, get_human_action


    env = MineCraftingEnv()
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


Environment can also be obtained throught the gym interface:

Install optional gym requirements:

.. code:: bash

   pip install irll-crafting[gym]


.. code:: python

   env = gym.make("MineCrafting-NoReward-v1")


.. Run MineCrafting with RandomLegal Agent [code]
.. Run MineCrafting with sb3 agent [code]

.. Run other crafting examples [recursive, tower, random] [gym, class]

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
