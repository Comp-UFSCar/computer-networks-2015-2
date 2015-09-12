__author__ = 'Thales Menato and Thiago Nogueira'

# Daemon Script
#
# This module works as a daemon on each host machine that will receive commands from the backend.py
# It uses the Protocol defined in backend (check that script for more information)
#

import SocketServer
from threading import Thread
import os
import socket
import sys
if os.name != "nt":
    import fcntl
    import struct
from backend import Protocol
import commands

class MyHandler(SocketServer.BaseRequestHandler):

    # Buffer code example
        # while True:
        #     if data:
        #         print 'sending data back to the client'
        #         self.request.send(data)
        #     else:
        #         print "no more data from ", self.client_address
        #         break

    # Responses for each command: 'ps', 'df', 'finger' and 'uptime'
    def response_ps(self, command):
        command.pop(0)
        args = " ".join(command)
        self.request.send(Protocol().createResponse("1", str(commands.getoutput("ps " + args))))
    def response_df(self, command):
        command.pop(0)
        args = " ".join(command)
        self.request.send(Protocol().createResponse("2", str(commands.getoutput("df " + args))))
    def response_finger(self, command):
        command.pop(0)
        args = " ".join(command)
        self.request.send(Protocol().createResponse("3", str(commands.getoutput("finger " + args))))
    def response_uptime(self, command):
        command.pop(0)
        args = " ".join(command)
        self.request.send(Protocol().createResponse("4", str(commands.getoutput("uptime " + args))))

    options = {
        "1" : response_ps,
        "2" : response_df,
        "3" : response_finger,
        "4" : response_uptime,
    }

    def isValid(self, data):
        #Verify malicious inputs like "|", ";", ">", so they're not executed
        if "|" in data or ";" in data or ">" in data:
            return False
        else:
            return True

    # Handler
    def handle(self):
        data = "dummy"
        print "Client {} connected...".format(self.client_address)

        while True:
            data = self.request.recv(Protocol.BUFF_SIZE)
            data = str(data).split()
            if len(data) > 0:
                print "\tReceived {} from {}".format(data, self.client_address)
                if str(data[0]).upper() in ["REQUEST"]:
                    data.pop(0) # remove REQUEST from list
                    # Verify if there is no malicious input
                    if self.isValid(data) is True:
                        self.options.get(data[0])(self, data)
                    else:
                        print "\tMalicious arguments."
                        self.request.send(Protocol().createResponse("ERROR","MALICIOUS ARGUMENT"))
                elif str(data[0]).upper() in ["CLOSE"]:
                    print "...client {} disconnected.".format(self.client_address)
                    self.request.close()
                    break
                else:
                    print "\tNot a valid protocol."
                    self.request.send(Protocol().createResponse("ERROR","NOT A REQUEST"))


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == '__main__':
    print "Starting Daemon..."
    # Port that will be used -- change this if necessary
    HOST = ''
    PORT = 9999
    # If no argument was used
    if len(sys.argv) is 1:
        print "No argument found, using all available interfaces at port {}".format(PORT)
    else:
        # verify if argument is a valid IP
        try:
            socket.inet_aton(sys.argv[1])
            HOST = str(sys.argv[1])
            print "Argument found, using {}:{}".format(HOST, PORT)
        except socket.error:
            print "Invalid argument - wrong ip: {}".format(sys.argv[1])
            exit(1)

    # Starts server
    server = ThreadedTCPServer((HOST, PORT), MyHandler)
    print "...daemon initialized."
    server.serve_forever()