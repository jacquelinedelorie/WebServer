# WebServer
A Multi-Threaded HTTP Web Server using Port Knocking for protection

The files with main functions are:
Server.py
Client.py

In order to start server:
python Server.py

In order to start client:
python Client.py

Note: "python" depends on your environment, if not setup please specify path to your specific python.exe.
Note2: This was tested with Python 3.10, issues do exist with Python 2.7.

There are no command line arguments at the moment, the focus was on implementing a Multi-Threaded HTTP Server and Client, which uses Port 
Knocking in order to limit/protect the HTTP Server port.

The variables for each file are highlighted at the top. 

The Client will run through a few test cases in order to highlight the Port Knocking and Multi-Threaded behavior. The test case and expectation
is highlighted in the comments and command line.

There are a few console prints, which are intentional to highlight the behaviors implemented/tested. 

This was created using the Eclipse IDE and then tested via command line.
