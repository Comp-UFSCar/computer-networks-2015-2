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
                if _port < 0:
                    raise ValueError
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
    # Boolean that verifies while receiver is being served
    communicating = False
    # buffer that will store the incoming file chunks
    chunks = []
    # the index of the next expected package
    _expected_package = 0
    _download_percentage = -1

    # Verify if directory exists, if not - creates it.
    if not os.path.exists(RECEIVED_FILES_DIR):
        os.makedirs(RECEIVED_FILES_DIR)

    while True:
        try:
            hostname, port, file_name = _user_input()

            timed_out = False
            # Starting handshake with server
            handshake = True
            handshake_attempts = 0
            max_handshake_attempts = 50
            SOCK.settimeout(3)

            print "receiver requesting to transmitter({}:{}) for file {}".format(hostname, port, file_name)
            while handshake:
                # SYN
                _package = pf.create_data(0, 'REQUEST ' + file_name, True)
                SOCK.sendto(_package.to_string(), (hostname, port))
                # Binario >> SOCK.sendto(_package.pack(), (hostname, port))
                try:
                    _data, _address = SOCK.recvfrom(4096)
                except socket.timeout:
                    sys.stdout.flush()
                    sys.stdout.write("Attempt {} out of {}. \r".format(handshake_attempts, max_handshake_attempts))
                    _data = None
                    handshake_attempts += 1

                if _data is not None:
                    _package = pf.ReliableUDP(_data)
                    if _package.package_type == pf.TYPE_ACK and _package.flag_syn is True:
                        # Received SYN-ACK"
                        # this is the transmitter response, if it has the named file, it will return it's size
                        total_chunks = _package.payload
                        # otherwise, it will return an ERROR and the handshake will no longer be needed
                        if "ERROR" in str(total_chunks):
                            handshake = False
                        else:
                            # since the transmitter responded with the correct chunk_size, the receiver will send an ack
                            #  and wait for the file to come
                            _package = pf.create_ack(0)
                            _package.payload = file_name
                            SOCK.sendto(_package.to_string(), _address)
                            # Binario >> SOCK.sendto(_package.pack(), _address)
                            # DATA-ACK was sent
                            handshake = False
                elif handshake_attempts > max_handshake_attempts:
                    print "Request timed out."
                    handshake = False
                    timed_out = True

            if not timed_out:
                _chunk_size = 0
                chunks = []

                # TODO: move this area of code back into the above loop to allow re-send of the final handshake
                if "ERROR" in total_chunks:
                    print "...{}".format(" ".join(total_chunks))
                else:
                    # Waiting for the first package of file
                    _chunk_size = int(total_chunks)
                    _data, _address = SOCK.recvfrom(4096)
                    # Build received package
                    _package = pf.ReliableUDP(_data)
                    if _package.package_type == pf.TYPE_DATA and _package.flag_syn is True:
                        chunks.append(_package.payload)
                        _package = pf.create_ack(_expected_package)
                        _expected_package += 1
                        SOCK.sendto(_package.to_string(), (hostname, port))
                        # Binario >> SOCK.sendto(_package.pack(), (hostname, port))

                        # if data is one-packet-only, the first package will contain the whole file
                        if _chunk_size > 2:
                            communicating = True

                    try:
                        # Receive all chunks and append it on list
                        while communicating:
                            _data, _address = SOCK.recvfrom(4096)
                            _package = pf.ReliableUDP(_data)
                            if int(_package.seq_number) == _expected_package:
                                # Updates condition to last package (If it contains FYN flag)
                                communicating = not _package.flag_fin
                                chunks.append(_package.payload)
                                sys.stdout.flush()
                                sys.stdout.write("Download progress: %d%%   \r" % (float(len(chunks)*100/_chunk_size)))
                                # if _download_percentage < (float(len(chunks)*100/_chunk_size)):
                                #     _download_percentage += 1
                                #     print 'Download progress: {}'.format(_download_percentage)
                                _package = pf.create_ack(_expected_package)
                                _expected_package += 1
                            else:
                                _package = pf.create_ack(_expected_package)

                            SOCK.sendto(_package.to_string(), (hostname, port))
                            # Binario >> SOCK.sendto(_package.pack(), (hostname, port))

                        # Write the binary file
                        if file_handler.write_file(RECEIVED_FILES_DIR + file_name, chunks) is True:
                            print "...file {} written.".format(file_name)
                        else:
                            print "...file could not be written."

                    except socket.timeout:
                        print "the socket has timed-out while receiving the file {}, " \
                              "please, try again later".format(file_name)

                # Prepares receiver for new REQUEST
                chunks = []
                _expected_package = 0
                _download_percentage = -1

        except socket.error:
            print 'The receiver could not establish a connection with the transmitter'
