# simulation2.py

import simpy
import random
import math
from matplotlib import pyplot


class Node():

	def __init__(self, env, id, lambda, algorithm):






class SlottedAloha():
	def __init__ (self, env, num_nodes, lambda, label, algorithm):
		self.env = env
		self.action = env.process(self.start())

	def start(self):

		yield self.env.timeout(1)


env = simpy.Environment()

label = 0
for i in range(.1, .9, .1):
	binary_exponential = SlottedAloha(env, 10, i, label, 'binary_exponential')
	#linear_exponential = SlottedAloha(env, 10, i, label, 'linear_exponential')
	label += 1

env.run(until=10000)