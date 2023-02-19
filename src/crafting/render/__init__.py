""" Render : Module for rendering Crafting environments. """

import os


def _default_resources_path() -> str:
    render_dir = os.path.dirname(__file__)
    return os.path.join(render_dir, "default_resources")
