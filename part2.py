from __future__ import division
import random
import simpy
import math
from matplotlib import pyplot

SLOT_LENGTH = 1
RANDOM_SEED = 29
SIM_TIME = 500000
NUM_NODES = 10
exp_throughput = []
linear_throughput = []
Lambda = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]

class node:
    def __init__(self, env, rate, my_id):
        self.env = env
        self.success_packets = 0
        self.flag_processing = 0
        self.packet_number = 0
        self.id = my_id
        self.rate = rate
        self.N = 0
        self.L = 0
        self.S = 0

    def process_packet(self, env):
        self.L -= 1
        #finish processing set attmpt to 0
        self.N = 0
        self.success_packets += 1
        self.S += 1
  
    def packets_arrival(self, env):
        # packet arrivals
        while True:
            # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.rate))
    
            # arrival time of one packet
            self.packet_number += 1
            self.L += 1
            

    def exponential_backoff(self):
        self.S = self.S + random.randint(0, 2**min(self.N, 10))
        self.N += 1
        
    def linear_backoff(self):
        self.S = self.S + random.randint(0, min(self.N, 1024)) + 1
        self.N += 1
        
class ethernet:
    def __init__(self, env, rate, algorithm):
        self.env = env
        self.slot_number = 0
        self.success_slots = 0
        self.collision_slots = 0
        self.empty_slots = 0
        self.list_nodes = [node(env, rate, x) for x in range(NUM_NODES)]
        self.rate = rate
        self.algorithm = algorithm 

    def start(self):
    #enable packet arrival at simultaneous time
        for x in range(NUM_NODES):
            self.env.process(self.list_nodes[x].packets_arrival(self.env))

        while True:
            yield self.env.timeout(SLOT_LENGTH)

            request = 0                 # counter used to keep track of requests at current slot
            node_index = -1             #   index of the first request
            for x in range(NUM_NODES):
                if(self.list_nodes[x].L == 0):
                    continue            # if list_nodes have no packets in their queue, ignore
                
                # list_nodes queue have packets,
                # update their slot if they are behind current slot
                if((self.list_nodes[x].S <= self.slot_number)):
                    request += 1
                    self.list_nodes[x].S = self.slot_number
                    node_index = x

            # If only one node wants to transmit 
            if request == 1:
                self.success_slots += 1
                
                self.list_nodes[node_index].process_packet(self.env)
            
            # If more than 1 request, go through and delay each list_nodes that requested
            elif request > 1:
                self.collision_slots += 1
                for x in range(NUM_NODES):
                    if(self.list_nodes[x].S == self.slot_number) and (self.list_nodes[x].L > 0):
                        if self.algorithm == 'exponential':
                            self.list_nodes[x].exponential_backoff()
                        if self.algorithm == 'linear':
                            self.list_nodes[x].linear_backoff()
            elif request == 0:
                self.empty_slots += 1          

            self.slot_number += 1

    def get_expthroughput(self):
        print("lambda: ", self.rate, " throughput: ", self.success_slots/self.slot_number)
        print("<success:", self.success_slots, " > <collision: ", self.collision_slots, " > <empty: ", self.empty_slots,
                "> <total", self.slot_number, " >") 
        exp_throughput.append(self.success_slots/self.slot_number)

    def get_linearthroughput(self):
        print("lambda: ", self.rate, " throughput: ", self.success_slots/self.slot_number)
        print("<success:", self.success_slots, " > <collision: ", self.collision_slots, " > <empty: ", self.empty_slots,
                "> <total", self.slot_number, " >") 
        linear_throughput.append(self.success_slots/self.slot_number)
                

def main():
   
    print("Exponential backoff")
    for rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        env = simpy.Environment()
        myethernet = ethernet(env, rate, 'exponential')
        env.process(myethernet.start())
        env.run(until=SIM_TIME)
        myethernet.get_expthroughput()
    print("graph will be saved as exponential_backoff.jpeg")
    print('\n')

    print("Linear backoff")
    for rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        env = simpy.Environment()
        myethernet = ethernet(env, rate, 'linear')
        env.process(myethernet.start())
        env.run(until=SIM_TIME)
        myethernet.get_linearthroughput()

    print("graph will be saved as linear_backoff.jpeg")


    pyplot.plot(Lambda, exp_throughput)
    pyplot.xlabel('arrival rate (pkts/sec)')
    pyplot.ylabel('throughput (pkts/sec)')
    pyplot.title('Project 2, part 2.1: exponential backoff')
    pyplot.grid(True)
    pyplot.savefig("exponential_backoff.jpeg")

    pyplot.clf() # clear the image

    pyplot.plot(Lambda, linear_throughput)
    pyplot.xlabel('arrival rate (pkts/sec)')
    pyplot.ylabel('throughput (pkts/sec)')
    pyplot.title('Project 2, part 2.2: linear backoff')
    pyplot.grid(True)
    pyplot.savefig("linear_backoff.jpeg")

if __name__ == '__main__': main()