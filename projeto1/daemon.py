__author__ = 'Thales Menato and Thiago Nogueira'

# Daemon Script
#
# This module works as a daemon on each host machine that will receive commands from the backend.py
# It uses the Protocol defined in backend (check that script for more information)
#

import SocketServer
import os
import socket
import sys
if os.name != "nt":
    import fcntl
    import struct
from backend import Protocol
import commands

# module for getting the lan ip address of the computer
class IPGetter:
    # This solution was found at - http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    # and it was suggested by user 'smerlin' ( http://stackoverflow.com/users/231717/smerlin )
    @staticmethod
    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

    @staticmethod
    def get_lan_ip():
        ip = socket.gethostbyname(socket.gethostname())
        if ip.startswith("127.") and os.name != "nt":
            interfaces = ["eth0","eth1","eth2","wlan0","wlan1","wifi0","ath0","ath1","ppp0"]
            for ifname in interfaces:
                try:
                    ip = IPGetter.get_interface_ip(ifname)
                    break
                except IOError:
                    pass
        return ip


class MyUDPHandler(SocketServer.BaseRequestHandler):
    # where:
#   1 - "ps"
#   2 - "df"
#   3 - "finger"
#   4 - "uptime"

    def response_ps(self, socket, command, client_address):
        socket.sendto(Protocol().createResponse(command, str(commands.getoutput("ps"))), client_address)

    def response_df(self, socket, command, client_address):
        socket.sendto(Protocol().createResponse(command, str(commands.getoutput("df"))), client_address)

    def response_finger(self, socket, command, client_address):
        socket.sendto(Protocol().createResponse(command, str(commands.getoutput("finger"))), client_address)

    def response_uptime(self, socket, command, client_address):
        socket.sendto(Protocol().createResponse(command, str(commands.getoutput("uptime"))), client_address)

    options = {
        "1" : response_ps,
        "2" : response_df,
        "3" : response_finger,
        "4" : response_uptime,
    }

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "Received {} from {}".format(data, self.client_address[0])

        #TODO: verificar se o comando do request nao eh malicioso
        data = str(data).split()

        if str(data[0]) in ["REQUEST"]:
            self.options.get(data[1])(self, socket, data[1], self.client_address)

        else:
            print "Not a REQUEST."
            socket.sendto(Protocol().createResponse("ERROR","NOT A REQUEST"), self.client_address)

if __name__ == '__main__':
    print "Starting Daemon..."
    # Port that will be used -- change this if necessary
    PORT = 9999
    # If no argument was used
    if len(sys.argv) is 1:
        HOST = IPGetter.get_lan_ip()
        print "No argument found, using {}:{}".format(HOST,PORT)
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
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    print "...daemon initialized."
    server.serve_forever()