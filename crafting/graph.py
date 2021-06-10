# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from typing import List
from copy import deepcopy

import numpy as np
import networkx as nx

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def compute_color(graph:nx.DiGraph):
    alphas = [1, 1, 0.9, 0.8, 0.7, 0.5, 0.4, 0.3]
    for node in graph.nodes():
        successors = list(graph.successors(node))
        for succ in successors:
            alpha = 0.2
            if graph.nodes[node]['level'] < graph.nodes[succ]['level']:
                if len(successors) < len(alphas):
                    alpha = alphas[len(successors)-1]
            else:
                graph.edges[node, succ]['linestyle'] = "dashed"
            if isinstance(graph.edges[node, succ]['color'], list):
                graph.edges[node, succ]['color'][3] = alpha

def compute_levels(graph:nx.DiGraph, weak_edges_type:List[str]=None):
    """ Compute the hierachical levels of all DiGraph nodes given some weak_edges.

    Adds the attribute 'level' for each node in the given graph.

    Args:
        graph: A networkx DiGraph.
        weak_edges_type: List of weak edges types (only the min level of those will be considered).
            Require edges to have the attribute 'type'.

    """

    if weak_edges_type is None:
        weak_edges_type = []

    def _compute_level_dependencies(graph, node, predecessors):
        strong_dependencies = [0]
        weak_dependencies = []
        incomplete = False
        for pred in predecessors:
            try:
                pred_level = graph.nodes[pred]['level']
                if graph.edges[pred, node]['type'] in weak_edges_type:
                    weak_dependencies.append(pred_level)
                else:
                    strong_dependencies.append(pred_level)
            except KeyError:
                if graph.edges[pred, node]['type'] not in weak_edges_type:
                    incomplete = True
        dependencies = strong_dependencies
        if len(weak_dependencies) > 0:
            dependencies += [min(weak_dependencies)]
        return 1 + max(dependencies), incomplete

    all_nodes_have_level = False
    while not all_nodes_have_level:
        all_nodes_have_level = True
        for node in graph.nodes():
            predecessors = list(graph.predecessors(node))

            if len(predecessors) == 0:
                level = 0
            else:
                level, incomplete = _compute_level_dependencies(graph, node, predecessors)
                if incomplete:
                    all_nodes_have_level = False
            if 'level' in graph.nodes[node] and graph.nodes[node]['level'] != level:
                all_nodes_have_level = False

            graph.nodes[node]['level'] = level

    nodes_by_level = {}
    for node, level in graph.nodes(data='level'):
        try:
            nodes_by_level[level].append(node)
        except KeyError:
            nodes_by_level[level] = [node]

    graph.graph['nodes_by_level'] = nodes_by_level
    graph.graph['depth'] = max(level for level in nodes_by_level)

# pylint: disable=protected-access
def leveled_layout(graph:nx.DiGraph, center=None,
    max_iterations=1000, max_iters_without_new=100,
    iters_without_new=0, initial_temperature=5):
    """ Compute positions for a levelled DiGraph.

    Requires each node to have a 'level' attribute.

    Args:
        graph: A networkx DiGraph.
        center: Center of the graph layout.

    Returns:
        pos: Positions of each node.
        nodes_by_level: List of nodes by levels.

    """
    graph, center = nx.drawing.layout._process_params(graph, center, dim=2)

    nodes_by_level = graph.graph['nodes_by_level']
    pos = {}
    step_size = 1 / max(len(nodes_by_level[level]) for level in nodes_by_level)
    spacing = np.arange(0, 1, step=step_size)
    for level in nodes_by_level:
        n_nodes_in_level = len(nodes_by_level[level])
        if n_nodes_in_level > 1:
            positions = np.linspace(0, len(spacing)-1, n_nodes_in_level,
                endpoint=True, dtype=np.int32)
            positions = spacing[positions]
        else:
            positions = [spacing[(len(spacing)-1)//2]]

        for i, node in enumerate(nodes_by_level[level]):
            pos[node] = [level, positions[i]]

    def energy(pos, nodes_by_level, nodes_strenght=1, edges_strenght=2):

        def dist(x, y):
            x_arr, y_arr = np.array(x), np.array(y)
            return np.linalg.norm(x_arr-y_arr)

        energy = 0
        for level in nodes_by_level:
            for node in nodes_by_level[level]:  
                energy += nodes_strenght * sum(
                    np.square(dist(pos[node], pos[n]))
                    for n in nodes_by_level[level] if n != node
                )
                energy -= sum(
                    edges_strenght \
                        # *graph.edges[pred, node]['color'][3]\
                        /abs(max(1, graph.nodes[node]['level'] - graph.nodes[pred]['level']))\
                        /max(1e-6, dist(pos[node], pos[pred]))
                    for pred in graph.predecessors(node)
                )
                energy -= sum(
                    edges_strenght \
                        # *graph.edges[node, succ]['color'][3]\
                        /abs(max(1, graph.nodes[node]['level'] - graph.nodes[succ]['level']))\
                        /max(1e-6, dist(pos[node], pos[succ]))
                    for succ in graph.successors(node)
                )
        return energy

    def neighbor(pos, step_size):
        pos_copy = deepcopy(pos)
        choosen_node = np.random.choice(list(pos_copy.keys()))
        try:
            choosen_node = int(choosen_node)
        except ValueError:
            pass
        x, y = pos_copy[choosen_node][0], pos_copy[choosen_node][1]

        if y <= 0:
            sign = 1
        elif y >= 1:
            sign = -1
        else:
            sign = np.random.choice((-1, 1))

        new_pos = [x, y + sign * step_size]

        for n in pos:
            if n != choosen_node and np.all(np.isclose(new_pos, pos_copy[n])):
                pos_copy[choosen_node], pos_copy[n] = pos_copy[n], pos_copy[choosen_node]
                return pos_copy

        pos_copy[choosen_node] = new_pos
        return pos_copy

    def prob_keep(temperature, delta_e):
        return min(1, np.exp(delta_e/temperature))

    energy_pos = energy(pos, nodes_by_level)
    for k in range(max_iterations):
        new_pos = neighbor(pos, step_size)
        new_e = energy(new_pos, nodes_by_level)
        temperature = initial_temperature/(k+1)
        iters_without_new += 1
        prob = prob_keep(temperature, energy_pos - new_e)
        if np.random.random() < prob:
            print(f"{k}\t({prob:.0%})\t{energy_pos:.2f}->{new_e:.2f}", end='\r')
            pos, energy_pos = new_pos, new_e
            iters_without_new = 0

        if iters_without_new >= max_iters_without_new:
            break

    return pos

def option_layout(graph:nx.DiGraph):
    graph, _ = nx.drawing.layout._process_params(graph, None, dim=2)

    nodes_by_level = {}
    for node, node_data in graph.nodes(data=True):
        level = node_data['level']
        try:
            nodes_by_level[level].append(node)
        except KeyError:
            nodes_by_level[level] = [node]

    pos = {}
    for level in range(max(nodes_by_level.keys()) + 1):
        for i, node in enumerate(nodes_by_level[level]):
            preds = list(graph.predecessors(node))
            if len(preds) == 0:
                x_pos = 0
            elif len(preds) == 1 and graph.edges[preds[0], node]['color'] == 'red':
                x_pos = pos[preds[0]][0]
            else:
                other_nodes_x = [pos[n][0] for n in nodes_by_level[level] if n in pos]
                x_pos = 1 + max(other_nodes_x + [0])
            pos[node] = [x_pos, -level]
    return pos

def draw_networkx_nodes_images(graph, pos, ax, img_zoom=1):
    for n in graph:
        img = graph.nodes[n]['image']
        color = graph.nodes[n]['color']
        if img is not None:
            min_dim = min(img.shape[:2])
            min_ax_shape = min(ax._position.width, ax._position.height)
            imagebox = OffsetImage(img, zoom = 100 * img_zoom * min_ax_shape / min_dim )
            imagebox = AnnotationBbox(
                imagebox, pos[n],
                frameon=True, box_alignment=(0.5, 0.5)
            )

            imagebox.patch.set_facecolor('None')
            imagebox.patch.set_edgecolor(color)
            imagebox.patch.set_linewidth(3)
            imagebox.patch.set_boxstyle("round", pad=0.15)
            ax.add_artist(imagebox)
