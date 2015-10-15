import networkx as nx
from base_player import BasePlayer

from time import sleep

class Player(BasePlayer):
    """
    You will implement this class for the competition. Do not change the class
    name or the base class.
    """

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        ----
        state : dict
          The initial state of the game. See state.py for more information.
        """

        return

    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. This function must take less than Settings.STEP_TIMEOUT
        seconds.
        -----
        state : dict
           The state of the game. See state.py for more information.
        """

        # We have implemented a naive bot for you that builds a single station
        # and tries to find the shortest path from it to the pending orders.
        # We recommend making it a bit smarter ;-)

        graph = state.get_graph()
        station = graph.nodes()[0]

        commands = [self.send_command(order, nx.shortest_path(graph, station,
                                                              order.get_node()))
                    for order in state.get_pending_orders()]
        commands.insert(0, self.build_command(station))

        return commands
