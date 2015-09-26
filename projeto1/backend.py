import logging
import os
import socket

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


class BackEnd:

    if not os.path.exists("log"):
        os.makedirs("log")
    logging.basicConfig(filename="log/"+str(socket.gethostname())+'_BackEnd.log',
                        filemode='w',
                        level=logging.DEBUG)

    HOSTS = {}      # Key is tuple (ip, port) and Value is Protocol that will be sent
    SOCKETS = {}    # Key is tuple (ip, port) and Value is socket TCP

    # Add a Host to the HOSTS dictionary, it's socket to SOCKETS and connects.
    @staticmethod
    def add_host(host):
        BackEnd.HOSTS[host] = []  # insert a tuple with ip:port
        BackEnd.SOCKETS[host] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket TCP
        BackEnd.SOCKETS[host].connect(host)
        logging.info("\tHost {} added and connected.".format(host))

    @staticmethod
    def remove_host(host):
        BackEnd.HOSTS.pop(host)
        BackEnd.SOCKETS[host].close()
        BackEnd.SOCKETS.pop(host)
        logging.info("\tHost {} removed and disconnected.".format(host))

    @staticmethod
    def close_all_connections():
        for h, s in BackEnd.SOCKETS.iteritems():
            s.sendall("CLOSE")
            s.close()
            logging.info("\tHost {} removed and disconnected.".format(h))

    # Add a Package to determined Host
    @staticmethod
    def add_package(host, protocol):
        if host not in BackEnd.HOSTS.keys():
            logging.error("\tError on trying to add package to {} - host doesn't exist.".format(host))
        else:
            BackEnd.HOSTS[host].append(protocol)

    # From a list of Hosts and list of Protocol, attribute each protocol to each host, respectively
    @staticmethod
    def mount_packages(hosts_list, protocol_list):
        logging.debug("\n\tMounting packages...")

        if len(hosts_list) is not len(protocol_list):
            logging.error("\t\tdifferent length of hosts and protocol, both should be lists.")

        else:
            for i in range(0, len(hosts_list)):
                BackEnd.HOSTS[hosts_list[i]] = protocol_list[i]
                logging.debug("\t\t{}\t:\t{}".format(hosts_list[i], protocol_list[i]))
        logging.debug("\t...finished.")

    # Send all packages to all hosts
    @staticmethod
    def send_all(host=None):
        logging.debug("\tSending to daemon...")

        if host is not None and host in BackEnd.HOSTS.keys():

                curr_socket = BackEnd.SOCKETS[host]
                messages = BackEnd.HOSTS[host]
                received_message = []
                for m in messages:
                    curr_socket.sendall(m)
                    received_message.append(curr_socket.recv(1024))

                # BackEnd.HOSTS[host] = recv_msg = curr_socket.recv(1024)

                logging.debug("\t\tSent to {} | msg: {}\n\t\treceived: {}"
                              .format(host, messages, received_message))
                logging.debug("\t...finished.")
                return received_message

        logging.warning("\t...finished without sending to HOSTS.")
        return "...finished without sending to HOSTS."

# Code for Debug / Test purposes only
# if __name__ == '__main__':

    # print "\nBackend test started..."
    # Host list
    # hosts = [('192.168.0.2', 9999)]

    # Add hosts to BackEnd
    # for h in hosts:
    #     BackEnd.add_host(h)
#
#     # # Trying to add package to a non existing host
#     # print "\nTrying to add a package to a nonexistent Host..."
#     # BackEnd.addPackage(('192.168.1.2', 9999), Protocol().createRequest(1))
#
    # print "\nCreating request for 1 - ps ..."
    # Adding package to first host
    # BackEnd.add_package(hosts[0], Protocol().create_request(1))
    # BackEnd.add_package(hosts[0], Protocol().create_request(2))
    # BackEnd.add_package(hosts[0], Protocol().create_request(3))
    # BackEnd.add_package(hosts[0], Protocol().create_request(4))
    # BackEnd.add_package(hosts[0], Protocol().create_request(1))
    # BackEnd.add_package(hosts[0], Protocol().create_request(2))
#
    # Send to 'key' host the 'value' protocol inside HOSTS dictionary
    # response = BackEnd.send_all(hosts[0])
    # for r in response:
    #     print r
#
#     print "\nCreating request for 2 - df ..."
#
#     BackEnd.add_package(hosts[0], Protocol().create_request(2))
#     BackEnd.send_all()
#
#     print "\nCreating request for 3 - finger ..."
#
#     BackEnd.add_package(hosts[0], Protocol().create_request(3))
#     BackEnd.send_all()
#
#     print "\nCreating request for 4 - uptime ..."
#
#     BackEnd.add_package(hosts[0], Protocol().create_request(4))
#     BackEnd.send_all()
#
    # BackEnd.close_all_connections()
