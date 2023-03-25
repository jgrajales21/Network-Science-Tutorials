#!/usr/bin/python3
#
# Wesleyan University
# COMP 332, Computer Networks, Spring 2023
# Homework 1: Tic-tac-toe game
# Joshua Andres Grajales
import random
import binascii
import socket
import sys

def sock_read(sock):
    bin_data = b''
    while True:
        bin_data += sock.recv(4096)
        try:
            bin_data.decode('utf-8').index('DONE')
            break
        except ValueError:
            pass

    return bin_data[:-4].decode('utf-8')

def sock_write(sock, str_data):
    str_data = str_data + 'DONE'
    bin_data = str_data.encode('utf-8')
    sock.send(bin_data)


class Board():
    """
    TicTacToe game board
    """

    def __init__(self, n):
        self.n = n

        # make the matrix: the empty board
        self.matrix = []
        for i in range(n):
            newRow = []
            for j in range(n):
                newRow.append("-")
            self.matrix.append(newRow)
        return

    def display(self):
        print("")

        # loop through matrix to display the board
        for array in self.matrix:
            print(array)

        return self.matrix


    def record(self,row,col,player):
        # record move in matrix
        # row and col are the int locations in matrix
        # player is a boolean: True = user
        if player:
            self.matrix[row][col] = 'X'
            return
        self.matrix[row][col] = 'O'
        return

class TicTacToe():
    """
    TicTacToe game
    """
    # keep track of
    # 1. state of game
    # 2. function for when server makes move --> random or intelligent
    # 3. function for when user makes move --> query the user

    def __init__(self, n):
        self.n = n
        self.board = Board(n)

    def display(self):
        return self.board.display()

    def isWinner(self):
        # returns tuple of bool and char of winner

        # check if any horizontal wins
        for array in self.board.matrix:
            if len(set(array)) == 1 and array[0] != '-': return (True,array[0])

        # check if any vertical wins
        for col in range(self.n):
            colData = []
            for row in range(self.n):
                colData.append(self.board.matrix[row][col])

            if len(set(colData)) == 1 and colData[0] != '-': return (True,colData[0])

        # check if any diagonal wins (Top left to Bottom right)
        diagData = []
        for i in range(self.n):
            diagData.append(self.board.matrix[i][i])

        if len(set(diagData)) == 1 and diagData[0] != '-':
            return (True,diagData[0])

        # check if any diagonal wins (Bottom left to top right)
        diagStairData = []
        j = 0
        for i in range(self.n-1,-1,-1):
            diagStairData.append(self.board.matrix[i][j])
            j += 1

        if len(set(diagStairData)) == 1 and diagStairData[0] != '-':
            return (True,diagStairData[0])


        return (False,"-")

    def isTie(self):
        # loop over matrix and check if a dash still exists
        for array in self.board.matrix:
            for elem in array:
                if elem == '-': return False
        return True

    def userMove(self):
        # prompt user to make a move and then validate the move
        row = int(input("Choose row ["+str(0)+"-"+str(self.n-1)+"]: "))
        col = int(input("Choose col ["+str(0)+"-"+str(self.n-1)+"]: "))

        # validate move
        # check if within bounds and that location is empty
        while row < 0 or self.n-1 < row or col < 0 or self.n-1 < col or self.board.matrix[row][col] != '-':
            print("Invalid row,col selection")
            print("row and col must be within [0-"+str(self.n-1)+"] and be empty (i.e must have -)")
            print()
            row = int(input("Choose row ["+str(0)+"-"+str(self.n-1)+"]: "))
            col = int(input("Choose col ["+str(0)+"-"+str(self.n-1)+"]: "))

        # record the move in the matrix
        self.board.record(row,col,True)

        # display the board
        self.display()

    def serverMove(self):

        # generate random number in between 0 and n
        while True:
            row = random.randint(0,self.n-1)
            col = random.randint(0,self.n-1)
            if self.board.matrix[row][col] == '-':

                # record player move in the matrix
                self.board.record(row,col,False)
                print("Server Move")
                self.display()
                return

    def validateServerMove(self,row,col):
        # tup = (row,col)
        # validates move made by server; move is passed as tuple of x (row) y
        # (col); for distributed edition
        if self.board.matrix[row][col] == '-':
            # record the server move in matrix
            self.board.record(row,col,False)
            print("Server Move")
            self.display()
            return True

        return False

def serverMoveDist(n):
    # make a move 0 to n-1 for row and col
    row = random.randint(0,n-1)
    col = random.randint(0,n-1)
    return (row,col)

class Server():
    """
    Server for TicTacToe game
    """

    # creates new game and then enter whole loop alt. between user and server

    def __init__(self):
        print('')

    def play(self):
        print("==================")
        print("| TicTacToe Game |")
        print("==================\n")

        numRows = 0
        while numRows < 3:
            numRows = int(input("Enter the number of rows in TicTacToe board: "))
            if numRows < 3: print("Number of rows must be 3 or greater.")

        # display the board by calling another class
        game = TicTacToe(numRows)
        game.display()
        # begin game loop, continue until win or board is full
        while True:
            # begin with user move
            game.userMove()
            # check if user is winner
            results1 = game.isWinner()
            if results1[0] and results1[1] == 'X':
                print("You Win!!!")
                return

            # if moves have been maxed out and there is no win
            if game.isTie():
                print("It's a tie!!!")
                return

            # if user is not winner, server move
            game.serverMove()
            # check if server is winner
            results2 = game.isWinner()
            if results2[0] and results2[1] == 'O':
                print("Server Wins!!!")
                return

            # if neither won check if there are any moves left in the game
            if game.isTie():
                print("It's a tie!!!")
                return


def main():
    s = Server()
    s.play()

if __name__ == '__main__':
    main()
