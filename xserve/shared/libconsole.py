from sys import stderr
import time as t


# Console
def base_err(message):
	stderr.write(base_log(message + "\n"))

def base_msg(message):
	print(base_log(message))

def base_log(message):
	return t.strftime("[%d %b %Y %H:%M:%S] ", t.gmtime()) + message


# Errors
def misc_err(message):
	base_err("Error: %s" %message)

def srvr_err(message):
	base_err("Server Error: %s" %message)

def clnt_err(message):
	base_err("Client Error: %s" %message)

def rtime_err(message):
	base_err("Runtime Error: %s" %message)


# Warnings
def misc_wrn(message):
	base_err("Warning: %s" %message)

def srvr_wrn(message):
	base_err("Server Warning: %s" %message)

def clnt_wrn(message):
	base_err("Client Warning: %s" %message)

def rtime_wrn(message):
	base_err("Runtime Warning: %s" %message)


# Info
def misc_inf(message):
	base_msg("Info: %s" %message)

def srvr_inf(message):
	base_msg("Server Info: %s" %message)

def clnt_inf(message):
	base_msg("Client Info: %s" %message)

def rtime_inf(message):
	base_msg("Runtime Info: %s" %message)


# Streams
def misc_stream(message):
	base_msg("Stream (In) => Stream (Out): %s" %message)

def srvr_clnt(message):
	base_msg("Server => Client: %s" %message)

def clnt_srvr(message):
	base_msg("Client => Server: %s" %message)

def mem_file(message):
	base_msg("Memory => File: %s" %message)

def file_mem(message):
	base_msg("File => Memory: %s" %message)
