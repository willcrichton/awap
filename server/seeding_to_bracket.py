bracket_size = 16
bracket = [[1,8,9,16],[3,6,11,14],[2,7,11,14],[4,5,12,13]]

a = open('scores', 'r')             #open it
b = a.read()                        #read it
c = b.split('\n')                   #split into games
d = [x.split(',') for x in c]       #split into people
e = [x[0] for x in d]               #remove bots
f = [x.split(' ') for x in e]       #split score from name
g = [(x[0][:-1], x[1]) for x in f]  #make (name, score) tuple
g.sort(key=lambda x: int(x[1]))     #sort by score

while(len(g) % bracket_size != 0):
    g.append(('bot', '0'))

output = ""
offset = len(g)/bracket_size

for i in range(offset):
    for x in bracket:                   #for given offset get matches
        temp = []
        for y in x:
            index = i*bracket_size+y-1
            temp.append(str(g[index][0]))
        output += ' '.join([temp[0], temp[1], temp[2], temp[3]])
        output += "\n"
        output += ' '.join([temp[1], temp[2], temp[3], temp[0]])
        output += "\n"
        output += ' '.join([temp[2], temp[3], temp[0], temp[1]])
        output += "\n"
        output += ' '.join([temp[3], temp[0], temp[1], temp[2]])
        output += "\n"
output = output[:-1]
w = open('matches', 'w')
w.write(output)