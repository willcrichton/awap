from copy import deepcopy
import networkx as nx
import json

class State:
    def __init__(self, graph, starting_money):
        self.graph = graph
        self.time = 0
        self.money = starting_money
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
