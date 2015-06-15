import networkx as nx
import random
import json
from copy import deepcopy

BUILD_COST = 1000
STARTING_MONEY = 1000
GRAPH_NODE_COUNT = 50

GENERIC_COMMAND_ERROR = 'Commands must be constructed with build_command and send_command'

class Game:
    def __init__(self, player):
        self.state = {
            'graph': nx.circular_ladder_graph(GRAPH_NODE_COUNT/2).to_directed(),
            'time': 0,                  # Current time step
            'money': STARTING_MONEY,    # Current amount of money
            'pending_orders': [],       # Orders generated but not with a train on the way
            'active_orders': []         # Orders with a train on the way
        }
        self.player = player

        G = self.state['graph']
        for (u, v) in G.edges():
            G.edge[u][v]['in_use'] = False # True if edge is used for any train

        for n in G.nodes():
            G.node[n]['building'] = False  # True if the node is a player's building
            G.node[n]['num_orders'] = 0

    def to_json(self):
        copy = deepcopy(self.state)
        copy['node_data'] = copy['graph'].node
        copy['graph'] = nx.to_dict_of_dicts(copy['graph'])
        return json.dumps(copy)

    # True iff there's no orders pending or active
    def no_orders(self):
        return len(self.state['pending_orders']) == 0 and len(self.state['active_orders']) == 0

    # True iff the game should end
    def is_over(self):
        # Arbitrary end condition for now, should think about this
        return self.state['time'] == 10

    # Create a new order to put in pending_orders
    # Can return None instead if we don't want to make an order this time step
    def generate_order(self):
        nodes = self.state['graph'].nodes()
        return {
            'node': random.choice(nodes),         # Originating node for the order
            'money': 100,                         # Initial reward for completing order
            'time_created': self.state['time'],   # Time step when order is created
            'time_started': None                  # Time step when player starts a delivery
        }

    def log(self, message):
        print 'Time %d: %s' % (self.state['time'], message)

    # Get the cost for constructing a new building
    def build_cost(self):
        return BUILD_COST

    # Converts a list of nodes into a list of edge pairs
    # e.g. [0, 1, 2] -> [(0, 1), (1, 2)]
    def path_to_edges(self, path):
        return [(path[i], path[i + 1]) for i in range(0, len(path) - 1)]

    # True iff the user can satisfy the given order with the given path
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

    # Attempt to execute each of the commands returned from the player
    def process_commands(self, commands):
        if not isinstance(commands, list):
            self.log('Player.step must return a list of commands')
            return

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

    # Take the world through a time step
    def step(self):
        G = self.state['graph']

        # First create a new order
        new_order = self.generate_order()
        if new_order is not None:
            if G.node[new_order['node']]['building']:
                self.state['money'] += new_order['money']
            else:
                G.node[new_order['node']]['num_orders'] += 1
                self.state['pending_orders'].append(new_order)

        # Then remove all finished orders (and update graph)
        predicate = lambda (order, path): (order['time_started'] + len(path) - 1) <= self.state['time']
        completed_orders = filter(predicate, self.state['active_orders'])
        for (order, path) in completed_orders:
            self.state['active_orders'].remove((order, path))
            self.state['money'] += order['money'] # times a scaling factor?

            G.node[order['node']]['num_orders'] -= 1

            for (u, v) in self.path_to_edges(path):
                G.edge[u][v]['in_use'] = False

        # Get commands from player and process them
        commands = self.player.step(deepcopy(self.state))
        self.process_commands(commands)

        # Go to the next time step
        self.state['time'] += 1