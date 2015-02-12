#!/usr/bin/python

import sys
import socket
import threading
import time 

#///////////////////////////////////////////////////////////////
#/
#/  class definition for the socket used to communicate 
#/  with the rtm
#/
#///////////////////////////////////////////////////////////////
class RtmSocket:
	def __init__(self, hostAddr, portNo, poisonPill):
		self._hostAddr = hostAddr
		self._portNo = portNo
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.connect((self._hostAddr, int(self._portNo)))
		self._poisonPill = poisonPill
		self._thr = RtmResponseThread(1, "RtmResponseThread", self._sock, self._poisonPill)
		self._thr.start()
	def close(self):
		self._sock.send(self._poisonPill + "\n")
		self._thr.join()


#///////////////////////////////////////////////////////////////
#/
#/  class definition for reading the rtm socket 
#/
#///////////////////////////////////////////////////////////////
class RtmResponseThread(threading.Thread):
        def __init__(self, threadID, name, sock, poisonPill):
                threading.Thread.__init__(self)
                self._threadID = threadID
                self._name = name
                self._sock = sock
		self._poisonPill = poisonPill
        def run(self):
                print "Starting " + self._name
                self.readRtmResponses()
                print "Exiting " + self._name
	# thread function that reads the rtm socket until it sees "exit"
	def readRtmResponses(self):
        	while True:
                	response = self._sock.recv(4096)
                	print response
			if response.find(self._poisonPill) != -1:
				break;
        	print "read thread exiting"


#///////////////////////////////////////////////////////////////
#/
#/  global functions... need to put these in a class
#/  of some sort
#/
#///////////////////////////////////////////////////////////////

# open a file and read contents into a list,
# process each element of the list
def handleFile(fname):
	print fname
	with open(fname) as f:
		lines = f.read().splitlines()
	for line in lines:
		processCmd(line.lower())


# read commands from stdin until either .quit or quit 
def handleStdin():
	while True:
		line = sys.stdin.readline().lower().strip()
		processCmd(line)


# process single command 

def processCmd(cmd):
	global sock
	global poisonPill
	if cmd[:5] == '.quit' or cmd[:4] == 'quit':
		if not sock is None:
			sock.close()
		sys.exit(1)
	if cmd[:5] == '.open':
		cmdList = cmd.split()
		host = cmdList[1]
		port = cmdList[2]
		if sock is None:
			sock = RtmSocket(host, port, poisonPill)
		else:
			print "rtm socket is already open"
	elif cmd[:5] == '.clos':
		if not sock is None:
			sock.close()
		sock = None
	elif cmd[:5] == '.dela':
		time.sleep(float(cmd.split()[1]))
	elif len(cmd) > 0 and cmd[0] <> '#':
		if not sock is None:
			sock._sock.send(cmd + "\n")


#///////////////////////////////////////////////
#/
#/  execution starts here  
#/
#///////////////////////////////////////////////

HOST = '10.0.0.3'
PORT = 30000

host = HOST
port = PORT
poisonPill = "exit"
sock = None

print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

if len(sys.argv) > 1:
	for i, arg in enumerate(sys.argv):
		if i > 0:
			handleFile(arg)
else:
	print 'reading arguments from stdin'
	handleStdin()

processCmd(".close")
print '...fini...'

