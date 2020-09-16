from threading import Thread, Event

from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None, logger=False, engineio_logger=False)

from proxy import run_proxy, toggle_intercept
thread = Thread(target=run_proxy)
thread_stop_event = Event()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/test')
def test():
    thread.start()
    return render_template("index.html")

@socketio.on('connect', namespace='/web')
def connect_web():
    print(f'[+] Web client connected: {request.sid}')

@socketio.on('disconnect', namespace='/web')
def disconnect_web():
    print(f'[-] Web client disconnected: {request.sid}')

@socketio.on('connect', namespace='/proxy')
def connect_proxy():
    print(f'[+] Proxy client connected: {request.sid}')

@socketio.on('disconnect', namespace='/proxy')
def disconnect_proxy():
    print(f'[-] Proxy client disconnected: {request.sid}')

@socketio.on('message', namespace='/web')
def handle_web_message(message):
    print(f'[-] Web client says: {message}')
    if (message == 'toggle intercept on/off'):
        toggle_intercept()
    else:
        thread.start()
        socketio.emit('server2proxy', message, namespace='/proxy')

@socketio.on('message', namespace='/proxy')
def handle_proxy_message(message):
    print(f'[-] proxy message stream {message["direction"]}')
    socketio.emit('server2web', message, namespace='/web')

if __name__ == '__main__':
    socketio.run(app) # port 5000
