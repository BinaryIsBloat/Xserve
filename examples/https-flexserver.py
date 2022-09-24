# The HTTPS clone of the original http flexserver
from xserve.libhttps import https   # The Xserve core API for writing servers that use the HTTP protocol plus SSL
from xserve.shared import *

Server = https("./server.pem")

bodydata = "<!DOCTYPE html>\n<html><head><title>Binary is Bloat Xserve 1.0 - 200 OK</title></head><body><center><h1>HTTPS - 200 OK</h1><hr>Binary is Bloat Xserve 1.0</center></body></html>"
replydata = datastream("HTTP/2 200 OK\r\nContent-Type: %s\r\nContent-Length: %s\r\n\r\n" %("text/html", len(bodydata)), bodydata)

serverbuffer = Server.returndata()

while True:
	try:
		Server.listen()
	except SSLConnectionFailure:
		continue
	while True:
		try:
			Server.getdata()
			serverbuffer.seek(0)
			clnt_req(str(serverbuffer.readline(), "utf-8", errors="replace"))
			Server.senddata(replydata)
		except ConnectionResetError:
			break