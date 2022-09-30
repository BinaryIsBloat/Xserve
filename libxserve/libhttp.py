import socket
import os
from .shared import *

class http:
	# Initialization Functions
	def __init__(self, host="127.0.0.1", port=8080): # OK
		addr = (host, port)
		# Create Socket
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			srvr_err("Failed to create socket")
			raise socket.error()
		# Bind Socket
		try:
			self.server.bind(addr)
		except OSError as error: # Unavailable Address
			srvr_err("Address tuple is not valid on the current machine: %s" %str(addr))
			raise error
		except socket.gaierror as error: # Invalid Address
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

	def setflags(self, **flags): # OK, updated dynamically
		# Note: All values are case-sensitive, setting eofmode to Lf or lf would not work for example
		if flags == {}:
			self.flags = {
				"debug": True,        # May tweak certain operations to behave diffrently to test for hidden bugs in the code. Should never be enabled in release versions
				"hardbuffer": False,  # All data will be written to a local file instead of the system memory. Recommended for servers which receive huge chunks of data at once or have very limited memory available
				"multibuffer": False, # Enables context-specific buffers with buffersize set to a dictionary
				"buffersize": None,   # Buffer size is unlimited if set to None. Not recommended for servers with large incoming traffic, as the memory may get exhausted very quickly. Must not be None if eofmode is set to Buffered
				"eofmode": "LF",      # May either be LF (line feed), SGLF (singular line feed) or Buffered. LF means that the server accepts all incoming data until it finds a line feed termination. SGLF means that that the server accepts all incoming data until it has read an entire line. Buffered means the server accepts all incoming data until the specified buffer is full
				"urimode": "D",       # May either be D (directory) or I (indexed). In directory mode, rooturi should point to the root folder of the ressource. In indexed mode, rooturi should point to an index file in the Xserve Parser Index file format (see specifications)
				"rooturi": os.getcwd(),
				"whitelist": [],      # If one of the lists is empty, the other one will be used to determine allowed IPs. If both lists are empty, no traffic will be blocked. It is not possible for both lists to contain IPs
				"blacklist": [],
				"blockmode": "S",     # May be set to either S (strict) or L (lax). Strict means all connections from a blocked address will be closed immediatly, lax means the server will return an error page and close the connection afterwards
				"timeout": 30,        # The time to wait for a response from the client in seconds
				"retrylimit": 0,      # The maximum amount of retries after a client connection timed out
				"uploadbuffer": None  # The amount of data to send back to a client per packet. None means there is no data limit and the size is determined by the underlying packet size limit. This is default
			}
		else:
			self.flags.update(flags)
		self.buffer.convert(hard=self.flags["hardbuffer"])
		# self.bffrcache.convert(hard=self.flags["hardbuffer"])

	def exportflags(self): # OK
		return self.flags.copy()


	# Connection Functions
	def listen(self): # OK
		srvr_inf("Waiting for incoming connections to %s on port %s" %self.addr)
		self.client, self.clientaddr = self.server.accept()
		clnt_srvr("Incoming connection from %s on port %s" %self.clientaddr)

	def close(self): # OK
		try:
			self.client.close()
		except:
			self.do_warn("Unable to close client connection. Assuming undefined client socket and proceeding with %W warnings")
		else:
			del self.client
		return


	# Data Functions
	def getdata(self, eofmode=None): # UnKnown, receives data from client and returns HTTP status code
		self.buffer.whipe()
		self.client.settimeout(self.flags["timeout"])
		retrycount = 0
		if eofmode is not None:
			self.setflags(eofmode=eofmode)
		while retrycount <= self.flags["retrylimit"]:
			try:
				if self.bffrcache:
					self.bffrcache.seek(0)
					data = self.bffrcache.pop()
				else:
					data = self.client.recv(4096)
			except TimeoutError:
				clnt_srvr("No data in socket after %s seconds" %self.flags["timeout"])
				if self.buffer:
					srvr_inf("Data buffer is not empty, running retry %s / %s" %(retrycount, self.flags["retrylimit"]))
					retrycount += 1
					continue
				else:
					srvr_inf("Data buffer is empty, resetting connection")
					self.close()
					raise ConnectionResetError()
			else:
				if data:
					clnt_srvr("Received %s bytes of data" %len(data))
					self.buffer.write(data)
				else:
					srvr_inf("The connection was reset by the client")
					del self.client
					raise ConnectionResetError()
			finally:
				if "LF" in self.flags["eofmode"]:
					if (self.flags["eofmode"] == "SGLF") and (b"\n" in self.buffer):
							clnt_srvr("Sent EOF terminator")
							self.buffer.seek(0)
							self.buffer.readline(silent=True)
							self.bffrcache.write(self.buffer.pop())
							return 0
					if (self.flags["eofmode"] == "LF") and ((b"\r\n\r\n" in self.buffer) or (b"\n\n" in self.buffer)):
							clnt_srvr("Sent EOF terminator")
							try:
								position = self.buffer.index(b"\r\n\r\n") + 4
							except ValueError:
								position = self.buffer.index(b"\n\n") + 2
							self.buffer.seek(position)
							self.bffrcache.write(self.buffer.pop())
							return 0
					if (self.flags["buffersize"] is not None) and (len(self.buffer) > self.flags["buffersize"]): # The buffer is exhausted and no further data is acceptable
						clnt_err("The data buffer was exhausted before an EOF terminator was sent")
						return 413
					clnt_inf("No EOF terminator was sent")
					srvr_inf("Expecting further data")

				elif self.flags["eofmode"] == "Buffered":
					if len(self.buffer) >= self.flags["buffersize"]:
						srvr_inf("The expected data buffer is full")
						srvr_inf("Closing data stream")
						self.buffer.seek(self.flags["buffersize"])
						self.bffrcache.write(self.buffer.pop())
						return 0
		else:
			clnt_err("Too many retries")
			return 408

	def senddata(self, *stream): # OK
		for segment in stream:
			if isinstance(segment, datastream):
				for chunk in segment(mode="chunked"):
					srvr_clnt("Sending %s bytes of data" %len(chunk))
					self.client.send(chunk)
			elif isinstance(segment, bytes):
				self.client.send(segment)
			elif isinstance(segment, str):
				self.client.sendfile(open(segment, "rb"))

	def returndata(self): # OK
		return self.buffer

	def returncache(self): # OK
		return self.bffrcache

	def storedata(self, storage): # Should flush a temporary buffer to a constant buffer on drive
		for chunk in self.buffer(mode="chunked"):
			storage.write(chunk)
		storage.close()

	def freedata(self): # OK
		self.buffer.whipe()


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
		if (self.warnlimit > -1) and (self.warnlimit < self.wrncount):
			rtime_err("Received more warnings than allowed")
			raise WarnLimitReached()


	# Parser Functions
	def parserequest(self, stream=None): # UnKnown
		if stream is None:
			stream = self.buffer
		if isinstance(stream, datastream):
			raise ValueError("Expected value of type datastream")

		request = {}
		while True:
			line = stream.readline()
			if not line:
				break
			line = line.split(b":", 1)

	def parsestatline(self, stream=None): # UnKnown
		if stream is None:
			stream = self.buffer # Internal buffer by default
		if not isinstance(stream, datastream):
			raise ValueError("Expected value of type datastream")

		stream.seek(0)
		line = stream.readline().split()
		if len(line) != 3: # Check for request triplet
			raise MalformedRequestTriplet("The first line did not contain the expected request triplet (Method, URI, Version)")

		statusline = {
			"method": line[0],
			"uri": line[1]
		}
		version = line[2]
		if version[:5] != b"HTTP/":
			raise MalformedRequestTriplet("Malformed HTTP version")
		del version[:5]
		versiontuple = version.split(b".")
		for digit, value in enumerate(version):
			version[digit] = int(value)
		statusline["version"] = tuple(version)
		return statusline


	# Exit Functions
	def shutdown(self, log=True): # Missing modules
		try:
			self.client.close()
		except:
			if log:
				rtime_inf("Ignoring 1 warning on shutdown: operation <client.close>")
		else:
			del self.client
		try:
			self.server.close()
		except:
			if log:
				rtime_inf("Ignoring 1 warning on shutdown: operation <server.close>")
		else:
			del self.server
		try:
			self.buffer.flush()
		except:
			if log:
				rtime_inf("Ignoring 1 error on shutdown: operation <buffer.flush>")
		else:
			del self.buffer
		del self.flags
		self.closed = True

	def __del__(self): # OK
		self.shutdown(log=False)


	# HTTP Status Codes
	status = {
		100: "Continue",
		101: "Switching Protocols",
		102: "Processing",
		103: "Early Hints",
		200: "OK",
		201: "Created",
		202: "Accepted",
		203: "Non-Authoritative Information",
		204: "No Content",
		205: "Reset Content",
		206: "Partial Content",
		207: "Multi Status",
		208: "Already Reported",
		226: "IM Used",
		300: "Multiple Choices",
		301: "Moved Permanently",
		302: "Found",
		303: "See Other",
		304: "Not Modified",
		305: "Use Proxy",
		306: "Switch Proxy",
		307: "Temporary Redirect",
		308: "Permanent Redirect",
		400: "Bad Request",
		401: "Unauthorized",
		402: "Payment Required",
		403: "Forbidden",
		404: "Not Found",
		405: "Method Not Allowed",
		406: "Not Acceptable",
		407: "Proxy Authentication Required",
		408: "Request Timeout",
		409: "Conflict",
		410: "Gone",
		411: "Lenght Required",
		412: "Precondition Failed",
		413: "Payload Too Large",
		414: "URI Too Long",
		415: "Unsupported Media Type",
		416: "Range Not Satisfiable",
		417: "Expectation Failed",
		418: "I'm a teapot",
		421: "Misdirected Request",
		422: "Unprocessable Entity",
		423: "Locked",
		424: "Failed Dependency",
		425: "Too Early",
		426: "Upgrade Required",
		428: "Precondition Required",
		429: "Too Many Requests",
		431: "Request Header Fields Too Large",
		451: "Unavailable For Legal Reasons",
		500: "Internal Server Error",
		501: "Not Implemented",
		502: "Bad Gateway",
		503: "Service Unavailable",
		504: "Gateway Timeout",
		505: "HTTP Version Not Supported",
		506: "Variant Also Negotiates",
		507: "Insufficient Storage",
		508: "Loop Detected",
		510: "Not Extended",
		511: "Network Authentication Required"
	}