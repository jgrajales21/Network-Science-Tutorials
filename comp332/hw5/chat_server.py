#!/usr/bin/python3
# Joshua Andres Grajales
# COMP 332, Spring 2023
# Chat server
#
# Usage:
#   python3 chat_server.py <host> <port>
#

import socket
import sys
import threading

class ChatProxy():

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.server_backlog = 1
        self.chat_list = {}
        self.chat_id = 0
        self.lock = threading.Lock()
        self.start()

    def start(self):

        # Initialize server socket on which to listen for connections
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind((self.server_host, self.server_port))
            server_sock.listen(self.server_backlog)
        except OSError as e:
            print ("Unable to open server socket")
            if server_sock:
                server_sock.close()
            sys.exit(1)

        # Wait for user connection
        while True:
            conn, addr = server_sock.accept()
            self.add_user(conn, addr)
            thread = threading.Thread(target = self.serve_user,
                    args = (conn, addr, self.chat_id))
            thread.start()

    def add_user(self, conn, addr):
        print ('User has connected', addr)
        self.chat_id = self.chat_id + 1
        self.lock.acquire()
        self.chat_list[self.chat_id] = (conn, addr)
        self.lock.release()

    def read_data(self, conn):

        # Fill this out
        print("In read data")

        # continously read data from the socket
        while True:
            rawData = conn.recv(4096)

            # if no message recieved indicate disconnect/quit by returning
            # False
            if rawData == b'':
                return ['' , False]

            data = rawData.decode('utf-8')
            idx = data.index(".")
            lenMsg = int(data[:idx])

            # check message is not corrupted
            if lenMsg <= len(data[idx::]):
                msg = data
                # indicate not corrupted by returning True
                return [msg,True]
            else:
                print("Mesasge is corrupted on server side retrieval at: "+str(conn))
                # indicat message is corrupt by returning False
                return ['' , False]

    def send_data(self, user, data):
        self.lock.acquire()

        print("In send data")
        # encode the data to prepare sending into socket
        rawData = data.encode('utf-8')

        # send message to all users
        for i in self.chat_list:
            # except the user that send the message
            if i != user:
                self.chat_list[i][0].sendall(rawData)

        self.lock.release()
        return

    def cleanup(self, conn, user):
        print("In cleanup")
        self.lock.acquire()

        # remove user from the dict (i.e the list of users in chat)
        del self.chat_list[user]
        self.lock.release()

    def serve_user(self, conn, addr, user):

        print("In serve user")

        # constantly read data from socket
        while True:
            [msg,stay] = self.read_data(conn)
            if not stay:
                break
            # send the message from the user to all other users
            self.send_data(user,msg)
        # remove user from the cat
        self.cleanup(conn,user)
        return


def main():

    print (sys.argv, len(sys.argv))
    server_host = 'localhost'
    server_port = 50007

    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    chat_server = ChatProxy(server_host, server_port)

if __name__ == '__main__':
    main()
