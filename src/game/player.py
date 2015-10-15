import networkx as nx
from base_player import BasePlayer
from settings import *

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """

    # You can set up static state here
    sample_step_counter = 0

    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : dict
            The initial state of the game. See state.py for more information.
        """

        return

    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. This function must take less than Settings.STEP_TIMEOUT
        seconds.
        --- Parameters ---
        state : dict
            The state of the game. See state.py for more information.
        --- Returns ---
        commands : command list
            Each command should be generated via self.send_command or
            self.build_command. The commands are evaluated in order.
        """

        # We have implemented a naive bot for you that builds a single station
        # and tries to find the shortest path from it to the pending orders.
        # We recommend making it a bit smarter ;-)

        graph = state.get_graph()
        station = graph.nodes()[0]

        commands = [self.build_command(station)]
        commands.extend([self.send_command(order,
                                           nx.shortest_path(graph, station,
                                                            order.get_node()))
                         for order in state.get_pending_orders()])

        self.sample_step_counter += 1

        return commands
