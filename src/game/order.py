import json

order_id = 0

class Order:
    def __init__(self, state, node, money):
        global order_id
        self.node = node
        self.money = money
        self.time_created = state.get_time()
        self.time_started = None
        self.id = order_id
        order_id += 1

    def __repr__(self):
        return "node %s, money %s, id %s" % (str(self.node), str(self.money), str(self.id))
        #return "Order %d" % self.id

    def get_node(self): return self.node
    def get_money(self): return self.money
    def get_time_created(self): return self.time_created
    def get_time_started(self): return self.time_started

    def to_json(self):
        return json.dumps(self.__dict__)

    def set_time_started(self, time):
        self.time_started = time
