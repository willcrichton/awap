from heapq import *

scores = {}
matches = []

for match in open('scores', 'r').read().strip().split('\n'):
    infos = match.split(',')
    players = set()

    for info in infos:
        parts = info.split(' ')
        name = parts[0]
        points = int(parts[1])

        if not name in scores:
            scores[name] = 0

        scores[name] += points
        players.add(name)

    if players not in matches:
        matches.append(players)

for match in matches:
    mscores = [(scores[player], player) for player in match]
    mscores.sort()
    mscores.reverse()

    if mscores[0][0] == mscores[1][0] or mscores[1][0] == mscores[2][0]:
        print 'TIE', mscores
    else:
        print mscores[0][1], mscores[1][1]