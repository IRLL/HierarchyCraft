# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=attribute-defined-outside-init, no-self-use, missing-function-docstring

""" Module to test that all HEBGraph can be drawn. """

import pytest
import matplotlib.pyplot as plt
from crafting.examples.minecraft.world import McWorld

ALL_BEHAVIORS = McWorld().get_all_behaviors()


class TestDrawHEBGraphs:

    """HEBGraph of the MineCrafting environment should be drawn correctly."""

    @pytest.mark.parametrize("behavior_name", list(ALL_BEHAVIORS.keys()))
    def test_can_draw_(self, behavior_name):
        behavior = ALL_BEHAVIORS[behavior_name]
        fig, ax = plt.subplots()
        fig.set_facecolor("#181a1b")
        ax.set_facecolor("#181a1b")
        behavior.graph.draw(ax, fontcolor="white")
        ax.set_axis_off()
        dpi = 96
        width, height = (1056, 719)
        fig.set_size_inches(width / dpi, height / dpi)
        plt.tight_layout()
        plt.title(behavior_name)
        show = False
        if show:
            plt.show()
        plt.close()
