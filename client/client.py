from socketIO_client import SocketIO
import fileinput

def on_connect():
    print 'connect'

socket = SocketIO('localhost', 8080)
socket.on('connect', on_connect)
    socket.wait()

    while True:
        move = raw_input('')
        print move
