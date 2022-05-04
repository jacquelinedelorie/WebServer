'''
Created on Apr 29, 2022

@author: jdelorie
'''
import sys
import socket
import http.server
import socketserver
import threading
from threading import Thread
import time

"""
Variables statically defined.
Future would implement a command line parser.
Note: For Testing these must be consistent with Client.py
"""
LOCAL_HOST = "127.0.0.1" # Loopback (localhost)
LOCAL_PORT = 1024 # 1023 and above are unpriviledged
KNOCK_PORT1 = 1025
KNOCK_PORT2 = 1026
TIMEOUT_VALUE = 60 # 60 seconds

"""
MakeHttpServerRequestHandler is a class factory used in order to 
get the knocker_list within the handler for use upon every HTTP request.
"""
def MakeHttpServerRequestHandler(knockers_list):
    class HttpServerRequestHandler(http.server.SimpleHTTPRequestHandler):
        knocker_list = []
        def __init__(self, *args, **kwargs):
            self.knocker_list = knockers_list
            super().__init__(*args, **kwargs)
            
        def do_GET(self):
            print("Current thread "+str(threading.current_thread())+ " ip "+ self.client_address[0])
            knocks_required = len(self.knocker_list)
            knocks_have = 0
            for k in self.knocker_list:
                if k.knock_exists(self.client_address[0]):
                    knocks_have += 1
            print("required "+str(knocks_required)+" have "+str(knocks_have))
            if knocks_required == knocks_have:
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
    return HttpServerRequestHandler

"""
ThreadedTCPServer
Used by HTTPListener in order support multiple threads for the requests.
"""
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

"""
KnockListener
An open TCP socket, which only cares about the initial connection attempt. Not about data reading/writing.

Two Threads are created:
1) The TCP listener thread which accepts client connections, upon connection a map entry per IP is updated with the current time stamp.(Producer)
2) The Reaper thread which checks the time stamps within the map and removes if stale.
"""                    
class KnockListener():
            
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ip_map = {}
        self.ip_map_lock = threading.Lock()
        try: 
            self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("Could not create server socket")
        
        self.knock_listen_thread = Thread(target=self.open)
        self.knock_listen_thread.start()
        self.reaper_thread = Thread(target=self.reaper)
        self.reaper_thread.start()
        
    def open(self):
        self.listen_sock.bind((self.host, self.port))
        self.listen_sock.listen(5) 
        while True:
            conn_sock, addr = self.listen_sock.accept()
            with conn_sock:
                print(f"Connected by {addr}")
                temp_knock_thread = Thread(target=self.knock_add, args=(addr,))
                temp_knock_thread.start()
        
    def reaper(self):
        while True:
            self.ip_map_lock.acquire()
            try:
                for ip in list(self.ip_map.keys()):
                    if self.ip_map[ip] + TIMEOUT_VALUE <= time.time():
                        print("Current reaper thread "+str(threading.current_thread()))
                        print("reaping {}".format(ip))
                        print(self.ip_map)
                        del self.ip_map[ip]
                        print(self.ip_map)
            finally:
                self.ip_map_lock.release()
            
            time.sleep(2)
            
    def knock_add(self, ip):
        self.ip_map_lock.acquire()
        try:
            self.ip_map[ip[0]] = time.time()
            print("knock_add {}".format(ip))
        finally:
            self.ip_map_lock.release()

    def knock_exists(self, ip):
        exists = bool(False)
        self.ip_map_lock.acquire()
        try:
            print("knock_check {}".format(ip))
            if ip in self.ip_map:
                exists = True
        finally:
            self.ip_map_lock.release() 
        
        return exists     

"""
HTTPListener 
Creates a TCP Listener which will trigger a new thread per HTTP request.
The HTTP request will be served out of the newly spawned thread.
"""
class HTTPListener():
            
    def __init__(self, host, port, knockers_list):
        self.host = host
        self.port = port
        self.knockers_list = knockers_list
        self.handler_class = MakeHttpServerRequestHandler(self.knockers_list)
        try:
            self.listen_sock = ThreadedTCPServer((self.host, self.port), self.handler_class)
        except:
            print("Unable to create HTTP server socket")
            
    def start(self):
        self.listen_sock.serve_forever()

"""
Server class triggers all of the Knock Listeners and HTTP Listener to be opened.
A server is made up of a list of Knock Listeners and an HTTP Listener
"""
class Server():
    
    def __init__(self):
        self.knockers_list = []
        self.knocker_threads = []
        
        knocker = KnockListener(LOCAL_HOST, KNOCK_PORT1)
        self.knockers_list.append(knocker)

        knocker = KnockListener(LOCAL_HOST, KNOCK_PORT2)
        self.knockers_list.append(knocker)
        
        self.weblistener = HTTPListener(LOCAL_HOST, LOCAL_PORT, self.knockers_list)
        http_server_thread = threading.Thread(target=self.weblistener.start())
        http_server_thread.daemon = True
        http_server_thread.start()
        

    
# Create main server object to trigger server start.
def main():
    Server()


if __name__ == "__main__":
    sys.exit(main())