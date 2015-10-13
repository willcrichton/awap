import networkx as nx
from base_player import BasePlayer

class Player(BasePlayer):
    """
    You will implement this class for the competition. Do not change the class
    name or the base class.
    """

    def __init__(self):
        # Initialize any persistent variables you want here
        pass

    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step.
        -----
        state : dict
           The state of the game. See state.py for more information.
        """

        # We have implemented a naive bot for you, but we recommend making it a
        # bit smarter ;-)

        graph = state.get_graph()
        station = graph.nodes()[0]

        commands = [self.send_command(order, nx.shortest_path(graph, station,
                                                              order.get_node()))
                    for order in state.get_pending_orders()]
        commands.insert(0, self.build_command(station))

        return commands
