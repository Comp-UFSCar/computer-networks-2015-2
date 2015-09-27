#!/usr/bin/python

import cgitb
import cgi
from backend import *
import collections
import cPickle as pickle

__author__ = "Thales Menato and Thiago Nogueira"

# This script is a CGI and must be used inside a web server like Apache
# you'll also have to configure '.py' files to work as cgi

cgitb.enable()


def html_header():
    print "Content-type : text/html\n\n"  # CGI Content Tag
    # Print the top part of the html using header.html
    with open("templates/header.html") as f:
        print f.read()


def html_footer():
    print "</body></html>"


def html_host_form(hosts):
    # If no host was found, no form is shown
    if len(hosts) > 0:
        print """<form method="post" action="webserver.py">"""  # Outside form tag
        # JavaScript to change all checkbutton style
        print """<script>
                $(document).ready(function() {
                    for(i = 0; i < %s; i++) {
                        for(j = 1; j <= 4; j++){
                            $( "#"+i+"_command_"+j ).button();
                        }
                    }
                });
            </script>""" % len(hosts.keys())
        # Gets each host and it's respectively data
        for host, host_data in hosts.items():
            i = hosts.keys().index(host)  # host index inside Host OrderedDictionary

            html_data = ""
            if host_data is not None:
                for d in host_data:
                    if "ERROR" in d:
                        html_data += "<code>" + str(d) + "</code><br />"
                    else:
                        html_data += "<code>" + str(d[11:]) + "</code><br />"  # Excludes header of Protocol
            # Dictionary for variables inside host_form.html
            html_variables = {"host-name": host,
                              "html-data": html_data,
                              "host": i}
            # Prints the host_form accordingly to the dictionary above
            with open("templates/host_form.html") as f:
                print f.read() % html_variables

        # Add Submit button and close the form tag
        print """<div class="host_submit">
                    <input class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"
                        type="submit" value="Submit">
                </div>
                </form>"""


# CGI "real magic" happens here
def submit(hosts):

    form = cgi.FieldStorage()

    if form.keys():  # The is something already checked inside the host form

        for h in hosts.keys():  # Adds hosts to HOST list and opens a TCP socket
            BackEnd.add_host(h)

        # For each host, create list with selected commands
        for host in hosts.keys():
            commands = [x for x in form.keys()
                        if str(x).startswith(str(hosts.keys().index(host))+"_command")]

            # Send the command list to backend for processing and receive the processed data
            if len(commands) is not 0:
                for c in sorted(commands):
                    # Get value from args input where c[0] is host number and c[-1] is desired command
                    args = form.getvalue(c[0]+"_args_"+c[-1])
                    BackEnd.add_package(host, Protocol().create_request(c[-1], args))

                hosts[host] = BackEnd.send_all(host)

        BackEnd.close_all_connections()


if __name__ == "__main__":

    # Host list
    HOSTS = collections.OrderedDict()

    try:
        host_list = open('host-list.txt', 'rb')
        HOSTS = pickle.load(host_list)
    except IOError:
        host_list = open('host-list.txt', 'wb')
        HOSTS[('192.168.0.2', 9999)] = None
        HOSTS[('192.168.0.3', 9999)] = None
        HOSTS[('192.168.0.4', 9999)] = None
        pickle.dump(HOSTS, host_list, 0)

    host_list.close()

    # CGI script
    submit(HOSTS)
    # Generates HTML
    html_header()
    # html_new_host(HOSTS)
    html_host_form(HOSTS)
    html_footer()
