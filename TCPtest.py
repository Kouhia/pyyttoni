#!/usr/bin/env python
#
# Simple TCP test example

import socket


TCP_IP = '127.0.0.1'
TCP_PORT = 5055
BUFFER_SIZE = 1024
MESSAGE="Hello, TCP socket!"

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((TCP_IP, TCP_PORT))
socket.send(MESSAGE)
data = socket.recv(BUFFER_SIZE)
s.close()

