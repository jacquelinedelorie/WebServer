'''
Created on Apr 29, 2022

@author: jdelorie
'''
import sys
import socket
import http.client
import threading
import time

"""
Variables statically defined.
Future would implement a command line parser.
Note: For Testing these must be consistent with Server.py
"""
LOCAL_HOST = "127.0.0.1" # Loopback (localhost)
LOCAL_PORT = 1024 # 1023 and above are unpriviledged
KNOCK_PORT1 = 1025
KNOCK_PORT2 = 1026
FILENAME = "index.html"


"""
Client will create with a Knock or a HTTP requested with a specified port and host. 
The difference is that the HTTP request send/receives data while the Knock just connect and closes.
"""
class Client:
    
    def __init__(self, host, port, knock):
        self.host = host
        self.port = port
        self.knock = knock
        if knock:
            try:
                self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except:
                print("Could not create client socket")

    def start(self):
        if self.knock:
            Client.knock_start(self)
        else:
            try:
                self.client_sock = http.client.HTTPConnection(self.host, self.port)
                self.client_sock.request("GET", "/")
                response = self.client_sock.getresponse()
                print("Status {} reason {}".format(response.status, response.reason))
                self.client_sock.close()
            except socket.error as msg:
                print("Could not connect to server socket error message: %s" % msg)
                      
    def knock_start(self):
        try:
            self.client_sock.connect((self.host, self.port))
            self.client_sock.close()
        except socket.error as msg:
            print("Could not connect to server socket error message: %s" % msg)
    
def main():
    
    """
    Test Case 1:
    Expectation: HTTP Request Failure
    Zero Knocks
    Attempt HTTP Request
    """
    print("Test Case 1: Expectation: HTTP Request Failure")
    client = Client(LOCAL_HOST, LOCAL_PORT, False)
    client.start()
    
    """
    Test Case 2:
    Expectation: HTTP Request Failure
    One Knock
    Attempt HTTP Request
    """   
    print("Test Case 2: Expectation: HTTP Request Failure")
    knock2 = Client(LOCAL_HOST, KNOCK_PORT2, True)
    knock2.start()
    client = Client(LOCAL_HOST, LOCAL_PORT, False)
    client.start()
    
    """
    Test Case 3:
    Expectation: HTTP Request Success
    Two Knocks
    This also tests the knock update since knock2 is a duplicate
    the time stamp in the knock table will be updated.
    Attempt 10 HTTP Request
    """  
    print("Test Case 3: Expectation: 10 Successful HTTP Requests")
    knock1 = Client(LOCAL_HOST, KNOCK_PORT1, True)
    knock1.start()

    knock2 = Client(LOCAL_HOST, KNOCK_PORT2, True)
    knock2.start()
    
    for a in range(10):
        client = Client(LOCAL_HOST, LOCAL_PORT, False)
        thread = threading.Thread(target= client.start())
        print(str(a)+" starting client thread "+thread.name)
        thread.start()
        
    """
    Test Case 4:
    Expectation: HTTP Request Failure
    Two Knocks that timeout then attempt an HTTP request.
    """  
    print("Test Case 4: Expectation: Two knocks 70 second delay and a failed HTTP request")
    knock1 = Client(LOCAL_HOST, KNOCK_PORT1, True)
    knock1.start()

    knock2 = Client(LOCAL_HOST, KNOCK_PORT2, True)
    knock2.start()
    
    time.sleep(70)

    client = Client(LOCAL_HOST, LOCAL_PORT, False)
    client.start()
    
if __name__ == "__main__":
    sys.exit(main())