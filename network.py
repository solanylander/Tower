import os.path
import numpy as np
import tensorflow as tf
from pathlib import Path

# Number of input neurons
INPUT_SIZE = 10
HIDDEN_LAYER_SIZE = 8
LEARNING_RATE = 0.5
CHECKPOINT_COUNTER = 2

class Network:
	def __init__(self, network_number):
		self.learning_rate = LEARNING_RATE
		self.network_number = network_number
		self.preset = False
		self.episode_number = 0
		self.turn_number = 0
		self.rate_counter = 20
		self.save_counter = 0
		self.decay_rates = [0.99, 0.99, 0.999, 0.999]
		self.sess = tf.InteractiveSession()
		self.batch_state_action_reward_tuples = []
		self.sar_tuples = []
		for i in range(4):
			self.sar_tuples.append([])


		self.input_layer = tf.placeholder(tf.float32, [None, INPUT_SIZE])
		# Rotate Anti-Clockwise, Hold Current Position, Rotate Clockwise
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

		# Train based on the log probability of the sampled action.
		# 
		# The idea is to encourage actions taken in rounds where the agent won,
		# and discourage actions in rounds where the agent lost.
		# More specifically, we want to increase the log probability of winning
		# actions, and decrease the log probability of losing actions.
		#
		# Which direction to push the log probability in is controlled by
		# 'advantage', which is the reward for each action in each round.
		# Positive reward pushes the log probability of chosen action up;
		# negative reward pushes the log probability of the chosen action down.
		self.loss = tf.losses.log_loss(
			labels=self.outputs,
			predictions=self.output_layer,
			weights=self.advantage)
		optimizer = tf.train.AdamOptimizer(self.learning_rate)
		self.train_op = optimizer.minimize(self.loss)

		tf.global_variables_initializer().run()

		self.saver = tf.train.Saver()
		self.checkpoint_file = 'checkpoints/policy_network.ckpt' + str(network_number)
		self.checkpoint_path = Path('checkpoints/policy_network.ckpt' + str(network_number) + '.meta')
		self.preset_file = 'checkpoints/preset_network.ckpt' + str(network_number)
		self.preset_path = Path('checkpoints/preset_network.ckpt' + str(network_number) + '.meta')
		print(self.checkpoint_file)

	def train(self, state_action_reward_tuples):
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


	def load_checkpoint(self, preset):
		print("Loading checkpoint...")
		if preset and self.preset_path.is_file():
			self.saver.restore(self.sess, self.preset_file)
			self.preset = True
		if not preset and self.checkpoint_path.is_file():
			self.saver.restore(self.sess, self.checkpoint_file)
			self.preset = False

	def save_checkpoint(self):
		print("Saving checkpoint...")
		self.saver.save(self.sess, self.checkpoint_file)

	def update_learn_rate(self, learning_rate):
		if not self.preset:
			self.save_checkpoint()
		print("Learning rate updated:", learning_rate)
		self.learning_rate = learning_rate
		optimizer = tf.train.AdamOptimizer(self.learning_rate)
		self.train_op = optimizer.minimize(self.loss)
		self.sess.run(tf.global_variables_initializer())
		self.load_checkpoint(self.preset)


	def forward_pass(self, inputs):
		inputs = np.array(inputs)
		probabilities = self.sess.run(
			self.output_layer,
			feed_dict={self.input_layer: inputs.reshape([1, -1])})
		#print("---------")
		#print(probabilities)
		return probabilities



	def discount_rewards(self, rewards, discount_factor):
		discounted_rewards = np.zeros_like(rewards, dtype=np.float64)
		for t in range(len(rewards)):
			discounted_reward_sum = 0
			discount = 1
			through = 0
			for k in range(t, len(rewards)):
				discounted_reward_sum += rewards[k] * discount
				discount *= discount_factor
				if rewards[k] != 0:
					# Don't count rewards from subsequent rounds
					break
			discounted_rewards[t] = discounted_reward_sum
		return discounted_rewards


	def finish_episode(self):


		for i in range(4):
			print("Start Training:", len(self.sar_tuples[i]), "Step:", i)
			states, actions, rewards = zip(*self.sar_tuples[i])
			rewards = self.discount_rewards(rewards, self.decay_rates[i])
			rewards -= np.mean(rewards)
			rewards /= np.std(rewards)

			self.sar_tuples[i] = list(zip(states, actions, rewards))
			for j in range(len(self.sar_tuples[i])):
				self.batch_state_action_reward_tuples.append(self.sar_tuples[i][j])
		states, actions, rewards = zip(*self.batch_state_action_reward_tuples)
		print("Start Training:", len(self.batch_state_action_reward_tuples))



		self.train(self.batch_state_action_reward_tuples)
		self.batch_state_action_reward_tuples = []

		self.sar_tuples = []
		for i in range(4):
			self.sar_tuples.append([])


		self.save_counter += 1

	def reset_training(self):
		self.batch_state_action_reward_tuples = []

		self.sar_tuples = []
		for i in range(4):
			self.sar_tuples.append([])

	def set_decay_rates(self, position, value):
		decay_rates = []
		for i in range(4):
			if i == position:
				decay_rates.append(value)
			else:
				decay_rates.append(self.decay_rates[i])
		self.decay_rates = decay_rates

