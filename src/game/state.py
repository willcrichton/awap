from copy import deepcopy
import networkx as nx
import json

STARTING_MONEY = 1000
GRAPH_NODE_COUNT = 50

class State:
    def __init__(self):
        self.graph = nx.circular_ladder_graph(GRAPH_NODE_COUNT/2).to_directed()
        self.time = 0
        self.money = STARTING_MONEY
        self.pending_orders = []
        self.active_orders = []

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
