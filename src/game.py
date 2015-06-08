import networkx as nx
import random
from copy import deepcopy

BUILD_COST = 1000
STARTING_MONEY = 1000
GRAPH_NODE_COUNT = 100

GENERIC_COMMAND_ERROR = 'Commands must be constructed with build_command and send_command'

V_ERRORS = 0
V_GAME_INFO = 1
VERBOSE_LEVELS = [V_ERRORS, V_GAME_INFO]


class Game:
    def __init__(self, player):
        self.state = {
            'graph': nx.complete_graph(GRAPH_NODE_COUNT),
            'time': 0,
            'money': STARTING_MONEY,
            'buildings': [],
            'pending_orders': [],
            'active_orders': []
        }
        self.player = player

    def no_orders(self):
        return len(self.state['pending_orders']) == 0 and len(self.state['active_orders']) == 0

    def generate_order(self):
        # Can return None instead if we don't want to make an order this time step
        nodes = self.state['graph'].nodes()
        return {
            'node': random.choice(nodes),
            'money': 100,
            'time_created': self.state['time'],
            'time_started': None
        }

    def log(self, message, verbocity):
        if(verbocity in VERBOSE_LEVELS):
            print 'Time %d: %s' % (self.state['time'], message)

    def build_cost(self):
        # Might be geometrically increasing
        return BUILD_COST

    def can_satisfy_order(self, order, path):
        return True

    def process_commands(self, commands):
        for command in commands:
            if not isinstance(command, dict) or 'type' not in command:
                self.log(GENERIC_COMMAND_ERROR, V_ERRORS)
                continue
            
            command_type = command['type']

            # Building a new location on the graph
            if command_type == 'build':
                if not 'node' in command:
                    self.log(GENERIC_COMMAND_ERROR, V_ERRORS)
                    continue

                node = command['node']
                if node in self.state['buildings']:
                    self.log('Can\'t build on the same place you\'ve already built', V_ERRORS)
                    continue
                
                cost = self.build_cost()
                if self.state['money'] < cost:
                    self.log('Don\'t have enough money to build a restaurant, need %s' % cost, V_ERRORS)
                    continue

                self.log("Build station at " + str(node), V_GAME_INFO)
                self.state['money'] -= cost
                self.state['buildings'].append(node)

            # Satisfying an order ("send"ing a train)
            elif command_type == 'send':
                if 'order' not in command or 'path' not in command:
                    self.log(GENERIC_COMMAND_ERROR)
                    continue

                order = command['order']
                path = command['path']
                self.log("Player accepted order and provided path: " + str(path), V_GAME_INFO)
                if not self.can_satisfy_order(order, path):
                    self.log('Can\'t satisfy order %s with path %s' % (order, path), V_ERRORS)
                    continue

                self.state['pending_orders'].remove(order)
                self.state['active_orders'].append((order, path))

                order['time_started'] = self.state['time']

    def step(self):
        print("====== Starting step " + str(self.state['time']) + " ======")

        # Create new order for player
        new_order = self.generate_order()
        if new_order is not None:
            if new_order['node'] in self.state['buildings']:
                self.state['money'] += new_order['money']
            else:
                self.state['pending_orders'].append(new_order)
        self.log("Created new order at " + str(new_order['node']), V_GAME_INFO)

        # Evaluate which orders the player has finished
        predicate = lambda (order, path): (order['time_started'] + len(path) - 1) <= self.state['time']
        completed_orders = filter(predicate, self.state['active_orders'])
        for (order, path) in completed_orders:
            self.log("Player completed order to " + str(order['node']), V_GAME_INFO)
            self.state['active_orders'].remove((order, path))
            self.state['money'] += order['money'] # times a scaling factor?
        
        # Let player take their turn
        print "Player has " + str(self.state['money']) + " dollars before their turn"
        commands = self.player.step(deepcopy(self.state))
        if not isinstance(commands, list):
            self.log('Player.step must return a list of commands', V_ERRORS)
        else:
            self.process_commands(commands)

        self.state['time'] += 1
