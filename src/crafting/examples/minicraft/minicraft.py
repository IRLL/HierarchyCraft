import os

from typing import Optional, List, Dict, Union
from abc import abstractmethod

from crafting.elements import Item, Stack, Zone
from crafting.transformation import Transformation
from crafting.env import CraftingEnv

from crafting.world import world_from_transformations


class MiniCraftEnv(CraftingEnv):
    """Environments representing abstractions from
    [minigrid environments](https://minigrid.farama.org/environments/minigrid/).
    """

    def __init__(
        self,
        minicraft_name: str,
        start_zone: Optional[Zone] = None,
        start_items: Optional[List[Union[Stack, Item]]] = None,
        start_zones_items: Optional[Dict[Zone, List[Union[Stack, Item]]]] = None,
        **kwargs,
    ) -> None:
        """
        Kwargs:
            invalid_reward: Reward given to the agent for invalid actions.
                Defaults to -1.0.
            max_step: Maximum number of steps before episode truncation.
                If None, never truncates the episode. Defaults to None.
            render_window: Window using to render the environment with pygame.
        """
        self.minicraft_name = minicraft_name
        transformations = self.build_transformations()
        world = world_from_transformations(
            transformations=transformations,
            start_zone=start_zone,
            start_items=start_items,
            start_zones_items=start_zones_items,
        )
        world.resources_path = os.path.join(os.path.dirname(__file__), "resources")
        super().__init__(world, name=f"MiniCraft{self.minicraft_name}", **kwargs)

    @abstractmethod
    def build_transformations(self) -> List[Transformation]:
        """Build transformations for this MiniCraft environment"""
        raise NotImplementedError

    @staticmethod
    def description(name: str) -> str:
        """Docstring description of the MiniCraft environment."""

        minigrid_link = (
            "https://minigrid.farama.org/environments/minigrid/<EnvName>Env/"
        )
        minigrid_gif = "https://minigrid.farama.org/_images/<EnvName>Env.gif"

        requirements_image = (
            "https://raw.githubusercontent.com/"
            "IRLL/Crafting/feature/minigrid-to-crafting"
            "/docs/images/requirements_graphs/MiniCraft<EnvName>.png"
        )

        template = "\n".join(
            (
                f"Reproduces the minigrid [<EnvName>]({minigrid_link})"
                " gridworld environment as a crafting environment.",
                "",
                "Minigrid representation:",
                "",
                f'<img src="{minigrid_gif}" width="40%"/>',
                "",
                "Crafting requirements graph:",
                f'<img src="{requirements_image}" width="90%"/>',
            )
        )
        return template.replace("<EnvName>", name)
