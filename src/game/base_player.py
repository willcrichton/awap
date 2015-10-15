class BasePlayer:
    """
    This class provides necessary methods for the Player class you will
    implement. Do not modify this code. You will want to use build_command and
    send_command.
    """

    def build_command(self, node):
        """
        Create a command for building a new station.
        --- Parameters ---
        node : int
            The node in the graph you want to build a station on.
        --- Returns ---
        command : command
            A command which will build a station at the input node.
        """

        return {
            'type': 'build',
            'node': node
        }

    def send_command(self, order, path):
        """
        Create a command for sending widgets to satisfy a particular order.
        --- Parameters ---
        order : dict
            The order object gotten from State.get_pending_orders().
        path  : int list
            All nodes on the path from the source (a station) to the destination
            (given by the order). First element is the source, last is the dest.
        --- Returns ---
        command : command
            A command which will send a widget along the given path.
        """

        return {
            'type': 'send',
            'order': order,
            'path': path
        }
