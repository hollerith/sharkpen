import inspect
import socket
import signal
import base64
import json
import re

from subprocess import PIPE, Popen
from Queue import Queue, Empty
from threading import Thread
from thread import *
import traceback

from bottle import Bottle, run, template, request, response, redirect, abort, static_file

from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

from pony.orm.integration.bottle_plugin import PonyPlugin
from pony.orm import *
from models import User, Site

from tee import *

app = Bottle()
app.install(PonyPlugin())

LHOST, LPORT = '0.0.0.0', 9090
buffer_size = 8192
regex = '^((http[s]?|ftp):\/)?\/?([^:\/\s]+)(:([^\/]*))?((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(\?([^#]*))?(#(.*))?$'
jsonmsg = """
{
    "type": "data",
    "path": "%s",
    "mode": "%s",
    "lhost": "%s",
    "lport": "%d",
    "rhost": "%s",
    "rport": "%d",
    "dump": "%s"
}
"""

class Object(dict):
    def __getattr__(self, name):
        return self[name]

wsock, tools = None, None
settings = Object({ "phost": LHOST, "pport" : LPORT })

proxy = ProxyServer(settings.phost, settings.pport)

def login_required(fn):
    def check_user(**kwargs):
        username = request.get_cookie("account", secret=secret())

        if username:
            user = select(u for u in User if u.username == username).first()
            args = inspect.getargspec(fn)[0]
            if 'user' in args:
                kwargs['user'] = user
            return fn(**kwargs)
        else:
            redirect("/login")

    return check_user

def secret():
    return 'supersecretsecret'

def check_login(username, password):
    if username == 'admin' and password == secret():
        return True

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def runcmd(chan, command=None):
    host = ''
    if chan is None:
        print('[-] Communication error - no web socket')
        return

    if command is None:
        print('[-] Communication error - no command')
        return

    groups = re.match('^launch (.*) on (.*)$', command)
    if groups:
        tool = groups.group(1)
        host = groups.group(2)
        path = './private/'+tool+'.yaml'
        if host != '(None)' and os.path.isfile(path):
            command = ["bashful", "run", path]
    else:
        command = command.split() # go on - run naked you filthy animal

    try:
        p = Popen(command, env=dict(os.environ, HOST=host), stdout=PIPE, bufsize=1, close_fds=True)
        q = Queue()
        if host:
            try:
                output = open('/tmp/%s.log' % tool)
            except:
                pass
        else:
            output = p.stdout
        t = Thread(target=enqueue_output, args=(output, q))
        t.daemon = True
        t.start()
    except Exception as error:
        chan.send({"type": "message", "text": trace(error)})
        return

    while t.isAlive():
        try:
            message = q.get_nowait() or q.get(timeout=1)
            encoded = base64.b64encode(message)
            chan.send('{ "type": "data", "text": "%s" }' % encoded)
            print('{ "type": "data", "text": "%s" }' % message)
        except Empty:
            pass
    chan.send({"type": "message", "text": '[+} *** job complete ***'})

def trace(error):
	exc_type, exc_obj, exc_tb = error
	tb = traceback.extract_tb(exc_tb)[-1]
	return "[33m%s : %s : %s[00m" % (exc_type, tb[2], tb[1])

def debug(tamper):
    global wsock, settings
    print('[-] local tamper')
    if tamper.data:
        try:
            line = tamper.data.split('\n')[0]
            url = line.split(' ')[1]
        except:
            line = 'Encrypted'
        lhost, lport = tamper.src.getpeername()
        rhost, rport = tamper.dest.getpeername()

        if wsock:
            b64dump = base64.b64encode(tamper.dump)
            action = tamper.action
            message = jsonmsg % (line.strip(), action, lhost, lport, rhost, rport, b64dump)
            wsock.send(message) # maybe encode this
            print(message)

def relay(conn, data):
    global wsock
    line = data.decode('utf-8').split('\n')[0]
    url = line.split(' ')[1]
    groups = re.match(regex, url)
    host = groups.group(3)
    port = groups.group(5) or 80

    print(data)
    b64dump = base64.b64encode(data.decode('utf-8'))
    lhost, lport = conn.src.getpeername()
    rhost, rport = conn.dest.getpeername()

    if wsock:
        message = jsonmsg % (line.strip(), 'Request', lhost, lport, rhost, rport, b64dump)
        wsock.send(message) # maybe encode this

    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.connect((host, port))
    r.send(data)

    reply = r.recv(buffer_size)  # Response
    line = reply.split('\r')[0]
    while reply:
        try:
            conn.send(reply)         # Client
            reply = r.recv(buffer_size)  # Response
        except:
            break

    b64dump = base64.b64encode(reply.decode('utf-8'))
    lhost, lport = conn.dest.getpeername()
    rhost, rport = conn.src.getpeername()

    if wsock:
        message = jsonmsg % (line.strip(), 'Response', lhost, lport, rhost, rport, b64dump)
        wsock.send(message) # maybe encode this

    r.close()
    conn.close()

def http_proxy():
    # web proxy server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((LHOST, LPORT))
    s.listen(20)  # max 20 connections
    print("[*] proxy listening on %s : %d \n" % (LHOST, LPORT))
    while 1:
        conn, addr = s.accept()       # Accept Connection From Client Browser
        data = conn.recv(buffer_size) # Receive Client Data
        start_new_thread(relay, (conn, data))
    s.close()

@app.route('/public/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./public')

@app.route('/')
@login_required
def home(user):
    sites = select(s for s in Site if s.owner.id == user.id)[:]
    return template('home', settings=settings, username=user.username, sites=sites)

@app.route('/site/new')
@login_required
def add_site(user):
    site = Object({"id": "None", "name":'', "color" : '#abcdef', "notes" : '', "owner" : user.id, "targets": ""})
    return template('site', site=site)

@app.route('/site/:id/edit')
@login_required
def show_site(id):
    try:
        site = Site[id]
    except ObjectNotFound:
        abort(404)
    return template('site', site=site)

@app.route('/site/:id/delete')
@login_required
def delete_site(id):
    if id:
        Site[id].delete()
        redirect("/")

@app.route('/site/:id/edit', method='POST')
@login_required
def save_site(id, user):
    print('[-] Jesus saves')
    name = request.forms.get('name')
    if id == 'None':
        s = Site(name=name, owner=user.id)
    else:
        s = Site[id]
        s.name = name
    s.color = request.forms.get('color')
    s.notes = request.forms.get('notes')
    s.targets = request.forms.get('targets')
    redirect("/")

@app.route('/logout')
@login_required
def logout(user):
    response.set_cookie("account", user.username, secret='wrong-secret-key')
    redirect('/')

@app.route('/login')
def login():
    return template('login')

@app.route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if check_login(username, password):
        response.set_cookie("account", username, secret=secret())
        redirect('/')
    else:
        abort(401, "Sorry, access denied.")

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

@app.route('/test')
def test():
    return template('test')

@app.route('/tools')
def tools():
    global tools
    tools = request.environ.get('wsgi.websocket')
    if not tools:
        abort(400, 'Expected WebSocket request.')

    while True:
        try:
            message = tools.receive()
            if message ==  'Connected with command server':
                tools.send('{ "type": "message", "text": "By your command" }')
            else:
                runcmd(tools, message)
        except WebSocketError:
            break

@app.route('/proxy')
def attach_websocket():
    global wsock
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')

    while True:
        try:
            message = wsock.receive()
            wsock.send('{ "type": "message", "text": "%s" }' % message)
        except WebSocketError:
            break

if __name__ == "__main__":

    # socks5 server
    t = Thread(target=proxy.run)
    t.start()

    tamper += debug   # first class overload

    # wsgi server
    print("[*] Sh4rkP3n listen on %s : %d \n" % (LHOST, 9999))
    server = WSGIServer((LHOST, 9999), app, handler_class=WebSocketHandler)
    server.serve_forever()
