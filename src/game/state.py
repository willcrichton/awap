from copy import deepcopy
from settings import *
import networkx as nx
import json

class State:
    """
    Describes the entire state of the game at a point in time. Tracks the
    following information:
    --- Fields ---
    graph : networkx.Graph
        The graph of the city. Stations and homes both exist on nodes, and edges
        are used to send widgets from stations to homes. Contains node and edge
        information as dictionaries in graph.node[node] and
        graph.edge[source][destination]. Edges are {'in_use': bool} indicating
        whether they are currently in use for an active order. Nodes are
        {'is_station': bool} indicating whether they a station.
    time : int
        The current time step. Starts at 0, incremented by 1 every step.
    money : int
        How much money you have.
    pending_orders : order list
        A list of outstanding orders that do not have widgets set for delivery.
        See order.py for how orders are described.
    active_orders : (order, path) list
        A list of orders with a delivery in progress. Each element in the list
        is a tuple containing the order and a list of nodes corresponding to the
        path that order is taking.
    """

    def __init__(self, graph):
        self.graph = graph
        self.time = 0
        self.money = STARTING_MONEY
        self.pending_orders = []
        self.active_orders = []
        self.over = False

    def get_graph(self): return self.graph
    def get_time(self): return self.time
    def get_money(self): return self.money
    def get_pending_orders(self): return self.pending_orders
    def get_active_orders(self): return self.active_orders

    def to_dict(self):
        obj = deepcopy(self.__dict__)
        del obj['graph']
        obj['pending_orders'] = map(lambda x: x.__dict__, obj['pending_orders'])
        obj['active_orders'] = map(lambda (x, path): (x.__dict__, path), obj['active_orders'])
        return obj

    def incr_money(self, money):
        self.money += money

    def incr_time(self):
        self.time += 1

    def money_from(self, order):
        total = order.get_money() - \
            (self.get_time() - order.get_time_created()) * \
            DECAY_FACTOR
        return max(total, 0)
