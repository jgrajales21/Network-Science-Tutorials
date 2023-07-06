# Joshua Andres Grajles
# COMP 332
# HW6 rom socket import *
from socket import *
from random import randint
import time

# server must
# 1. Turn on
# 2. Listen for messages
#   2.1: Receive Message
#   2.2: Randomly decide whether it will
#       (a): echo the message to client
#       (b): drop the message and allow for timeout to occur
# 3. Terminates when client sends close socket prompt

# 1. turn on
server_port = 50007
server_sock = socket(AF_INET, SOCK_DGRAM)
server_sock.bind(('', server_port))
print("Server is ready to receive.")

i = 0
# 2., listen
while True:
    print("Msg number: "+str(i))

    # 2.1 receive message
    # get message from the client
    message, add = server_sock.recvfrom(4096)

    # 3. close
    if message == b'': server_sock.close()

    # 2.2 begin drop procedure
    # if we get a number above 8 then we force a timeout
    drop = randint(0,10) >= 8

    # 2.2 (a)
    # if drop send nothing
    if drop:
        print("Server will not echo.")

    # 2.2 (b) send the message back to the client
    else:
        server_sock.sendto(message, add)

    i+=1
