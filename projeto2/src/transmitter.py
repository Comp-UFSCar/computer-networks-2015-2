"""Transmitter

This module has the responsibility of a server. It will receive a request from the Receiver (client) containing
a file's name, will search if that file is inside the files folder and if true, this module will send the file
to the receiver using a reliable UDP protocol.

"""

import SocketServer
import file_handler


class MyUDPHandler(SocketServer.BaseRequestHandler):

    file_to_test = 'voyage.mp4'

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote: {}".format(self.client_address[0], data)

        if 'request' == data:
            data, chunks = file_handler.read_file(self.file_to_test)
            socket.sendto(str(len(chunks)), self.client_address)

        if 'ok' == data:
            data, chunks = file_handler.read_file(self.file_to_test)
            for c in chunks:
                socket.sendto(c, self.client_address)


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    print "Transmitter is running..."
    server.serve_forever()
