"""Receiver

This module defines the Receiver. It will be on the client side and can execute commands on the terminal to request
files from the transmitter. If the files exists on the transmitter (server), they will be received by this module
using a reliable UDP protocol.

"""

import socket
import file_handler

HOST, PORT = "localhost", 9999  # for test only

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send a request to Transmitter
sock.sendto('request', (HOST, PORT))
print "Sent 'request'"

# Receives the number of chunks that must be transferred
total_chunks = sock.recv(socket.SO_RCVBUF)
print "Received {}".format(total_chunks)

# Acknowledge transmitter that total_chunks were received
sock.sendto('ok', (HOST, PORT))
print "Sent 'ok'"

# Receive all chunks and append it on list
chunks = []
for i in range(0, int(total_chunks)):
    chunks.append(sock.recv(socket.SO_RCVBUF))
print "Chunks received."

# Write the binary file
file_handler.write_file('test.mp4', chunks)
print "File written. Receiver finished."
