import logging
import os
import socket
import collections
import cPickle as pickle

__author__ = 'Thales Menato and Thiago Nogueira'

log_folder = "/tmp/"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
logging.basicConfig(filename=log_folder + str(socket.gethostname()) + '_BackEnd.log',
                    filemode='w',
                    level=logging.DEBUG)


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


class BackEnd:

    HOSTS = collections.OrderedDict()      # Key is tuple (ip, port) and Value is Protocol that will be sent
    SOCKETS = collections.OrderedDict()    # Key is tuple (ip, port) and Value is socket TCP

    def __init__(self):
        try:
            host_list = open('/tmp/host-list', 'rb')
            self.HOSTS = pickle.load(host_list)
            host_list.close()
        except IOError:
            host_list = open('/tmp/host-list', 'wb')
            pickle.dump(self.HOSTS, host_list, 0)
            host_list.close()

    # Add a Host to the HOSTS dictionary, it's socket to SOCKETS and connects.
    def add_host(self, _new_host):
        # Try connection
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket TCP
            s.connect(_new_host)
            logging.info("\tHost {} added and connection working.".format(_new_host))
            s.sendall("CLOSE")
            s.close()
            # Try to add _new_host to host_list file.
            try:
                host_list = open('/tmp/host-list', 'wb')
                self.HOSTS[_new_host] = []  # insert a tuple with ip:port
                pickle.dump(self.HOSTS, host_list, 0)
                host_list.close()
                return " "
            except IOError:
                return "Can't add host to file '/tmp/host_list'."
        except socket.error:
            return "Can't add host: Daemon not running or not accessible."

    # Remove host from HOST dictionary
    def remove_host(self, _host):
        try:
            host_list = open('/tmp/host-list', 'wb')  # Get host_list file
            if self.HOSTS.has_key(_host):
                self.HOSTS.pop(_host)  # Remove host from HOSTS and SOCKETS dictionaries
            if self.SOCKETS.has_key(_host):
                self.SOCKETS.pop(_host)
            pickle.dump(self.HOSTS, host_list, 0)  # Write alterations to file
            host_list.close()
            logging.info("\tHost {} removed and disconnected.".format(_host))
            return " "
        except IOError:
            return "Couldn't reach the file '/tmp/host_list'."

    def connect_host(self, host):
        self.SOCKETS[host] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket TCP
        self.SOCKETS[host].connect(host)

    def disconnect_host(self, host):
        self.SOCKETS[host].sendall("CLOSE")
        self.SOCKETS[host].close()

    def close_all_connections(self):
        for h, s in self.SOCKETS.iteritems():
            s.sendall("CLOSE")
            s.close()
            logging.info("\tHost {} removed and disconnected.".format(h))

    # Add a Package to determined Host
    def add_package(self, host, protocol):
        if host not in self.HOSTS.keys():
            logging.error("\tError on trying to add package to {} - host doesn't exist.".format(host))
        else:
            self.HOSTS[host].append(protocol)

    # Send all packages to all hosts
    def send_all(self, host=None):
        logging.debug("\tSending to daemon...")

        if host is not None and host in self.HOSTS.keys():

                curr_socket = self.SOCKETS[host]
                messages = self.HOSTS[host]
                received_message = []
                for m in messages:
                    curr_socket.sendall(m)
                    received_message.append(curr_socket.recv(1024))

                logging.debug("\t\tSent to {} | msg: {}\n\t\treceived: {}"
                              .format(host, messages, received_message))
                logging.debug("\t...finished.")
                return received_message

        logging.warning("\t...finished without sending to HOSTS.")
        return "...finished without sending to HOSTS."
