"""# Solving behaviors

The crafting environment comes with built-in solutions.
For ANY task in ANY crafting environment, a solving behavior can be given 
thanks to the fact that no feature extraction is required.

This behavior can be called on the observation and will return relevant actions, like any agent.

Solving behavior for any task can simply be obtained like this:

```python
behavior = env.solving_behavior(task)
action = behavior(observation)
```

Solving behaviors can be used for imitation learning, as teacher or an expert policy.

## Example

Let's get a DIAMOND in MineCrafting:

```python
from crafting.examples import MineCraftingEnv
from crafting.examples.minecraft.items import DIAMOND
from crafting.task import GetItemTask

get_diamond = GetItemTask(DIAMOND)
env = MineCraftingEnv(purpose=get_diamond)
solving_behavior = env.solving_behavior(get_diamond)

done = False
observation = env.reset()
while not done:
    action = solving_behavior(observation)
    observation, _reward, done, _info = env.step(action)

assert get_diamond.is_terminated # DIAMOND has been obtained !
```


"""


from typing import TYPE_CHECKING, Dict

from hebg import Behavior

from crafting.task import Task, GetItemTask, GoToZoneTask, PlaceItemTask
from crafting.behaviors.behaviors import (
    AbleAndPerformTransformation,
    GetItem,
    PlaceItem,
    ReachZone,
)

if TYPE_CHECKING:
    from crafting.env import CraftingEnv
    from crafting.world import World


def build_all_solving_behaviors(world: "World") -> Dict[str, "Behavior"]:
    """Return a dictionary of handcrafted behaviors to get each item, zone and property."""
    all_behaviors = {}
    all_behaviors = _reach_zones_behaviors(world, all_behaviors)
    all_behaviors = _get_item_behaviors(world, all_behaviors)
    all_behaviors = _get_zone_item_behaviors(world, all_behaviors)
    all_behaviors = _do_transfo_behaviors(world, all_behaviors)
    return all_behaviors


def task_to_behavior_name(task: Task) -> str:
    """Get the behavior name that will solve the given task.

    Args:
        task: Task to be solved.

    Raises:
        NotImplementedError: If task is not supported yet.

    Returns:
        str: Name of the solving behavior.
    """
    if isinstance(task, GetItemTask):
        behavior_name = GetItem.get_name(task.item_stack.item)
    elif isinstance(task, GoToZoneTask):
        behavior_name = ReachZone.get_name(task.zone)
    elif isinstance(task, PlaceItemTask):
        behavior_name = PlaceItem.get_name(task.item_stack.item, task.zones)
    else:
        raise NotImplementedError
    return behavior_name


def _reach_zones_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for zone in env.world.zones:
        behavior = ReachZone(zone, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _get_item_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for item in env.world.items:
        behavior = GetItem(item, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _get_zone_item_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for zone in [None] + env.world.zones:  # Anywhere + in every specific zone
        for item in env.world.zones_items:
            behavior = PlaceItem(item, env, all_behaviors=all_behaviors, zones=zone)
            all_behaviors[behavior.name] = behavior
    return all_behaviors


def _do_transfo_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for transfo in env.world.transformations:
        behavior = AbleAndPerformTransformation(
            env, transfo, all_behaviors=all_behaviors
        )
        all_behaviors[behavior.name] = behavior
    return all_behaviors
