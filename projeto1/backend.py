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

    HOSTS = {}  # Key is tuple (ip, port) and Value is Protocol that will be sent
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Socket UDP

    # Add a Host to the HOSTS dictionary
    @staticmethod
    def addHost(host):
        BackEnd.HOSTS[host] = None # insert a tuple with ip:port
        print "\tHost " + str(host) + " added."

    # Add a Package to determined Host
    @staticmethod
    def addPackage(host, protocol):
        if BackEnd.HOSTS.has_key(host) is False:
            print "\tError on trying to add package to {} - host doesn't exist.".format(host)
        else:
            BackEnd.HOSTS[host] = protocol

    # From a list of Hosts and list of Protocol, attribute each protocol to each host, respectively
    @staticmethod
    def mountPackages(hosts_list, protocol_list):
        print "\n\tMounting packages..."

        if len(hosts_list) is not len(protocol_list):
            print "\t\terror: different length of hosts and protocol, both should be lists."

        else:
            for i in range(0, len(hosts_list)):
                BackEnd.HOSTS[hosts_list[i]] = protocol_list[i]
                print "\t\t{}\t:\t{}".format(hosts_list[i], protocol_list[i])
        print "...finished."

    # Send all packages to all hosts
    @staticmethod
    def sendAll():
        #TODO: testar com N daemons na rede
        data = []
        print "\tSending to daemons..."
        for host in BackEnd.HOSTS:
            # Sending to HOST
            send_msg = str(BackEnd.HOSTS[host])
            BackEnd.SOCK.sendto(send_msg, host)

            # Receiving from HOST
            #TODO: parser na msg de volta, separando o HEADER do Protocolo com o retorno do comando
            BackEnd.HOSTS[host] = recv_msg = BackEnd.SOCK.recv(1024)
            print "\t\tSent to {} | msg: {}\n\t\treceived:\n{}\n".format(host,send_msg,recv_msg)

        print "...finished."


if __name__ == '__main__':
    print "\nBackend test started..."
    # Host list
    hosts = [('192.168.1.101', 9999)]

    # Add hosts to BackEnd
    for h in hosts:
        BackEnd.addHost(h)

    # Trying to add package to a non existing host
    print "\nTrying to add a package to a nonexistent Host..."
    BackEnd.addPackage(('192.168.1.2', 9999), Protocol().createRequest(1))

    print "\nCreating request for 1 - ps ..."
    # Adding package to first host
    BackEnd.addPackage(hosts[0], Protocol().createRequest(1))

    # Mount packages, assumes hosts and packages have same order respectively
    #BackEnd.mountPackages(hosts,p)

    # Send to 'key' host the 'value' protocol inside HOSTS dictionary
    BackEnd.sendAll()

    print "\nCreating request for 2 - df ..."

    BackEnd.addPackage(hosts[0], Protocol().createRequest(2))
    BackEnd.sendAll()

    print "\nCreating request for 3 - finger ..."

    BackEnd.addPackage(hosts[0], Protocol().createRequest(3))
    BackEnd.sendAll()

    print "\nCreating request for 4 - uptime ..."

    BackEnd.addPackage(hosts[0], Protocol().createRequest(4))
    BackEnd.sendAll()