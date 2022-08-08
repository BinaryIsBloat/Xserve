# Specific parser exceptions
class MalformedRequestTriplet(Exception):
	pass

def httpheader(stream):
	line = stream.readline(0).split()
	try:
		head = {
			"method": line[0],
			"uri": line[1],
			"version": line[2]
		}
	except IndexError:
		raise MalformedRequestTriplet("The header did not contain the expected data triplet (method, uri, version)")
	if head["method"] not in (b"GET", b"POST", b"HEAD", b"DELETE"):
		pass
