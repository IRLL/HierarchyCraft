"""# Solving behaviors

HierarchyCraft environments comes with built-in solutions.
For ANY task in ANY HierarchyCraft environment, a solving behavior can be given
thanks to the fact that no feature extraction is required.

This behavior can be called on the observation and will return relevant actions, like any agent.

Solving behavior for any task can simply be obtained like this:

```python
behavior = env.solving_behavior(task)
action = behavior(observation)
```

Solving behaviors can be used for imitation learning, as teacher or an expert policy.

## Example

Let's get a DIAMOND in MineHcraft:

```python
from hcraft.examples import MineHcraftEnv
from hcraft.examples.minecraft.items import DIAMOND
from hcraft.task import GetItemTask

get_diamond = GetItemTask(DIAMOND)
env = MineHcraftEnv(purpose=get_diamond)
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

from hcraft.behaviors.behaviors import (
    AbleAndPerformTransformation,
    GetItem,
    DropItem,
    PlaceItem,
    ReachZone,
)
from hcraft.requirements import RequirementNode, req_node_name
from hcraft.task import GetItemTask, GoToZoneTask, PlaceItemTask, Task

from hebg.unrolling import unroll_graph

if TYPE_CHECKING:
    from hcraft.env import HcraftEnv


def build_all_solving_behaviors(env: "HcraftEnv") -> Dict[str, "Behavior"]:
    """Return a dictionary of handcrafted behaviors to get each item, zone and property."""
    all_behaviors = {}
    all_behaviors = _reach_zones_behaviors(env, all_behaviors)
    all_behaviors = _get_item_behaviors(env, all_behaviors)
    all_behaviors = _drop_item_behaviors(env, all_behaviors)
    all_behaviors = _get_zone_item_behaviors(env, all_behaviors)
    all_behaviors = _do_transfo_behaviors(env, all_behaviors)

    # empty_behaviors = []
    # for name, behavior in all_behaviors.items():
    #     try:
    #         behavior.graph
    #     except ValueError:
    #         empty_behaviors.append(name)
    # for name in empty_behaviors:
    #     all_behaviors.pop(name)

    # TODO: Use learning complexity instead for more generality
    requirements_graph = env.world.requirements.graph

    for behavior in all_behaviors.values():
        if isinstance(behavior, AbleAndPerformTransformation):
            behavior.complexity = 1
            continue
        if isinstance(behavior, GetItem):
            req_node = req_node_name(behavior.item, RequirementNode.ITEM)
        elif isinstance(behavior, DropItem):
            # TODO: this clearly is not general enough,
            # it would need requirements for non-accumulative to be fine
            req_node = req_node_name(behavior.item, RequirementNode.ITEM)
        elif isinstance(behavior, ReachZone):
            req_node = req_node_name(behavior.zone, RequirementNode.ZONE)
        elif isinstance(behavior, PlaceItem):
            req_node = req_node_name(behavior.item, RequirementNode.ZONE_ITEM)
        else:
            raise NotImplementedError
        behavior.complexity = requirements_graph.nodes[req_node]["level"]
        continue

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
        behavior_name = PlaceItem.get_name(task.item_stack.item, task.zone)
    else:
        raise NotImplementedError
    return behavior_name


def _reach_zones_behaviors(env: "HcraftEnv", all_behaviors: Dict[str, "Behavior"]):
    for zone in env.world.zones:
        behavior = ReachZone(zone, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _get_item_behaviors(env: "HcraftEnv", all_behaviors: Dict[str, "Behavior"]):
    for item in env.world.items:
        behavior = GetItem(item, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _drop_item_behaviors(env: "HcraftEnv", all_behaviors: Dict[str, "Behavior"]):
    for item in env.world.items:
        behavior = DropItem(item, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _get_zone_item_behaviors(env: "HcraftEnv", all_behaviors: Dict[str, "Behavior"]):
    for zone in [None] + env.world.zones:  # Anywhere + in every specific zone
        for item in env.world.zones_items:
            behavior = PlaceItem(item, env, all_behaviors=all_behaviors, zone=zone)
            all_behaviors[behavior.name] = behavior
    return all_behaviors


def _do_transfo_behaviors(env: "HcraftEnv", all_behaviors: Dict[str, "Behavior"]):
    for transfo in env.world.transformations:
        behavior = AbleAndPerformTransformation(
            env, transfo, all_behaviors=all_behaviors
        )
        all_behaviors[behavior.name] = behavior
    return all_behaviors
