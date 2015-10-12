import networkx as nx

class BasePlayer:
    """
    This class provides necessary methods for the Player class you will
    implement. Do not modify this code. You will want to use build_command and
    send_command.
    """

    # Utility for the calling code. Ignore me
    def _step(self, state, queue):
        queue.put(self.step(state))

    def build_command(self, node):
        """
        Create a command for building a new station.
        -----
        node : int
            The node in the graph you want to build a station on.
        """

        return {
            'type': 'build',
            'node': node
        }

    def send_command(self, order, path):
        """
        Create a command for sending widgets to satisfy a particular order.
        -----
        order : dict
            The order object gotten from State.get_pending_orders().
        path  : int list
            All nodes on the path from the source (a station) to the destination
            (given by the order). First element is the source, last is the dest.
        """

        return {
            'type': 'send',
            'order': order,
            'path': path
        }

class Player(BasePlayer):
    """
    You will implement this class for the competition. Do not change the class
    name or the base class.
    """

    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. We have implemented a naive bot for you, but we recommend
        making it a bit smarter ;-)
        -----
        state : dict
           The state of the game. See state.py for more information.
        """

        graph = state.get_graph()
        station = graph.nodes()[0]

        commands = [self.send_command(order, nx.shortest_path(graph, station, order.get_node()))
                    for order in state.get_pending_orders()]
        commands.insert(0, self.build_command(station))

        return commands
