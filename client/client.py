#!/usr/bin/python
from socketIO_client import SocketIO, BaseNamespace
from subprocess import Popen, PIPE, STDOUT
import pty
import os
import sys
import fileinput
import threading
import json

stdin_handle = None

def write(message):
    if type(message) is not str:
        message = json.dumps(message)
    
    stdin_handle.write(message + "\n")
    stdin_handle.flush()

# All events from socket go to the GameNamespace
class GameNamespace(BaseNamespace):
    def on_setup(self, *args):
        state = args[0]
        write(state)

    def on_update(self, *args):
        state = args[0]
        write(state)

    def on_moveResponse(self, *args):
        resp = args[0]
        if not resp: write(json.dumps({'error': 'fail'}))

def main():
    # Check for input args
    if (len(sys.argv)<2):
        print "Usage: python " + sys.argv[0] + " <your binary path and args>"
        print "e.g. python " + sys.argv[0] + " python echo.py"
        print "e.g. python " + sys.argv[0] + " 'python echo.py'"
        exit(1)

    # Set up command to run using arguments
    cmd = " ".join(sys.argv[1:])
    master, slave = pty.openpty()

    # Set up pipes
    pipe = Popen(['python','game.py'], stdin=PIPE, stdout=PIPE)

    global stdin_handle
    stdin_handle = pipe.stdin
    sys.stdin = pipe.stdout

    socket = SocketIO('127.0.0.1', 8080, GameNamespace)

    def on_setup(state):
        write(state)

    def get_input():
        while True:
            try:
                args = raw_input('').split(' ')
            except:
                # Script died or game is over
                exit()

            print 'received from script', args
            socket.emit('move', {
                'block': int(args[0]),
                'rotation': int(args[1]),
                'pos': {
                    'x': int(args[2]),
                    'y': int(args[3])
                }
            })

    threading.Thread(target=get_input).start()
    socket.wait()

if __name__ == "__main__":
    main()
