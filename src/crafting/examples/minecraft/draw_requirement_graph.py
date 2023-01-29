import matplotlib.pyplot as plt

from crafting import MineCraftingEnv

if __name__ == "__main__":
    fig, ax = plt.subplots()
    env = MineCraftingEnv()
    env.draw_requirements_graph(ax)
    plt.show()
