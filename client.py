import uuid
import textwrap
import string


class PlayerConnection(object):
    id_mapping = {}

    @staticmethod
    def id(id):
        return PlayerConnection.id_mapping.get(id, None)

    def __init__(self, sock, server):
        self.sock = sock
        self.server = server
        self.buffer = ''
        self.id = str(uuid.uuid4())
        self.state = 'init'
        self.preamble = {}

        PlayerConnection.id_mapping[self.id] = self

    def ready(self, sock, mask):
        data = self.sock.recv(1000)
        if data:
            for line in data.splitlines(True):
                for c in line.decode('ascii', 'replace'):
                    if c == '\b' and self.buffer:
                        self.buffer = self.buffer[:-1]
                    elif c in string.printable:
                        self.buffer += c
                if self.buffer and self.buffer[-1] in ['\r', '\n']:
                    self.server.receive_input(self, self.buffer.rstrip())
                    self.buffer = ''
        else:
            self.sock.close()
            self.state = 'shutdown'
            del PlayerConnection.id_mapping[self.id]

            self.server.handle_disconnect(self)

    def send(self, data):
        self.sock.send(data.encode('ascii'))

    def send_line(self, data):
        self.send(data + '\r\n')

    def send_wrapped(self, data):
        for l in textwrap.wrap(data) or ['']:
            self.send_line(l)
