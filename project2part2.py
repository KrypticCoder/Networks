import simpy
import random
import math
from matplotlib import pyplot

RANGE = 10000

print('Running (the results will be saved automatically on the project folder)...')

yPoints1 = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0];
yPoints2 = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0];
xPoints = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09];

# math function to perform the exponential backoff
def exponential_backoff(N):
    return random.randint(0, 2**(min(N, 10)))

def linear_backoff(N):
    return random.randint(0, 1024)

class Node(object):
    def __init__(self, env, id, algorithm,rate = 0):
        self.env = env # it holds a simpy environment
        self.id = id # to debug
        self.rate = rate # the rate 
        self.L = 0
        self.N = 0
        self.S = math.ceil(1/rate)
        self.ready = 0 # flag => 0: the node is not ready to send data; 1: the node is ready to send data
        self.algorithm = algorithm

    # method responsible to flag if a node is OK to transfer data
    def isReady(self):
        self.L = self.L + self.rate
        if((self.env.now == self.S) and (self.L > 1)):
            self.ready = 1
        else:
            if(self.S <= self.env.now): # if true, Node is out of sync and needs to be refreshed according to env.now
                self.S = self.env.now + 1
            self.ready = 0

            #print('Node.isReady Debugging: id:%d, L:%d, N:%d, S:%d, ready:%d' % (self.id, self.L, self.N, self.S, self.ready))

    # method: deals with the Node state after a transmission is allowed 
    def transfering(self):
        self.L = self.L - 1
        self.S = self.env.now + 1
        self.N = self.N = 0
        self.ready = 0

    # method: deals with the collision state afer a collision is detected.
    def collision(self):
        if(self.algorithm==0):
            self.S = self.env.now + 1 + exponential_backoff(self.N)
        else:
             self.S = self.env.now + 1 + linear_backoff(self.N)
        self.N = self.N + 1
        self.ready = 0

class Ethernet(object):
    def __init__(self, env, number_of_nodes, rate, label, algorithm):
        self.env = env
        self.number_of_nodes = number_of_nodes
        self.algorithm = algorithm
        self.Nodes = [Node(env, i,algorithm, rate) for i in range(number_of_nodes)]
        self.ready_nodes = 0 # amount of nodes ready to be transfer in a certain period of time
        self.action = env.process(self.run()) # creates the process
        self.label = label

    # method: deals with the collision state on ethernet
    def collision(self): 
        for i in range(self.number_of_nodes):
            if(self.Nodes[i].ready == 1): # in a collision, those who are ready to transfer need to go through the exponential backoff phase
                self.Nodes[i].collision()
        
    def run(self):
        ready_node = -1 # flag used to identify the ready node, in case of a non-collision situation
        
        while True:
            for i in range(self.number_of_nodes): # see how many nodes are ready to transfer
                self.Nodes[i].isReady()
                if (self.Nodes[i].ready == 1): # if ready, iterate the number of ready nodes, and setup the ready_node flag
                    self.ready_nodes = self.ready_nodes + 1
                    ready_node = i # only useful if there is no collision
                    
            if (self.ready_nodes  == 1 and ready_node != -1): # no collision at all
               # print('Node %d transfering on slot %d' % (ready_node, self.env.now))
                self.Nodes[ready_node].transfering()
                if(self.algorithm==0):
                    yPoints1[self.label] = yPoints1[self.label] + 1
                else:
                    yPoints2[self.label] = yPoints2[self.label] + 1
            else:
                if(ready_node != -1): # collision detected
                    self.collision()

            # reset the flags
            ready_node = -1
            self.ready_nodes = 0
            yield self.env.timeout(1)
        
env = simpy.Environment()

ethernet11 = Ethernet(env, 10, 0.01, 0, 0)
ethernet12 = Ethernet(env, 10, 0.02, 1, 0)
ethernet13 = Ethernet(env, 10, 0.03, 2, 0)
ethernet14 = Ethernet(env, 10, 0.04, 3, 0)
ethernet15 = Ethernet(env, 10, 0.05, 4, 0)
ethernet16 = Ethernet(env, 10, 0.06, 5, 0)
ethernet17 = Ethernet(env, 10, 0.07, 6, 0)
ethernet18 = Ethernet(env, 10, 0.08, 7, 0)
ethernet19 = Ethernet(env, 10, 0.09, 8, 0)

ethernet21 = Ethernet(env, 10, 0.01, 0, 1)
ethernet22 = Ethernet(env, 10, 0.02, 1, 1)
ethernet23 = Ethernet(env, 10, 0.03, 2, 1)
ethernet24 = Ethernet(env, 10, 0.04, 3, 1)
ethernet25 = Ethernet(env, 10, 0.05, 4, 1)
ethernet26 = Ethernet(env, 10, 0.06, 5, 1)
ethernet27 = Ethernet(env, 10, 0.07, 6, 1)
ethernet28 = Ethernet(env, 10, 0.08, 7, 1)
ethernet29 = Ethernet(env, 10, 0.09, 8, 1)

env.run(until=RANGE)

yPoints1 = [yPoints1[i]/RANGE for i in range(9)];

pyplot.plot(xPoints, yPoints1)
pyplot.xlabel('arrival rate (pkts/sec)')
pyplot.ylabel('throughput (pkts/sec)')
pyplot.title('Project 2, part 2.1: exponential backoff')
pyplot.grid(True)
pyplot.savefig("Project2Part21.jpeg")

pyplot.clf() # clear the image

yPoints2 = [yPoints1[i]/RANGE for i in range(9)];

pyplot.plot(xPoints, yPoints2)
pyplot.xlabel('arrival rate (pkts/sec)')
pyplot.ylabel('throughput (pkts/sec)')
pyplot.title('Project 2, part 2.2: linear backoff')
pyplot.grid(True)
pyplot.savefig("Project2Part22.jpeg")

print('Done!')