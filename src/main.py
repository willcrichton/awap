from game.game import Game
from game.player import Player
from game.settings import Settings
from server.server import run_server
import sys, json

def print_usage():
    print 'Usage: %s [shell|web]' % sys.argv[0]
    exit(1)

def main():
    player = Player()
    settings = Settings()
    game = Game(player, settings)

    if len(sys.argv) == 1: print_usage()

    command = sys.argv[1]
    if command == 'web':
        run_server(game)
    elif command == 'shell':
        while not game.is_over():
            game.step()

        print 'Final money: %d' % game.state.get_money()
    else: print_usage()

if __name__ == "__main__":
    main()
