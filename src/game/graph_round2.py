import networkx as nx
import random
import math
from settings import *

def node_index(row, col, row_size):
    return row * row_size + col

GRAPH_SEED = 'banana phone 123'

def generate_graph():
    return nx.connected_watts_strogatz_graph(GRAPH_SIZE, 5, 0.2, GRAPH_SEED)

