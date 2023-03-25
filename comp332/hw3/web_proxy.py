#!/usr/bin/python3
# Joshua Andres Grajales
# Wesleyan University
# COMP 332, Spring 2023
# Homework 3: Simple multi-threaded web proxy

# Usage:
#   python3 web_proxy.py <proxy_host> <proxy_port> <requested_url>
#

# Python modules
import socket
import sys
import threading
from readWrite import *

class WebProxy():
    '''
    recieves get request from web client and forwards it to the host name
    server. GET request is forwarded by parsing the get request and then
    initiating socket with the host name server. The host name servers'
    response is forwarded back to the web client at which both communication
    with the host name server and web client terminate
    '''
    def __init__(self, proxy_host, proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_backlog = 1
        self.web_cache = {}
        self.start()

    def start(self):

        # Initialize server socket on which to listen for connections
        try:
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.bind((self.proxy_host, self.proxy_port))
            proxy_sock.listen(self.proxy_backlog)

        except OSError as e:
            print ("Unable to open proxy socket: ", e)
            if proxy_sock:
                proxy_sock.close()
            sys.exit(1)

        # Wait for client connection
        while True:
            client_conn, client_addr = proxy_sock.accept()
            print ('Client with address has connected', client_addr)
            thread = threading.Thread(
                    target = self.serve_content, args = (client_conn, client_addr))
            thread.start()

    def serve_content(self, client_conn, client_addr):

        # Todos
        # Receive request from client
        # Send request to web server
        # Wait for response from web server
        # Send web server response to client

        print("Waiting to recieve Client URL")

        # manage messages from web_client
        getR_msg = client_conn.recv(1024).decode('utf-8')

        print("Message recieved by web proxy:")
        print(getR_msg)

        # 4. parse out the host name from get request; we know this will always be the
        # third element from the back; also parse out path, this will always be
        # second element
        host_name = list(filter(None, getR_msg.split()))[-3]
        print("Host name handled by Proxy : " +str(host_name))

        path = list(filter(None, getR_msg.split()))[1]
        print("Path handled by Proxy: "+ str(path))

        # 5. connect to host server using the url

        # 5.1 make new TCP socket with the host
        host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 5.2 connect to socket to url at port 80
        host_socket.connect((host_name,80))

        # 5.3 send GET request to host
        host_socket.send(getR_msg.encode('utf-8'))

        # 5.4 recieve the HTTP response from host
        # while response from host is not empty
        #while host_socket.recv(1024) != '':
        response = host_socket.recv(1024)
        print("Response from host server as handled by Proxy: ")
        print(response)
        host_socket.close()

        # 6. send response to client
        print("Sending host response to web client.")
        client_conn.send(response)
        #sock_write(client_conn,response)

        print("Host response sent to web client.")
        # Close connection to client
        client_conn.close()
        return
def main():

    print (sys.argv, len(sys.argv))

    proxy_host = 'localhost'
    proxy_port = 50007

    if len(sys.argv) > 1:
        proxy_host = sys.argv[1]
        proxy_port = int(sys.argv[2])

    web_proxy = WebProxy(proxy_host, proxy_port)

if __name__ == '__main__':

    main()
