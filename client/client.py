from socketIO_client import SocketIO
import fileinput, threading, json

socket = SocketIO('localhost', 8080)

def on_setup(state):
    print state

def on_move_response(resp):
    if not resp: print json.dumps({'error': 'fail'})

def on_update(state):
    print state

def get_input():
    while True:
        args = raw_input('').split(' ')
        socket.emit('move', {
            'block': int(args[0]),
            'rotation': int(args[1]),
            'pos': {
                'x': int(args[2]),
                'y': int(args[3])
            }
        })

threading.Thread(target=get_input).start()

socket.on('setup', on_setup)
socket.on('moveResponse', on_move_response)
socket.on('update', on_update)
socket.wait()

