"""# Environment builder

You can easily create your own customized HierarchyCraft environment with the all the benefits
(graphical user interface, tasks, reward shaping, solving behavior, requirements graph).

For this, you just need to understand how to design transformations
and how to build a world from those.

You can see `hcraft.transformation` for more details or the full example bellow.

You can also check more complex examples in `hcraft.examples`.

# Example: Simple customed environment

Let's make a simple environment, where the goal is to open a the treasure chest and take it's gold.

## Create items

First, we need to represent the items we want to be able to manipulate.

For now, we only have two items we can simply build using the Item class from `hcraft.world`:

```python
from hcraft.elements import Item

CHEST = Item("treasure_chest")
GOLD = Item("gold")
```

## Link items with transformations

We want to remove the chest from the zone where our player is, and add it to his inventory.

We can then link those two items with a Tranformation from `hcraft.transformation`:

```python
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE

TAKE_GOLD_FROM_CHEST = Transformation(
    inventory_changes=[
        Use(CURRENT_ZONE, CHEST),
        Yield(PLAYER, GOLD),
    ]
)
```

Of course, `TAKE_GOLD_FROM_CHEST` will not be valid unless there is a `CHEST` in the zone.

Let's create a zone where we want our `CHEST` to be.

## Create a zone

Like items, zones are created with a Zone object from `hcraft.world`:

```python
from hcraft.elements import Zone

TREASURE_ROOM = Zone("treasure_room")
```

To place our `CHEST` in the `TREASURE_ROOM`, we need to build a World
from `hcraft.world` that will define our environment.

## Build a World from transformations

Items and zones in transformations will automaticaly be indexed by the World
to be stored in the environment state. (See `hcraft.state` for more details)
We can simply build a world from a list of transformations:

```python
from hcraft.elements import world_from_transformations

WORLD = world_from_transformations(
    transformations=[TAKE_GOLD_FROM_CHEST],
    start_zone=TREASURE_ROOM,
    start_zones_items={TREASURE_ROOM: [CHEST]}
)
```

Note that the world also stores the initial state of the world.
So we can add our `CHEST` in the `TREASURE_ROOM` here !

## Complete your first HierarchyCraft environment

To build a complete hcraft environment,
we simply need to pass our `WORLD` to HcraftEnv from `hcraft.env`:

```python
from hcraftnv import HcraftEnv

env = HcraftEnv(WORLD)
```

We can already render it in the GUI:

```python
from hcraft.render.human import render_env_with_human

render_env_with_human(env)
```
![](../../docs/images/TreasureEnvV1.png)

## Add a goal

For now, our environment is a sandbox that never ends and has no goal.
We can simply add a Purpose from `hcraft.purpose` like so:

```python
from hcraft.purpose import GetItemTask

get_gold_task = GetItemTask(GOLD)
env = HcraftEnv(WORLD, purpose=get_gold_task)
render_env_with_human(env)
```

## Turn up the challenge

Now that we have the basics done, let's have a bit more fun with our environment!
Let's lock the chest with keys, and add two room, a start room and a keys room.

First let's build the `KEY` item and the `KEY_ROOM`.

```python
KEY = Item("key")
KEY_ROOM = Zone("key_room")
```

Now let's make the `KEY_ROOM` a source of maximum 2 `KEY` with a transformation:

```python
SEARCH_KEY = Transformation(
    inventory_changes=[
        Yield(PLAYER, KEY, max=1),
    ],
    zones=[KEY_ROOM],
)
```
Note that `max=1` because max is the maximum *before* the transformation.

Then add the 'new state' for the `CHEST`, for this we simply build a new item `LOCKED_CHEST`,
and we add a transformation that will unlock the `LOCKED_CHEST` into a `CHEST` consuming two `KEYS`.

```python
LOCKED_CHEST = Item("locked_chest")
UNLOCK_CHEST = Transformation(
    inventory_changes=[
        Use(PLAYER, KEY, 2),
        Use(CURRENT_ZONE, LOCKED_CHEST, consume=1),
        Yield(CURRENT_ZONE, CHEST),
    ],
)
```

Now we need to be able to move between zones, for this we use (again) transformations:

Let's make the `START_ROOM` the link between the two other rooms.

```python
START_ROOM = Zone("start_room")
MOVE_TO_KEY_ROOM = Transformation(
    destination=KEY_ROOM,
    zones=[START_ROOM],
)
MOVE_TO_TREASURE_ROOM = Transformation(
    destination=TREASURE_ROOM,
    zones=[START_ROOM],
)
MOVE_TO_START_ROOM = Transformation(
    destination=START_ROOM,
)
```

We are ready for our V2 !
Again, we build the world from all our transformations and the env from the world.

But now the chest inside the `TREASURE_ROOM` is the `LOCKED_CHEST`
and our player start in `START_ROOM`.

Also, let's add a time limit to spice things up.

```python
from hcraft.elements import world_from_transformations

WORLD_2 = world_from_transformations(
    transformations=[
        TAKE_GOLD_FROM_CHEST,
        SEARCH_KEY,
        UNLOCK_CHEST,
        MOVE_TO_KEY_ROOM,
        MOVE_TO_TREASURE_ROOM,
        MOVE_TO_START_ROOM,
    ],
    start_zone=START_ROOM,
    start_zones_items={TREASURE_ROOM: [LOCKED_CHEST]},
)
env = HcraftEnv(WORLD_2, purpose=get_gold_task, max_step=10)
render_env_with_human(env)
```

## Add graphics

For now, our environment is a bit ... ugly.
Text is cool, but images are better !

For example, we can use cool
[2D assets from Pixel_Poem on itch.io](https://pixel-poem.itch.io/dungeon-assetpuck)

We simply have to put them into a folder like so:
```bash
├───myscript.py
├───resources
│   ├───items
│   │   ├───gold.png
│   │   ├───key.png
│   │   ├───locked_chest.png
│   │   └───treasure_chest.png
│   ├───zones
│   └───font.ttf
```

To simplify our case, we can use the already built folder under the treasure example:

```python
import os
import hcraft

hcraft_path = os.path.dirname(hcraft.__file__)
resources_path = os.path.join(hcraft_path, "examples", "treasure", "resources")
env = HcraftEnv(
    WORLD_2, purpose=get_gold_task, resources_path=resources_path, max_step=7
)
render_env_with_human(env)
```
And we now have cool images for items !
Try to do the same with zones and change the font aswell!

![](../../docs/images/TreasureEnvV2.png)

## Package into a class

If you wish to have someone else use your enviroment,
you should pack it up into a class and inherit HcraftEnv directly like so:

```python
.. include:: examples/treasure/__init__.py
```

That's it for this small customized env if you want more, be sure to check Transformation
 form `hcraft.transformation`, there is plenty we didn't cover here.


"""

import collections
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import numpy as np

from hcraft.metrics import SuccessCounter
from hcraft.purpose import Purpose
from hcraft.render.render import HcraftWindow
from hcraft.render.utils import surface_to_rgb_array
from hcraft.solving_behaviors import (
    Behavior,
    build_all_solving_behaviors,
    task_to_behavior_name,
)
from hcraft.planning import HcraftPlanningProblem
from hcraft.state import HcraftState

if TYPE_CHECKING:
    from hcraft.task import Task
    from hcraft.world import World

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


class HcraftEnv(Env):
    """Environment to simulate inventory management."""

    def __init__(
        self,
        world: "World",
        purpose: Optional[Union[Purpose, List["Task"], "Task"]] = None,
        invalid_reward: float = -1.0,
        render_window: Optional[HcraftWindow] = None,
        name: str = "HierarchyCraft",
        max_step: Optional[int] = None,
    ) -> None:
        """
        Args:
            world: World defining the environment.
            purpose: Purpose of the player, defining rewards and termination.
                Defaults to None, hence a sandbox environment.
            invalid_reward: Reward given to the agent for invalid actions.
                Defaults to -1.0.
            render_window: Window using to render the environment with pygame.
            name: Name of the environement. Defaults to 'HierarchyCraft'.
            max_step: (Optional[int], optional): Maximum number of steps before episode truncation.
                If None, never truncates the episode. Defaults to None.
        """
        self.world = world
        self.invalid_reward = invalid_reward
        self.max_step = max_step
        self.name = name
        self._requirements = None
        self._all_behaviors = None

        self.render_window = render_window
        self.render_mode = "rgb_array"

        self.state = HcraftState(self.world)
        self.current_step = 0
        self.current_score = 0
        self.cumulated_score = 0
        self.episodes = 0
        self.task_successes: Optional[SuccessCounter] = None
        self.terminal_successes: Optional[SuccessCounter] = None

        if purpose is None:
            purpose = Purpose(None)
        if not isinstance(purpose, Purpose):
            purpose = Purpose(tasks=purpose)
        self.purpose = purpose
        self.metadata = {}

    @property
    def truncated(self) -> bool:
        """Whether the time limit has been exceeded."""
        if self.max_step is None:
            return False
        return self.current_step >= self.max_step

    @property
    def terminated(self) -> bool:
        """Whether the environment tasks are all done (if any)"""
        return self.purpose.is_terminal(self.state)

    @property
    def observation_space(self) -> Union[BoxSpace, TupleSpace]:
        """Observation space for the Agent."""
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
        """Action space for the Agent.

        Actions are expected to often be invalid.
        """
        return DiscreteSpace(len(self.world.transformations))

    def action_masks(self) -> np.ndarray:
        """Return boolean mask of valid actions."""
        return np.array([t.is_valid(self.state) for t in self.world.transformations])

    def step(self, action: int):
        """Perform one step in the environment given the index of a wanted transformation.

        If the selected transformation can be performed, the state is updated and
        a reward is given depending of the environment tasks.
        Else the state is left unchanged and the `invalid_reward` is given to the player.

        """
        if not isinstance(action, int):
            raise TypeError(
                "Actions should be integers corresponding the a transformation index."
            )

        self.current_step += 1

        self.task_successes.step_reset()
        self.terminal_successes.step_reset()

        success = self.state.apply(action)
        if success:
            reward = self.purpose.reward(self.state)
        else:
            reward = self.invalid_reward

        terminated = self.terminated
        truncated = self.truncated

        self.task_successes.update(self.episodes)
        self.terminal_successes.update(self.episodes)

        self.current_score += reward
        self.cumulated_score += reward
        return self._step_output(reward, terminated, truncated)

    def render(self, mode: Optional[str] = None, **_kwargs) -> Union[str, np.ndarray]:
        """Render the observation of the agent in a format depending on `render_mode`."""
        if mode is not None:
            self.render_mode = mode

        if self.render_mode in ("human", "rgb_array"):  # for human interaction
            return self._render_rgb_array()
        if self.render_mode == "console":  # for console print
            raise NotImplementedError
        raise NotImplementedError

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ) -> np.ndarray:
        """Resets the state of the environement.

        Returns:
            (np.ndarray): The first observation.
        """

        if not self.purpose.built:
            self.purpose.build(self)
            self.task_successes = SuccessCounter(self.purpose.tasks)
            self.terminal_successes = SuccessCounter(self.purpose.terminal_groups)

        self.current_step = 0
        self.current_score = 0
        self.episodes += 1

        self.task_successes.new_episode(self.episodes)
        self.terminal_successes.new_episode(self.episodes)

        self.state.reset()
        self.purpose.reset()
        return self.state.observation

    def close(self):
        """Closes the environment."""
        if self.render_window is not None:
            self.render_window.close()

    @property
    def all_behaviors(self) -> Dict[str, "Behavior"]:
        """All solving behaviors using hebg."""
        if self._all_behaviors is None:
            self._all_behaviors = build_all_solving_behaviors(self)
        return self._all_behaviors

    def solving_behavior(self, task: "Task") -> "Behavior":
        """Get the solving behavior for a given task.

        Args:
            task: Task to solve.

        Returns:
            Behavior: Behavior solving the task.

        Example:
            ```python
            solving_behavior = env.solving_behavior(task)

            done = False
            observation = env.reset()
            while not done:
                action = solving_behavior(observation)
                observation, _reward, done, _info = env.step(action)

            assert task.is_terminated # Task is successfuly terminated
            ```
        """
        return self.all_behaviors[task_to_behavior_name(task)]

    def planning_problem(self) -> HcraftPlanningProblem:
        """Build this hcraft environment planning problem.

        Returns:
            Problem: Unified planning problem cooresponding to that environment.

        Example:
            Write as PDDL files:
            ```python
            from unified_planning.io import PDDLWriter
            problem = env.planning_problem()
            writer = PDDLWriter(problem.upf_problem)
            writer.write_domain("domain.pddl")
            writer.write_problem("problem.pddl")
            ```

            Using a plan to solve a HierarchyCraft gym environment:
            ```python
            hcraft_problem = env.planning_problem()

            done = False
            _observation = env.reset()
            while not done:
                action = hcraft_problem.action_from_plan(env.state)
                _observation, _reward, done, _ = env.step(action)
            assert env.purpose.is_terminated # Purpose is achieved
            ```
        """
        return HcraftPlanningProblem(self.state, self.name, self.purpose)

    def _step_output(self, reward: float, terminated: bool, truncated: bool):
        infos = {
            "action_is_legal": self.action_masks(),
            "score": self.current_score,
            "score_average": self.cumulated_score / self.episodes,
        }
        infos.update(self._tasks_infos())
        return (
            self.state.observation,
            reward,
            terminated or truncated,
            infos,
        )

    def _tasks_infos(self):
        infos = {}
        infos.update(self.task_successes.done_infos)
        infos.update(self.task_successes.rates_infos)
        infos.update(self.terminal_successes.done_infos)
        infos.update(self.terminal_successes.rates_infos)
        return infos

    def _render_rgb_array(self) -> np.ndarray:
        """Render an image of the game.

        Create the rendering window if not existing yet.
        """
        if self.render_window is None:
            self.render_window = HcraftWindow()
        if not self.render_window.built:
            self.render_window.build(self)
        fps = self.metadata.get("video.frames_per_second")
        self.render_window.update_rendering(fps=fps)
        return surface_to_rgb_array(self.render_window.screen)
