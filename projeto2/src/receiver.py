"""Receiver

This module defines the Receiver. It will be on the client side and can execute commands on the terminal to request
files from the transmitter. If the files exists on the transmitter (server), they will be received by this module
using a reliable UDP protocol.

"""

import socket
import os
import sys
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

    _receiver_seq_number = 0
    _transmitter_seq_number = 0
    while True:
        hostname, port, file_name = _user_input()
        _time_out = 0

        # Handshake
        print "Starting handshake..."
        handshake = True

        while handshake:
            # SYN
            print "SYN"
            print "...requesting to transmitter({}:{}) for file {}".format(hostname, port, file_name)
            _package = pf.create_data(0, 'REQUEST '+file_name, True)
            SOCK.sendto(_package.to_string(), (hostname, port))
            # Binario >> SOCK.sendto(_package.pack(), (hostname, port))
            print "...sent SYN"
            _data, _address = SOCK.recvfrom(4096)
            _package = pf.ReliableUDP(_data)
            if _package.package_type == pf.TYPE_ACK and _package.flag_syn is True:
                print "...received SYN-ACK"
                # this is the transmitter response, if it has the named file, it will return it's size
                total_chunks = _package.payload
                # otherwise, it will return an ERROR and the handshake will no longer be needed
                if "ERROR" in str(total_chunks):
                    handshake = False
                else:
                    # since the transmitter responded with the correct chunk_size, the receiver will send an ack and
                    # wait for the file to come
                    _package = pf.create_ack(_receiver_seq_number)
                    _package.payload = file_name
                    SOCK.sendto(_package.to_string(), _address)
                    # Binario >> SOCK.sendto(_package.pack(), _address)
                    _receiver_seq_number += 1
                    print "...sent DATA-ACK"
                    handshake = False

        _chunk_size = 0
        chunks = []

        # TODO:move this area of code back into the above loop to allow re-send of the final handshake
        if "ERROR" in total_chunks:
            print "...{}".format(" ".join(total_chunks))
        else:
            print 'waiting for the first package of file'
            _chunk_size = int(total_chunks)
            _data, _address = SOCK.recvfrom(4096)
            _package = pf.ReliableUDP(_data)
            if _package.package_type == pf.TYPE_DATA and _package.flag_syn is True:
                chunks.append(_package.payload)
                _package = pf.create_ack(_receiver_seq_number)
                # TODO: resend the ACK when it times out
                SOCK.sendto(_package.to_string(), (hostname, port))
                # Binario >> SOCK.sendto(_package.pack(), (hostname, port))

                # if data is one-packet-only, the first package will contain the whole file
                if _chunk_size != 1:
                    communicating = True

        # Receive all chunks and append it on list
        while communicating:
            # TODO: check the number in the package header to be sure it's the right one
            # TODO: for when there will be a full fledged package, separate the header from the data
            _data, _address = SOCK.recvfrom(4096)
            _package = pf.ReliableUDP(_data)
            _last_package = _package.flag_fin
            chunks.append(_package.payload)
            sys.stdout.flush()
            sys.stdout.write("Download progress: %d%%   \r" % (float(len(chunks)*100/_chunk_size)))
            _package = pf.create_ack(_receiver_seq_number)
            # TODO: resend the ACK when it times out
            SOCK.sendto(_package.to_string(), (hostname, port))
            # Binario >> SOCK.sendto(_package.pack(), (hostname, port))
            _receiver_seq_number += 1

            communicating = not _last_package

    # Write the binary file
    if file_handler.write_file(RECEIVED_FILES_DIR + file_name, chunks) is True:
        print "...file {} written.".format(file_name)
    else:
        print "...file could not be written."