__author__ = 'Thales Menato and Thiago Nogueira'

import socket
import sys

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

# Class Protocol
class Protocol:
    # Standardization of communication protocol between backend and daemon
    def __init__(self):
        self.type = None            # REQUEST or RESPONSE
        self.command = None         # if REQUEST, which command will be sent
        self.parameters = None      # parameters for command
        self.response = None        # if RESPONSE, the response from executed command

    # Create a REQUEST header and content
    def createRequest(self, command, parameters = None):
        self.type = "REQUEST"
        self.command = command
        self.parameters = parameters
        if parameters is None:
            return self.type + " " + str(self.command)
        else:
            return self.type + " " + str(self.command) + " " + str(self.parameters)

    # Create a RESPONSE header and content
    def createResponse(self, command, response):
        self.type = "RESPONSE"
        self.command = command
        self.response = response
        return self.type + " " + str(self.command) + " " + str(self.response)

class BackEnd:

    HOSTS = {}  # all the ip:port from machines with daemon
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Socket UDP

    @staticmethod
    def addHost(host):
        BackEnd.HOSTS[host] = None # insert a tuple with ip:port
        print "Host " + str(host) + " added."

    @staticmethod
    def mountPackages(host, protocol):
        print "\nMounting packages..."

        if len(host) is not len(protocol):
            print "\terror: different length of hosts and protocol, both should be lists."

        else:
            for i in range(0, len(host)):
                BackEnd.HOSTS[host[i]] = protocol[i]
                print "\t{}\t:\t{}".format(host[i], protocol[i])
        print "...finished.\n"

    @staticmethod
    def sendAll():
        #TODO: testar com N daemons na rede
        print "\nSending to daemons..."
        for host in BackEnd.HOSTS:
            BackEnd.SOCK.sendto(str(BackEnd.HOSTS[host]) + "\n", host)
            print "\tSent from {}:\t{}".format(host,BackEnd.HOSTS[host])
        print "...finished.\n"

    @staticmethod
    def receiveAll():
        #TODO: testar metodo para N daemons na rede - como ele recebe os dados
        print "\nReceiving data from daemons..."
        received = BackEnd.SOCK.recv(1024)
        print "\tReceived:\t{}".format(received)
        print "...finished.\n"


if __name__ == '__main__':

    # Host list
    hosts = [('127.0.0.1', 9999)]

    # Add hosts to BackEnd
    for h in hosts:
        BackEnd.addHost(h)

    # Protocol list -- message to be sent
    p = []
    p.append(Protocol().createRequest(1))

    # Mount packages, assumes hosts and packages have same order respectively
    BackEnd.mountPackages(hosts,p)
    # Send to 'key' host the 'value' protocol inside HOSTS dictionary
    BackEnd.sendAll()
    # Receive everything from daemon
    BackEnd.receiveAll()
