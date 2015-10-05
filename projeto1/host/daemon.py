import SocketServer
import socket
import sys
import commands

__author__ = 'Thales Menato and Thiago Nogueira'

# Protocol HEADER - ASCII in a single String:
#
#   ["REQUEST"|"RESPONSE"][1-4][<parameters>]
#
# where:
#   1 - "ps"
#   2 - "df"
#   3 - "finger"
#   4 - "uptime"
# and <parameters> can only be used in a "REQUEST" message, also, the daemon must parse
# and verify malicious inputs like "|", ";", ">", so they're not executed


class Protocol:
    BUFF_SIZE = 1024

    # Standardization of communication protocol between backend and daemon
    def __init__(self):
        self.type = None            # REQUEST or RESPONSE
        self.command = None         # if REQUEST, which command will be sent
        self.parameters = None      # parameters for command
        self.response = None        # if RESPONSE, the response from executed command

    # Create a REQUEST header and content
    def create_request(self, command, parameters=None):
        self.type = "REQUEST"
        self.command = command
        self.parameters = parameters
        if parameters is None:
            return self.type + " " + str(self.command)
        else:
            return self.type + " " + str(self.command) + " " + str(self.parameters)

    # Create a RESPONSE header and content
    def create_response(self, command, response):
        self.type = "RESPONSE"
        self.command = command
        self.response = response
        return self.type + " " + str(self.command) + " " + str(self.response) + "\n"


# Daemon Script
#
# This module works as a daemon on each host machine that will receive commands from the backend.py
# It uses the Protocol defined in backend (check that script for more information)
#


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
        self.request.send(Protocol().create_response("1", str(commands.getoutput("ps " + args))))

    def response_df(self, command):
        command.pop(0)
        args = " ".join(command)
        self.request.send(Protocol().create_response("2", str(commands.getoutput("df " + args))))

    def response_finger(self, command):
        command.pop(0)
        args = " ".join(command)
        self.request.send(Protocol().create_response("3", str(commands.getoutput("finger " + args))))

    def response_uptime(self, command):
        command.pop(0)
        args = " ".join(command)
        self.request.send(Protocol().create_response("4", str(commands.getoutput("uptime " + args))))

    options = {
        "1": response_ps,
        "2": response_df,
        "3": response_finger,
        "4": response_uptime,
    }

    @staticmethod
    def is_valid(data):
        # Verify malicious inputs like "|", ";", ">", so they're not executed
        if "|" in data or ";" in data or ">" in data:
            return False
        else:
            return True

    # Handler
    def handle(self):
        print "Client {} connected...".format(self.client_address)
        while True:
            data = self.request.recv(Protocol.BUFF_SIZE)
            data = str(data).split()
            if len(data) > 0:
                print "\tReceived {} from {}".format(data, self.client_address)
                if str(data[0]).upper() in ["REQUEST"]:
                    data.pop(0)  # remove REQUEST from list
                    # Verify if there is no malicious input
                    if self.is_valid(data) is True:
                        self.options.get(data[0])(self, data)
                    else:
                        print "\tMalicious arguments."
                        self.request.send(Protocol().create_response("ERROR", "MALICIOUS ARGUMENT"))
                elif str(data[0]).upper() in ["CLOSE"]:
                    print "...client {} disconnected.".format(self.client_address)
                    self.request.close()
                    break
                else:
                    print "\tNot a valid protocol."
                    self.request.send(Protocol().create_response("ERROR", "NOT A REQUEST"))


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

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print "\nDaemon finished."
