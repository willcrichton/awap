import math
import random
import networkx as nx

DEBUG = 1               # 0 = no debug messages, 1 = debug messages

GRAPH_SEED = 'i am a graph seed!'   # Seed for generating a graph
ORDER_SEED = 'i am an order seed!'  # Seed for generating orders
GRAPH_SIZE = 100        # Graph size
HUBS = 5                # Number of hubs where orders are centered around
ORDER_CHANCE = 0.9      # Chance that some order will be created at a step
ORDER_VAR = 3.0         # Stddev for the Gaussian used to generate random walk
SCORE_MEAN = 100.0      # Mean for score distribution of an order
SCORE_VAR = 25.0        # Stddev for score distribution of an order
STARTING_MONEY = 1000   # Starting money value
BUILD_COST = 1000       # Cost to build a widget station
DECAY_FACTOR = 2.0      # Amount that order value decays per step
GAME_LENGTH = 100       # Number of steps in a game
INIT_TIMEOUT = 1.0
STEP_TIMEOUT = 0.5

# These two constants modify the GridGraph
SPARCITY = 0.02         # Proportion of edges which will be removed
DIAGONALS = 0.2        # Proportion of vertices with diagonals

def NODE_INDEX(row, col, row_size):
    return row * row_size + col

# General class that returns various settings that will be used
class Settings:

    # Returns an nx.Graph object specifying the graph
    def Graph(self):
        # Try these included graphs! Play around with the constants!
        # Feel free to define your own graph for testing.

        return self.GridGraph()
        # return nx.connected_watts_strogatz_graph(GRAPH_SIZE, 5, 0.3, seed=GRAPH_SEED)
        # return nx.random_regular_graph(5, GRAPH_SIZE, seed=GRAPH_SEED)

    # Parameters passed to the game
    def Params(self):
       
        # Hubs are the the center of where orders are being generated from
        # These hubs will be unknown to your code running in player.py
        random.seed(GRAPH_SEED)
        hubs = []
        for i in range(HUBS):
            hubs.append(int(random.random() * GRAPH_SIZE))

        return {
            'debug': DEBUG,
            'graph_size': GRAPH_SIZE,
            'seed': ORDER_SEED,
            'hubs': hubs,
            'order_chance': ORDER_CHANCE,
            'order_var': ORDER_VAR,
            'score_mean': SCORE_MEAN,
            'score_var': SCORE_VAR,
            'starting_money': STARTING_MONEY,
            'build_cost': BUILD_COST,
            'decay_factor': DECAY_FACTOR,
            'game_length': GAME_LENGTH,
            'init_timeout': INIT_TIMEOUT,
            'step_timeout': STEP_TIMEOUT,
        }

    # A very visualizable grid graph (GRAPH_SIZE should be a square)
    def GridGraph(self):
        random.seed(GRAPH_SEED)
        width = int(round(math.sqrt(GRAPH_SIZE)))
        if width**2 != GRAPH_SIZE:
            raise ValueError("GRAPH_SIZE must be a square for GridGraph")

        # Generate the base grid (no diagonals added yet)
        graph = nx.Graph()
        graph.add_nodes_from(range(GRAPH_SIZE))

        # NOTE: there is no check for graph connectivity!
        # Add horizontal edges
        for r in range(width):
            for c in range(width - 1):
                if random.random() > SPARCITY:
                    graph.add_edge(NODE_INDEX(r, c, width),
                                   NODE_INDEX(r, c+1, width))

        # Add vertical edges
        for r in range(width - 1):
            for c in range(width):
                if random.random() > SPARCITY:
                    graph.add_edge(NODE_INDEX(r, c, width),
                                   NODE_INDEX(r+1, c, width))

        # Add some random diagonals
        for i in range(int(GRAPH_SIZE * DIAGONALS / 2)):
            row = int(random.random() * width-1)
            col = int(random.random() * width-1)
            ind1 = NODE_INDEX(row, col, width)
            ind2 = NODE_INDEX(row+1, col+1, width)
            graph.add_edge(ind1, ind2)

        for i in range(int(GRAPH_SIZE * DIAGONALS / 2)):
            row = int(random.random() * width-1)
            col = int(random.random() * width-1) + 1
            ind1 = NODE_INDEX(row, col, width)
            ind2 = NODE_INDEX(row+1, col-1, width)
            graph.add_edge(ind1, ind2)

        return graph

