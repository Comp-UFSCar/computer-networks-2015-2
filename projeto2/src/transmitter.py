"""Transmitter

This module has the responsibility of a server. It will receive a request from the Receiver (client) containing
a file's name, will search if that file is inside the files folder and if true, this module will send the file
to the receiver using a reliable UDP protocol.

"""

import socket

from toolbox import file_handler
from toolbox import package_factory as pf
from random import randint

_FILES_FOLDER = "../files/"
"""str: Folder where files are located."""
# The max number of times a window will be re-sent before giving up
_MAX_ATTEMPTS = 5
# Go-Back-N default window size
_DEFAULT_WINDOW_SIZE = 5
# Percentage of packages that will be intentionally lost
_PACKAGE_LOSS = 0
# Percentage of packages that will be intentionally corrupted
_PACKAGE_CORRUPTION = 0


def handler():
    # Size of the window. It changes according to received packages and timeouts
    _window_size = 0
    # Number of chunks from the file being transferred
    _number_of_chunks = 0
    # Boolean that verifies if a file is being sent or if server is idle
    _sending_files = False
    # Array that contains unconfirmed packets to be sent
    _packages = []
    # Index of last sent package but not confirmed yet
    _unconfirmed_index = -1
    # Index of last confirmed package
    _confirmed_index = -1
    # How many times the same window was re-sent
    _resents = 0
    # Flag used to show the correct outcome of the file request
    _file_found = False

    # OBS: Socket timeout is initially None (for REQUESTs)
    while True:

        try:
            # Receive new REQUEST or ACK
            _data, _address = server.recvfrom(4096)

            # After receiving the package, it will be selected if it will be lost or corrupt(for testing in a LAN sake)
            if randint(0, 100) < _PACKAGE_LOSS:
                raise socket.timeout

            if randint(0, 100) < _PACKAGE_CORRUPTION:
                raise pf.corrupted_package

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
                        _number_of_chunks = len(_chunks)
                        print "transmitter created {} chunks".format(_number_of_chunks)
                        # Response package contains the number of chunks
                        _package.payload = str(_number_of_chunks)
                        server.sendto(_package.to_string(), _address)
                        # Binario >> s.sendto(_package.pack(), _address)
                        _sending_files = True
                        # Update window size to default
                        _window_size = _DEFAULT_WINDOW_SIZE
                        # Set timeout to 1 second
                        server.settimeout(1)

                # If received package is an ACK
                if _package.package_type == pf.TYPE_ACK and _package.seq_number > 0:
                    _resents = 0
                    _old_confirmed_index = _confirmed_index
                    _confirmed_index = int(_package.seq_number)
                    # If it is not negative, remove confirmed packages from _packages
                    if (_confirmed_index - _old_confirmed_index) > 0:
                        # remove confirmed packages from list
                        for x in range(0, _confirmed_index - _old_confirmed_index):
                            _packages.pop(0)
                        # increase the size of the window (Additive Increase Multiplicative Decrease)
                        _window_size += 1
                    # Else, an old ACK has arrived and it doesn't update
                    else:
                        _confirmed_index = _old_confirmed_index

            # If there are packages to be sent
            if _packages:
                # Index cannot be greater than number of packages
                _max_index = min(_confirmed_index + _window_size, _number_of_chunks - 1)
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
                _unconfirmed_index = -1
                _confirmed_index = -1

        # If timeout has finished
        except socket.timeout:
            # Reduce the size of the window (Additive Increase Multiplicative Decrease)
            if _window_size > 1:
                _window_size /= 2
            # Index cannot be greater than number of packages
            _max_index = min(_confirmed_index + _window_size, _number_of_chunks - 1)
            # Update _unconfirmed_index with last sent package
            _unconfirmed_index = _max_index
            # If the resent didn't reached it's max attempts number, the transmitter will send the window
            if _resents < _MAX_ATTEMPTS:
                _resents += 1
                print 'Socket timed out!     Packages from {} to {} will be resent and window size reduced' \
                      ' to {}'.format(_confirmed_index, _max_index, _window_size)
                for x in range(_confirmed_index, _max_index):
                    server.sendto(_packages[x - _confirmed_index].to_string(), _address)
                    # Binario >> s.sendto(_packages.pop(x - _confirmed_index).pack(), _address)
            # IF the maximum number of attempts was reached, the transmitter gives up and wait for another file request
            else:
                _sending_files = False
                server.settimeout(None)
                _unconfirmed_index = -1
                _confirmed_index = -1
                print 'Max number of window re-transmit attempts was reached'

        except pf.corrupted_package:
            print "transmitter received corrupted package"
            pass


def _user_input():
    """Print the transmitter command line and parse the input from user."""

    print "Enter the server PORT NUMBER and optional arguments"
    print "Input is: <Port> <Window size = 5> " \
        "<Package loss percentage = 0> " \
        "<Package corruption percentage = 0>"

    while True:
        _command = raw_input("transmitter>").split()
        if 0 < len(_command) <= 4:
            try:
                _port = int(_command[0])  # verify if port is a valid positive int
                if not 0 <= _port <= 65535:
                    print "Invalid port"
                    raise ValueError
                if len(_command) > 1:
                    _CWnd = int(_command[1])  # verify if window size is valid
                    if not _CWnd > 0:
                        print "Invalid window size. Remainder: It must be bigger than 0"
                        raise ValueError
                else:
                    _CWnd = 5
                if len(_command) > 2:
                    _pl = int(_command[2])  # verify if package loss is an int between 0 and 100
                    if not 0 <= _pl <= 100:
                        print "Invalid package loss percentage. Remainder: It must be a number between 0 and 100"
                        raise ValueError
                else:
                    _pl = 0
                if len(_command) > 3:
                    _pc = int(_command[3])  # verify if package corruption is an int between 0 and 100
                    if not 0 <= _pc <= 100:
                        print "Invalid package corruption percentage. Remainder: It must be a number between 0 and 100"
                        raise ValueError
                else:
                    _pc = 0
            except ValueError:
                _pl = _pc = 0
                _CWnd = 5
                pass
            else:
                return _port, _CWnd, _pl, _pc
        else:
            _command = "".join(str(c) for c in _command)
            if _command == "exit" or _command == "quit":  # input command to end process
                exit(0)  # exit the program
            print "Incorrect input. Input must be: <Port> <Window size>? <Package loss>? <Package corruption>?"


if __name__ == "__main__":
    # Create a UDP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Flag used to show that the users's input is correct and the transmitter is on
    _server_open = False

    # this will force the user to choose a correct, non used port to serve the transmitter
    while not _server_open:
        _server_port, _DEFAULT_WINDOW_SIZE, _PACKAGE_LOSS, _PACKAGE_CORRUPTION = _user_input()

        try:
            # Bind the socket to the port
            server_address = ('', _server_port)  # ip address is '' so all interfaces will be used
            server.bind(server_address)
            _server_open = True
        except socket.error, exc:
            if 10048 in exc:
                print "Port is already being used, please, choose another one"

    print "transmitter is running on port {}...".format(_server_port)
    # Loop to serve the socket server
    handler()
