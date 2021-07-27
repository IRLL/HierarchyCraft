# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=attribute-defined-outside-init

""" Module to test that all OptionGraph can be drawn. """

from option_graph.node import Action
import pytest
import matplotlib.pyplot as plt
from crafting.examples.minecraft.world import McWorld

ALL_OPTIONS = McWorld().get_all_options()

class TestDrawOptionGraphs():

    """OptionGraph of the MineCrafting environment should be drawn correctly. """

    @pytest.mark.parametrize('option_name', list(ALL_OPTIONS.keys()))
    def test_can_draw_(self, option_name):
        option = ALL_OPTIONS[option_name]
        fig, ax = plt.subplots()
        fig.set_facecolor('#181a1b')
        ax.set_facecolor('#181a1b')
        option.graph.draw(ax, fontcolor='white')
        ax.set_axis_off()
        dpi = 96
        width, height = (1056, 719)
        fig.set_size_inches(width/dpi, height/dpi)
        plt.tight_layout()
        plt.title(option_name)
        show = False
        if show:
            plt.show()
        plt.close()
