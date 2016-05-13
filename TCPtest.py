#!/usr/bin/env python
#
# Simple TCP client test

import socket


target_host = 'www.google.fi'
target_port = 80
http_request = "GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % target_host
buffer_size = 4096


# new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect
client.connect((target_host, target_port))

# send data
client.send(http_request)

# recieve data
response_data = client.recv(buffer_size)

# print data
print response_data

# Close connection
client.close()

