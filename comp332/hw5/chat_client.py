#!/usr/bin/python3
# Joshua Andres Grajales
# COMP 332, Spring 2023
# Chat client
#
# Example usage:
#
#   python3 chat_client.py <chat_host> <chat_port>
#

import socket
import sys
import threading


class ChatClient:

    '''
    Message format:

    to most emulate the behavior of UDP -- the transport layer protocol used by
    most real-time applications -- we choose to specify the length of the
    message and client username omitting the port numbers to decrease overhead.

        length.userName:msg

    this makes for easy access of lenght of string because it is the integer
    before the period
    '''

    def __init__(self, chat_host, chat_port, userName):
        self.chat_host = chat_host
        self.chat_port = chat_port
        self.userName = userName
        self.start()

    def start(self):

        # Open connection to chat
        try:
            chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            chat_sock.connect((self.chat_host, self.chat_port))
            print("Connected to socket")
        except OSError as e:
            print("Unable to connect to socket: ")
            if chat_sock:
                chat_sock.close()
            sys.exit(1)

        threading.Thread(target=self.write_sock, args=(chat_sock,)).start()
        threading.Thread(target=self.read_sock, args=(chat_sock,)).start()

    def write_sock(self, sock):

        print("In write sock")
        # continuosly read data from the command line
        while True:
            msg = input(" ")
            # transform the data so that it is in the correct format

            data = str(len(self.userName+": "+msg))+"."+self.userName+":"+msg
            sock.sendall(data.encode('utf-8'))

        return
    def read_sock(self, sock):

        print("In read sock")

        resp = b''

        while True:
            # get data from the socket
            rawData = sock.recv(4096)

            # if no message is recieved
            if rawData == resp:
                return

            # otherwise allow us to check that our message is not corrupted i.e
            # our mock checksum function
            data = rawData.decode('utf-8')
            # index between the user name and length of message
            idx = data.index(".")
            lenMsg = int(data[:idx])
            if lenMsg <= len(data[idx::]):
                msg = data[idx+1::]
                print(msg)
            else:
                print('Message was corruptedi in client side at: '+str(sock))

        return
def main():

    print (sys.argv, len(sys.argv))
    chat_host = 'localhost'
    chat_port = 50007

    if len(sys.argv) > 1:
        chat_host = sys.argv[1]
        chat_port = int(sys.argv[2])
    userName = input("Enter username: ")
    chat_client = ChatClient(chat_host, chat_port, userName)

if __name__ == '__main__':
    main()
