import random
import networkx as nx

GRAPH_SEED = 'banana phone 123'
ORDER_SEED = 'phanana bone'
GRAPH_SIZE = 10         # Graph height & width
SPARCITY = 0.05         # Proportion of edges which will be removed
DIAGONALS = 0.15        # Proportion of vertices with diagonals
HUBS = 5                # Number of hubs where orders are centered around
ORDER_CHANCE = 0.9      # Chance that some order will be created at a step
ORDER_VAR = 5.0         # Stddev for the Gaussian used to generate orders
SCORE_VAR = 25.0        # Stddev for score distribution (centered around 100)

def NODE_INDEX(row, col):
    return row * GRAPH_SIZE + col

# General class that returns various settings that will be used
class Settings:

    # Returns an nx.Graph object specifying the graph
    def Graph(self):

        random.seed(GRAPH_SEED)

        # Generate the base grid (no diagonals added yet)
        graph = nx.Graph()
        graph.add_nodes_from(range(GRAPH_SIZE**2))

        # NOTE: there is no check for graph connectivity! 
        # Add horizontal edges
        for r in range(GRAPH_SIZE):
            for c in range(GRAPH_SIZE - 1):
                if random.random() > SPARCITY:
                    graph.add_edge(NODE_INDEX(r, c), NODE_INDEX(r, c+1))

        # Add vertical edges
        for r in range(GRAPH_SIZE - 1):
            for c in range(GRAPH_SIZE):
                if random.random() > SPARCITY:
                    graph.add_edge(NODE_INDEX(r, c), NODE_INDEX(r+1, c))

        # Add some random diagonals
        for i in range(int(GRAPH_SIZE**2 * DIAGONALS / 2)):
            row = int(random.random() * GRAPH_SIZE-1)
            col = int(random.random() * GRAPH_SIZE-1)
            ind1 = NODE_INDEX(row, col)
            ind2 = NODE_INDEX(row+1, col+1)
            graph.add_edge(ind1, ind2)

        for i in range(int(GRAPH_SIZE**2 * DIAGONALS / 2)):
            row = int(random.random() * GRAPH_SIZE+1)
            col = int(random.random() * GRAPH_SIZE-1) + 1
            ind1 = NODE_INDEX(row, col)
            ind2 = NODE_INDEX(row+1, col-1)
            graph.add_edge(ind1, ind2)

        return graph

    # Other tune-able parameters used in the game
    def Params(self):
       
        # Hubs are the the center of where orders are being generated from
        # These hubs will be unknown to your code running in player.py
        hubs = []
        for i in range(HUBS):
            row = int(random.random() * GRAPH_SIZE)
            col = int(random.random() * GRAPH_SIZE)
            hubs.append((row, col))

        return {
            'graph_size': GRAPH_SIZE,
            'seed': ORDER_SEED,
            'hubs': hubs,
            'order_chance': ORDER_CHANCE,
            'order_var': ORDER_VAR,
            'score_var': SCORE_VAR
        }
