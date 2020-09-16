import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('[INFO] Successfully connected to server.')

@sio.event
def connect_error():
    print('[INFO] Failed to connect to server.')

@sio.event
def disconnect():
    print('[INFO] Disconnected from server.')

class ProxyClient(object):
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.server_port = 5001

    def setup(self):
        print('[INFO] Connecting to server http://{}:{}...'.format(
            self.server_addr, self.server_port))
        sio.connect(
                'http://{}:{}'.format(self.server_addr, self.server_port),
                transports=['websocket'],
                namespaces=['/proxy'])
        time.sleep(1)
        return self

    def send_data(self, frame, text):
        # Process and send frame to web client
        pass
        
    def check_exit(self):
        pass

    def close(self):
        sio.disconnect()
