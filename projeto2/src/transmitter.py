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
    file_name = ''

    while inputs:

        timeout = 1
        # Wait for at least one of the sockets to be ready for processing
        readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
        _packages = []

        if not (readable or writable or exceptional) and _sending_files:
            print 'timed out, the package should be resent'
        else:
            # Handle inputs
            for s in readable:
                    # # handshake
                    # _data, _address = s.recvfrom(1024)
                    # _package = pf.ReliableUDP(_data)
                    #
                    # if _package.package_type == pf.TYPE_DATA:
                    #     _package = pf.create_ack(3)
                    #     _package.flag_syn = True
                    #     s.sendto(_package.to_string(), _address)
                    #
                    # if _package.package_type == pf.TYPE_ACK:
                    #     print "ACK chegou"

                    _data, _address = s.recvfrom(4096)
                    _package = pf.ReliableUDP(_data)

                    if _data:
                        if _package.flag_syn and 'REQUEST' in str(_package.payload):  # Request from Receiver for a file
                            file_name = str(_package.payload).split()[1]
                            print '...receiver({}) requested file {}'.format(_address, file_name)
                            data, _chunks = file_handler.read_file(_FILES_FOLDER + file_name)

                            _package = pf.create_ack(expected_package)
                            _package.flag_syn = True
                            if not data:  # file does not exists
                                _package.payload = 'ERROR file not found'
                                print "transmitter>file not found!"
                                s.sendto(_package.to_string(), _address)
                                # Binario >> s.sendto(_package.pack(), _address)
                            else:  # send back number of chunks that will be sent
                                _packages = pf.pack_chunks(_chunks)
                                _chunk_size = len(_chunks)
                                _package.payload = str(_chunk_size)
                                s.sendto(_package.to_string(), _address)
                                # Binario >> s.sendto(_package.pack(), _address)

                        if _package.package_type == pf.TYPE_ACK :
                            _sending_files = True
                            # TODO: check the number in the package header to be sure it's the right one
                            if _packages:
                                s.sendto(_packages.pop().to_string(), _address)
                                # Binario >> s.sendto(_packages.pop().pack(), _address)
                            else:
                                print "transmitter>file '{}' sent to receiver({})".format(file_name, _address)
                                _sending_files = False


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
    # server.setblocking(0)

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
