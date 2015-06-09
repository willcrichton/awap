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
    first_step = True;

    def step(self, state):
        if len(state['pending_orders']) == 0: return []
        
        graph = state['graph']
        for (u,v) in graph.edges():
            if(graph.edge[u][v]['in_use'] == True):
                graph.remove_edge(u,v)
        station = graph.nodes()[0]
        order = state['pending_orders'][0]
        try:
            path = nx.shortest_path(graph, station, order['node'])

            if(self.first_step):
                self.first_step = False
                return [self.build_command(station),
                        self.send_command(order, path)]
            else:
                return [self.send_command(order, path)]
        except:
            print("Client found no path")
            return []
