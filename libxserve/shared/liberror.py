if __name__ == "__main__":
	raise RuntimeError("This file is a library and may not be run directly")

class WarnLimitReached(Exception):
	pass

class MalformedRequestTriplet(Exception):
	pass

class MissingSSLCertificate(Exception):
	pass

class SSLConnectionFailure(Exception):
	pass