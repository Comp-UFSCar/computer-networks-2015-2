"""Transmitter

This module has the responsibility of a server. It will receive a request from the Receiver (client) containing
a file's name, will search if that file is inside the files folder and if true, this module will send the file
to the receiver using a reliable UDP protocol.

"""

import SocketServer

from toolbox import file_handler


class MyUDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        _data = str(self.request[0].strip()).split()  # get message content
        _socket = self.request[1]
        print "receiver({})>\t{}".format(self.client_address[0], _data)

        if 'REQUEST' in _data:  # Request from Receiver for a file
            _data, _chunks = file_handler.read_file(_data[1])
            if _data is False:  # file does not exists
                print "transmitter>file not found!"
                _socket.sendto("ERROR file not found", self.client_address)
            else:  # send back number of chunks that will be sent
                _socket.sendto(str(len(_chunks)), self.client_address)

        elif 'OK' in _data:
            _file_name = _data[1]
            _data, _chunks = file_handler.read_file(_file_name)
            for c in _chunks:  # loop for sending all chunks
                _socket.sendto(c, self.client_address)
            print "transmitter>file '{}' sent to receiver({})".format(_file_name, self.client_address[0])


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
    server = SocketServer.UDPServer(('', port), MyUDPHandler)
    print "transmitter is running on port {}...".format(port)
    server.serve_forever()
