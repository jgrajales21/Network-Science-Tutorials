# Joshua Andres Grajles
# COMP 332
# HW6
from socket import *
import time

# 1. Send the message AND
#   1.1 Begin RTT timer that determines how long it takes for message to be echoed
#   1.2 Keep track of timer to determine if it exceeds timeout
#       (a): IF RTT timer <= timeout
#               print message received and RTT timer
#       (b): ELSE
#               indicate timout occurred
# 2. Close socket after 10 messages have been sent from client


serverName = ''
serverPort = 50007
clientSocket = socket(AF_INET,SOCK_DGRAM)
msg = 'Test Message'
clientSocket.settimeout(5.0)

# begin loop to send multiple messages
i = 1
while i < 11:
    print("Trying to send msg number: "+str(i))

    # 1. send message and start timer
    start_time = time.time()
    clientSocket.sendto((msg+" "+str(i)).encode('utf-8'), (serverName,serverPort))
    print("Sent Message: "+str(msg))

    try:
        # receive message
        message, serverAddr = clientSocket.recvfrom(2048)

        # end timer
        end_time = time.time()

        time_lapsed = end_time - start_time
        print("Recieved message from: " +str(serverAddr))
        print("Msg content: "+str(message.decode('utf-8')))
        print("RTT [sec]: "+str(time_lapsed))

    except:
        print("Timed out, message took longer than 5 seconds to arrive")

    i += 1
    print()
