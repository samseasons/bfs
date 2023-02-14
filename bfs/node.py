import json
import socket
from threading import Thread
from .crypto import decrypt, encrypt
from .util import config, decode, encode

backlog = 128
packet = 2048

class node:
    def __init__(self, host=None, port=None):
        self.key = encode(config['key'])
        self.host = host or config['host']
        self.port = port or config['port']
        self.peers = config['peers']
        self.threads = {}
              
    def start(self, port=None):
        port = port or self.port
        if self.port not in self.threads:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            thread = Thread(target=self._start)
            self.threads[self.port] = thread
            thread.start()
            
    def _start(self):
        self.connected = True
        while self.connected:
            try:
                self.server.listen(backlog)
                conn, addr = self.server.accept()
                Thread(target=self.serve, args=(conn, addr)).start()
            except OSError as error:
                if '[Errno 22] Invalid argument' not in str(error):
                    print('OSError:', error)
                    
    def serve(self, conn, addr):
        try:
            request = decrypt(conn.recv(packet), self.key)
            if request[:5] == b'path:':
                file = open(request[5:], 'rb')
                line = file.read(packet)
                while line:
                    conn.send(line)
                    line = file.read(packet)
                conn.send(line)
                file.close()
        finally:
            conn.close()

    def request(self, request, path, peer):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((peer['ip'], peer['port']))
        try:
            if isinstance(request, str):
                request = encode(request)
            self.client.send(encrypt(request, self.key))
            file = open(path, 'wb')
            line = self.client.recv(packet)
            while line:
                file.write(line)
                line = self.client.recv(packet)
            file.close()
        finally:
            self.client.close()

    def stop(self):
        self.connected = False
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()
        for port in list(self.threads):
            self.threads[port].join()
            del self.threads[port]