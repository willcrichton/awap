import itertools
import random
numPlayers = 40
numGames = 104
nm = 0

comb = list(itertools.combinations(xrange(1,numPlayers+1), 4))
random.shuffle(comb)

def get_points(game):
	(a,b,c,d) = game
	return [(a,b),(a,c),(a,d),(b,c),(b,d),(c,d)]

def under_attack(new_game, games):
	global nm
	nm += 1
	for game in games:
		if len([i for i in game if (i in new_game)]) > 1:
			return True
	return False

def solve(n):
    solutions = [[]]
    for row in range(n):
        solutions = (solution+[comb[i]]
                       for solution in solutions 
                       for i in xrange(len(comb))
                       if not under_attack(comb[i], solution))
    return solutions

def print2dList(a):
    if (a == []):
        print []
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = len(str(numGames))
    print "[ ",
    for row in xrange(rows):
        if (row > 0): print "\n  ",
        print "[ ",
        for col in xrange(cols):
            if (col > 0): print ",",
            format = "%" + str(fieldWidth) + "s"
            print format % str(a[row][col]),
        print "]",
    print "]"
def set_points(points, num, relArray):
	for x in points:
		relArray[x[0]-1][x[1]-1] = num
	return
def check_open(points, relArray):
	return all(map(lambda x: relArray[x[0]-1][x[1]-1] == 0, points))
def display_answer(answer):
	ar = [[0 for x in xrange(numPlayers)] for x in xrange(numPlayers)]
	for i in range(len(answer)):
		game = answer[i]
		if(not check_open(get_points(game),ar)):
			print("we have a problem")
		else:
			set_points(get_points(game), i+1, ar)
	print2dList(ar)

def output_answer(answer):
    fo = open("matches.txt", "w")
    for game in answer:
        fo.write(str(game)+"\n")
    fo.close()

answers = solve(numGames)
first_answer = next(answers)
# print nm
display_answer(first_answer)
output_answer(first_answer)