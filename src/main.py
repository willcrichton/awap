from game.game import Game
from game.player import Player
from game.settings import Settings
from server.server import run_server
import sys

def print_usage():
    print 'Usage: %s [shell|web]' % sys.argv[0]
    exit()

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

        print 'Money: %s' % game.state['money']
    else: print_usage()

if __name__ == "__main__":
    main()
