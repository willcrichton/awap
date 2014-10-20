##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################

import sys
import json

# Simple point class that supports equality, addition, and rotations
class Point:
    x = 0
    y = 0

    # Can be instantiated as either Point(x, y) or Point({'x': x, 'y': y})
    def __init__(self, x=0, y=0):
        if isinstance(x, dict):
            self.x = x['x']
            self.y = x['y']
        else:
            self.x = x
            self.y = y

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __eq__(self, point):
        return self.x == point.x and self.y == point.y

    # rotates 90deg counterclockwise
    def rotate(self, num_rotations):
        if num_rotations == 1: return Point(-self.y, self.x)
        if num_rotations == 2: return Point(-self.x, -self.y)
        if num_rotations == 3: return Point(self.y, -self.x)
        return self

    def distance(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)

class Game:
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1

    my_corner = (-1, -1)
    my_center = (-1, -1)
    distance_from_center = 20

    # variables for AI
    
    """block_size_weight = (lambda s, bs : bs * 10)
    hits_bonus_weight = (lambda s, hb : 200 if hb else 0)
    bonus_points_weight = (lambda s, bp : bp * 2)
    delta_my_liberties_weight = (lambda s, dml : dml * 2)
    delta_other_liberties_weight = (lambda s, dol : dol * -5)
    area_enclosed_weight = (lambda s, ae : ae * 5)
"""
    points_weight = (lambda s, p: (p**2)/5)
    center_dist_weight = (lambda s: 25 - (1.24**s.distance_from_center))
    def bonus_dist_weight(self, nbd):
      if nbd == 0:
        return 30 
      if nbd == 1:
        return -30
      return 2 * (12 - nbd)

    def __init__(self, args):
        self.interpret_data(args)
        c = self.dimension / 2
        self.my_center = [(c+1, c+1), (c, c+1), (c, c), (c+1, c)][self.my_number]
        #print >> sys.stderr, self.bonus_squares
        self.bonus_dist_map = dict(((bx, by), 0) for (bx, by) in self.bonus_squares if self.grid[bx][by] == -1)
        for i in xrange(25):
          frontier = []
          for (bx, by) in self.bonus_dist_map:
            if self.bonus_dist_map[(bx, by)] == i:
              for (newx, newy) in [(bx+1, by), (bx-1, by), (bx, by+1), (bx, by-1)]:
                if (newx, newy) not in self.bonus_dist_map and newx >= 0 and newx < 20 and newy >= 0 and newy < 20:
                  frontier.append(((newx, newy), i + 1))
          for ((nx, ny), d) in frontier:
            self.bonus_dist_map[(nx, ny)] = d

    def score_move(self, block, point):
        score = 0
        points = len(block)
        new_bonus_dist = 100
        
        newly_occupied = []

        N = self.dimension
        for offset in block:
            s = point + offset
            newly_occupied.append(s)
            new_bonus_dist = min(new_bonus_dist, self.bonus_dist_map[(s.x, s.y)])
            for bs in self.bonus_squares:
                if s.x == bs[0] and s.y == bs[1]:
                    points *= 3
            this_center_dist = s.distance(Point(self.my_center[0], self.my_center[1]))
            self.distance_from_center = min(this_center_dist, self.distance_from_center)

        #N = self.dimension
        #for x in range(0, N):
        #    for y in range(0, N):
        #        if self.grid[x][y] == self.my_number:
        #            for offset in block:
        #                score -= (point + offset).distance(Point(x, y)) * 0.05 / len(block)
        #
        #score -= point.distance(Point(N / 2, N / 2)) * 2
        
        score += self.points_weight(points)
        score += self.center_dist_weight()
        score += self.bonus_dist_weight(new_bonus_dist)
        return int(score)

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)
    def find_move(self):
        moves = []
        N = self.dimension
        for index, block in enumerate(self.blocks):
            for i in range(0, N * N):
                x = i / N
                y = i % N

                for rotations in range(0, 4):
                    new_block = self.rotate_block(block, rotations)
                    if self.can_place(new_block, Point(x, y)):
                        moves.append((index, rotations, new_block, Point(x, y)))

        move_scores = map(lambda (i, j, b, p) : (i, j, b, p, self.score_move(b, p)), moves)
        sorted_moves = sorted(move_scores, lambda (i, j, b1, p1, s1), (k, l, b2, p2, s2) : int(s2 - s1))
        best_move = sorted_moves[0]
        return (best_move[0], best_move[1], best_move[3].x, best_move[3].y)

    # Checks if a block can be placed at the given point
    def can_place(self, block, point):
        onAbsCorner = False
        onRelCorner = False
        N = self.dimension - 1

        corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
        corner = corners[self.my_number]

        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            if (x > N or x < 0 or y > N or y < 0 or self.grid[x][y] != -1 or
                (x > 0 and self.grid[x - 1][y] == self.my_number) or
                (y > 0 and self.grid[x][y - 1] == self.my_number) or
                (x < N and self.grid[x + 1][y] == self.my_number) or
                (y < N and self.grid[x][y + 1] == self.my_number)
            ): return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and self.grid[x - 1][y - 1] == self.my_number) or
                (x > 0 and y < N and self.grid[x - 1][y + 1] == self.my_number) or
                (x < N and y > 0 and self.grid[x + 1][y - 1] == self.my_number) or
                (x < N and y < N and self.grid[x + 1][y + 1] == self.my_number)
            )

        if self.grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
        if not onAbsCorner and not onRelCorner: return False

        return True

    # rotates block 90deg counterclockwise
    def rotate_block(self, block, num_rotations):
        return [offset.rotate(num_rotations) for offset in block]

    # updates local variables with state from the server
    def interpret_data(self, args):
        if 'error' in args:
            debug('Error: ' + args['error'])
            return

        if 'number' in args:
            self.my_number = args['number']

        if 'board' in args:
            self.dimension = args['board']['dimension']
            self.turn = args['turn']
            self.grid = args['board']['grid']
            self.blocks = args['blocks'][self.my_number]
            self.bonus_squares = args['board']['bonus_squares']

            for index, block in enumerate(self.blocks):
                self.blocks[index] = [Point(offset) for offset in block]

#        if 'bonus_squares' in args:
#           self.bonus_squares = args['bonus_squares']

        if (('move' in args) and (args['move'] == 1)):
            send_command(" ".join(str(x) for x in self.find_move()))
        

    def is_my_turn(self):
        return self.turn == self.my_number

def get_state():
    return json.loads(raw_input())

def send_command(message):
    print message
    sys.stdout.flush()

def debug(message):
    send_command('DEBUG ' + str(message))

def main():
    setup = get_state()
    game = Game(setup)

    while True:
        state = get_state()
        game.interpret_data(state)

if __name__ == "__main__":
    main()
