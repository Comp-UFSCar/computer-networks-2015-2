"""Receiver

This module defines the Receiver. It will be on the client side and can execute commands on the terminal to request
files from the transmitter. If the files exists on the transmitter (server), they will be received by this module
using a reliable UDP protocol.

"""

import socket
import os
from toolbox import file_handler

SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
"""socket: Socket using UDP protocol."""
RECEIVED_FILES_DIR = "received_files/"
"""str: Folder where files will be created."""


def _user_input():
    """Print the receiver command line and parse the input from user."""

    while True:
        _command = raw_input("receiver>").split()
        if len(_command) is 3:  # receiver> <hostname> <port> <file_name>
            try:
                _hostname = _command[0]
                _port = int(_command[1])  # verify port
                _file_name = _command[2]
            except ValueError:
                print "Invalid port."
            else:
                return _hostname, _port, _file_name
        else:
            _command = "".join(str(c) for c in _command)
            if _command == "exit" or _command == "quit":  # input command to end process
                exit(0)  # exit the program
            print "Incorrect input. Input must be: <hostname> <port> <file_name>"


if __name__ == '__main__':
    """Receiver main loop"""

    # Verify if directory exists, if not - creates it.
    if not os.path.exists(RECEIVED_FILES_DIR):
        os.makedirs(RECEIVED_FILES_DIR)

    while True:
        hostname, port, file_name = _user_input()

        # Send a request to Transmitter
        SOCK.sendto('REQUEST ' + file_name, (hostname, port))
        print "...requesting to transmitter({}:{}) for file {}".format(hostname, port, file_name)

        # Receives the number of chunks that must be transferred
        total_chunks = SOCK.recv(socket.SO_RCVBUF)

        if "ERROR" in str(total_chunks).split():
            print "...{}".format(" ".join(str(total_chunks).split()[1:]))
        else:
            # Acknowledge transmitter that total_chunks were received
            SOCK.sendto('OK ' + file_name, (hostname, port))

            # Receive all chunks and append it on list
            chunks = []
            for i in range(0, int(total_chunks)):
                chunks.append(SOCK.recv(socket.SO_RCVBUF))

            # Write the binary file
            if file_handler.write_file(RECEIVED_FILES_DIR + file_name, chunks) is True:
                print "...file {} written.".format(file_name)
            else:
                print "...file could not be written."
