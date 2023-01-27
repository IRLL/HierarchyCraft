from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.render.utils import build_transformation_image


def test_render_transformation():
    env = MineCraftingEnv()
    for transfo in env.transformations:
        image = build_transformation_image(transfo, env.resources_path)