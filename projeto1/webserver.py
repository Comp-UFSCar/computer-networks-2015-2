#!C:\Python27\python.exe -u
#!/usr/bin/env python

__author__ = "Thales Menato and Thiago Nogueira"

# This script is a CGI and must be used inside a web server like Apache
# you'll also have to configure '.py' files to work as cgi

import cgi
import cgitb; cgitb.enable()

print "Content-type : text/html"
print

# print """
# <html>
# <head>
#     <title>Sample CGI Example</title>
# </head>
#
# <body>
#     <h3>Sample CGI Example</h3>
# """

print
with open('html\header.html') as f:
    print f.read()

form = cgi.FieldStorage()
message = form.getvalue("message", "(no message)")

print
with open('html\/form.html') as f:
    print f.read() % cgi.escape(message)

# print """
#     <p>Previous message: %s</p>
#     <p>form
#
#     <form method="post" action="webserver.py">
#         <p>message: <input type="text" name="message"/></p>
#     </form>
# </body>
# </html>
# """ % cgi.escape(message)