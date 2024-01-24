from pathlib import Path
from typing import TYPE_CHECKING, Type

import pytest
from pytest_mock import MockerFixture


from hcraft.examples import EXAMPLE_ENVS
from hcraft.env import HcraftEnv

if TYPE_CHECKING:
    import matplotlib.pyplot


@pytest.mark.slow
@pytest.mark.parametrize("env_class", EXAMPLE_ENVS)
def test_can_draw(env_class: Type[HcraftEnv], mocker: MockerFixture):
    draw_plt = True
    draw_html = True
    save = False
    env = env_class()
    requirements = env.world.requirements
    requirements_dir = Path("docs", "images", "requirements_graphs")

    if draw_plt:
        plt: "matplotlib.pyplot" = pytest.importorskip("matplotlib.pyplot")

        width = max(requirements.depth, 10)
        height = max(9 / 16 * width, requirements.width / requirements.depth * width)
        resolution = max(64 * requirements.depth, 900)
        dpi = resolution / width

        fig, ax = plt.subplots()
        plt.tight_layout()
        fig.set_size_inches(width, height)

        save_path = None
        if save:
            save_path = requirements_dir / f"{env.name}.png"
        requirements.draw(ax, save_path=save_path, dpi=dpi)

        plt.close()

    if draw_html:
        pytest.importorskip("pyvis")
        mocker.patch("pyvis.network.webbrowser.open")
        requirements_dir.mkdir(exist_ok=True)
        filepath = requirements_dir / f"{env.name}.html"
        if not save:
            mocker.patch("pyvis.network.Network.write_html")
        requirements.draw(engine="pyvis", save_path=filepath, with_web_uri=False)
