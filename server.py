import selectors
import socket
import sched
import sys

import bcrypt

from client import PlayerConnection
from recurring import Task
from structure import Player


class Server(object):
    def __init__(self, state):
        self.state = state

        self.selector = selectors.DefaultSelector()

        self.events = sched.scheduler()

        self.sock = socket.socket()
        self.sock.bind(('localhost', 4000))
        self.sock.listen()
        self.sock.setblocking(False)
        self.selector.register(self.sock, selectors.EVENT_READ, self.accept)

    def accept(self, sock, mask):
        client, addr = self.sock.accept()
        client.setblocking(False)

        conn = PlayerConnection(client, self)
        self.selector.register(client, selectors.EVENT_READ, conn.ready)
        self.handle_connect(conn)

    def handle_connect(self, conn):
        conn.send_wrapped('Hi there!')
        conn.send_wrapped('')
        conn.send('Your Name: ')

        print('CLIENT CONNECTED')

    def handle_disconnect(self, conn):
        self.selector.unregister(conn.sock)

        player = self.state.query(Player).filter_by(socket_id=conn.id).one_or_none()
        if player:
            player.socket_id = None
            self.state.commit()

        print('CLIENT DISCONNECTED')

    def receive_input(self, conn, data):
        print('INPUT RECEIVED:', data)
        if data == 'STOP':
            raise sys.exit()

        if conn.state == 'init':
            conn.preamble['name'] = data
            conn.state = 'login_password'
        elif conn.state == 'login_password':
            player = self.state.query(Player).filter_by(name=conn.preamble['name']).one_or_none()
            if player:
                if bcrypt.checkpw(data.encode('ascii'), player.password):
                    if player.socket_id:
                        # It may be better to forceably kill the existing socket and replace with this one
                        conn.send_wrapped('Duplicate logins are not allowed.')
                        conn.state = 'reinit'
                    else:
                        conn.send_wrapped('Welcome back!')
                        conn.state = 'playing'

                        player.socket_id = conn.id
                        self.state.commit()
                else:
                    conn.send_wrapped('Login failed.')
                    conn.state = 'reinit'
            else:
                conn.send_wrapped('Login failed.')
                conn.state = 'reinit'
            conn.preamble = {}

        if conn.state == 'reinit':
            conn.state = 'init'
            conn.send_wrapped('')
            conn.send('Your Name: ')
        elif conn.state == 'login_password':
            conn.send('Your Password: ')


@Task(0.1, start='hot', priority=-1)
def check_sockets(server):
    events = server.selector.select(0)
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
