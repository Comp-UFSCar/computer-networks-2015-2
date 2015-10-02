#!/usr/bin/env python

import cgitb
import cgi
from backend import *

__author__ = "Thales Menato and Thiago Nogueira"

# This script is a CGI and must be used inside a web server like Apache
# you'll also have to configure '.py' files to work as cgi


def html_header(message):
    # Print the top part of the html using header.html
    with open("templates/header.html") as f:
        print f.read()
    print """<p class="error_message">%s</p>""" % message


def html_footer():
    print "</div></body></html>"


def html_host_form(_backend):
    # If no host was found, no form is shown
    if len(_backend.HOSTS) > 0:
        print """<form method="post" action="/cgi-bin/webserver.py">"""  # Outside form tag
        # JavaScript to change all checkbutton style
        print """<script>
                $(document).ready(function() {
                    for(i = 0; i < %s; i++) {
                        for(j = 1; j <= 5; j++){
                            $( "#"+i+"_command_"+j ).button();
                        }
                    }
                });
            </script>""" % len(_backend.HOSTS.keys())
        # Gets each host and it's respectively data
        for host, host_data in _backend.HOSTS.items():
            i = _backend.HOSTS.keys().index(host)  # host index inside Host OrderedDictionary

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
                    <input id="host-submit" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"
                        type="submit" value="Submit">
                </div>
                </form>"""


def html_new_host():
    with open("templates/new_host.html") as f:
        print f.read()


# CGI "real magic" happens here
def submit(_backend):

    form = cgi.FieldStorage()

    if form.keys():  # The is something already checked inside the host form
        if form.has_key('ip'):
                ip = str(form.getvalue("ip"))
                port = int(form.getvalue("port"))
                new_host = (ip, port)
                return _backend.add_host(new_host)

        else:
            # For each host, create list with selected commands
            for h in _backend.HOSTS.keys():
                commands = [x for x in form.keys()
                            if str(x).startswith(str(_backend.HOSTS.keys().index(h))+"_command")]

                # Send the command list to backend for processing and receive the processed data
                if len(commands) is not 0:
                    if int(sorted(commands)[len(commands)-1][-1]) is not 5:  # Remove Host is NOT checked
                        _backend.connect_host(h)
                        for c in sorted(commands):
                            # Get value from args input where c[0] is host number and c[-1] is desired command
                            args = form.getvalue(c[0]+"_args_"+c[-1])
                            _backend.add_package(h, Protocol().create_request(c[-1], args))
                        _backend.HOSTS[h] = _backend.send_all(h)
                        _backend.disconnect_host(h)

                    else:  # Code for Remove Host
                        return _backend.remove_host(h)
            return " "
    return " "


if __name__ == "__main__":

    cgitb.enable()
    print "Content-type: text/html; charset=utf-8\n\n"  # CGI Content Tag
    error_msg = " "

    backend = BackEnd()

    # CGI script
    error_msg = submit(backend)
    # Generates HTML
    html_header(error_msg)
    html_new_host()
    html_host_form(backend)
    html_footer()
