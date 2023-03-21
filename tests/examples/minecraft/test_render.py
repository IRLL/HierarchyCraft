from hcraft.examples.minecraft.env import MineHcraftEnv
from hcraft.render.utils import build_transformation_image


def test_render_transformation():
    env = MineHcraftEnv()
    for transfo in env.world.transformations:
        build_transformation_image(transfo, env.world.resources_path)
