from game.game import Game
from game.player import Player
from server.server import run_server
import sys
import networkx as nx

def print_usage():
    print 'Usage: %s [shell|web]' % sys.argv[0]
    exit()

# TODO: consider using YAML for file
# TODO: other settings (RNG seed, starting money, etc...)
def parse_settings(filename):
    with open(filename) as f:
        lines = f.readlines()

    graph = nx.Graph()
    graph.add_nodes_from(range(int(lines[0])))

    for line in lines[1:]:
        toks = line.split()
        graph.add_edge(int(toks[0]), int(toks[1]))

    return {
            'graph': graph
    }

def main():
    player = Player()
    settings = parse_settings('src/settings.awap')
    game = Game(player, settings['graph'])

    if len(sys.argv) == 1: print_usage()

    command = sys.argv[1]
    if command == 'web':
        run_server(game)
    elif command == 'shell':
        while not game.is_over():
            game.step()

        print 'Money: %s' % game.state['money']
    else: print_usage()

if __name__ == "__main__":
    main()
