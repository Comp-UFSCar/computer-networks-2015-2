Project 1
==================================

Description
--------------
Briefly: Using a web interface, the user can pick from a limited set of *commands* and add arguments, if desired, that will be sent to a group of *Hosts (linux)* to execute it and reply the data back to the web interface.


Using a CGI written in Python *[(webserver.py)](cgi_bin/webserver.py)*, the user can access a web interface that allows  him to see the available hosts and the commands that can be sent: *ps*, *df*, *finger* and *uptime*. 

The CGI communicates directly with the *[backend.py](cgi_bin/backend.py)* where the *protocol* and sockets for  communicating with the host machines are defined.

To answer the *backend*, an instance of *[daemon.py](host/daemon.py)* must be running on each host machine. It keeps listening to a defined port *(default=9999)* and when the backend sends something it verifies if the *request* is valid, executes the command locally and send back the command's output.

The answer is then processed by the *webserver* that exhibits it to the user. 


![A simplified diagram of the project](docs/simple_diagram.png)

Protocol of communication
----------------------
Composed by a single String using only ASCII:
```
    ["REQUEST"|"RESPONSE"][1-4][<parameters>]
```  
The first part \["REQUEST"|"RESPONSE"\] defines the type of the message:

* *REQUEST* is the message that contains the command and the parameters that will be executed.  Normally used from the *backend* to the *daemon*;
* *RESPONSE* is the reply from the *daemon* to the *backend* and contains the command that was executed  and the output that was retrieved;

Now, \[1-4\] are the Linux commands where:

1. "ps"
2. "df"
3. "finger"
4. "uptime"

And last but not least, \<parameters\> contains all the parameters that the user wants to add to each specific command.  If none is filled an empty string is added to it.
**Notes:** *parameters* can only be used in a "REQUEST" message, also, the daemon parses and verify malicious inputs like "|", ";", ">", that are not executed.
