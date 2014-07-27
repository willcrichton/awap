#!/usr/bin/python

#################################################################################
# Client.py - Communicates with server via socketIO and AI via stdin/stdout
# Gets moves via stdin in the form of "# # # #" (block index, # rotations, x, y)
# Consists mainly of setup, helper funtions, and a loop that gets moves.
#################################################################################

from socketIO_client import SocketIO, BaseNamespace
from subprocess import Popen, PIPE, STDOUT
from argparse import ArgumentParser
import pty
import os
import sys
import fileinput
import threading
import json

SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 8080

team_id = ''
stdin_handle = None

# write message to stdout
def write(message):
    if type(message) is not str:
        message = json.dumps(message)
    
    stdin_handle.write(message + "\n")
    stdin_handle.flush()

# All events from socket go to the GameNamespace
class GameNamespace(BaseNamespace):
    def on_connect(self, *args):
        print 'Connected to server'
        self.emit('teamId', team_id)
    
    def on_setup(self, *args):
        initState = args[0]
        write(initState)

    def on_update(self, *args):
        state = args[0]
        write(state)

    def on_moveRequest(self, *args):
        moveReq = args[0]
        write(moveReq)

    def on_moveResponse(self, *args):
        resp = args[0]
        if not resp: write(json.dumps({'error': 'fail'}))

    def on_end(self, *args):
        scores = args[0]
        print(scores)

def main():

    # Set up command to run using arguments
    parser = ArgumentParser()
    parser.add_argument("command", help="A game.py file for AI input")
    parser.add_argument("teamid", default='test', help="A teamid for serverside identification, default is test")
    args = parser.parse_args()

    # Set up pipes
    global team_id
    team_id = args.teamid
    pipe = Popen(args.command.split(' '), stdin=PIPE, stdout=PIPE)

    global stdin_handle
    stdin_handle = pipe.stdin
    sys.stdin = pipe.stdout

    socket = SocketIO(SOCKET_HOST, SOCKET_PORT, GameNamespace)

    def on_setup(state):
        write(state)

    def get_input():
        while True:
            try:
                args = raw_input('').split(' ')
            except:
                # Script died or game is over
                exit()

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
