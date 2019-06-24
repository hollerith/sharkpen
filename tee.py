#!/usr/bin/python2.7
#encoding=utf-8

import socket
from threading import Thread
import sys
import signal
from hexdump import dumpgen
import os

from datetime import datetime

VER="\x05"
METHOD="\x00"

SUCCESS="\x00"
SOCKFAIL="\x01"
NETWORKFAIL="\x02"
HOSTFAIL="\x04"
REFUSED="\x05"
TTLEXPIRED="\x06"
UNSUPPORTCMD="\x07"
ADDRTYPEUNSPPORT="\x08"
UNASSIGNED="\x09"

SOCKTIMEOUT=5
RELAYTIMEOUT=500

class Server(Thread):
	def __init__(self, src, dest_ip, dest_port, bind=False):
		Thread.__init__(self)
		self.dest_ip = dest_ip
		self.dest_port = dest_port
		self.sock = src
		self.bind = bind
		self.setDaemon(True)

	def run(self):
		try:
			print("[+] New connection %s:%s" % (self.dest_ip, self.dest_port))
			self.dest = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.dest.connect((self.dest_ip, self.dest_port))

			if self.bind:
				self.sock, addr = sock.accept()

			self.sock.settimeout(RELAYTIMEOUT)
			self.dest.settimeout(RELAYTIMEOUT)

			Relay(self.sock, self.dest, 'Request').start()
			Relay(self.dest, self.sock, 'Response').start()

		except Exception,e:
			print("[-] Error on Server %s" % e.message)
			self.sock.close()
			self.dest.close()

class Relay(Thread):
	def __init__(self, src, dest, action):
		Thread.__init__(self)
		self.src = src
		self.dest = dest
		self.data = ''
		self.dump = ''
		self.setDaemon(True)
		self.action = action

		lhost, lport = src.getpeername()
		rhost, rport = dest.getpeername()
		print("*** [%s:%s]---%s--->[%s:%s] " % (lhost, lport, action, rhost, rport))

	def run(self):
		try:
			data = self.src.recv(16)
			while data:
				if data[-4:] == '\r\n\r\n':
					print("[-] transmission break")
					tamper(self)
				for hx in dumpgen(data):
					self.dump += (hx)
				self.data += data
				self.dest.sendall(data)
				data = self.src.recv(16)
		except Exception,e:
			print("[-] Connection lost %s" % e.message)

		if self.action == 'Response':
			tamper(self)

		self.src.close()
		self.dest.close()

class ProxyServer():
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((ip, port))
		self.sock.listen(1000)

		signal.signal(signal.SIGTERM, self.nuke)
		print("[*] Initialized proxy: ((([%s:%d])))" % (ip, port))

	def run(self):
		while True:
			ip, port = self.ip, self.port
			conn, addr = self.sock.accept()
			conn.settimeout(SOCKTIMEOUT)
			print("[+] %s" % str(datetime.now()))
			try:
				ver, nmethods, methods = (conn.recv(1), conn.recv(1), conn.recv(1))
				conn.sendall(VER+METHOD)
				ver, cmd, rsv, atyp = (conn.recv(1), conn.recv(1), conn.recv(1), conn.recv(1))
				dst_addr = None
				dst_port = None
				if atyp == "\x01":# IPV4
					dst_addr, dst_port = conn.recv(4), conn.recv(2)
					dst_addr = ".".join([str(ord(i)) for i in dst_addr])
				elif atyp=="\x03": # Domain
					addr_len = ord(conn.recv(1))
					dst_addr, dst_port = conn.recv(addr_len), conn.recv(2)
					dst_addr = "".join([unichr(ord(i)) for i in dst_addr])
				elif atyp == "\x04": # IPV6
					dst_addr,dst_port=conn.recv(16),conn.recv(2)
					tmp_addr=[]
					for i in xrange(len(dst_addr)/2):
						tmp_addr.append(unichr(ord(dst_addr[2*i])*256+ord(dst_addr[2*i+1])))
					dst_addr=":".join(tmp_addr)
				dst_port = ord(dst_port[0])*256+ord(dst_port[1])
				print("[*] Connect to %s:%d" % (dst_addr, dst_port))

				server_sock = conn
				server_ip = "".join([chr(int(i)) for i in ip.split(".")])

				if cmd == "\x02": # BIND todo
					conn.close()
				elif cmd == "\x03": # UDP todo
					conn.close()
				elif cmd=="\x01": # CONNECT
					print("[+] Connection ")
					conn.sendall(VER+SUCCESS+"\x00"+"\x01"+server_ip+chr(port/256)+chr(port%256))
					self.server = Server(server_sock, dst_addr, dst_port)
					self.server.start()
				else: # unsupported
					conn.sendall(VER+UNSUPPORTCMD+server_ip+chr(port/256)+chr(port%256))
					conn.close()
			except Exception,e:
				print("[-] Error on starting proxy: %s" % e.message)
				conn.close()

	def attach(self, ws):
		self.wsock = ws
		ws.send('{ "type": "message", "text": "Attached websocket" }')

	def nuke(self, a, b):
		os.system('fuser -k 9999/tcp')

class overloadable(object):

    def __init__(self, func):
        self.callbacks = []
        self.basefunc = func

    def __iadd__(self, func):
        if callable(func):
            self.__isub__(func)
            self.callbacks.append(func)
        return self

    def callback(self, func):
        if callable(func):
            self.__isub__(func)
            self.callbacks.append(func)
        return func

    def __isub__(self, func):
        try:
            self.callbacks.remove(func)
        except ValueError:
            pass
        return self

    def __call__(self, *args, **kwargs):
        result = self.basefunc(*args, **kwargs)
        for func in self.callbacks:
            newresult = func(result)
            result = result if newresult is None else newresult
        return result

@overloadable
def tamper(conn):
	print('[ ] tamper stub')
	return conn

if __name__=='__main__':
	try:
		p = ProxyServer('0.0.0.0', 9999)
		p.run()
	except Exception,e:
		print("Main startup error: %s" % e.message)
