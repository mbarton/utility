#!/usr/bin/env python
"""File class that displays a progress bar whilst being read

ProgressFile is a file like class that automatically displays a
progress bar on stdout whilst reading lines from the file

Notes for blog post:
- With statement since Python 2.5
- Only offering line by line iteration avoids dealing with seek etc
- Only works in text mode because of r, see caveat on tell() in docs
"""
import sys

def convert_byte_len_to_readable(bytes):
	"""Returns the human readable version of the length in bytes

	For example 10562675 would return "10.07 MB". Largest unit it
	will deal with is terabytes
	"""
	for suffix, size in [
		("TB", 1099511627776),
		("GB", 1073741824),
		("MB", 1048576),
		("KB", 1024)
	]:
		if bytes > size:
			return "%.2f %s" % ((bytes / size), suffix)
	return bytes

class ProgressFile(object):
	"""File like class that automatically displays a progress bar

	This class opens a file for reading upon construction and can be
	directly iterated over using the for statement but will display a
	progress bar on stdout as the underlying file is read
	"""
	def __init__(self, file, bars=50, show_filename=False,
		         show_human_readable_progress=False):
		"""Create a new ProgressFile that reads the given file

		Optionally provide the number of individual bars to display
		in the progress bar and whether to show the filename and/or
		read progress in a human readable format
		"""
		f = open(file, "r")
		# Seek to the end to get the total size of the file
		f.seek(0, 2)
		self.file_len = f.tell()
		# Seek back to the start again in preperation for reading
		f.seek(0, 0)
		self.file_name = file if show_filename else None
		self.file = f
		self.bars = bars
		self.bar_size = self.file_len / bars
		self.target = self.bar_size
		self.show_filename = show_filename
		self.show_human_readable = show_human_readable_progress

	def close(self):
		"""Closes the underlying file"""
		# We also provide this method in case the class has been used
		# outside of a with statement
		self.file.close()

	def __enter__(self):
		# Return the current object for use in a with statement
		return self

	def __exit__(self, type, value, traceback):
		# If any exceptions have occurred then we will let the client
		# code deal with it. Just make sure we close the file
		self.close()
		sys.stdout.write("\n")
	
	def __draw_bars(self, pos):
		num_bars = int((pos / float(self.file_len)) * self.bars)
		if self.file_name:
			sys.stdout.write(self.file_name)
			sys.stdout.write(" ")
		sys.stdout.write("|")
		sys.stdout.write("|" * num_bars)
		sys.stdout.write(" " * (self.bars - num_bars))
		sys.stdout.write("|")
		if self.show_human_readable:
			sys.stdout.write(" ")
			sys.stdout.write(convert_byte_len_to_readable(pos))
		sys.stdout.write("\r")
		sys.stdout.flush()

	def __iter__(self):
		# We use a generator to provide the lines from the file
		for line in self.file:
			pos = self.file.tell()
			# Check to see if we need to draw a new bar
			if pos >= self.target:
				self.__draw_bars(pos)
				self.target += self.bar_size
			yield line