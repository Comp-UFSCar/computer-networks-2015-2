__author__ = 'Thales Menato and Thiago Nogueira'

# Client script

#from backend import Protocol
import SocketServer

class MyUDPHandler(SocketServer.BaseRequestHandler):
    #TODO: verificar se o comando do request nao eh malicioso
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print"{} wrote:".format(self.client_address[0])
        print data
        socket.sendto(data.lower(), self.client_address)

if __name__ == '__main__':
    HOST, PORT = "localhost", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    print "Daemon started -- " + str(HOST) +":"+ str(PORT)
    server.serve_forever()