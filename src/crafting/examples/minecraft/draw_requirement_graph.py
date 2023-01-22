"""Module to simply plot the MineCrafting requirement graph."""

import matplotlib.pyplot as plt

from crafting.examples.minecraft.world import McWorld


def draw_minecrafting_requirements_graph():
    """Draw the MineCrafting requirement graph using matplotlib."""
    world = McWorld()
    fig = plt.figure(0, figsize=(16, 9), dpi=40)
    ax = fig.add_subplot(111)
    world.draw_requirements_graph(ax)
    return fig, ax


if __name__ == "__main__":
    draw_minecrafting_requirements_graph()
    plt.show()
