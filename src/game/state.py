from copy import deepcopy
import networkx as nx
import json

class State:
    """
    Describes the entire state of the game at a point in time. Tracks the
    following information:
    -----
    graph : networkx.Graph
        The graph of the city. Stations and homes both exist on nodes, and edges
        are used to send widgets from stations to homes.
    time : int
        The current time step. Starts at 0, incremented by 1 every step.
    money : int
        How much money you have.
    pending_orders : order list
        A list of outstanding orders that do not have widgets set for delivery.
        See order.py for how orders are described.
    active_orders : order list
        A list of orders with a delivery in progress.
    """

    def __init__(self, graph, starting_money):
        self.graph = graph
        self.time = 0
        self.money = starting_money
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