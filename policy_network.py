import os.path
import numpy as np
import tensorflow as tf

OBSERVATIONS_SIZE = 17


class Network:
    #Good
    def __init__(self, hidden_layer_size, learning_rate, checkpoints_dir):
        self.learning_rate = 0.005
        self.save_counter = 0
        self.sess = tf.InteractiveSession()
        self.batch_state_action_reward_tuples = []

        self.observations = tf.placeholder(tf.float32,
                                           [None, OBSERVATIONS_SIZE])
        # +1 for up, -1 for down
        self.sampled_actions = tf.placeholder(tf.float32, [None, 3])
        self.advantage = tf.placeholder(
            tf.float32, [None, 1], name='advantage')

        h_one = tf.layers.dense(
            self.observations,
            units=14,
            activation=tf.nn.relu,
            kernel_initializer=tf.contrib.layers.xavier_initializer())

        h_two = tf.layers.dense(
            h_one,
            units=14,
            activation=tf.nn.relu,
            kernel_initializer=tf.contrib.layers.xavier_initializer())

        h_three = tf.layers.dense(
            h_two,
            units=14,
            activation=tf.nn.relu,
            kernel_initializer=tf.contrib.layers.xavier_initializer())

        self.up_probability = tf.layers.dense(
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
            labels=self.sampled_actions,
            predictions=self.up_probability,
            weights=self.advantage)
        optimizer = tf.train.AdamOptimizer(self.learning_rate)
        self.train_op = optimizer.minimize(self.loss)

        tf.global_variables_initializer().run()

        self.saver = tf.train.Saver()
        self.checkpoint_file_new = os.path.join(checkpoints_dir,
                                            'policy_network_new.ckpt')
        self.checkpoint_file_updated = os.path.join(checkpoints_dir,
                                            'policy_network_multi.ckpt')
        self.checkpoint_file_81 = os.path.join(checkpoints_dir,
                                            'policy_network_81.ckpt')
    #Good
    def load_checkpoint(self):
        print("Loading checkpoint...")
        self.saver.restore(self.sess, self.checkpoint_file_81)
    #Good
    def save_checkpoint(self):
        print("Saving checkpoint...")
        self.saver.save(self.sess, self.checkpoint_file_81)
    #Good
    def forward_pass(self, observations):
        observations = np.array(observations)
        up_probability = self.sess.run(
            self.up_probability,
            feed_dict={self.observations: observations.reshape([1, -1])})
        return up_probability
    #Good
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

    def update_learn_rate(self, success_rate):
        self.z = [0,1,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0]
        print(self.z)
        print(self.forward_pass(self.z))

        print("------")



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
        rewards = self.discount_rewards(rewards, 0.9995)
        rewards -= np.mean(rewards)
        rewards /= np.std(rewards)
        i = 0
        while i < len(rewards):
            print("Reward Tracker", i, rewards[i])
            i += 100
        self.batch_state_action_reward_tuples = list(zip(states, actions, rewards))
        self.train(self.batch_state_action_reward_tuples)
        self.batch_state_action_reward_tuples = []


        self.save_counter += 1

        if self.save_counter % 2 == 0:
            self.save_checkpoint()