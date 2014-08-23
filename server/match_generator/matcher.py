import itertools
import random
numPlayers = 50 #number of teams competing
numGames = 150 #number of total games to be played

#create every possible game and then shuffle it for even probability
comb = list(itertools.combinations(xrange(1,numPlayers+1), 4))
random.shuffle(comb)

#checks that the game about to be added doesn't conatin any pairs
# of players that have already played.
def under_attack(new_game, games):
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

def get_adj_matrix(answer):
    #create an adjecency matrix for a graph of players where edges are games
    adjMatrix = [[0 for x in xrange(numPlayers)] for x in xrange(numPlayers)]

    for i in range(len(answer)):
        (a,b,c,d) = answer[i] #represent the game as the 6 edges it creates
        edges = [(a,b),(a,c),(a,d),(b,c),(b,d),(c,d),(b,a),(c,a),(d,a),(c,b),(d,b),(d,c)]

        #check that we didn't mess up and then add the edges to the graph
        if(not check_open(edges, adjMatrix)):
            print("we have a problem")
        else:
            for j in edges:
                adjMatrix[j[0]-1][j[1]-1] = i+1
    return adjMatrix


# Neatly print out the adjecency matrix
def display_matrix(answer):
    adjMatrix = get_adj_matrix(answer)
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

# Display number of games each player is missing
def display_num_missing(answer):
    adjMatrix = get_adj_matrix(answer)
    print(map(lambda x: (reduce(lambda a, b: a+1 if (b == 0) else a, x, 0) -1)/3, adjMatrix))

# Output a file with all of the game pairings
def output_answer(answer):
    fo = open("matches.txt", "w")
    for game in answer:
        fo.write(str(game)+"\n")
    fo.close()

# Output a file for use with Dot
def output_dot_file(answer):
    fo = open("matches.dot", "w")
    fo.write("graph matches {\n")
    for game in answer:
        (a,b,c,d) = game #represent the game as the 6 edges it creates
        edges = [(a,b),(a,c),(a,d),(b,c),(b,d),(c,d)]
        for edge in edges:
            fo.write("    " + str(edge[0]) + " -- " + str(edge[1]) +";\n")
    fo.write("}")
    fo.close()    

# Run program and output selected formats
answers = solve(numGames)
first_answer = next(answers)

#display_matrix(first_answer)
output_dot_file(first_answer)
display_num_missing(first_answer)
output_answer(first_answer)
