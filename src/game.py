import networkx as nx
import random
from copy import deepcopy

BUILD_COST = 1000
STARTING_MONEY = 1000
GRAPH_NODE_COUNT = 100

GENERIC_COMMAND_ERROR = 'Commands must be constructed with build_command and send_command'

class Game:
    def __init__(self, player):
        self.state = {
            'graph': nx.circular_ladder_graph(GRAPH_NODE_COUNT/2).to_directed(),
            'time': 0,
            'money': STARTING_MONEY,
            'pending_orders': [],
            'active_orders': []
        }
        self.player = player

        G = self.state['graph']
        for (u, v) in G.edges():
            G.edge[u][v]['in_use'] = False

        for n in G.nodes():
            G.node[n]['building'] = False

    def no_orders(self):
        return len(self.state['pending_orders']) == 0 and len(self.state['active_orders']) == 0

    def generate_order(self):
        # Can return None instead if we don't want to make an order this time step
        nodes = self.state['graph'].nodes()
        return {
            'node': random.choice(nodes),
            'money': 1000,
            'time_created': self.state['time'],
            'time_started': None
        }

    def log(self, message):
        print 'Time %d: %s' % (self.state['time'], message)

    def build_cost(self):
        # Might be geometrically increasing
        return BUILD_COST

    def path_to_edges(self, path):
        return [(path[i], path[i + 1]) for i in range(0, len(path) - 1)]

    def can_satisfy_order(self, order, path):
        G = self.state['graph']
        for (u, v) in self.path_to_edges(path):
            if G.edge[u][v]['in_use']:
                self.log('Cannot use edge (%d, %d) that is already in use (your path: %s)' % (u, v, path))
                return False

        if path[-1] != order['node']:
            self.log('Path must end at the order node')
            return False

        return True

    def process_commands(self, commands):
        G = self.state['graph']
        for command in commands:
            if not isinstance(command, dict) or 'type' not in command:
                self.log(GENERIC_COMMAND_ERROR)
                continue

            command_type = command['type']

            # Building a new location on the graph
            if command_type == 'build':
                if not 'node' in command:
                    self.log(GENERIC_COMMAND_ERROR)
                    continue

                node = command['node']
                if G.node[node]['building']:
                    self.log('Can\'t build on the same place you\'ve already built')
                    continue

                cost = self.build_cost()
                if self.state['money'] < cost:
                    self.log('Don\'t have enough money to build a restaurant, need %s' % cost)
                    continue

                self.state['money'] -= cost
                G.node[node]['building'] = True

            # Satisfying an order ("send"ing a train)
            elif command_type == 'send':
                if 'order' not in command or 'path' not in command:
                    self.log(GENERIC_COMMAND_ERROR)
                    continue

                order = command['order']
                path = command['path']
                if not self.can_satisfy_order(order, path):
                    self.log('Can\'t satisfy order %s with path %s' % (order, path))
                    continue

                self.state['pending_orders'].remove(order)
                self.state['active_orders'].append((order, path))

                for (u, v) in self.path_to_edges(path):
                    G.edge[u][v]['in_use'] = True

                order['time_started'] = self.state['time']

    def step(self):
        G = self.state['graph']
        new_order = self.generate_order()
        if new_order is not None:
            if G.node[new_order['node']]['building']:
                self.state['money'] += new_order['money']
            else:
                self.state['pending_orders'].append(new_order)

        predicate = lambda (order, path): (order['time_started'] + len(path) - 1) <= self.state['time']
        completed_orders = filter(predicate, self.state['active_orders'])
        for (order, path) in completed_orders:
            self.state['active_orders'].remove((order, path))
            self.state['money'] += order['money'] # times a scaling factor?

            for (u, v) in self.path_to_edges(path):
                G.edge[u][v]['in_use'] = False

        commands = self.player.step(deepcopy(self.state))
        if not isinstance(commands, list):
            self.log('Player.step must return a list of commands')
        else:
            self.process_commands(commands)

        self.state['time'] += 1
