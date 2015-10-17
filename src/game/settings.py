import logging as log

LOG_LEVEL = log.DEBUG   # change this to DEBUG, WARNING, ERROR to suppress
                        # info/warning messages

INIT_TIMEOUT = 10.0     # Number of seconds your Player can take to load
STEP_TIMEOUT = 0.5      # Number of seconds your Player.step can take

GAME_LENGTH = 1000      # Number of steps in a game
STARTING_MONEY = 1000   # Starting money value
INIT_BUILD_COST = 1000  # Initial cost to build a widget station
BUILD_FACTOR = 1.5      # Multiplicative factor for each subsequent station
GRAPH_SIZE = 100        # Graph size
HUBS = 5                # Number of hubs where orders are centered around
ORDER_CHANCE = 0.9      # Chance that some order will be created at a step
ORDER_VAR = 3.0         # Stddev for the Gaussian used to generate random walk
DECAY_FACTOR = 8.0      # Amount that order value decays per step
SCORE_MEAN = 100.0      # Mean for score distribution of an order
SCORE_VAR = 50.0        # Stddev for score distribution of an order

# These two constants modify the grid_graph
SPARSITY = 0.02        # Proportion of edges which will be removed
DIAGONALS = 0.3        # Proportion of vertices with diagonals
