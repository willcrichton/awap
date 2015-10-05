import random
import networkx as nx

GRAPH_SEED = 'i am a random seed'
REQUEST_SEED = 'i am a different random seed'
GRAPH_SIZE = 10         # Graph height & width
SPARCITY = 0.05         # Proportion of edges which will be removed
DIAGONALS = 0.10        # Proportion of vertices with diagonals

def NODE_INDEX(row, col):
    return row * GRAPH_SIZE + col

def NODE_RC(index):
    return (index / GRAPH_SIZE, index % GRAPH_SIZE)

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
        



