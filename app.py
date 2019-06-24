import inspect
import socket
import signal

import json
import re

from threading import Thread
from thread import *

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

LHOST, LPORT = '0.0.0.0', 9999
buffer_size = 8192
regex = '^((http[s]?|ftp):\/)?\/?([^:\/\s]+)(:([^\/]*))?((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(\?([^#]*))?(#(.*))?$'
msgjson = """
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

wsock = None
proxy = ProxyServer('0.0.0.0', 9999)

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
    if username == 'admin' and password == 'Administrator':
        return True

class Object(dict):
    def __getattr__(self, name):
        return self[name]

@app.route('/public/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./public')

@app.route('/')
@login_required
def index(user):
    sites = select(s for s in Site if s.owner.id == user.id)[:]
    return template('index', username=user.username, sites=sites)

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

@app.route('/home')
def home():
    return template('home')

@app.route('/msgq')
def handle_websocket():
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

@app.route('/attach')
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

def debug(conn):
    global wsock
    print('[-] local tamper')
    if conn.data:
        try:
            line = conn.data.split('\n')[0]
            url = line.split(' ')[1]
        except:
            line = 'Encrypted'
        lhost, lport = conn.src.getpeername()
        rhost, rport = conn.dest.getpeername()

        if wsock:
            message = msgjson % (line.strip(), conn.action, lhost, lport, rhost, rport, conn.dump)
            wsock.send(message) # maybe encode this
            print(message)

if __name__ == "__main__":

    # socks5 server
    t = Thread(target=proxy.run)
    t.start()

    tamper += debug   # first class overload

    # wsgi server
    server = WSGIServer((LHOST, 9090), app, handler_class=WebSocketHandler)
    print("[*] Sh4rkP3n listening on %s : %d \n" % (LHOST, 9090))
    server.serve_forever()
