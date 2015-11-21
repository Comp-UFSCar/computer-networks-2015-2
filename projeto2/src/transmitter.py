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

    # Array that contains unconfirmed packets to be sent
    _packages = []
    _timeout = None
    _unconfirmed_index = 0
    _confirmed_index = 0
    _batch_quantity = 5
    while inputs:

        # Wait for at least one of the sockets to be ready for processing
        readable, writable, exceptional = select.select(inputs, outputs, inputs, _timeout)

        if not (readable or writable or exceptional) and _sending_files:
            # timeout is over
            print 'timed out, {} packages will be resent'.format(_batch_quantity)

            _timeout = 1
            _max_index = min(_confirmed_index + _batch_quantity, _chunk_size)
            _unconfirmed_index = _max_index
            for x in range(_confirmed_index, _max_index):
                s.sendto(_packages[x - _confirmed_index].to_string(), _address)
                # Binario >> s.sendto(_packages.pop(x - _confirmed_index).pack(), _address)
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

                    if _data:
                        # Received package
                        _package = pf.ReliableUDP(_data)

                        if not _sending_files \
                                and _package.flag_syn \
                                and 'REQUEST' in str(_package.payload):  # Request from Receiver for a file

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
                                _sending_files = True
                                _timeout = 1

                        if _package.package_type == pf.TYPE_ACK and _package.seq_number > 0:
                            _old_confirmed_index = _confirmed_index
                            _confirmed_index = int(_package.seq_number) + 1
                            # remove confirmed packages from list
                            if (_confirmed_index - _old_confirmed_index) > 0:
                                _timeout = 1
                                for x in range(0, _confirmed_index - _old_confirmed_index):
                                    _packages.pop(0)

                    if _packages:
                        _max_index = min(_confirmed_index + _batch_quantity, _chunk_size)
                        for x in range(_unconfirmed_index, _max_index):
                            _unconfirmed_index += 1
                            s.sendto(_packages[x - _confirmed_index].to_string(), _address)
                            # Binario >> s.sendto(_packages.pop(x - _confirmed_index).pack(), _address)
                    else:
                        print "transmitter>file '{}' sent to receiver({})".format(file_name, _address)
                        _sending_files = False
                        _timeout = None


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
