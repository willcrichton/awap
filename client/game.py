from subprocess import Popen, PIPE

args = ['python', 'client.py']
p = Popen(args, stdin=PIPE, stdout=PIPE)
(stdout, stdin) = (p.stdout, p.stdin)

#print 'bye', script.communicate('0 0 0 0')
# todo: how does Popen work?