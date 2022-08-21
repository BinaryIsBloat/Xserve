# LICENSE
# -----------------------------------------------------------------------------------------------------------------------------------------
# Copyright 2022 BinaryIsBloat
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------------------------------------------------------------------------
#
# A library that makes file objects behave like bytearrays and bytearrays like file objects
# Streams may be extended upon request for further convenient functions directly built into the data type
# Streams may also be extended by the end user, as the library is released under the MIT license and may therefore be edited
# by very much everyone who owns a copy.
#
# In hope this library will be of use for you
#
# RandomGuyWithoutY

import tempfile as tmp

class datastream:
	def __init__(self, data=b"", hard=False): # OK
		self.hard = hard
		if self.hard:
			self.stream = tmp.TemporaryFile(suffix=".xstream")
		else:
			self.stream = bytearray()
		self.offset = 0
		self.setchunksize()
		self.setitermode()
		self.write(data)

	def convert(self, hard=False): # OK
		if self.hard == hard:
			return
		posclone = self.offset
		self.seek(0)
		clone = self.read()
		if hard:
			self.stream = tmp.TemporaryFile(suffix=".xstream")
			self.stream.write(clone)
		else:
			self.stream = clone
		self.hard = hard
		self.offset = posclone

	def write(self, *data, offset=None): # OK
		for segment in data:
			if isinstance(segment, str):
				segment = bytes(segment, "utf-8")
			elif isinstance(segment, datastream):
				for chunk in segment(mode="chunked"):
					self.write(chunk)
				return self.offset
			if offset is None:
				offset = self.offset
			if self.hard:
				self.stream.seek(offset)
				self.offset = self.stream.write(segment)
			else:
				self.stream[offset:len(segment)] = segment
				self.offset = offset + len(segment)
		return self.offset

	def append(self, data): # OK
		self.seek(0, 2)
		return self.write(data)

	def seek(self, offset, whence=0): # OK
		if whence == 0:
			self.offset = offset
		elif whence == 1:
			self.offset = offset + self.offset
		elif whence == 2:
			self.offset = self.__len__() + offset
		else:
			raise ValueError("Unknown whence: %s" %whence)
		return self.offset

	def clone(self):
		return datastream(self, self.hard)

	def tell(self): # OK
		return self.offset

	def read(self, size=None, startbyte=None, endbyte=None): # OK
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

	def truncate(self):
		if self.hard:
			self.stream.seek(self.offset)
			self.stream.truncate()
		else:
			del self.stream[self.offset:]

	def pop(self):
		prevoffset = self.offset
		data = self.read()
		self.seek(prevoffset)
		self.truncate()
		return data

	def flush(self): # OK
		if self.hard:
			self.stream.close()
		try:
			del self.stream
		except:
			pass
		self.closed = True

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

	def setitermode(self, mode="chunked"):
		if mode == "chunked":
			self.mode = "chunked"
		elif mode == "lined":
			self.mode = "lined"
		else:
			raise ValueError("Unknown iterator mode")

	def __iter__(self): # OK
		self.oldoffset = self.offset
		self.seek(0)
		if self.mode == "lined":
			self.eof = False
		return self

	def __next__(self): # OK
		if self.mode == "chunked":
			data = self.read(self.chunksize)
			if data:
				return data
			else:
				self.offset = self.oldoffset
				del self.oldoffset
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
						self.offset = self.oldoffset
						del self.oldoffset
						raise StopIteration()
					else:
						self.eof = True
						return data
		else:
			raise ValueError("Unknown iterator mode")

	def readline(self, silent=False): # UnKnown
		self.mode = "lined"
		self.eof = False
		self.oldoffset = self.__len__()
		if silent:
			self.__next__()
			return
		return self.__next__()

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

	def __call__(self, chunksize=None, mode=None):
		if chunksize is not None:
			self.setchunksize(chunksize)
		if mode is not None:
			self.setitermode(mode)
		return self

# class multistream: # Should support multiple data segments in one stream, simmilar to the list type but with Xstreams
# 	def __init__(self, *data, hard=False):
# 		self.hard = hard
# 		if self.hard:
# 			self.stream = tmp.TemporaryFile(suffix=".xstream")
# 		else:
# 			self.stream = bytearray()
# 		self.selected = 0
# 		self.offset = 0
# 		self.setchunksize()
# 		self.setitermode()
# 		self.write(data)

class namedstream(datastream):
	def __init__(self, data=b"", file=None, hard=True): # OK
		self.hard = hard
		if self.hard:
			if file is None:
				raise ValueError("File path required for named stream object")
			try:
				self.stream = open(file, "r+b")
			except FileNotFoundError:
				self.stream = open(file, "w+b")
		else:
			self.stream = bytearray()
		self.offset = 0
		self.setchunksize()
		self.setitermode()
		self.write(data)

	def convert(self, file=None, hard=False): # OK
		if self.hard == hard:
			return
		posclone = self.offset
		self.seek(0)
		clone = self.read()
		if hard:
			if file is None:
				raise ValueError("File path required for named stream object")
			try:
				self.stream = open(data, "r+b")
			except FileNotFoundError:
				self.stream = open(data, "w+b")
			self.stream.write(clone)
		else:
			self.stream = clone
		self.hard = hard
		self.offset = posclone

	def clone(self, file=None):
		return namedstream(self, file, self.hard)