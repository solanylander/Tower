import math, random, sys, pygame
from pygame.locals import *
from network import Network

# Collection of neural networks. One for the 3 main body segments and 2 per set of 3 legs
class NetworkCollection:

	# Initialize array
	def __init__(self):
		self.network_array = []
		for i in range(7):
			self.network_array.append(Network(i))

	# Return current networks turn. This is the same for all the networks
	def get_turn(self):
		return self.network_array[0].turn_number

	# Increment each networks turn. Turn number is capped at 3 then it resets
	def increment_turn(self):
		turn = self.get_turn()
		for i in range(7):
			self.network_array[i].turn_number = (turn + 1) % 4

	# Save each neural network
	def save_checkpoint(self):
		for i in range(7):
			self.network_array[i].save_checkpoint()

	# Load each neural network
	def load_checkpoint(self, preset):
		for i in range(7):
			self.network_array[i].load_checkpoint(preset)

	# Reset all the neural networks
	def new_network(self):
		self.network_array = []
		for i in range(7):
			self.network_array.append(Network(i))

	# Reset each networks training data
	def reset_training(self):
		for i in range(7):
			self.network_array[i].reset_training()

	# Update the learning rate of each network
	def update_learn_rate(self, learn_rate):
		for i in range(7):
			self.network_array[i].update_learn_rate(learn_rate)

	# Update the learning rate of each network
	def get_learn_rate(self):
		return self.network_array[0].learning_rate

	# Get the decay rates of each training stage. Same for each network
	def get_decay_rate(self, stage):
		return self.network_array[0].decay_rates[stage]

	# Set the decay rate of a training stage. Same for each network
	def set_decay_rate(self, stage, amount):
		for i in range(7):
			self.network_array[i].set_decay_rate(stage, amount)

	# Train the network from the data it gathered in the previous episode
	# then prepare for next episode
	def finish_episode(self):
		for i in range(7):
			self.network_array[i].finish_episode()

	# Return amount of data cumulatively the networks have gathered for this turn
	def get_length(self):
		length = 0
		turn = self.get_turn()
		for i in range(7):
			length += len(self.network_array[i].sar_tuples[turn])
		return length

	# Request a move from a network given an array of inputs
	def forward_pass(self, inputs, network):
		return self.network_array[network].forward_pass(inputs)[0]

	# Add data to the network to be later trained with
	def append_tuple(self, tup, network):
		self.network_array[network].sar_tuples[self.get_turn()].append(tup)

