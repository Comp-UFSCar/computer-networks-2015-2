# Receiver works as a client and requests the file to transmitter.

# First example from https://docs.python.org/2/library/socketserver.html
import socket
import sys
import file_handler

HOST, PORT = "localhost", 9999

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().

sock.sendto('request', (HOST, PORT))
print "Sent 'request'"

total_chunks = sock.recv(socket.SO_RCVBUF)
print "Received {}".format(total_chunks)

sock.sendto('ok', (HOST, PORT))
print "Sent 'ok'"

chunks = []
for i in range(0, int(total_chunks)):
    chunks.append(sock.recv(socket.SO_RCVBUF))
print "Chunks received."

file_handler.write_file('test.mp4', chunks)
print "File written. Receiver finished."
