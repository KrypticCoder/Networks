# This is a simpy based  simulation of a M/M/1 queue system
# Dimitar Vasilev 999307063, Matt Quesada 998871736
import random
import simpy
import math
RANDOM_SEED = 29
SIM_TIME = 1000000
MU = 1
Lambda = [.2, .4, .6, .8, .9, .99]
BufferSize = [10, 50]


class server_queue:
    """ Queue system  """

    def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods, buffer_size, dropped_pkt):
        self.server = simpy.Resource(env, capacity=1)
        self.env = env
        self.queue_len = 0
        self.flag_processing = 0
        self.packet_number = 0
        self.sum_time_length = 0
        self.start_idle_time = 0
        self.arrival_rate = arrival_rate
        self.Packet_Delay = Packet_Delay
        self.Server_Idle_Periods = Server_Idle_Periods
        self.buffer_size = buffer_size
        self.dropped_pkt = dropped_pkt

    def process_packet(self, env, packet):
        with self.server.request() as req:
            yield req
            yield env.timeout(random.expovariate(MU))
            latency = env.now - packet.arrival_time
            self.Packet_Delay.addNumber(latency)
            self.queue_len -= 1
            if self.queue_len == 0:
                self.flag_processing = 0
                self.start_idle_time = env.now

    def packets_arrival(self, env):
        # packet arrivals
        while True:
            # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.arrival_rate))
            # arrival time of one packet
            if self.queue_len < self.buffer_size:  # packet can fit in buffer
                self.packet_number += 1
                # packet id
                arrival_time = env.now
                # print(self.num_pkt_total, "packet arrival")
                new_packet = Packet(self.packet_number, arrival_time)
                if self.flag_processing == 0:
                    self.flag_processing = 1
                    idle_period = env.now - self.start_idle_time
                    self.Server_Idle_Periods.addNumber(idle_period)
                    # print("Idle period of length {0} ended".format(idle_period))
                self.queue_len += 1
                env.process(self.process_packet(env, new_packet))
                self.dropped_pkt.addNumber(0.)
            else:  # If packet doesn't fit in buffer, packet dropped
                self.dropped_pkt.addNumber(1.)


class Packet:
    """Packet class """
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time


class StatObject:
    def __init__(self):
        self.dataset = []

    def addNumber(self, x):
        self.dataset.append(x)

    def sum(self):
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum

    def mean(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum / n

    def maximum(self):
        return max(self.dataset)

    def minimum(self):
        return min(self.dataset)

    def count(self):
        return len(self.dataset)

    def median(self):
        self.dataset.sort()
        n = len(self.dataset)
        if n // 2 != 0:  # get the middle number
            return self.dataset[n // 2]
        else:  # find the average of the middle two numbers
            return ((self.dataset[n // 2] + self.dataset[n // 2 + 1]) / 2)

    def standarddeviation(self):
        temp = self.mean()
        sum = 0
        for i in self.dataset:
            sum = sum + (i - temp)**2
        sum = sum / (len(self.dataset) - 1)
        return math.sqrt(sum)


def main():
    print("Simple queue system model: (mu = {0})".format(MU))
    print("{0:<9} {9:<9} {10:<9}".format("Lambda",
                                         "Count",
                                         "Min",
                                         "Max",
                                         "Mean",
                                         "Median",
                                         "Sd",
                                         "Utilization",
                                         "Theoretical",
                                         "BuffSize",
                                         "Pkt-Loss"))
    random.seed(RANDOM_SEED)
    for arrival_rate in Lambda:
        for buffer_size in BufferSize:
            env = simpy.Environment()
            Packet_Delay = StatObject()
            Server_Idle_Periods = StatObject()
            dropped_pkt = StatObject()
            router = server_queue(env, arrival_rate, Packet_Delay, Server_Idle_Periods, buffer_size, dropped_pkt)
            env.process(router.packets_arrival(env))
            env.run(until=SIM_TIME)
            print("{0:<9.3f} {8:<9.3f} {9:<9.3f}".format(
                round(arrival_rate, 3),
                int(Packet_Delay.count()),
                round(Packet_Delay.minimum(), 3),
                round(Packet_Delay.maximum(), 3),
                round(Packet_Delay.mean(), 3),
                round(Packet_Delay.median(), 3),
                round(Packet_Delay.standarddeviation(), 3),
                round(1 - Server_Idle_Periods.sum() / SIM_TIME, 3),
                int(buffer_size),
                round(dropped_pkt.mean(), 3)))

if __name__ == '__main__':
    main()
