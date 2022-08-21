# A flexible Python HTTP server which is intended to give new users of the Xserve library an overview over how certain things can be done here
# This server is mainly intended for fooling around with the software at it's core, and therefore is in public domain, excluding it from any licences of this project
# It has no dependencies aside from the Python standard modules and should run smooth on almost all platforms
# It should not be used in any production releases without certain modifications, as it has only very limited security features

from xserve.libhttp import http   # The Xserve core API for writing servers that use the HTTP protocol
from xserve.shared import *
import os

Server = http()

Buffer = Server.returndata()

while True:
	Server.listen()
	while True:
		Server.freedata()
		try:
			Server.getdata("SGLF")
		except ConnectionResetError:
			break
		try:
			statusline = Server.parsestatline()
		except MalformedRequestTriplet:
			try:
				ResponseBody = namedstream(file=os.path.abspath("./HTML/Errors/400.html"))
				ResponseHeader = bytes("HTTP/1.1 400 Bad Request\r\nContent-Length: %s\r\nContent-Type: text/html\r\nServer: Xserve1\r\n\r\n" %len(ResponseBody), "ascii")
				Server.senddata(ResponseHeader, ResponseBody)
			except ConnectionResetError:
				break
		else:
			try:
				Server.getdata("LF")
			except ConnectionResetError:
				break
			ResponseBody = namedstream(file=os.path.abspath("./HTML/default.html"))
			ResponseHeader = bytes("HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: text/html\r\nServer: Xserve1\r\n\r\n" %len(ResponseBody), "ascii")
			Server.senddata(ResponseHeader, ResponseBody)