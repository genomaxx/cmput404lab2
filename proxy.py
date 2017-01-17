#!/usr/bin/env python
#Copied from joshua2ua during lab, some syntax changes, mostly identical to:
#https://github.com/joshua2ua/cmput404w17lab2/blob/master/proxy.py

import socket
import os, sys, select

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#We are not root and only root users can use ports less than 1000
#We are instructing to listen on port 8000
#The 0.0.0.0 part is instructing to listen on all IP addresses for this machine
serverSocket.bind(("0.0.0.0",8002))

#keep up to 5 incoming connections
serverSocket.listen(5)

while True:
	(incomingSocket, address) = serverSocket.accept()
	print "We got a connection from %s" % (str(address))
	
	if os.fork() != 0:
		continue

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.connect(("www.google.com", 80))

	incomingSocket.setblocking(0)
	clientSocket.setblocking(0)

	while True:
		#This is the client portion which 
		request = bytearray()
		while True:
			try:
				part = incomingSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
					part = None
				else:
					raise
			if  (part):
				clientSocket.sendall(part)
				request.extend(part)
			elif part is None:
				break
			else:
				exit(0)
		if len(request) > 0:
			print request
	
		#This is the server part which is listening
		response = bytearray()
		while True:
			try:
				part = clientSocket.recv(1024)
			except IOError, e:
				if e.errno == socket.errno.EAGAIN:
					part = None
				else:
					raise
			if (part):
				incomingSocket.sendall(part)
				response.extend(part)
			elif part is None:
				break
			else:
				exit(0)
		if len(response) > 0:
			print response
		
		select.select(
			[incomingSocket, clientSocket],	#read
			[], 				#write
			[incomingSocket, clientSocket],	#exceptions
			1.0)				#timeout after 1 second

