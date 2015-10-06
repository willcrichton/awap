from game.game import Game
from game.player import Player
from server.server import run_server
import sys, json

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
        print json.dumps(game.get_graph())
        while not game.is_over():
            game.step()
            print json.dumps(game.to_dict())

        print 'Money: %s' % game.state.get_money()
    else: print_usage()

if __name__ == "__main__":
    main()
