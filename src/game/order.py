import json

order_id = 0

class Order:
    """
    Describes a single order from a home. Tracks the following information:
    --- Fields ---
    node : int
        The node (or destination) in the graph issuing the order.
    money : int
        The quantity of cash given for satisfying this order.
    time_created : int
        The time step the order was created.
    time_started : int
        The time step delivery was started to the order. None if the order is
        still pending.
    """

    def __init__(self, state, node, money):
        global order_id
        self.node = node
        self.money = money
        self.time_created = state.get_time()
        self.time_started = None
        self.id = order_id
        order_id += 1

    def __repr__(self):
        return "(id %s, node %s, money %s)" % (str(self.id), str(self.node), str(self.money))

    def get_node(self): return self.node
    def get_money(self): return self.money
    def get_time_created(self): return self.time_created
    def get_time_started(self): return self.time_started

    def to_json(self):
        return json.dumps(self.__dict__)

    def set_time_started(self, time):
        self.time_started = time
