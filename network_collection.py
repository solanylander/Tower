import math, random, sys, pygame
from pygame.locals import *
from network import Network

class NetworkCollection:
	def __init__(self):
		self.network_array = []
		for i in range(7):
			self.network_array.append(Network(i))

	def get_turn(self):
		return self.network_array[0].turn_number

	def increment_turn(self):
		turn = self.get_turn()
		for i in range(7):
			self.network_array[i].turn_number = (turn + 1) % 4

	def save_checkpoint(self):
		for i in range(7):
			self.network_array[i].save_checkpoint()

	def load_checkpoint(self, preset):
		print("loading", preset)
		for i in range(7):
			self.network_array[i].load_checkpoint(preset)

	def new_network(self):
		print("new network")
		self.network_array = []
		for i in range(7):
			self.network_array.append(Network(i))

	def reset_training(self):
		for i in range(7):
			self.network_array[i].reset_training()

	def update_learn_rate(self, learn_rate):
		for i in range(7):
			self.network_array[i].update_learn_rate(learn_rate)

	def get_decay_rate(self, stage):
		return self.network_array[0].decay_rates[stage]

	def set_decay_rate(self, stage, amount):
		for i in range(7):
			self.network_array[i].set_decay_rates(stage, amount)

	def finish_episode(self):
		for i in range(7):
			self.network_array[i].finish_episode()

	def get_length(self):
		length = 0
		turn = self.get_turn()
		for i in range(7):
			length += len(self.network_array[i].sar_tuples[turn])
		return length


	def forward_pass(self, inputs, network):
		return self.network_array[network].forward_pass(inputs)[0]

	def append_tuple(self, tup, network):
		#print("Network:", network, "Move:", tup[1], "Reward:", tup[2])
		self.network_array[network].sar_tuples[self.get_turn()].append(tup)

