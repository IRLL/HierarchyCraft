# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module to define Action nodes for the HEBGraph of the Crafting environment. """

from typing import TYPE_CHECKING

import numpy as np
from hebg import Action

from crafting.render.utils import build_transformation_image

if TYPE_CHECKING:
    from crafting.env import CraftingEnv
    from crafting.transformation import Transformation


class DoTransformation(Action):

    """Perform a transformation."""

    def __init__(self, transformation: "Transformation", env: "CraftingEnv") -> None:
        image = np.array(build_transformation_image(transformation, env.resources_path))
        action = env.transformations.index(transformation)
        self.transformation = transformation
        super().__init__(
            action,
            name=str(transformation),
            image=image,
            complexity=1,
        )
