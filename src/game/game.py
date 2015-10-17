import networkx as nx
import random
import json
import multiprocessing
import logging as log
import functools
import traceback
from importlib import import_module
from copy import deepcopy
from state import State
from order import Order
from threading import Thread
from settings import *
from graphs import generate_graph

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    log.error(traceback.format_exc(e))
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
    def __init__(self, player_module_path):
        log.basicConfig(level=LOG_LEVEL,
                        format='%(levelname)7s:%(filename)s:%(lineno)03d :: %(message)s')
        self.random = random.Random()
        self.state = State(generate_graph())
        G = self.state.get_graph()
        for (u, v) in G.edges():
            G.edge[u][v]['in_use'] = False # True if edge is used for any train

        for n in G.nodes():
            G.node[n]['is_station'] = False  # True if the node is a player's building

        def initialize_player(state):
            module = import_module(player_module_path)
            return module.Player(state)

        func = timeout(timeout=INIT_TIMEOUT)(initialize_player)
        try:
            player = func(deepcopy(self.state))
        except:
            exit()

        self.player = player
        self.random.seed('I am an order seed!')

        hubs = deepcopy(G.nodes())
        random.shuffle(hubs)
        self.hubs = hubs[:HUBS]

    def to_dict(self):
        G = self.state.get_graph()
        dict = self.state.to_dict()
        dict['buildings'] = [i for i, x in G.node.iteritems() if x['is_station']]
        return dict

    def get_graph(self):
        return nx.to_dict_of_dicts(self.state.get_graph())

    # True iff there's no orders pending or active
    def no_orders(self):
        return len(self.state.get_pending_orders()) == 0 and len(self.state.get_active_orders()) == 0

    # True iff the game should end
    def is_over(self):
        # Arbitrary end condition for now, should think about this
        return self.state.get_time() >= GAME_LENGTH

    # Create a new order to put in pending_orders
    # Can return None instead if we don't want to make an order this time step
    def generate_order(self):
        if (self.random.random() > ORDER_CHANCE):
            return None

        graph = self.state.get_graph()
        node = self.random.choice(self.hubs)

        # Perform a random walk on a Gaussian distance from the hub
        for i in range(int(abs(self.random.gauss(0, ORDER_VAR)))):
            node = self.random.choice(graph.neighbors(node))

        # Money for the order is from a Gaussian centered around 100
        money = int(self.random.gauss(SCORE_MEAN, SCORE_VAR))

        return Order(self.state, node, money)

    # Get the cost for constructing a new building
    # TODO: CHANGEME??
    def build_cost(self):
        current = len([i for i, x in self.state.graph.node.iteritems() if x['is_station']])
        return INIT_BUILD_COST * (BUILD_FACTOR ** current)

    # Converts a list of nodes into a list of edge pairs
    # e.g. [0, 1, 2] -> [(0, 1), (1, 2)]
    def path_to_edges(self, path):
        return [(path[i], path[i + 1]) for i in range(0, len(path) - 1)]

    # True iff the user can satisfy the given order with the given path
    def can_satisfy_order(self, order, path):
        G = self.state.get_graph()
        for (u, v) in self.path_to_edges(path):
            if G.edge[u][v]['in_use']:
                log.warning('Cannot use edge (%d, %d) that is already in use (your path: %s)' % (u, v, path))
                return False

        if not G.node[path[0]]['is_station']:
            log.warning('Path must start at a station')
            return False

        if path[-1] != order.get_node():
            log.warning('Path must end at the order node')
            return False

        return True

    # Attempt to execute each of the commands returned from the player
    def process_commands(self, commands):
        if not isinstance(commands, list):
            log.warning('Player.step must return a list of commands')
            return

        GENERIC_COMMAND_ERROR = 'Commands must be constructed with build_command and send_command'
        G = self.state.get_graph()
        for command in commands:
            if not isinstance(command, dict) or 'type' not in command:
                log.warning(GENERIC_COMMAND_ERROR)
                continue

            command_type = command['type']

            # Building a new location on the graph
            if command_type == 'build':
                if not 'node' in command:
                    log.warning(GENERIC_COMMAND_ERROR)
                    continue

                node = command['node']
                if G.node[node]['is_station']:
                    log.warning('Can\'t build on the same place you\'ve already built')
                    continue

                cost = self.build_cost()
                if self.state.get_money() < cost:
                    log.warning('Don\'t have enough money to build a restaurant, need %s' % cost)
                    continue

                self.state.incr_money(-cost)
                G.node[node]['is_station'] = True

            # Satisfying an order ("send"ing a train)
            elif command_type == 'send':
                if 'order' not in command or 'path' not in command:
                    log.warning(GENERIC_COMMAND_ERROR)
                    continue

                order = command['order']
                path = command['path']
                if not self.can_satisfy_order(order, path):
                    log.warning('Can\'t satisfy order %s with path %s' % (order, path))
                    continue

                pending_orders = self.state.get_pending_orders()
                for i in range(0, len(pending_orders)):
                    if pending_orders[i].id == order.id:
                        del(pending_orders[i])
                        break

                self.state.get_active_orders().append((order, path))

                for (u, v) in self.path_to_edges(path):
                    G.edge[u][v]['in_use'] = True
                    G.edge[v][u]['in_use'] = True

                order.set_time_started(self.state.get_time())

    # Take the world through a time step
    def step(self):
        if self.is_over():
            log.warning("Attempted to step after game is over")
            return

        log.info("~~~~~~~ TIME %04d ~~~~~~~" % self.state.get_time())

        G = self.state.get_graph()

        # First create a new order
        new_order = self.generate_order()
        if new_order is not None:
            if G.node[new_order.get_node()]['is_station']:
                self.state.incr_money(new_order.get_money())
            else:
                self.state.get_pending_orders().append(new_order)

        # Then remove all finished orders (and update graph)
        predicate = lambda (order, path): \
                    (order.get_time_started() + len(path) - 1) <= \
                    self.state.get_time()
        completed_orders = filter(predicate, self.state.get_active_orders())
        for (order, path) in completed_orders:
            self.state.get_active_orders().remove((order, path))
            money_gained = self.state.money_from(order)
            self.state.incr_money(money_gained)
            log.info("Fulfilled order of %d" % money_gained)

            for (u, v) in self.path_to_edges(path):
                G.edge[u][v]['in_use'] = False
                G.edge[v][u]['in_use'] = False

        # Remove all negative money orders
        positive = lambda order: self.state.money_from(order) > 0
        self.state.pending_orders = filter(positive, self.state.get_pending_orders())

        func = timeout(timeout=STEP_TIMEOUT)(self.player.step)
        try:
            commands = func(deepcopy(self.state))
        except:
            commands = []

        self.process_commands(commands)

        # Go to the next time step
        self.state.incr_time()
