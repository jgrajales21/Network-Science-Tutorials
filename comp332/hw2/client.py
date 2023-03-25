#!/usr/bin/python3
#
# Wesleyan University
# COMP 332, Spring 2023
# Homework 2: Distributed tic-tac-toe game
# Joshua Andres Grajales
import binascii
import random
import socket
import sys

from tictactoe import *

class Client:

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.start()

    def start(self):
        # this function connects client to the server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host,self.server_port))

        # start the game by calling the play function
        self.play(client)

        client.close()
        # Fill this out
        print("start game")

    def play(self, sock):

        # enocde the game procedure here (i.e the while loop that runs until
        # game terminates)
        # Fill this out
        print("play game")

        # get board dimensions
        print("==================")
        print("| TicTacToe Game |")
        print("==================")

        numRows = 0
        while numRows < 3:
            numRows = int(input("Enter the number of rows in the TicTacToe board: "))
            if numRows < 3: print("# of rows must be 3 or greater.")
        # send board dimensions to server
        sock_write(sock,str(numRows))
        # display the board
        game = TicTacToe(numRows)
        game.display()

        while True:
            # have the client (you) make a move and apply it to the board
            game.userMove()
            # check if it is a win or a tie to end game
            results1 = game.isWinner()
            if results1[0] and results1[1] == 'X':
                print("You Win!!!")
                sock_write(sock,"Game Over.")
                return

            if game.isTie():
                print("It's a tie!!!")
                sock_write(sock,"Game Over.")
                return

            # prompt the server to make a move by saying "Make a move"
            sock_write(sock,"Make a move")
            # get the servers move (decode it), validate and apply to board or
            serverResponse = sock_read(sock)
            row = int(serverResponse[1])
            col = int(serverResponse[4])
            while not game.validateServerMove(row,col):
                # ask for a valid move
                sock_write(sock,"Make a move")
                serverResponse = sock_read(sock)
                row = int(serverResponse[1])
                col = int(serverResponse[4])

            # check if it us a win or a tie to end game
            results2 = game.isWinner()
            # if we break out of the loop game is over so client will disconnect
            if results2[0] and results2[1] == 'O':
                print("Server Wins!!!")
                sock_write(sock,"Game Over.")
                return

            if game.isTie():
                print("It's a tie!!!")
                sock_write(sock,"Game Over.")
                return

def main():
    server_host = 'localhost'
    server_port = 50007

    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    client = Client(server_host, server_port)

if __name__ == '__main__':
    main()
