def parseheader(datastream):
	datastream = datastream.splitlines()
	line = datastream[0].split()
	version = line[2].split(b"/")[1].split(b".")
	request = {
		"method": line[0],
		"uri": line[1],
		"version": tuple(int(version[0]), int(version[1]))
	return 0 #returns very useful data
	}
