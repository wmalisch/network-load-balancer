A client, server, and load balancer solution for a network control when accessing files from multiple

loadbalancer
------

To run the server, simple execute:
  cd load-balancer
  python balancer.py config.txt

potentially substituting your installation of python3 in for python depending
on your distribution and configuration.  The server will report the port 
number that it is listening on for your client to use.  Place any files to 
transfer into the same directory as the server.

One of the first lines of declares the global variable TEST_FILE. You will need
to have a copy of this file in each server folder to execute this program without 
error.

balancer.py uses a config.txt to interpret the active servers. Enter the active servers
in the config.txt, with one host:port per line. There is some minor error handling,
but try to keep them without random white space. Example config.txt below:

localhost:5050
localhost:5060
localhost:5070


server
------

To run the server, simple execute:

  cd server
  python server.py

You may run several servers. server-rep1 and server-rep2 have been provided, 
copies to the server directory to use. 

You may have to substitute your installation of python3 in for python depending 
on your distribution and configuration.  The server will report the port number 
that it is listening on for your client to use.  Place any files to transfer into 
the same directory as the server.

client
------

To run the client, execute:

  cd client
  python client.py http://host:port/file

where host is where the server is running (e.g. localhost), port is the port 
number reported by the server where it is running and file is the name of the 
file you want to retrieve.  Again, you might need to substitute python3 in for
python depending on your installation and configuration.

