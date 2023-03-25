#!/usr/bin/python3
#
# Wesleyan University
# COMP 332, Spring 2023
# Homework 2: Distributed tic-tac-toe game
# Joshua Grajales
import binascii
import random
import socket
import sys
import threading
# thread allows us to run code without having to wait for something else to
# execuite
from tictactoe import *

class Server():
    """
    Server for TicTacToe game
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.backlog = 1
        self.end = "Game Over."
        self.makeMove = "Make a move"
        self.start()

    def start(self):
        # Init server socket to listen for connections
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bind the socket to this server host and port
            server_sock.bind((self.host, self.port))
            # allow one client to connecit to socket
            server_sock.listen(self.backlog)
        except OSError as e:
            print ("Unable to open server socket: ", e)
            if server_sock:
                server_sock.close()
                sys.exit(1)

        # Wait for client connection
        while True:
            # once we have a client connect, store its address and an object
            # that allows us to communicate/send message to client
            # (client_conn)
            client_conn, client_addr = server_sock.accept()
            print ('Client with address has connected', client_addr)

            thread = threading.Thread(target = self.play, args = (client_conn, client_addr))
            thread.start()

    def play(self, conn, addr):
        # this function will run concurrently for each cleint (number of
        # clients = self.backlog)

        # Fill out this function
        print('Play game here')
        connected = True

        # have the server parse for "Make a move" to generate random move and
        # sned it to the client

        # if the client ever sends disconnect string  break out of the loop
        while connected:
            # wait until we recieve a message from the client
            msg = sock_read(conn)
            if msg == self.end:
                connected = False
                break
            if msg.isnumeric():
                n = int(msg)
            if msg == self.makeMove:
                serverMove = serverMoveDist(n)
                try:
                    sock_write(conn,str(serverMove))
                except:
                    print("Server failed to send")

        conn.close()


            # enter game logic
        print("Client Disconnect")
        return

def main():

    server_host = 'localhost'
    server_port = 50007

    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    s = Server(server_host, server_port)

if __name__ == '__main__':
    main()
