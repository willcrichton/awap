import networkx as nx

class BasePlayer:
    def build_command(self, node):
        return {
            'type': 'build',
            'node': node
        }

    def send_command(self, order, path):
        return {
            'type': 'send',
            'order': order,
            'path': path
        }

# This is the class the competitors would implement
class Player(BasePlayer):
    def step(self, state):
        if len(state['pending_orders']) == 0: return []

        graph = state['graph']
        station = graph.nodes()[0]

        commands = [self.send_command(order, nx.shortest_path(graph, station, order['node']))
                    for order in state['pending_orders']]
        commands.insert(0, self.build_command(station))

        return commands
