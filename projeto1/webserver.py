#!/usr/bin/python

__author__ = "Thales Menato and Thiago Nogueira"

# This script is a CGI and must be used inside a web server like Apache
# you'll also have to configure '.py' files to work as cgi

import cgi
import cgitb; cgitb.enable()

print "Content-type : text/html"
print

form = cgi.FieldStorage()
message = form.getvalue("message", "(no message)")

print
with open("index.html") as f:
    print f.read() % cgi.escape(message)

