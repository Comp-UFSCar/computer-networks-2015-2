"""Transmitter

This module has the responsibility of a server. It will receive a request from the Receiver (client) containing
a file's name, will search if that file is inside the files folder and if true, this module will send the file
to the receiver using a reliable UDP protocol.

"""

import socket
import select

from toolbox import file_handler
from toolbox import package_factory as pf

_FILES_FOLDER = "../files/"
"""str: Folder where files are located."""


def handle():

    _sending_files = False
    expected_package = 0
    _chunk_size = 0

    while inputs:

        timeout = 1
        # Wait for at least one of the sockets to be ready for processing
        readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)

        if not (readable or writable or exceptional) and _sending_files:
            print 'timed out, the package should be resent'
        else:
            # Handle inputs
            for s in readable:
                    _data, _address = s.recvfrom(1024)
                    _package = pf.ReliableUDP(_data)

                    if _package.package_type == pf.TYPE_DATA:
                        _package = pf.create_ack(3)
                        _package.flag_syn = True
                        s.sendto(_package.to_string(), _address)

                    if _package.package_type == pf.TYPE_ACK:
                        print "ACK chegou"

                    # data, addr = s.recvfrom(1024)
                    # data = str(data).split()
                    #
                    # if data:
                    #     # print "receiver({})>\t{}".format(data[1], addr, expected_package)
                    #     if 'REQUEST' in data:  # Request from Receiver for a file
                    #         print '...receiver({}) requested file {}'.format(addr, data[1])
                    #         data, _chunks = file_handler.read_file(_FILES_FOLDER + data[1])
                    #
                    #         if not data:  # file does not exists
                    #             print "transmitter>file not found!"
                    #             s.sendto("ERROR file not found", addr)
                    #         else:  # send back number of chunks that will be sent
                    #             _chunk_size = len(_chunks)
                    #             s.sendto(str(_chunk_size), addr)
                    #
                    #     elif 'OK' in data:
                    #         _sending_files = True
                    #         _file_name = data[1]
                    #         # TODO: check the number in the package header to be sure it's the right one
                    #         # TODO: remove this loop and send a chunk at time, after the previously sent was received
                    #         if _chunks:
                    #             s.sendto(_chunks.pop(0), addr)
                    #         else:
                    #             # for now, it's sending a simple 'finished' text, soon it will be be a full fledged
                    #             # package
                    #             s.sendto('FINISHED', addr)
                    #             print "transmitter>file '{}' sent to receiver({})".format(_file_name, addr)
                    #             _sending_files = False


def _set_port():
    """Define the port that will be used for communication."""

    while True:
        _port = raw_input("transmitter>")
        try:
            _port = int(_port)  # verify if port is valid int
        except ValueError:
            print "Invalid port."
        else:
            return _port


if __name__ == "__main__":
    port = _set_port()
    # Create a UDP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setblocking(0)

    # Bind the socket to the port
    server_address = ('localhost', port)
    print "transmitter is running on port {}...".format(port)
    server.bind(server_address)

    # Sockets from which we expect to read
    inputs = [server]

    # Sockets to which we expect to write
    outputs = []

    # Loop to serve the socket server
    handle()
