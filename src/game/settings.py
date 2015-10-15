import logging as log

LOG_LEVEL = log.INFO    # change this to log.WARNING or log.ERROR to suppress
                        # info/warning messages

INIT_TIMEOUT = 10.0     # Number of seconds your Player can take to load
STEP_TIMEOUT = 0.5      # Number of seconds your Player.step can take

STARTING_MONEY = 1000   # Starting money value
BUILD_COST = 1000       # Cost to build a widget station
BUILD_FACTOR = 1.5      # Multiplicative factor for each subsequent station
DECAY_FACTOR = 2.0      # Amount that order value decays per step
GAME_LENGTH = 100       # Number of steps in a game

GRAPH_SIZE = 100        # Graph size
HUBS = 5                # Number of hubs where orders are centered around
ORDER_CHANCE = 0.9      # Chance that some order will be created at a step
ORDER_VAR = 3.0         # Stddev for the Gaussian used to generate random walk
SCORE_MEAN = 100.0      # Mean for score distribution of an order
SCORE_VAR = 25.0        # Stddev for score distribution of an order

GRAPH_SEED = 'i am a graph seed!'   # Seed for generating a graph
ORDER_SEED = 'i am an order seed!'  # Seed for generating orders

# These two constants modify the grid_graph
SPARSITY = 0.02        # Proportion of edges which will be removed
DIAGONALS = 0.2        # Proportion of vertices with diagonals
