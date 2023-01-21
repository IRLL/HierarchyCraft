"""Module to simply plot the MineCrafting requirement graph."""

import matplotlib.pyplot as plt

from crafting.examples.minecraft.world import McWorld

if __name__ == "__main__":
    world = McWorld()

    fig, axes = plt.subplots(1, 1)
    world.draw_requirements_graph(axes)
    plt.show()
