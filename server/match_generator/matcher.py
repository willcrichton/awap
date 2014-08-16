import itertools
import random
numPlayers = 40 #number of teams competing
numGames = 104 #number of total games to be played
nm = 0

#create every possible game and then shuffle it for even probability
comb = list(itertools.combinations(xrange(1,numPlayers+1), 4))
random.shuffle(comb)

#checks that the game about to be added doesn't conatin any pairs
# of players that have already played.
def under_attack(new_game, games):
    # global nm
    # nm += 1
    for game in games: 
        if len([i for i in game if (i in new_game)]) > 1:
            return True
    return False

#Basic n-queens algorithm with back-tracking taken from Stack Overflow
# and modified to work with combinations of people rather than locations
def solve(n):
    solutions = [[]]
    for person in range(n):
        solutions = (solution+[comb[i]]
                       for solution in solutions 
                       for i in xrange(len(comb))
                       if not under_attack(comb[i], solution))
    return solutions

#checks that none of the specified edges already exist
def check_open(edges, relArray):
    return all(map(lambda x: relArray[x[0]-1][x[1]-1] == 0, edges))

def display_answer(answer):
    #create an adjecency matrix for a graph of players where edges are games
    adjMatrix = [[0 for x in xrange(numPlayers)] for x in xrange(numPlayers)]

    for i in range(len(answer)):
        (a,b,c,d) = answer[i] #represent the game as the 6 edges it creates
        edges = [(a,b),(a,c),(a,d),(b,c),(b,d),(c,d)]

        #check that we didn't mess up and then add the edges to the graph
        if(not check_open(edges, adjMatrix)):
            print("we have a problem")
        else:
            for j in edges:
                adjMatrix[j[0]-1][j[1]-1] = i+1

    #Neatly print out the answer
    rows = len(adjMatrix)
    cols = len(adjMatrix[0])
    fieldWidth = len(str(numGames))
    print "[ ",
    for row in xrange(rows):
        if (row > 0): print "\n  ",
        print "[ ",
        for col in xrange(cols):
            if (col > 0): print ",",
            format = "%" + str(fieldWidth) + "s"
            print format % str(adjMatrix[row][col]),
        print "]",
    print "]"

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