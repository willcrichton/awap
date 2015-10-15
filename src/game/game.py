import networkx as nx
import random
import json
import multiprocessing
from copy import deepcopy
from state import State
from order import Order
from threading import Thread
import functools

GENERIC_COMMAND_ERROR = 'Commands must be constructed with build_command and send_command'

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception, e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception, je:
                print 'error starting thread'
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

class Game:
    def __init__(self, Player, settings):
        self.params = settings.Params()
        self.state = State(settings.Graph(), self.params['starting_money'])

        def initialize_player(state): return Player(state)
        func = timeout(timeout=self.params['init_timeout'])(initialize_player)
        try:
            player = func(deepcopy(self.state))
        except Exception as exception:
            self.log(exception)
            exit()

        self.player = player
        random.seed(self.params['seed'])

        G = self.state.get_graph()
        for (u, v) in G.edges():
            G.edge[u][v]['in_use'] = False # True if edge is used for any train

        for n in G.nodes():
            G.node[n]['building'] = False  # True if the node is a player's building
            G.node[n]['num_orders'] = 0

    def to_dict(self):
        G = self.state.get_graph()
        dict = self.state.to_dict()
        dict['buildings'] = [i for i, x in G.node.iteritems() if x['building']]
        return dict

    def get_graph(self):
        return nx.to_dict_of_dicts(self.state.get_graph())

    # True iff there's no orders pending or active
    def no_orders(self):
        return len(self.state.get_pending_orders()) == 0 and len(self.state.get_active_orders()) == 0

    # True iff the game should end
    def is_over(self):
        # Arbitrary end condition for now, should think about this
        return self.state.over

    # Create a new order to put in pending_orders
    # Can return None instead if we don't want to make an order this time step
    def generate_order(self):
        if (random.random() > self.params['order_chance']):
            return None

        graph = self.state.get_graph()
        hub = random.choice(self.params['hubs'])
        node = graph.nodes()[hub]

        # Perform a random walk on a Gaussian distance from the hub
        for i in range(int(abs(random.gauss(0, self.params['order_var'])))):
            node = random.choice(graph.neighbors(node))

        # Money for the order is from a Gaussian centered around 100
        money = int(random.gauss(100, self.params['score_var']))

        return Order(self.state, node, money)

    def log(self, message):
        if(self.params['debug']):
            print message

    # Get the cost for constructing a new building
    def build_cost(self):
        return self.params['build_cost']

    # Converts a list of nodes into a list of edge pairs
    # e.g. [0, 1, 2] -> [(0, 1), (1, 2)]
    def path_to_edges(self, path):
        return [(path[i], path[i + 1]) for i in range(0, len(path) - 1)]

    # True iff the user can satisfy the given order with the given path
    def can_satisfy_order(self, order, path):
        G = self.state.get_graph()
        for (u, v) in self.path_to_edges(path):
            if G.edge[u][v]['in_use']:
                self.log('Cannot use edge (%d, %d) that is already in use (your path: %s)' % (u, v, path))
                return False

        if not G.node[path[0]]['building']:
            self.log('Path must start at a station')
            return False

        if path[-1] != order.get_node():
            self.log('Path must end at the order node')
            return False

        return True

    # Attempt to execute each of the commands returned from the player
    def process_commands(self, commands):
        if not isinstance(commands, list):
            self.log('Player.step must return a list of commands')
            return

        G = self.state.get_graph()
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
                if self.state.get_money() < cost:
                    self.log('Don\'t have enough money to build a restaurant, need %s' % cost)
                    continue

                self.state.incr_money(-cost)
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

                pending_orders = self.state.get_pending_orders()
                for i in range(0, len(pending_orders)):
                    if pending_orders[i].id == order.id:
                        del(pending_orders[i])
                        break

                self.state.get_active_orders().append((order, path))

                for (u, v) in self.path_to_edges(path):
                    G.edge[u][v]['in_use'] = True

                order.set_time_started(self.state.get_time())

    # Take the world through a time step
    def step(self):
        if self.state.get_time() >= self.params['game_length']:
            self.state.over = True
            return

        self.log("~~~~~~~ TIME %d ~~~~~~~" % self.state.get_time())

        G = self.state.get_graph()

        # First create a new order
        new_order = self.generate_order()
        if new_order is not None:
            if G.node[new_order.get_node()]['building']:
                self.state.incr_money(new_order.get_money())
            else:
                G.node[new_order.get_node()]['num_orders'] += 1
                self.state.get_pending_orders().append(new_order)

        # Then remove all finished orders (and update graph)
        predicate = lambda (order, path): (order.get_time_started() + len(path) - 1) <= self.state.get_time()
        completed_orders = filter(predicate, self.state.get_active_orders())
        for (order, path) in completed_orders:
            self.state.get_active_orders().remove((order, path))
            self.state.incr_money(order.get_money() - (self.state.get_time() - order.get_time_created()) * self.params['decay_factor'])
            self.log("Fulfilled order of " + str(order.get_money() - (self.state.get_time() - order.get_time_created()) * self.params['decay_factor']))
            G.node[order.get_node()]['num_orders'] -= 1

            for (u, v) in self.path_to_edges(path):
                G.edge[u][v]['in_use'] = False

        # Remove all negative money orders
        positive = lambda order: (order.get_money() - (self.state.get_time() - order.get_time_created()) * self.params['decay_factor']) >= 0
        self.state.pending_orders = filter(positive, self.state.get_pending_orders())

        func = timeout(timeout=self.params['step_timeout'])(self.player.step)
        try:
            commands = func(deepcopy(self.state))
        except Exception as exception:
            self.log(exception)
            commands = []

        self.process_commands(commands)

        # Go to the next time step
        self.state.incr_time()
