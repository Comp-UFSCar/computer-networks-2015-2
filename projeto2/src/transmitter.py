# Transmitter works as a server. 
# It receives a request from receiver with a file name and send that file back.

# First example from https://docs.python.org/2/library/socketserver.html
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
