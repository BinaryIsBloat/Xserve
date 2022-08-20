# A flexible Python HTTP server which is intended to give new users of the Xserve library an overview over how certain things can be done here
# This server is mainly intended for fooling around with the software at it's core, and therefore is in public domain, excluding it from any licences of this project
# It has no dependencies aside from the Python standard modules and should run smooth on almost all platforms
# It should not be used in any production releases without certain modifications, as it has only very limited security features

from lib.http import http        # The Xserve core API for writing servers that use HTTP data
from lib.streams import datastream
from lib.console import *

Server = http()

bodydata = "<!DOCTYPE html>\n<html><head><title>Binary is Bloat Xserve 1.0 - 200 OK</title></head><body><center><h1>200 OK</h1><hr>Binary is Bloat Xserve 1.0</center></body></html>"
replydata = datastream("HTTP/1.1 200 OK\r\nContent-Length: %s\r\n\r\n" %len(bodydata) + bodydata)

serverbuffer = Server.returndata()

while True:
	Server.listen()
	Server.getdata()
	for line in serverbuffer(mode="lined"):
		clnt_srvr(str(line, "oem"))
	Server.senddata(replydata)
	Server.close()