from game.game import Game
from server.server import run_server
import sys, json

def print_usage():
    print 'Usage: %s [shell|web]' % sys.argv[0]
    exit(1)

def make_game():
    return Game("game.player")

def main():
    if len(sys.argv) == 1: print_usage()

    command = sys.argv[1]
    if command == 'web':
        run_server(make_game())
    elif command == 'shell':
        game = make_game()
        while not game.is_over():
            game.step()

        print 'Final money: $%d' % game.state.get_money()
    else: print_usage()

if __name__ == "__main__":
    main()
