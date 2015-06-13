from game.game import Game
from game.player import Player
from server.server import run_server

def main():
    player = Player()
    game = Game(player)
    run_server(game)

if __name__ == "__main__":
    main()

# def main():
#     command = sys.argv[1]
#     player = Player()
#     game = Game(player)
#     if command == 'web':

#     else:
#         for _ in range(1, 10):
#             game.step()

#     print 'Money: $%d' % game.state['money']

# if __name__ == "__main__":
#     main()
