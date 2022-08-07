import os, tempfile as tmp

class datastream():
	def __init__(self, hard=False):
		self.hard = hard
		if self.hard:
			self.stream = tmp.TemporaryFile(suffix=".xserver-buffer")
		else:
			self.stream = bytearray()
		self.offset = 0

	def write(self, data, offset=None):
		if offset is None:
			offset = self.offset
		if self.hard:
			self.stream.seek(offset)
			self.offset = self.stream.write(data)
		else:
			self.stream[offset:len(data)] = data
			self.offset = offset + len(data)
		return self.offset

	def seek(self, offset, whence=0):
		if whence == 0:
			self.offset = offset
		elif whence == 1:
			self.offset = offset + self.offset
		elif whence == 2:
			self.offset = self.__len__() + offset
		else:
			raise ValueError("Unknown whence: %s" %whence)
		return self.offset
	
	def tell(self):
		return self.offset

	def read(self, size=None, startbyte=None, endbyte=None):
		if startbyte is None:
			startbyte = self.offset
		received = bytearray(self._read(size, startbyte, endbyte))
		if self.hard:
			self.offset = received.tell()
		return received

	def _read(self, size, startbyte, endbyte):
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

	def whipe(self):
		if self.hard:
			self.stream.seek(0)
			self.stream.truncate()
		else:
			self.stream.clear()
		self.offset = 0

	def flush(self):
		if self.hard:
			self.stream.close()
		try:
			del self.stream
		except:
			pass

	def endswith(self, string):
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

	def __bool__(self):
		if self.hard:
			self.stream.seek(0)
			return bool(self.stream.read(1))
		else:
			return bool(self.stream)

	def __len__(self):
		if self.hard:
			self.stream.seek(0, 2)
			return self.stream.tell()
		else:
			return len(self.stream)

	def __str__(self):
		return f"<Xtraordinary Data Stream (byteoffset={self.offset}, lenght={self.__len__()}, has_data={self.__bool__()})>"

	def __repr__(self):
		return self.__str__()

	def __del__(self):
		self.flush()