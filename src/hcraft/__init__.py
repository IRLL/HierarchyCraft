"""
.. include:: ../../README.md

## Custom purposes for agents in HierarchyCraft environments

HierarchyCraft allows users to specify custom purposes (one or multiple tasks) for agents in their environments.
This feature provides a high degree of flexibility and allows users to design environments that
are tailored to specific applications or scenarios.
This feature enables to study mutli-task or lifelong learning settings.

See [`hcraft.purpose`](https://irll.github.io/HierarchyCraft/hcraft/purpose.html) for more details.

## Solving behavior for all tasks of most HierarchyCraft environments

HierarchyCraft also includes solving behaviors that can be used to generate actions
from observations that will complete most tasks in any HierarchyCraft environment, including user-designed.
Solving behaviors are handcrafted, and may not work in some edge cases when some items are rquired in specific zones.
This feature makes it easy for users to obtain a strong baseline in their custom environments.

See [`hcraft.solving_behaviors`](https://irll.github.io/HierarchyCraft/hcraft/solving_behaviors.html) for more details.

## Visualizing the underlying hierarchy of the environment (requirements graph)

HierarchyCraft gives the ability to visualize the hierarchy of the environment as a requirements graph.
This graph provides a potentialy complex but complete representation of what is required
to obtain each item or to go in each zone, allowing users to easily understand the structure
of the environment and identify key items of the environment.

For example, here is the graph of the 'MiniCraftUnlock' environment where the goal is to open a door using a key:
![Unlock requirements graph](../../docs/images/requirements_graphs/MiniHCraftUnlock.png)


And here is much more complex graph of the 'MineHcraft' environment shown previously:
![Minehcraft requirements graph](../../docs/images/requirements_graphs/MineHcraft.png)

See [`hcraft.requirements`](https://irll.github.io/HierarchyCraft/hcraft/requirements.html) for more details.

"""

import hcraft.state as state
import hcraft.solving_behaviors as solving_behaviors
import hcraft.purpose as purpose
import hcraft.transformation as transformation
import hcraft.requirements as requirements
import hcraft.env as env
import hcraft.examples as examples
import hcraft.world as world
import hcraft.planning as planning

from hcraft.elements import Item, Stack, Zone
from hcraft.transformation import Transformation
from hcraft.env import HcraftEnv
from hcraft.state import HcraftState
from hcraft.purpose import Purpose
from hcraft.render.human import get_human_action, render_env_with_human
from hcraft.task import GetItemTask, GoToZoneTask, PlaceItemTask


__all__ = [
    "HcraftState",
    "Transformation",
    "Item",
    "Stack",
    "Zone",
    "HcraftEnv",
    "get_human_action",
    "render_env_with_human",
    "Purpose",
    "GetItemTask",
    "GoToZoneTask",
    "PlaceItemTask",
    "state",
    "transformation",
    "purpose",
    "solving_behaviors",
    "requirements",
    "world",
    "env",
    "planning",
    "examples",
]
