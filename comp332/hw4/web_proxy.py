#!/usr/bin/python3
# Joshua Andres Grajales
# Wesleyan University
# COMP 332, Spring 2023
# Homework 3: Simple multi-threaded web proxy

# Usage:
#   python3 web_proxy.py <proxy_host> <proxy_port> <requested_url>

# Python modules
import socket
import sys
import threading

# Project modules
import http_constants as const
import http_util
import re
class WebProxy():

    '''
    implements a web proxy with a cache (dictionary); proxy sends conditional
    GET statements when the client requests a URL they have already visited in
    a session and infroms client of the http response code
    '''
    def __init__(self, proxy_host, proxy_port):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_backlog = 1
        self.cache = dict() # stores (hostname,pathname): http response pairs
        self.iscondGet = False # boolean indicating if handling conditional GET
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
            conn, addr = proxy_sock.accept()
            print ('Client has connected', addr)
            thread = threading.Thread(target = self.serve_content, args = (conn, addr))
            thread.start()

    def serve_content(self, conn, addr):

        # Receive binary request from client
        bin_req = conn.recv(4096)
        try:
            # decode the message
            str_req = bin_req.decode('utf-8')
            print(str_req)
        except ValueError as e:
            print ("Unable to decode request, not utf-8", e)
            conn.close()
            return

        # Extract host and path using http_util library
        hostname = http_util.get_http_field(str_req, 'Host: ', const.END_LINE)
        pathname = http_util.get_http_field(str_req, 'GET ', ' HTTP/1.1')
        if hostname == -1 or pathname == -1:
            print ("Cannot determine host")
            client_conn.close()
            return
        elif pathname[0] != '/':
            [hostname, pathname] = http_util.parse_url(pathname)
        str_req = http_util.create_http_req(hostname, pathname)

        ###################################
        #####CHECK if Conditional GET######
        ###################################

        # cache is a global dict variable to this class; look in init function

        # I choose to uniquely identify request by a hostname+pathname dict key
        url = (hostname,pathname)

        # if hostname+pathname IN dict then send CONDITIONAL GET
        if url in self.cache:
            print("Formating Conditional GET statment.")
            self.iscondGet = True
            # get the last modified date
            prevResponse = self.cache[url].decode('utf-8')
            # try Last Modified as field
            tryLastMod = re.search('Last-Modified.+\r\n',prevResponse)
            if not tryLastMod:
                # if Last Modified DNE then try Last Modified field
                tryLastMod = re.search('Last-Modified field.+\r\n',prevResponse)
                if not tryLastMod:
                    #if Last modified DNE then try date field
                    tryLastMod = re.search('Date:.+\r\n',prevResponse)
                    if not tryLastMod:
                        print("Cannot access last modified date in response when creating conditional GET request.")
                        return
                    else:
                        #extract the date from Date:
                        prec = len('Date: ')
                        # cleave the returned string
                        tryLastMod = tryLastMod.group()[prec:-2]
                        print("Formatted Conditional GET using 'Date' field from previous HTTP response.")
                else:
                    # extract the date from Last-Modified
                    prec = len('Last-Modified: ')
                    #cleave the returned string
                    tryLastMod = tryLastMod.group()[prec:-2]
                    print("Formatted Conditional GET using 'Last-Modified' field form previous HTTP response.")
            else:
                # extract date from Last-Modified field
                prec = len('Last-Modified field: ')
                #cleave the returned string
                tryLastMod = tryLastMod.group()[prec-6:-2]
                print("Formatted Conditional GET using 'Last-Modified field' field from previous HTTP response.")

            print()
            print("Date extracted from HTTP response: " + tryLastMod)
            print()
            # at this point we have all we need to make the conditional GET
            # make the conditional GET
            str_req = http_util.add_http_field(str_req,'If-Modified-Since',' '+tryLastMod)

        # if hostname+pathname NOT in dict then send GET as is
        else:
            print("Formatting standard GET request.")
            self.iscondGet = False

        print(str_req)
        bin_req = str_req.encode('utf-8')

        # Open connection to host and send binary request
        try:
            web_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            web_sock.connect((hostname, 80))
            print ("Sending request to web server: ", bin_req)
            web_sock.sendall(bin_req)
        except OSError as e:
            print ("Unable to open web socket: ", e)
            if web_sock:
                web_sock.close()
            conn.close()
            return

        # Wait for response from web server
        bin_reply = b''
        while True:
            more = web_sock.recv(4096)
            if not more:
                break
            bin_reply += more

        ###################################
        ####REPONSE if Conditional GET#####
        ###################################
        # FIX THIS so that you correctly parse the repsonse for the codes
        # if our response is to a conditional get
        if self.iscondGet:
            # check if response 200 OK signifiying that the url object changed
            print("Interpreting Conditional GET response code.")
            respCode = re.search('HTTP/1.1.+\r\n', bin_reply.decode('utf-8'))
            prec = len('HTTP/1.1 ')
            respCode = respCode.group()[prec:-2]
            if respCode == '200 OK':
                print("Conditional GET response code: 200 OK.")
                # update cache
                self.cache[url] = bin_reply
            elif respCode == '304 Not Modified':
                print('Conditional GET response code: 304 Not Modified.')
                # cache has up-to-date information, forward this to the client
                bin_reply = self.cache[url]
            else:
                print("An error occurred when accessing HTTP code response in conditional GET request. Treating response as 200 OK")
                self.cache[url] = bin_reply
        else:
            print("No interpretation needed. Saving standard GET request in cahce.")
            # if this is not a conditional GET response then add to cache
            self.cache[url] = bin_reply
        # Send web server response to client
        print('Proxy received from server (showing 1st 300 bytes): ', bin_reply[:300])
        conn.sendall(bin_reply)

        # Close connection to client
        conn.close()

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
