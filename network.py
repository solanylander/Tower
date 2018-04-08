import os.path
import numpy as np
import tensorflow as tf

# Number of input neurons
INPUT_SIZE = 17
HIDDEN_LAYER_SIZE = 14
LEARNING_RATE = 0.1
CHECKPOINT_COUNTER = 2

class Network:
	def __init__(self, load_checkpoint):
		self.learning_rate = LEARNING_RATE
		self.save_counter = 0
		self.sess = tf.InteractiveSession()
		self.batch_state_action_reward_tuples = []

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

		h_three = tf.layers.dense(
		h_two,
		units=HIDDEN_LAYER_SIZE,
		activation=tf.nn.relu,
		kernel_initializer=tf.contrib.layers.xavier_initializer())

		self.output_layer = tf.layers.dense(
		h_three,
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
		self.checkpoint_file = 'checkpoints/policy_network.ckpt'
		print("LOAD checkpoint", load_checkpoint)

	def train(self, state_action_reward_tuples):
		states, actions, rewards = zip(*state_action_reward_tuples)
		states = np.vstack(states)
		actions = np.vstack(actions)
		rewards = np.vstack(rewards)

		feed_dict = {
			self.observations: states,
			self.sampled_actions: actions,
			self.advantage: rewards
		}

		self.sess.run(self.train_op, feed_dict)


	def load_checkpoint(self):
		print("Loading checkpoint...")
		self.saver.restore(self.sess, self.checkpoint_file)

	def save_checkpoint(self):
		print("Saving checkpoint...")
		self.saver.save(self.sess, self.checkpoint_file)

	def update_learn_rate(self):
		self.learning_rate /= 10
		optimizer = tf.train.AdamOptimizer(self.learning_rate)
		self.train_op = optimizer.minimize(self.loss)
		tf.global_variables_initializer().run()
		self.load_checkpoint()


	def forward_pass(self, inputs):
		inputs = np.array(inputs)
		probabilities = self.sess.run(
			self.output_layer,
			feed_dict={self.input_layer: inputs.reshape([1, -1])})
		return probabilities



	def discount_rewards(self, rewards, discount_factor):
		discounted_rewards = np.zeros_like(rewards)
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


	def finishEpisode(self):
		print("Start Training:", len(self.batch_state_action_reward_tuples))
		states, actions, rewards = zip(*self.batch_state_action_reward_tuples)
		rewards = self.discount_rewards(rewards, 0.9999)
		i = 0
		while i < len(rewards):
			print("Reward Tracker", i, rewards[i])
			i += 100
		self.batch_state_action_reward_tuples = list(zip(states, actions, rewards))
		self.train(self.batch_state_action_reward_tuples)
		self.batch_state_action_reward_tuples = []


		self.save_counter += 1

		if self.save_counter % CHECKPOINT_COUNTER == 0:
			self.save_checkpoint()