"""Receiver

This module defines the Receiver. It will be on the client side and can execute commands on the terminal to request
files from the transmitter. If the files exists on the transmitter (server), they will be received by this module
using a reliable UDP protocol.

"""

import socket
import os
import sys
import select
from toolbox import file_handler
from toolbox import package_factory as pf

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
    communicating = False
    # buffer that will store the incoming file
    chunks = []

    # the number of the next expected package
    expected_package = 0

    # Verify if directory exists, if not - creates it.
    if not os.path.exists(RECEIVED_FILES_DIR):
        os.makedirs(RECEIVED_FILES_DIR)

    while True:
        hostname, port, file_name = _user_input()

        # SOCK.setblocking(0)
        # Sockets from which we expect to read
        inputs = [SOCK]
        # Sockets to which we expect to write
        outputs = []

        timeout = 1

        _ack = pf.create_ack(0)
        _ack.payload = file_name

        _receiver_seq_number = 0
        _transmitter_seq_number = 0

        # Handshake
        print "Starting handshake..."
        handshake = True

        while handshake:
            # SYN
            print "SYN"
            _package = pf.create_data(_receiver_seq_number, None, True, False)
            SOCK.sendto(_package.to_string(), (hostname, port))
            print "...sent SYN"
            _data, _address = SOCK.recvfrom(1024)
            _package = pf.ReliableUDP(_data)
            if _package.package_type == pf.TYPE_ACK and _package.flag_syn is True:
                print "...received SYN-ACK"
                _package = pf.create_ack(4)
                _package.payload = file_name
                SOCK.sendto(_package.to_string(), _address)
                print "...sent ACK"
                handshake = False

        """ WORKS """
        # # Send a request to Transmitter
        # SOCK.sendto('REQUEST ' + file_name, (hostname, port))
        # print "...requesting to transmitter({}:{}) for file {}".format(hostname, port, file_name)
        #
        # # Receives the number of chunks that must be transferred
        # total_chunks = str(SOCK.recv(socket.SO_RCVBUF).split())
        # _chunk_size = int(total_chunks[2:-2])
        #
        # if "ERROR" in total_chunks:
        #     print "...{}".format(" ".join(total_chunks))
        # else:
        #     # Acknowledge transmitter that total_chunks were received
        #     SOCK.sendto('OK ' + file_name, (hostname, port))
        #     communicating = True
        #
        # # Receive all chunks and append it on list
        # while communicating:
        #     # TODO: check the number in the package header to be sure it's the right one
        #     # TODO: for when there will be a full fledged package, separate the header from the data
        #     pack = SOCK.recv(socket.SO_RCVBUF)
        #
        #     if 'FINISHED' not in pack:
        #         chunks.append(pack)
        #         sys.stdout.flush()
        #         sys.stdout.write("Download progress: %d%%   \r" % (float(len(chunks)*100/_chunk_size)))
        #
        #         SOCK.sendto('OK ' + file_name, (hostname, port))
        #     else:
        #         communicating = False
        #         # Write the binary file
        #         if file_handler.write_file(RECEIVED_FILES_DIR + file_name, chunks) is True:
        #             print "...file {} written.".format(file_name)
        #         else:
        #             print "...file could not be written."
        #         chunks = []
