"""Module to simply plot the MineCrafting requirement graph."""

import matplotlib.pyplot as plt

from crafting.examples.minecraft.world import McWorld


def draw_minecrafting_requirements_graph():
    """Draw the MineCrafting requirement graph using matplotlib."""
    world = McWorld()
    fig, ax = plt.subplots(1, 1)
    world.draw_requirements_graph(ax)
    return fig, ax


if __name__ == "__main__":
    draw_minecrafting_requirements_graph()
    plt.show()
