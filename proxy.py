import os, sys, select, socket
import time
import base64
import socketio

from struct import pack, unpack
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
from hexdump import dumpgen

BUFF_SIZE = 0x1000 #4096
INTERCEPT = True

sio = socketio.Client()

@sio.event
def connect():
    print('[+] Proxy socketio client successfully connected to server.')

@sio.event
def connect_error():
    print('[*] Proxy socketio client failed to connect to server.')

@sio.event
def disconnect():
    print('[-] Proxy socketio client has disconnected from server.')

@sio.event(namespace='/proxy')
def server2proxy(data):
    print(f'[+] Proxy socketio client received data: \n {data}')
    if (data == 'intercept on/off'):
        toggle_intercept()

@sio.event
def multi(message):
    pass

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True

class SocksProxy(StreamRequestHandler):
    global INTERCEPT

    RELAYTIMEOUT=500

    SOCKS_VERSION = 5

    SOCKS_E_SUCCESS = 0
    SOCKS_E_CONN_ERROR = 4
    SOCKS_E_BAD_COMMAND = 7
    SOCKS_E_BAD_ADDRESS = 8

    SOCKS_ADDR_IPv4 = 1
    SOCKS_ADDR_DOMAIN = 3

    def receive(self, size):
        ret = b''
        while len(ret) < size:
            # receive needed amount of data
            data = self.connection.recv(size - len(ret))
            if len(data) <= 0:
                raise(Exception('Client disconnected'))
            ret = b"".join([ret, data])
        return ret

    def stream(self, pid, direction, data):
        if INTERCEPT:
            #print(f'[+] From {pid} sending {direction} proxy data ')
            text = data.decode('UTF-8','backslashreplace')
            dump = os.linesep.join([x for x in dumpgen(data)])
            #print(f"\n\x1b[32mData:\n{text}\x1b[0m")
            #print(f"\x1b[33m{dump}\x1b[0m")
            message = {'pid': pid, 'direction': direction, 'raw': dump, 'text': text}
            sio.emit('message', message, namespace='/proxy')

    def send(self, data):
        self.connection.sendall(data)

    def send_reply(self, command, addr = 0, port = 0):
        self.send(pack('!BBBBIH', self.SOCKS_VERSION, command, 0, self.SOCKS_ADDR_IPv4, addr, port))

    def log(self, message):
        print(f"\x1b[36m[{self.client_address[0]}:{self.client_address[1]}] \x1b[37m{message}\x1b[0m")

    def handle(self):
        self.log('Incoming connection accepted')

        try:
            # receive method request
            method_request = self.receive(1 + 1)
            version, method_num = unpack('BB', method_request)

            if version != self.SOCKS_VERSION:
                raise(Exception('Unsupported protocol version (%d)' % version))

            if method_num > 0:
                methods = self.receive(method_num)  # receive methods list

            # send method reply
            self.send(pack('BB', self.SOCKS_VERSION, 0))

            # receive request
            request = self.receive(1 + 1 + 1 + 1)
            version, command, _, addr_type = unpack('BBBB', request)

            if command == 1:
                if addr_type in [ self.SOCKS_ADDR_IPv4, self.SOCKS_ADDR_DOMAIN ]:
                    success = False

                    if addr_type == self.SOCKS_ADDR_IPv4:
                        addr, port = unpack('!IH', self.receive(4 + 2))
                        addr = socket.inet_ntoa(addr) # convert IP address to string
                        self.log('IPv4: connecting to %s:%d' % (addr, port))
                        success = True
                    elif addr_type == self.SOCKS_ADDR_DOMAIN: # DNS
                        addr_len, = unpack('B', self.receive(1))
                        addr = self.receive(addr_len)
                        port, = unpack('!H', self.receive(2))
                        self.log('DNS: connecting to %s:%d' % (addr, port))
                        try:
                            addr = socket.gethostbyname(addr)
                            success = True
                        except socket.gaierror:
                            self.log('ERROR: Unable to resolve hostname')
                            self.send_reply(self.SOCKS_E_CONN_ERROR)

                    if success:
                        success = False
                        try:
                            # connect to the remote host
                            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            remote.connect(( addr, port ))
                            bind_addr, bind_port = remote.getsockname()
                            bind_addr, = unpack('!I', socket.inet_aton(bind_addr))
                            self.send_reply(self.SOCKS_E_SUCCESS, bind_addr, bind_port)
                            success = True
                        except socket.error:
                            self.log('ERROR: Unable to connect to the remote server')
                            self.send_reply(self.SOCKS_E_CONN_ERROR)

                        if success:
                            self.log('Connection established')
                            # transfer data between client and remote host
                            self.exchange_loop(self.connection, remote)
                else:
                    # bad address type
                    self.send_reply(self.SOCKS_E_BAD_ADDRESS)
            else:
                # bad command
                self.send_reply(self.SOCKS_E_BAD_COMMAND)

        except Exception as error:
            self.log(f"ERROR: { str(error) }")

        # disconnect client
        self.server.close_request(self.request)
        self.log('Connection closed')

    def exchange_loop(self, client, remote):
        while True:
            # wait until client or remote is available for read
            stdin, stdout, stderr = select.select([ client, remote ], [], [])

            # ====>
            if client in stdin:
                data = client.recv(BUFF_SIZE)
                data = data.replace(b'Accept-Encoding: gzip, deflate', b'Accept-Encoding: deflate')

                if len(data) == 0: break
                if remote.send(data) <= 0: break
                self.stream(self.client_address[1], 'request', data)

            # <====
            if remote in stdin:
                data = remote.recv(BUFF_SIZE)

                if len(data) == 0: break
                if client.send(data) <= 0: break
                self.stream(self.client_address[1], 'response', data)

def toggle_intercept():
    global INTERCEPT
    INTERCEPT = not INTERCEPT

def run_proxy(host='127.0.0.1', port=1080):
    print(f'[+] Connecting to websocket http://{host}:5000/proxy \n')
    sio.connect(f'http://127.0.0.1:5000', transports=['websocket'], namespaces=['/proxy'])

    print(f"[+] Starting server socks5://{host}:{port} \n")
    with ThreadingTCPServer((host, port), SocksProxy) as server:
        server.serve_forever()

if __name__ == '__main__':
    run_proxy('127.0.0.1', 1080)