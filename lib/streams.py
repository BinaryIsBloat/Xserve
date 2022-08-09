import os, tempfile as tmp

class datastream():
	def __init__(self, hard=False): # OK
		self.hard = hard
		if self.hard:
			self.stream = tmp.TemporaryFile(suffix=".xserver-buffer")
		else:
			self.stream = bytearray()
		self.offset = 0
		self.setchunksize()
		self.setitermode()

	def write(self, data, offset=None): # UnKnown
		if offset is None:
			offset = self.offset
		if self.hard:
			self.stream.seek(offset)
			self.offset = self.stream.write(data)
		else:
			self.stream[offset:len(data)] = data
			self.offset = offset + len(data)
		return self.offset

	def seek(self, offset, whence=0): # UnKnown
		if whence == 0:
			self.offset = offset
		elif whence == 1:
			self.offset = offset + self.offset
		elif whence == 2:
			self.offset = self.__len__() + offset
		else:
			raise ValueError("Unknown whence: %s" %whence)
		return self.offset

	def tell(self): # OK, may conflict with incorrectly set offset by UnKnown functions
		return self.offset

	def read(self, size=None, startbyte=None, endbyte=None): # UnKnown with dependency _read
		if startbyte is None:
			startbyte = self.offset
		received = bytearray(self._read(size, startbyte, endbyte))
		if self.hard:
			self.offset = self.stream.tell()
		return received

	def _read(self, size, startbyte, endbyte): # UnKnown
		if self.hard:
			self.stream.seek(startbyte)
			if endbyte is None:
				if size is None:
					return self.stream.read()
				else:
					return self.stream.read(size)
			else:
				return self.stream.read(endbyte - startbyte)
		else:
			if endbyte is None:
				if size is None:
					self.offset = len(self.stream)
					return self.stream[startbyte:]
				else:
					self.offset = startbyte + size
					return self.stream[startbyte:startbyte + size]
			else:
				self.offset = endbyte
				return self.stream[startbyte:endbyte]

	def whipe(self): # OK
		if self.hard:
			self.stream.seek(0)
			self.stream.truncate()
		else:
			self.stream.clear()
		self.offset = 0

	def flush(self): # OK
		if self.hard:
			self.stream.close()
		try:
			del self.stream
		except:
			pass

	def endswith(self, string): # UnKnown
		string = bytes(string)
		if self.hard:
			self.stream.seek(-len(string), 2)
			if string == self.stream.read():
				return True
			else:
				return False
		else:
			if bytes(self.stream[-len(string):]) == string:
				return True
			else:
				return False

	def __bool__(self): # OK
		if self.hard:
			self.stream.seek(0)
			return bool(self.stream.read(1))
		else:
			return bool(self.stream)

	def __len__(self): # OK
		if self.hard:
			self.stream.seek(0, 2)
			return self.stream.tell()
		else:
			return len(self.stream)

	def _contains(self, key, start=0, end=None): # UnKnown
		if not type(key) == bytes:
			raise ValueError("Expected bytes as key value")
		if self.hard:
			if len(key) >= self.chunksize:
				raise ValueError("Key is too long (expected less than 4096 bytes)")
			self.stream.seek(start)
			overlap = - (len(key))
			while True:
				position = self.stream.tell()
				if end is not None and position > end:
					return None
				array = self.stream.read(self.chunksize)
				if key in array:
					index = position + array.index(key)
					if (end is None) or (index - overlap > end):
						return index
					else:
						return None
				if self.stream.read(1) == b"":
					return None
				self.stream.seek(overlap, 1)
		else:
			if key in self.stream:
				return self.stream.index(key, start, end)
			else:
				return None

	def __contains__(self, key): # UnKnown
		if self._contains(key) is None:
			return False
		else:
			return True

	def feed(self, file, override=True): # UnKnown
		if override:
			self.whipe()
		file.seek(0)
		while True:
			data = file.read(self.chunksize)
			if data == b"":
				file.close()
				return
			else:
				self.write(data)

	def setchunksize(self, size=4096): # OK
		if size < 1:
			raise ValueError("Chunk size must be set to at least 1 or higher")
		self.chunksize = size

	def setitermode(self, mode="chunk"):
		if mode == "chunk":
			self.mode = "chunk"
		elif mode == "lined":
			self.mode = "lined"
		else:
			raise ValueError("Unknown iterator mode")

	def __iter__(self): # OK
		self.seek(0)
		self.eof = False
		return self

	def __next__(self): # OK
		if self.mode == "chunk":
			data = self.read(self.chunksize)
			if data:
				return data
			else:
				raise StopIteration()
		elif self.mode == "lined":
			data = bytearray()
			while True:
				prevlen = len(data)
				data.extend(self.read(1))
				if data[-1:None] == b"\n":
					del data[-1]
					if data[-1:None] == b"\r":
						del data[-1]
					return data
				if prevlen == len(data):
					if self.eof:
						del self.eof
						raise StopIteration()
					else:
						self.eof = True
						return data
		else: 
			raise ValueError("Unknown iterator mode")

	def index(self, key, start=0, end=None): # UnKnown
		if start < 0:
			raise IndexError("Start byte may not be negative")
		if (end is not None) and (start > end):
			raise IndexError("End byte may not be smaller than the start byte")
		number = self._contains(key, start, end)
		if number is None:
			raise ValueError("%s is not in stream" %key)
		else:
			return number

	def __str__(self): # OK
		return f"<Xtraordinary Data Stream (byteoffset={self.offset}, lenght={self.__len__()}, has_data={self.__bool__()}, is_hard={self.hard}, chunk_size={self.chunksize}, iterator_mode={self.mode})>"

	def __repr__(self): # OK
		return self.__str__()

	def __del__(self): # OK
		self.flush()

	def __call__(self, chunksize=None):
		if chunksize is not None:
			self.setchunksize(chunksize)
		return self