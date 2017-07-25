# Dimitar Vasilev, Matthew Quesada

from __future__ import division
import random
import simpy
import math
from matplotlib import pyplot

SLOT_LENGTH = 1
RANDOM_SEED = 29
SIM_TIME = 100000
NUM_NODES = 10
exp_throughput = []
linear_throughput = []
Lambda = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]


class node:
    def __init__(self, env, rate):
        self.env = env
        self.rate = rate
        self.N = 0
        self.L = 0
        self.S = 0

    def process_packet(self, env):
        self.L -= 1
        # finish processing set attmpt to 0
        self.N = 0
        self.S += 1

    def packets_arrival(self, env):
        # packet arrivals
        while True:
            # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.rate))
            # arrival time of one packet
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
        self.wasted_slots = 0
        self.list_nodes = [node(env, rate) for currNode in range(NUM_NODES)]
        self.rate = rate
        self.algorithm = algorithm

    def start(self):
        # enable packet arrival at simultaneous time
        for eachNode in range(NUM_NODES):
            currentN = self.list_nodes[eachNode].packets_arrival(self.env)
            self.env.process(currentN)

        while True:
            transmissions = 0
            yield self.env.timeout(SLOT_LENGTH)

            # first index
            node_index = -1
            for current in range(NUM_NODES):
                packets_in_queue = self.list_nodes[current].L
                next_transmission = self.list_nodes[current].S
                # Check if node has packets
                # Check if behind in slots and update if so
                if(packets_in_queue and (next_transmission <= self.slot_number)):
                    transmissions = transmissions + 1
                    self.list_nodes[current].S = self.slot_number
                    node_index = current

            # if no wasted slots
            if(transmissions > 0):
                if(transmissions == 1):
                    self.success_slots = self.success_slots + 1
                    self.list_nodes[node_index].process_packet(self.env)
                else:   # there will be collisions since transmissions is greater than 1
                    self.collision_slots = self.collision_slots + 1
                    for currentNode in range(NUM_NODES):
                        if(self.list_nodes[currentNode].L > 0):
                            if(self.list_nodes[currentNode].S == self.slot_number):
                                # check which algorithm to use
                                if self.algorithm == 'exponential':
                                    self.list_nodes[currentNode].exponential_backoff()
                                else:
                                    self.list_nodes[currentNode].linear_backoff()
            else:  # increment wasted slot counter
                self.wasted_slots = self.wasted_slots + 1
            self.slot_number = self.slot_number + 1

    def get_expthroughput(self):
        throughput = self.success_slots / self.slot_number
        print("Lambda: %.2f" % self.rate + "| Total Slots: %i " % self.slot_number + " | Throughput: %.4f " % throughput + " | Successful Transmissions: %i " % self.success_slots + " | Collisions: %i " % self.collision_slots + " | Wasted Slots: %i" % self.wasted_slots)
        # append throughput to exponential throughputs list
        exp_throughput.append(throughput)

    def get_linearthroughput(self):
        throughput = self.success_slots / self.slot_number
        print("Lambda: %.2f " % self.rate + "| Total Slots: %i " % self.slot_number + " | Throughput: %.4f " % throughput + " | Successful Transmissions: %i " % self.success_slots + " | Collisions: %i " % self.collision_slots + " | Wasted Slots: %i" % self.wasted_slots)
        # append throughput to linear throughputs list
        linear_throughput.append(throughput)


def main():
    print("\nPlease Note: Matplotlib may display errors at end of output. Please ignore, as graphs are included in hard submission.\n")
    print("Simulation time is: %i. Slot Time T = 1. Number of Hosts N = 10\n" % SIM_TIME)
    print("Exponential Backoff Results")

    for rate in Lambda:
        env = simpy.Environment()
        myethernet = ethernet(env, rate, 'exponential')
        env.process(myethernet.start())
        env.run(until=SIM_TIME)
        myethernet.get_expthroughput()
    print("graph will be saved as exponential_backoff.jpeg")
    print('\n')

    print("Linear Backoff Results")
    for rate in Lambda:
        env = simpy.Environment()
        myethernet = ethernet(env, rate, 'linear')
        env.process(myethernet.start())
        env.run(until=SIM_TIME)
        myethernet.get_linearthroughput()

    print("graph will be saved as linear_backoff.jpeg")

    try:
        pyplot.plot(Lambda, exp_throughput)
        pyplot.xlabel('arrival rate (pkts/sec)')
        pyplot.ylabel('throughput (pkts/sec)')
        pyplot.title('Project 2, part 2.1: exponential backoff')
        pyplot.grid(True)
        pyplot.savefig("exponential_backoff.jpeg")

        pyplot.clf()  # clear the image

        pyplot.plot(Lambda, linear_throughput)
        pyplot.xlabel('arrival rate (pkts/sec)')
        pyplot.ylabel('throughput (pkts/sec)')
        pyplot.title('Project 2, part 2.2: linear backoff')
        pyplot.grid(True)
        pyplot.savefig("linear_backoff.jpeg")
    except:
        print("Graph function not supported")

if __name__ == '__main__':
    main()
