from game.game import Game
from game.player import Player
from server.server import run_server
import sys, json, zlib

def print_usage():
    print 'Usage: %s [shell|web]' % sys.argv[0]
    exit(1)

def main():
    player = Player()
    game = Game(player)

    if len(sys.argv) == 1: print_usage()

    command = sys.argv[1]
    if command == 'web':
        run_server(game)
    elif command == 'shell':
        output = json.dumps(game.get_graph())
        while not game.is_over():
            game.step()
            output += json.dumps(game.to_dict())

        print zlib.compress(output)
    else: print_usage()

if __name__ == "__main__":
    main()
