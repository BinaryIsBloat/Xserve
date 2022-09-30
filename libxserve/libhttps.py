import socket
import os
import ssl
from .shared import *
from .libhttp import *

class https(http):
	def __init__(self, sslkeychain=None, sslprivatekey=None, host="127.0.0.1", port=8443):
		addr = (host, port)
		try:
			baseserver = socket.socket(sock.AF_INET, sock.SOCK_STREAM)
		except socket.error as error:
			srvr_err("Failed to create socket")
			raise error

		# SSL Initialization
		if sslkeychain is None:
			raise MissingSSLCertificate()
		context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
		context.load_cert_chain(sslkeychain, sslprivatekey)
		context.set_alpn_protocols(["http/1.1"])
		self.server = context.wrap_socket(baseserver, server_side=True)

		try:
			self.server.bind(addr)
		except OSError as error:
			srvr_err("Address tuple is not valid on the current machine: %s" %str(addr))
			raise error
		except socket.gaierror as error:
			srvr_err("The address tuple could not be translated to a valid socket address: %s" %str(addr))
			raise error
		self.wrncount = 0
		self.closed = False
		self.buffer = datastream()
		self.bffrcache = datastream()
		self.flags = {}
		self.setflags()
		self.server.listen()
		self.addr = self.server.getsockname()
		return

	def listen(self): # OK
		srvr_inf("Waiting for incoming connections to %s on port %s" %self.addr)
		try:
			self.client, self.clientaddr = self.server.accept()
		except ssl.SSLError:
			clnt_err("Unable to establish SSL connection to client")
			raise SSLConnectionFailure("SSL handshake did not succeed")
		else:
			clnt_srvr("Incoming connection from %s on port %s" %self.clientaddr)