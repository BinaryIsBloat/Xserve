# A flexible Python HTTP server which is intended to give new users of the Xserve library an overview over how certain things can be done here
# This server is mainly intended for fooling around with the software at it's core, and therefore is in public domain, excluding it from any licences of this project
# It has no dependencies aside from the Python standard modules and should run smooth on almost all platforms
# It should not be used in any production releases without certain modifications, as it has only very limited security features

from lib.http import http        # The Xserve core API for writing servers that use HTTP data
from lib.parse import httpheader # The Xserve parser for extracting information from raw data

Server = http()

while True:
	Server.listen()
	Server.getdata()
