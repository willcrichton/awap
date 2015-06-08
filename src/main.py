from game import Game
from player import Player

def main():
    player = Player()
    game = Game(player)

    for _ in range(1, 10):
        game.step()

    print 'Money: $%d' % game.state['money']

if __name__ == "__main__":
    main()
