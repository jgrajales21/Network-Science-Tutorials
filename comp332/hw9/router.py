# Joshua Andres Grajales
# Distance Vector Algorithm
# HW9

from socket import *
import time
import numpy as np
import threading
import pickle # The pickle module can transform a complex object into a byte stream and it can transform the byte stream into an object with the same internal structure
import sys

class Router:

    # port is (an int) port number of current router
    # neighbors is a dictionary:
    #       key = router_port , value = (port #, cost to router_port from
    #       current router)

    IP_ADDRESS = 'localhost'
    BUFFER = 2048
    INFINITY = 16

    def __init__(self, port, neighbors):

        ''' creating the routing table '''
        self.port = port
        self.neighbors = neighbors
        self.neighbors[port] = (port,0)
        self.RoutingTable = self.create_table()
        self.initiate()

    def create_table(self):
        '''
        for an n router network we need to make a table of the form
            a | b | c | ... | n
        ________________________
        a |   |   |   | ... | n
        _______________________
        b |   |   |   | ... | n
        _______________________
        c |   |   |   | ... | n
        .
        .
        .
        n |   |   |   | ... | n

        we use the information in self.neighbors to do this

        Returns Routing table given initial conditions; routing table is in the
        form of a matrix

        RUNTIME: o(n^2); n is the number of routers
        '''

        RoutingTable = []
        # we need to have the same order of entries in our routing tables, so
        # long as we sort by router_port we can ensure this
        entries = sorted(self.neighbors.keys())
        DistanceVector_currentRouter = [self.neighbors[router][1] for router in entries]

        # loop over rows of the matrix in order of port number
        for router in entries:
            if router == self.port:
                RoutingTable.append(DistanceVector_currentRouter)
            else:
                # initialize nbrs distance vectors to infinity
                initialDV_nbr = []
                for col in range(len(entries)):
                    initialDV_nbr.append(np.inf)
                RoutingTable.append(initialDV_nbr)

        self.print_table(RoutingTable)
        return RoutingTable

    def print_table(self, RoutingTable):
        '''
        prints the routing table

        RUNTIME: o(n); n is the number of routers
        '''
        entries = sorted(self.neighbors.keys())
        print('____________________________________________________________________')
        print("ROUTER "+str(self.port)+"'s routing table: ")
        for i in range(len(RoutingTable)):
            print('____________________________________________________________________')
            print('Distance Vector for node:'+str(entries[i])+'\n'+str(RoutingTable[i]))
            print('____________________________________________________________________')

        print('____________________________________________________________________')
        print()

    def update_RoutingTable(self):
        '''
        updates routing table using Bellman Ford equation:
        D_x(y) = min_v { c(x,v) + D_v(y) }

        where
            - D_x(y) is the minimum distance from x to y using the cost from node x to y
            and the distance vectors from neighbors
            - v are all of the neighbors of x
            - c(x,v) is the edge weight from x to v
            - d_v(y) is the distance from v to y as seen in v's Distance vector

        Distance vector current router is updated IFF a new lower cost is
        computed

        RUNTIME: o(n^3); n is the number of routers in the network
        '''

        # find the index of the current port number
        entries = sorted(self.neighbors.keys())
        # get the current router's DV
        currentRouter_idx = entries.index(self.port)

        # assuming the cost to neighbors is fixed we can always use
        # self.neighbors for c(x,v)

        isUpdated = False # boolean variable keeps track of whether current
                          # router's routing table was changed
        for destination in entries:
            dest_idx = entries.index(destination)
            min_dist_to_dest = self.RoutingTable[currentRouter_idx][dest_idx]
            #loop over current routers neighbors
            for nbr in self.neighbors.keys():
                nbr_port, c_OFxv = self.neighbors[nbr]
                if nbr_port != self.port:
                    # get the index of the neighbor
                    nbr_idx = entries.index(nbr_port)
                    # determine the distance from neighbor to destination
                    D_vOFdest = self.RoutingTable[nbr_idx][dest_idx]
                    if c_OFxv+D_vOFdest < min_dist_to_dest:
                        self.RoutingTable[currentRouter_idx][dest_idx] = c_OFxv+D_vOFdest

                        isUpdated = True
        if isUpdated:
            print("TABLE CHANGED")
        else:
            print("TABLE DID NOT CHANGE")

        self.print_table(self.RoutingTable)

        return isUpdated

    def send_DV(self):
        '''
        send the Router object for current router to other routers in the network using UDP
        '''
        while True:
            for nbrs_port in self.neighbors.keys():
                if nbrs_port != self.port:
                    my_socket = socket(AF_INET, SOCK_DGRAM)
                    address = (Router.IP_ADDRESS, nbrs_port)
                    # send this entire Router Instance to the other Routers in
                    # the Network using pickle to preserve the format of the
                    # data
                    my_socket.sendto(pickle.dumps(self),address)
                    my_socket.close()
                    time.sleep(1)

    def receive_DV(self):
        '''
        receives router object, unpacks it and sends the updated DV
        '''
        entries = sorted(self.neighbors.keys())

        numConverged = 0 # number of converged tables
        access_key = threading.Lock()
        while True:
            my_socket = socket(AF_INET, SOCK_DGRAM)
            my_socket.settimeout(2.25)
            address = (Router.IP_ADDRESS, self.port)
            try:
                my_socket.bind(address)
                data, address = my_socket.recvfrom(Router.BUFFER)
                decodedRouterObject = pickle.loads(data)

                # need to interact with the newly received routing table from
                # neighbor x, RT', and swap the DV for x in the
                # current routers routing table RT, for the DV of x found in
                # RT'

                # get the port number of the owner of the RT' table
                RTp_port = decodedRouterObject.port

                # get the idx of x in the routing table; b/c we sorted our routing tables by port number it is in the same
                # idx as in the current routing table RT
                nbrs_idx = entries.index(RTp_port)
                # get the nbrs DV
                nbrs_DV = decodedRouterObject.RoutingTable[nbrs_idx]
                # update current routing table RT using newly received DV from nbr x
                self.RoutingTable[nbrs_idx] = nbrs_DV

                # recaluclate the routing Table; if it returns true then we
                # updated our table and need to forward to other routers in the
                # network
                isUpdated = self.update_RoutingTable()
                print(isUpdated)
                if isUpdated:
                    self.send_DV()


            except Exception as e:
                print('____________________________________________________________________')
                print("ERROR RECEIVING DATA")
                print(e)
                print('____________________________________________________________________')
                my_socket.close()


    def initiate(self):
        '''
        start the communication between routers
        '''
        print("ROUTER: "+str(self.port))
        print()
        sender_thread = threading.Thread(target=self.send_DV)
        receiver_thread = threading.Thread(target=self.receive_DV)
        sender_thread.start()
        receiver_thread.start()
# input format: Router(x, y)
# x is the port number of a router;
# y is a dictionary of the form port #: (port #, distance from x)
# in other words y is the set of routers in the network
# it's unclear to me how the DV algorithm works with networks that are not
# strongly connected (i.e if all routers are neighbors to all routers)

# NOTE: I decided to take my own approach and not specify as many input parameters as
# encouraged in the homework, nonetheless I hope this code is acceptable and
# just as easy to follow. YOU RUN DV ON THE NETWORK BY SPECIFYING ALL INFO
# BELOW

# NOTE: one quirk is that my code does not terminate even after tables
# converge, advice on how to do this is appreciated
router1 = Router(50001, {50002:(50002,2), 50003:(50003,7)})
router2 = Router(50002, {50001:(50001,2), 50003:(50003,1)})
router3 = Router(50003, {50001:(50001,7), 50002:(50002,1)})
