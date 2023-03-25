#!/usr/bin/python3
# Joshua Andres Grajales
# Wesleyan University
# COMP 332, Spring 2023
# Homework 3: Simple web client to interact with proxy
#
# Example usage:
#
#   python3 web_client.py <proxy_host> <proxy_port> <requested_url>

# Python modules
import binascii
import socket
import sys
class WebClient:
    '''
    takes as input http url and sends it to a web proxy as a get request that
    will then be forwarded to the host name server; the host name is the
    'owner' of the url; after the web proxy recieves the response from the host
    name server it forwards it back to web client at which point communication
    between the web proxy and web server terminates
    '''
    def __init__(self, proxy_host, proxy_port, url):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.url = url
        self.start()

    def start(self):

        # 1. Open connection to proxy
        try:
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_sock.connect((self.proxy_host, self.proxy_port))
            print("Connected to socket")
        except OSError as e:
            print("Unable to connect to socket: ", message)
            if proxy_sock:
                proxy_sock.close()
            sys.exit(1)

        # TODOs
        # Send requested URL to proxy
        # Receive binary data from proxy

        # 2. get url from user and pass to client
        #url = input("Input URL: ")
        #url = 'eu.httpbin.org'
        #url = 'wesleyan.edu'
        #url = 'http://wesleyan.edu/mathcs/index.html'

        # 2.1 cleave the http://
        url = self.url[7:]

        # 2.2 parse for path: split the url str at the first appearance of /
        host_name = url.split('/',1)[0]
        print("Input host name handled by Client: "+host_name)
        if len(url.split('/',1)) > 1:
            path = '/'+url.split('/',1)[1]
        else:
            path = '/'
        print("Input path handled by Client: "+path)

        # 2.3 format the URL such that it is now a GET request
        getR = 'GET '+path+' HTTP/1.1\r\n' + 'HOST: ' + host_name + '\r\n\r\n' + 'Connection: close \r\n'

        # 3. send HTTP get request to web_proxy
        proxy_sock.send(getR.encode('utf-8'))

        # step 4, 5, 6 in client_proxy.py; send request to host via url, get
        # response from host, and forward host repsonse to web_client

        # 7. read host response
        print("Host response below: ")
        print(proxy_sock.recv(1024))
        #host_response = sock_read(proxy_sock)

        proxy_sock.close()

def main():

    print (sys.argv, len(sys.argv))
    proxy_host = 'localhost'
    proxy_port = 50007
    #url = 'http://example.com/'
    #url = 'http://eu.httpbin.org'
    url = 'http://info.cern.ch/'
    #url = 'http://www-db.deis.unibo.it/'

    if len(sys.argv) > 1:
        proxy_host = sys.argv[1]
        proxy_port = int(sys.argv[2])
        url = sys.argv[3]

    web_client = WebClient(proxy_host, proxy_port, url)

if __name__ == '__main__':
    main()
