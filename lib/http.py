import socket as sock, os
from .console import *  # Logging
from .base import *     # Special Exceptions
from . import streams   # Buffers & Streams

class http():
	# Initialization Functions
	def __init__(self, host="127.0.0.1", port=8080): # OK
		self.addr = (host, port)
		# Create Socket
		try:
			self.server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
		except sock.error:
			srvr_err("Failed to create socket")
			raise sock.error()
		# Bind Socket
		try:
			self.server.bind(self.addr)
		except OSError as error:
			srvr_err("Address tuple is not valid on the current machine: %s" %str(self.addr))
			raise error
		except sock.gaierror as error:
			srvr_err("The address tuple could not be translated to a valid socket address: %s" %str(self.addr))
			raise error
		# Server Environment Variables
		self.defaultenv = {
			""
		}
		self.wrncount = 0
		self.closed = False
		self.setflags()
		return

	def setflags(flags=None):
		if flags is None:
			self.flags = {
				"debug": True,        # May tweak certain operations to behave diffrently to test for hidden bugs in the code. Should never be enabled in release versions
				"hardbuffer": False,  # All data will be written to a local file instead of the system memory. Recommended for servers which receive huge chunks of data at once or have very limited memory available
				"multibuffer": False, # Enables context-specific buffers with buffersize set to a dictionary
				"buffersize": None,   # Buffer size is unlimited if set to None. Not recommended for servers with large incoming traffic, as the memory may get exhausted very quickly
				"eofmode": "LF",      # May either be LF (line feed) or Buffered. LF means that the server accepts all incoming data until it finds a line feed termination. Buffered means the server accepts all incoming data until the specified buffer is full
				"urimode": "D",       # May either be D (directory) or I (indexed). In directory mode, rooturi should point to the root folder of the ressource. In indexed mode, rooturi should point to an index file in the Xserve Parser Index file format (see specifications)
				"rooturi": os.getcwd(),
				"whitelist": [],      # If one of the lists is empty, the other one will be used to determine allowed IPs. If both lists are empty, no traffic will be blocked. It is not possible for both lists to contain IPs
				"blacklist": [],
				"blockmode": "S",     # May be set to either S (strict) or L (lax). Strict means all connections from a blocked address will be closed immediatly, lax means the server will return an error page and close the connection afterwards
				"timeout": 10,        # The time to wait for a response from the client in seconds
				"retrylimit": 10,     # The maximum amount of retries after a client connection timed out
				"uploadbuffer": None  # The amount of data to send back to a client per packet. None means there is no data limit and the size is determined by the underlying packet size limit. This is default
			}
		else:
			for key in flags.keys():
				if key.lower() in self.flags.keys():
					self.flags[key.lower()] = flags[key]
				else:
					rtime_err("The flag '%s' is not valid and has been ignored" %key)


	# Connection Functions
	def listen(self): # OK
		self.server.listen()
		srvr_inf("Waiting for incoming connections to %s on port %s" %self.addr)
		self.client, self.clientaddr = self.server.accept()
		clnt_srvr("Incoming connection from %s with port %s" %self.clientaddr)

	def close(self): # OK
		try:
			self.client.close()
			del self.client
		except:
			self.do_warn("Unable to close client connection. Assuming undefined client socket and proceeding with %W warnings")
		return


	# Data Functions
	def getdata(self): # Should recieve data from client
		self.client.settimeout(self.flags["timeout"])
		self.buffer = streams.datastream(self.flags["hardbuffer"])
		retriecount = 0
		while retriecount <= self.flags["retrylimit"]:
			try:
				data = self.client.recv(4096)
				if data:
					clnt_srvr("Received %s bytes of data" %len(data))
				else:
					clnt_srvr("Connection has been closed")
					return 1
				self.buffer.write(data)
			except TimeoutError:
				clnt_srvr("No data in socket after waiting for %s seconds" %self.flags["timeout"])
				srvr_inf("Checking for existing previous data")
				if self.data:
					print(f"Server Info: Data buffer not empty, retry {retriecount} / {retries}")
					continue
				else:
					print("Client Error: No data has been sent")
					return 408
			print("Server Info: Performing data check")
			if eofmode == "termination":
				if b"\r\n\r\n" in self.data or b"\n\n" in self.data:
					print("Client => Server: Received EOF string")
					return 0
				if len(self.data) > buffersize:
					print("Client Error: The data buffer was exhausted before an EOF string was sent")
					return 413
				print("Client Info: No EOF string received")
				print("Client => Server: Expecting further data")
			elif eofmode == "buffer":
				if len(self.data) >= buffersize:
					print("Server Info: The expected data buffer is full")
					print("Server Info: Closing data stream")
					return 0
		else:
			print("Client Error: Too many retries")
			return 408

	def returndata(self): # Should send response data to client
		pass

	def storedata(self, storage): # Should flush a temporary buffer to a constant buffer on drive
		pass

	def freedata(self, storage):
		pass


	# Logging Functions
	def do_warn(self, message="Proceeding with %W warnings", warntype="server"): # OK
		self.wrncount += 1
		if warntype == "server":
			srvr_wrn(message.replace("%W", str(self.wrncount)))
		elif warntype == "client":
			clnt_wrn(message.replace("%W", str(self.wrncount)))
		elif warntype == "runtime":
			rtime_wrn(message.replace("%W", str(self.wrncount)))
		else:
			misc_wrn(message.replace("%W", str(self.wrncount)))
		if self.warnlimit > -1:
			if self.warnlimit < self.wrncount:
				rtime_err("Received more warnings than allowed")
				raise WarnLimitReached()


	# Exit Functions
	def shutdown(self, log=True): # Missing modules
		if self.closed:
			if log:
				rtime_inf("Server has already been shut down")
			return
		try:
			self.client.close()
			del self.client
		except:
			if log:
				rtime_inf("Ignoring 1 warning on shutdown: operation <client.close>")
		try:
			self.server.close()
			del self.server
		except:
			if log:
				rtime_inf("Ignoring 1 warning on shutdown: operation <server.close>")
		try:
			self.buffer.flush(operation="flush", obj="_all") # No buffer module
		except:
			if log:
				rtime_inf("Ignoring 1 error on shutdown: operation <buffer.flush>")
		del self.flags
		self.closed = True

	def __del__(self): # OK
		self.shutdown(log=False)


	# HTTP Standards
	status = {
		100: "continue",
		101: "switching_protocols",
		102: "processing",
		103: "early_hints",
		200: "ok",
		201: "created",
		202: "accepted",
		203: "non-authoritative_information",
		204: "no_content",
		205: "reset_content",
		206: "partial_content",
		207: "multi_status",
		208: "already_reported",
		226: "im_used",
		300: "multiple_choices",
		301: "moved_permanently",
		302: "found",
		303: "see_other",
		304: "not_modified",
		305: "use_proxy",
		306: "switch_proxy",
		307: "temporary_redirect",
		308: "permanent_redirect",
		400: "bad_request",
		401: "unauthorized",
		402: "payment_required",
		403: "forbidden",
		404: "not_found",
		405: "method_not_allowed",
		406: "not_acceptable",
		407: "proxy_authentication_required",
		408: "request_timeout",
		409: "conflict",
		410: "gone",
		411: "lenght_required",
		412: "precondition_failed",
		413: "payload_too_large",
		414: "uri_too_long",
		415: "unsupported_media_type",
		416: "range_not_satisfiable",
		417: "expectation_failed",
		418: "i'm_a_teapot",
		421: "misdirected_request",
		422: "unprocessable_entity",
		423: "locked",
		424: "failed_dependency",
		425: "too_early",
		426: "upgrade_required",
		428: "precondition_required",
		429: "too_many_requests",
		431: "request_header_fields_too_large",
		451: "unavailable_for_legal_reasons",
		500: "internal_server_error",
		501: "not_implemented",
		502: "bad_gateway",
		503: "service_unavailable",
		504: "gateway_timeout",
		505: "http_version_not_supported",
		506: "variant_also_negotiates",
		507: "insufficient_storage",
		508: "loop_detected",
		510: "not_extended",
		511: "network_authentication_required"
	}
