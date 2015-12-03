"""Transmitter

This module has the responsibility of a server. It will receive a request from the Receiver (client) containing
a file's name, will search if that file is inside the files folder and if true, this module will send the file
to the receiver using a reliable UDP protocol.

"""

import socket

from toolbox import file_handler
from toolbox import package_factory as pf

_FILES_FOLDER = "../files/"
"""str: Folder where files are located."""
# The max number of times a window will be re-sent before giving up
_MAX_ATTEMPTS = 5


def handler():

    # Boolean that verifies if a file is being sent or if server is idle
    _sending_files = False
    # Array that contains unconfirmed packets to be sent
    _packages = []
    # Index of last sent package but not confirmed yet
    _unconfirmed_index = 0
    # Index of last confirmed package
    _confirmed_index = 0
    # Go-Back-N window size
    _window_size = 5
    # How many times the same window was re-sent
    _resents = 0
    # Flag used to show the correct outcome of the file request
    _file_found = False

    # OBS: Socket timeout is initially None (for REQUESTs)
    while True:

        try:
            # Receive new REQUEST or ACK
            _data, _address = server.recvfrom(4096)

            # If a package has arrived
            if _data:
                # Build received package
                _package = pf.ReliableUDP(_data)

                # If package contains new REQUEST and no other request is being served
                if not _sending_files \
                        and _package.flag_syn \
                        and 'REQUEST' in str(_package.payload):

                    _file_name = str(_package.payload).split()[1]
                    print 'receiver({}) requested file {}'.format(_address, _file_name)
                    # Breaks fila data into many chunks
                    data, _chunks = file_handler.read_file(_FILES_FOLDER + _file_name)

                    # Build response package
                    _package = pf.create_ack(0)
                    _package.flag_syn = True
                    if not data:  # file does not exists
                        _file_found = False
                        _package.payload = 'ERROR file not found!'
                        print "transmitter>file not found!"
                        server.sendto(_package.to_string(), _address)
                        # Binario >> s.sendto(_package.pack(), _address)
                    else:  # send back number of chunks that will be sent
                        _file_found = True
                        _packages = pf.pack_chunks(_chunks)
                        _chunk_size = len(_chunks)
                        # Response package contains the number of chunks
                        _package.payload = str(_chunk_size)
                        server.sendto(_package.to_string(), _address)
                        # Binario >> s.sendto(_package.pack(), _address)
                        _sending_files = True
                        # Set timeout to 1 because next received package will be an ACK
                        server.settimeout(1)

                # If received package is an ACK
                if _package.package_type == pf.TYPE_ACK and _package.seq_number > 0:
                    _resents = 0
                    _old_confirmed_index = _confirmed_index
                    _confirmed_index = int(_package.seq_number) + 1
                    # If it is not negative, remove confirmed packages from _packages
                    if (_confirmed_index - _old_confirmed_index) > 0:
                        # remove confirmed packages from list
                        for x in range(0, _confirmed_index - _old_confirmed_index):
                            _packages.pop(0)
                    # Else, an old ACK has arrived and it doesn't update
                    else:
                        _confirmed_index = _old_confirmed_index

            # If there are packages to be sent
            if _packages:
                # Index cannot be greater than number of packages
                _max_index = min(_confirmed_index + _window_size, _chunk_size)
                for x in range(_unconfirmed_index, _max_index):
                    # Update last sent package index
                    _unconfirmed_index += 1
                    server.sendto(_packages[x - _confirmed_index].to_string(), _address)
                    # Binario >> s.sendto(_packages.pop(x - _confirmed_index).pack(), _address)
            # Else, all packets have successfully been sent and confirmed
            else:
                if _file_found:
                    print "transmitter successfully sent file '{}' to receiver({})".format(_file_name, _address)
                # Prepares server for new REQUEST
                _sending_files = False
                server.settimeout(None)
                _unconfirmed_index = 0
                _confirmed_index = 0
                _window_size = 5

        # If timeout has finished
        except socket.timeout:
            _data = None
            # Index cannot be greater than number of packages
            _max_index = min(_confirmed_index + _window_size, _chunk_size)
            # Update _unconfirmed_index with last sent package
            _unconfirmed_index = _max_index
            # If the resent didn't reached it's max attempts number, the transmitter will send the window
            if _resents < _MAX_ATTEMPTS:
                _resents += 1
                print 'timed out, packages from {} to {} will be resent'.format(_confirmed_index, _max_index - 1)
                for x in range(_confirmed_index, _max_index):
                    server.sendto(_packages[x - _confirmed_index].to_string(), _address)
                    # Binario >> s.sendto(_packages.pop(x - _confirmed_index).pack(), _address)
            # IF the maximum number of attempts was reached, the transmitter gives up and wait for another file request
            else:
                _sending_files = False
                server.settimeout(None)
                _unconfirmed_index = 0
                _confirmed_index = 0
                _window_size = 5
                print 'Max number of window re-transmit attempts was reached'


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

    # Bind the socket to the port
    server_address = ('', port)  # ip address is '' so all interfaces will be used
    print "transmitter is running on port {}...".format(port)
    server.bind(server_address)

    # Loop to serve the socket server
    handler()
