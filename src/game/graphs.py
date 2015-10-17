import networkx as nx
import random
import math
from settings import *

def node_index(row, col, row_size):
    return row * row_size + col

GRAPH_SEED = 'I am a graph seed!'

# A very visualizable grid graph (GRAPH_SIZE should be a square)
def grid_graph():
    random.seed(GRAPH_SEED)
    width = int(round(math.sqrt(GRAPH_SIZE)))
    if width**2 != GRAPH_SIZE:
        print width, GRAPH_SIZE
        raise ValueError("GRAPH_SIZE must be a square for grid_graph")

    # Generate the base grid (no diagonals added yet)
    graph = nx.Graph()
    graph.add_nodes_from(range(GRAPH_SIZE))

    # NOTE: there is no check for graph connectivity!
    # Add horizontal edges
    for r in range(width):
        for c in range(width - 1):
            if random.random() > SPARSITY:
                graph.add_edge(node_index(r, c, width),
                               node_index(r, c+1, width))

    # Add vertical edges
    for r in range(width - 1):
        for c in range(width):
            if random.random() > SPARSITY:
                graph.add_edge(node_index(r, c, width),
                               node_index(r+1, c, width))

    # Add some random diagonals
    for i in range(int(GRAPH_SIZE * DIAGONALS / 2)):
        row = int(random.random() * width-1)
        col = int(random.random() * width-1)
        ind1 = node_index(row, col, width)
        ind2 = node_index(row+1, col+1, width)
        graph.add_edge(ind1, ind2)

    for i in range(int(GRAPH_SIZE * DIAGONALS / 2)):
        row = int(random.random() * width-1)
        col = int(random.random() * width-1) + 1
        ind1 = node_index(row, col, width)
        ind2 = node_index(row+1, col-1, width)
        graph.add_edge(ind1, ind2)

    return graph

def generate_graph():
    # Try these included graphs! Play around with the constants!
    # Feel free to define your own graph for testing.

    #return nx.random_regular_graph(5, GRAPH_SIZE, seed=GRAPH_SEED)
    return grid_graph()
