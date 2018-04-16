import os.path
import numpy as np
import tensorflow as tf
from pathlib import Path

# network initialization variable
INPUT_SIZE = 10
HIDDEN_LAYER_SIZE = 8
CHECKPOINT_COUNTER = 2
INITIAL_LEARNING_RATE = 0.1

class Network:
	def __init__(self, network_number):
		# The networks current learning rate
		self.learning_rate = INITIAL_LEARNING_RATE
		# between 0 and 6
		self.network_number = network_number
		# Using the prebuilt neural network
		self.preset = False
		# With round the network is currently training in
		self.turn_number = 0
		# Networks current decay rates. Can be different for each training step
		self.decay_rates = [0.99, 0.99, 0.999, 0.9999]
		# Stores the data across all training stages for each round
		self.batch_state_action_reward_tuples = []
		# Stores the data for each training stage seperately. This way the data can be compared seperately
		self.sar_tuples = []
		for i in range(4):
			self.sar_tuples.append([])

		# Network initializers
		self.sess = tf.InteractiveSession()
		self.input_layer = tf.placeholder(tf.float32, [None, INPUT_SIZE])
		self.outputs = tf.placeholder(tf.float32, [None, 3])
		self.advantage = tf.placeholder(tf.float32, [None, 1], name='advantage')

		# This network has 3 hidden layers
		h_one = tf.layers.dense(
		self.input_layer,
		units=HIDDEN_LAYER_SIZE,
		activation=tf.nn.relu,
		kernel_initializer=tf.contrib.layers.xavier_initializer())

		h_two = tf.layers.dense(
		h_one,
		units=HIDDEN_LAYER_SIZE,
		activation=tf.nn.relu,
		kernel_initializer=tf.contrib.layers.xavier_initializer())

		self.output_layer = tf.layers.dense(
		h_two,
		units=3,
		activation=tf.sigmoid,
		kernel_initializer=tf.contrib.layers.xavier_initializer())

		#  Network initialization
		self.loss = tf.losses.log_loss(
			labels=self.outputs,
			predictions=self.output_layer,
			weights=self.advantage)
		optimizer = tf.train.AdamOptimizer(self.learning_rate)
		self.train_op = optimizer.minimize(self.loss)

		tf.global_variables_initializer().run()

		self.saver = tf.train.Saver()

		# Checkpoint file as well as preset networks file. Saved to file, path is used to check the file exists for laoding
		self.checkpoint_file = 'checkpoints/policy_network.ckpt' + str(network_number)
		self.checkpoint_path = Path('checkpoints/policy_network.ckpt' + str(network_number) + '.meta')
		self.preset_file = 'checkpoints/preset_network.ckpt' + str(network_number)
		self.preset_path = Path('checkpoints/preset_network.ckpt' + str(network_number) + '.meta')

	# Train the network from an episodes data
	def train(self, state_action_reward_tuples):
		print(1, self.network_number, self.forward_pass([0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0]))
		states, actions, rewards = zip(*state_action_reward_tuples)
		states = np.vstack(states)
		actions = np.vstack(actions)
		rewards = np.vstack(rewards)

		feed_dict = {
			self.input_layer: states,
			self.outputs: actions,
			self.advantage: rewards
		}

		self.sess.run(self.train_op, feed_dict)

	# Load checkpoint.
	def load_checkpoint(self, preset):
		print(2, self.network_number, self.forward_pass([0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0]))
		# Load preset file and set preset to true
		if preset and self.preset_path.is_file():
			self.saver.restore(self.sess, self.preset_file)
			self.preset = True
		# Load checkpoint file and set preset to false
		if not preset and self.checkpoint_path.is_file():
			self.saver.restore(self.sess, self.checkpoint_file)
			self.preset = False

	# Save checkpoint
	def save_checkpoint(self):
		print(3, self.network_number, self.forward_pass([0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0]))
		self.saver.save(self.sess, self.checkpoint_file)

	# Updates the networks learn rate
	def update_learn_rate(self, learning_rate):
		print(4, self.network_number, self.forward_pass([0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0]))
		# Save checkpoint since all variables are reset
		if not self.preset:
			self.save_checkpoint()
		# Update Learning Rate
		self.learning_rate = learning_rate
		optimizer = tf.train.AdamOptimizer(self.learning_rate)
		self.train_op = optimizer.minimize(self.loss)
		self.sess.run(tf.global_variables_initializer())
		# Load Checkpoint
		self.load_checkpoint(self.preset)
		
	# Giving an array of inputs the network returns the expected utility of each move
	def forward_pass(self, inputs):
		inputs = np.array(inputs)
		probabilities = self.sess.run(
			self.output_layer,
			feed_dict={self.input_layer: inputs.reshape([1, -1])})
		return probabilities

	# Discount an episodes rewards based off the decay rate
	def discount_rewards(self, rewards, decay_rate):
		# Create an empty array of size len(rewards)
		discounted_rewards = np.zeros_like(rewards, dtype=np.float64)
		# Keep discounting until you find a result with a reward not 0. This means it was the last move
		# from a subsequent round and the discount should be reset
		for t in range(len(rewards)):
			discounted_reward_sum = 0
			# Multiplied by the decay rate each iteration
			discount = 1
			through = 0
			for k in range(t, len(rewards)):
				# Multiply reards be the discounted
				discounted_reward_sum += rewards[k] * discount
				discount *= decay_rate
				if rewards[k] != 0:
					# Don't count rewards from subsequent rounds
					break
			discounted_rewards[t] = discounted_reward_sum
		return discounted_rewards

	# Finish episode
	def finish_episode(self):
		print(5, self.network_number,  self.forward_pass([0, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0]))
		# Handle each training step seperately. Then add the results together
		for i in range(4):
			states, actions, rewards = zip(*self.sar_tuples[i])
			# Discount rewards
			rewards = self.discount_rewards(rewards, self.decay_rates[i])
			# by setting the mean to 0 the network stays balanced
			rewards -= np.mean(rewards)
			# More unique rewards get more attention
			rewards /= np.std(rewards)

			# Add rewards to shared array for the entire episode
			self.sar_tuples[i] = list(zip(states, actions, rewards))
			for j in range(len(self.sar_tuples[i])):
				self.batch_state_action_reward_tuples.append(self.sar_tuples[i][j])

		# Train network
		self.train(self.batch_state_action_reward_tuples)

		# Reset variables
		self.batch_state_action_reward_tuples = []
		self.sar_tuples = []
		for i in range(4):
			self.sar_tuples.append([])

	# Set the decay rate for one training stage
	def set_decay_rate(self, position, value):
		decay_rates = []
		for i in range(4):
			if i == position:
				decay_rates.append(value)
			else:
				decay_rates.append(self.decay_rates[i])
		self.decay_rates = decay_rates

	# Reset training data if the episode ending prematurely
	def reset_training(self):
		self.batch_state_action_reward_tuples = []
		self.sar_tuples = []
		self.turn_number = 0
		for i in range(4):
			self.sar_tuples.append([])
