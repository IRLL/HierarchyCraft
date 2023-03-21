""" Module to define Action nodes for the HEBGraph of the HierarchyCraft environment. """

from typing import TYPE_CHECKING

import numpy as np
from hebg import Action

from hcraft.render.utils import build_transformation_image

if TYPE_CHECKING:
    from hcraft.env import HcraftEnv
    from hcraft.transformation import Transformation


class DoTransformation(Action):

    """Perform a transformation."""

    def __init__(self, transformation: "Transformation", env: "HcraftEnv") -> None:
        image = np.array(
            build_transformation_image(transformation, env.world.resources_path)
        )
        action = env.world.transformations.index(transformation)
        self.transformation = transformation
        super().__init__(
            action,
            name=repr(transformation),
            image=image,
            complexity=1,
        )
