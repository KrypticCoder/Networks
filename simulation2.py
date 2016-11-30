# simulation2.py

import simpy
import random
import math
from matplotlib import pyplot

SLOT_LENGTH= 1
MU = 1
NUM_NODES = 10
RANDOM_SEED = 29
SIM_TIME = 1000000
success_slots = [0, 0, 0, 0, 0, 0, 0, 0, 0]
total_packets = [0, 0, 0, 0, 0, 0, 0, 0, 0]
Lambda = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]



class Node():
    def __init__(self, env, ethernet, node_id, algorithm, rate=0):
        self.env = env 
        self.ethernet = ethernet
        self.node_id = node_id # to debug
        self.rate = rate # the rate 
        self.queue_len = 0  # (L) number of packets in queue
        self.attempts = 0 # (N) number of times packet @ head of queue has been retransmitted
        self.transmit_slot = 0  #  (S) slot # when next transmission attempt will be made for packet # head of queue
        self.ready = False # flag => 0: the node is not ready to send data; 1: the node is ready to send data
        self.algorithm = algorithm 
        self.packet_number = 0
        self.success_packets = 0


    def process_packet(self, env, packet):
        
        process_time = random.expovariate(MU)
        self.queue_len -= 1
        yield env.timeout(process_time)
        self.attempts = 0
        self.success_packets += 1
        self.transmit_slot += 1

    def packets_arrival(self, env):
        while True:
            yield env.timeout(random.expovariate(self.rate))
            self.packet_number += 1
            self.queue_len += 1

    def exponential_backoff(self):
        self.transmit_slot = self.transmit_slot + random.randint(0, 2**min(self.attempts, 10)) + 1
        self.attempts += 1

    def linear_backoff(self):
        self.transmit_slot = self.transmit_slot + random.randint(0, min(self.attempts, 1024))  + 1
        self.attempts += 1  



class Ethernet():
    def __init__ (self, env, rate, algorithm):
        self.resource = simpy.Resource(env, capacity = 1)
        self.env = env
        self.rate = rate
        self.algorithm = algorithm
        self.nodes = [Node(env, Ethernet, x, self.algorithm, self.rate) for x in range(NUM_NODES)]
        self.slot_number = 0
        self.success_slots = 0

    def start(self):
        for x in range(NUM_NODES):
            self.env.process(self.nodes[x].packets_arrival(self.env))

        while True:
            yield self.env.timeout(SLOT_LENGTH)
            request = 0
            node_index = -1

            for x in range(NUM_NODES):
                if(self.nodes[x].queue_len == 0):
                    continue

                if((self.nodes[x].transmit_slot <= self.slot_number)):
                    request += 1
                    self.nodes[x].transmit_slot = self.slot_number
                    host_index = x

            # If only one node wants to transmit
            if request == 1:
                self.success_slots += 1
                self.env.process(self.nodes[node_index].process_packet(self.env, self.resource))
            
            # If more than 1 request, delay all other hosts that requested
            elif request > 1:
                for x in range(NUM_NODES):
                    if(self.nodes[x].transmit_slot == self.slot_number) and (self.nodes[x].queue_len > 0):
                        if self.algorithm == 'exponential':
                            self.nodes[x].exponential_backoff()
                        elif self.algorithm == 'linear':
                            self.nodes[x].linear_backoff()

            self.slot_number += 1

    def get_throughput(self):
        print("lambda: ", self.rate, " throughput: ", self.success_slots/self.slot_number)



def main():
    random.seed(RANDOM_SEED)
    for arrival_rate in Lambda:
        env = simpy.Environment()
        ethernet = Ethernet(env, arrival_rate, 'exponential')
        env.process(ethernet.start())
        env.run(until=SIM_TIME)
        ethernet.get_throughput()

    for arrival_rate in Lambda:
        env = simpy.Environment()
        ethernet2 = Ethernet(env, arrival_rate, 'linear')
        env.process(ethernet2.start())
        env.run(until=SIM_TIME)
        ethernet2.get_throughput()


if __name__ == '__main__': main()
