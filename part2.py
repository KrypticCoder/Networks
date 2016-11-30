from __future__ import division
import random
import simpy
import math
from matplotlib import pyplot

SLOT_LENGTH = 1
RANDOM_SEED = 31
SIM_TIME = 500000
MU = 1
NUM_NODES = 10
exp_throughput = []
linear_throughput = []
Lambda = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]

class host:
    def __init__(self, env, ethernet, arrival_rate, my_id):
        self.ethernet = ethernet#the resource
        self.env = env
        self.transmit_slot= 0
        self.success_packets = 0
        self.flag_processing = 0
        self.packet_number = 0
        self.arrival_rate = arrival_rate
        self.attempts = 0
        self.queue_len = 0
        self.id = my_id


    def process_packet(self, env, ethernet):
        #print("Call process packet on Host ", self.id)
        #print("Process takes ", process_time)
        self.queue_len -= 1
        #yield env.timeout(process_time)
        #print("After call process packet, Host ", self.id, " quelength is ", self.queue_len)
        #finish processing set attmpt to 0
        self.attempts = 0
        self.success_packets += 1
        self.transmit_slot += 1
  
    def packets_arrival(self, env):
        # packet arrivals
        #print('Initiating packet arrival.')
        while True:
             # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.arrival_rate))
            #print("Host ", self.id, "has incomming packet. <---------------------------------------")
              # arrival time of one packet

            self.packet_number += 1
            self.queue_len += 1
            #print("Host ", self.id, " queue is now ", self.queue_len)

    #if collision this reset host's next transmit slot
    def delay_transmission_exp(self):
        self.transmit_slot = self.transmit_slot + random.randint(0, 2**min(self.attempts, 10))
        self.attempts += 1
        #print("Host ", self.id, " delayed packet to slot ", self.transmit_slot, " with attempts ", self.attempts)
    def delay_transmission_lin(self):
        self.transmit_slot = self.transmit_slot + random.randint(0, min(self.attempts, 1024)) + 1
        self.attempts += 1
        #print("Host ",self.id," is delayed to ", self.transmit_slot, "with attempts", self.attempts)
class ethernet:
    def __init__(self, env, arrival_rate):
        self.env = env
        self.server = simpy.Resource(env, capacity=1)
        self.slot_number = 0
        self.success_slots = 0
        self.collision_slots = 0
        self.empty_slots = 0
        self.hosts = []
        self.arrival_rate = arrival_rate
        for x in range(NUM_NODES):
            self.hosts.append(host(env, ethernet, arrival_rate, x))

    def ethernet_control_exponential_delay(self):#only one line difference
    #enable packet arrival at simultaneous time
        for x in range(NUM_NODES):
            self.env.process(self.hosts[x].packets_arrival(self.env))

        while True:
            #wait for slot time
            yield self.env.timeout(SLOT_LENGTH)
            #print("=====================")
            #print("Time ", self.env.now)
            #print("Slot number", self.slot_number)
            request = 0 #how many request at current slot?
            host_index = -1 #index of the first request
            for x in range(NUM_NODES):
                if(self.hosts[x].queue_len == 0):
                    continue#don't even care if hosts have no queue, packets
                
                #hosts queue have packets,
                # update their slot if they are behind current slot
                if((self.hosts[x].transmit_slot <= self.slot_number)):
                    request += 1
                    self.hosts[x].transmit_slot = self.slot_number
                    host_index = x

                #print("Host ", x, " can possibly transmit at slot ", self.hosts[x].transmit_slot, "Queue is ", self.hosts[x].queue_len)
                #count only hosts that have stuff to transmit
            #print("total host request at current slot: ", request)

            #allow the host to process
            if request == 1:
                self.success_slots += 1
                #print(">>Can TRANSMIT<< since request = 1")
                self.hosts[host_index].process_packet(self.env, self.server)
            
            #more than 1 request? then go through and delay each hosts that requested
            elif request > 1:
                self.collision_slots += 1
                for x in range(NUM_NODES):
                    if(self.hosts[x].transmit_slot == self.slot_number) and (self.hosts[x].queue_len > 0):
                        self.hosts[x].delay_transmission_exp()
            elif request == 0:
                self.empty_slots += 1          

            self.slot_number += 1

    def ethernet_control_linear_delay(self):#only 1 line difference
    #enable packet arrival at simultaneous time
        for x in range(NUM_NODES):
            self.env.process(self.hosts[x].packets_arrival(self.env))

        while True:
            #wait for slot time
            yield self.env.timeout(SLOT_LENGTH)
            #print("=====================")
            #print("Time ", self.env.now)
            #print("Slot number", self.slot_number)
            request = 0 #how many request at current slot?
            host_index = -1 #index of the first request
            for x in range(NUM_NODES):
                if(self.hosts[x].queue_len == 0):
                    continue#don't even care if hosts have no queue, packets
                
                #hosts queue have packets,
                # update their slot if they are behind current slot
                if((self.hosts[x].transmit_slot <= self.slot_number)):
                    request += 1
                    self.hosts[x].transmit_slot = self.slot_number
                    host_index = x

                #print("Host ", x, " can possibly transmit at slot ", self.hosts[x].transmit_slot, "Queue is ", self.hosts[x].queue_len)
                #count only hosts that have stuff to transmit
            #print("total host request at current slot: ", request)

            #allow the host to process
            if request == 1:
                self.success_slots += 1
                #print(">>Can TRANSMIT<< since request = 1")
                self.hosts[host_index].process_packet(self.env, self.server)
            
            #more than 1 request? then go through and delay each hosts that requested
            elif request > 1:
                self.collision_slots += 1
                for x in range(NUM_NODES):
                    if(self.hosts[x].transmit_slot == self.slot_number) and (self.hosts[x].queue_len > 0):
                        self.hosts[x].delay_transmission_lin()

            elif request == 0:
                self.empty_slots += 1          

            self.slot_number += 1

    def get_expthroughput(self):
        print("lambda: ", self.arrival_rate, " throughput: ", self.success_slots/self.slot_number)
        print("<success:", self.success_slots, " > <collision: ", self.collision_slots, " > <empty: ", self.empty_slots,
                "> <total", self.slot_number, " >") 
        exp_throughput.append(self.success_slots/self.slot_number)

    def get_linearthroughput(self):
        print("lambda: ", self.arrival_rate, " throughput: ", self.success_slots/self.slot_number)
        print("<success:", self.success_slots, " > <collision: ", self.collision_slots, " > <empty: ", self.empty_slots,
                "> <total", self.slot_number, " >") 
        linear_throughput.append(self.success_slots/self.slot_number)
                

def main():
    throughput = [0]*9
   
    print("Running Exponential backoff at simulation time ", SIM_TIME)
    print("Please wait patiently, numbers are being calculated")
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        env = simpy.Environment()
        myethernet = ethernet(env, arrival_rate)
        env.process(myethernet.ethernet_control_exponential_delay())
        env.run(until=SIM_TIME)
        myethernet.get_expthroughput()
    
    print("====")
    print("====")
    print("Running Linear backoff at simulation time ", SIM_TIME)
    print("Please wait patiently, numbers are being calculated")

    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        env = simpy.Environment()
        myethernet = ethernet(env, arrival_rate)
        env.process(myethernet.ethernet_control_linear_delay())
        env.run(until=SIM_TIME)
        myethernet.get_linearthroughput()


    pyplot.plot(Lambda, exp_throughput)
    pyplot.xlabel('arrival rate (pkts/sec)')
    pyplot.ylabel('throughput (pkts/sec)')
    pyplot.title('Project 2, part 2.1: exponential backoff')
    pyplot.grid(True)
    pyplot.savefig("Proj2exp.jpeg")

    pyplot.clf() # clear the image

    pyplot.plot(Lambda, linear_throughput)
    pyplot.xlabel('arrival rate (pkts/sec)')
    pyplot.ylabel('throughput (pkts/sec)')
    pyplot.title('Project 2, part 2.2: linear backoff')
    pyplot.grid(True)
    pyplot.savefig("Proj2linear.jpeg")

if __name__ == '__main__': main()