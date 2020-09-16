import hashlib
import base64

from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler

guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True

HOST, PORT = '127.0.0.1', 9999

class WebSocketHandler(BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).decode('utf8').strip() 
        headers = self.data.split("\r\n")

        # is it a websocket request?
        if "Connection: Upgrade" in self.data and "Upgrade: websocket" in self.data:
            # getting the websocket key out
            for h in headers:
                if "Sec-WebSocket-Key" in h:
                    key = h.split(" ")[1]
                    
            # calculating response as per protocol RFC
            self.handshake(key)
            
            while True:
                payload = self.decode_frame(bytearray(self.request.recv(1024).strip()))
                decoded_payload = payload.decode('utf-8')
                self.send_frame(payload)
                if "bye" == decoded_payload.lower(): return
        else:
            self.request.sendall("HTTP/1.1 400 Bad Request\r\n" + \
                                 "Content-Type: text/plain\r\n" + \
                                 "Connection: close\r\n" + \
                                 "\r\n" + \
                                 "Incorrect request")

    def handshake(self,key):
        # calculating response as per protocol RFC
        key = key + guid
        resp_key = base64.standard_b64encode(hashlib.sha1(key.encode()).digest())
        resp="HTTP/1.1 101 Switching Protocols\r\n" + \
             "Upgrade: websocket\r\n" + \
             "Connection: Upgrade\r\n" + \
             "Sec-WebSocket-Accept: %s\r\n\r\n"%(resp_key.decode())
        self.request.sendall(resp.encode())
        
    def decode_frame(self,frame):
        opcode_and_fin = frame[0]

        # assuming it's masked, hence removing the mask bit(MSB) to get len. also assuming len is <125
        payload_len = frame[1] - 128

        mask = frame [2:6]
        encrypted_payload = frame [6: 6+payload_len]

        payload = bytearray([ encrypted_payload[i] ^ mask[i%4] for i in range(payload_len)])

        return payload

    def send_frame(self, payload):
        # setting fin to 1 and opcpde to 0x1
        frame = [129]
        # adding len. no masking hence not doing +128
        frame += [len(payload)]
        # adding payload
        frame_to_send = bytearray(frame) + payload

        self.request.sendall(frame_to_send)

def run_ws(host='127.0.0.1', port=9999):
    print(f"[+] Starting server ws://{host}:{port}")
    with ThreadingTCPServer((HOST, PORT), WebSocketHandler) as server:
        server.serve_forever()

if __name__ == "__main__":
    run_ws('localhost', 9999)