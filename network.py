import gym, random, os, tflearn
import tensorflow as tf
import numpy as np
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean, median
from collections import Counter

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
LR = 1e-3

class random_network:
	def __init__(self):
		self.trainingData = []
		self.scores = []
		self.acceptedScores = []
		self.gameMemory = []
		self.prevObs = []
		self.max = 0


	def nextGame(self):
		#if score > 4:
		#	self.acceptedScores.append(score)
		#	for data in self.gameMemory:
		#		output = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		#		output[data[1]] = 1
		#		self.trainingData.append([data[0], output])
		#self.scores.append(score)
		#self.gameMemory = []
		#self.prevObs = []
		self.model.set_weights(self.network.W, np.random.rand(128, 30))
		print("randomize")
		#print("here")

	def initialiseNetwork(self):
		#self.loadNetwork()
		self.trainModel()
		self.trainingData = []
		self.scores = []
		self.acceptedScores = []
		self.gameMemory = []
		self.prevObs = []

	def saveNetwork(self):
		print("save")
		trainingDataSave = np.array(self.trainingData)
		scoresSave = np.array(self.acceptedScores)
		np.save('trainingData17.npy', trainingDataSave)
		np.save('scores17.npy', scoresSave)

	def loadNetwork(self):
		#self.trainingData1 = np.load('trainingData15.npy')
		#self.trainingData2 = np.load('trainingData16.npy')
		#self.trainingData3 = np.load('trainingData13.npy')
		#self.trainingData4 = np.load('trainingData14.npy')
		print("hi")

	def afterInitial(self):
		self.scores = []


	def neuralNetworkModel(self, input_size):
		network = input_data(shape=[None, input_size, 1], name='input')

		network = fully_connected(network, 128, activation='relu')
		network = dropout(network, 0.8)


		network = fully_connected(network, 256, activation='relu')
		network = dropout(network, 0.8)


		network = fully_connected(network, 512, activation='relu')
		network = dropout(network, 0.8)


		network = fully_connected(network, 256, activation='relu')
		network = dropout(network, 0.8)


		network = fully_connected(network, 128, activation='relu')
		network = dropout(network, 0.8)

		network = fully_connected(network, 30, activation='softmax')
		self.network = regression(network, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

		model = tflearn.DNN(self.network, tensorboard_dir='log')
		return model

	def trainModel(self):
		#print("train", len(self.trainingData))

		trainingData = []
		#for j in range(len(self.trainingData1)):
		#	trainingData.append(self.trainingData1[j])
		#for j in range(len(self.trainingData2)):
		#	trainingData.append(self.trainingData2[j])
		#for j in range(len(self.trainingData4)):
		#	trainingData.append(self.trainingData4[j])
		#print(len(trainingData))

		#X = np.array([i[0] for i in trainingData]).reshape(-1, len(trainingData[0][0]), 1)
		#y = [i[1] for i in trainingData]

		self.model = self.neuralNetworkModel(input_size = 51)

		#self.model.fit({'input':X}, {'targets':y}, n_epoch=5, snapshot_step=500, show_metric=True, run_id='openaistuff')

		#self.model.load('test3.model')
		#self.model.fit({'input':A}, {'targets':b}, n_epoch=3, snapshot_step=500, show_metric=True, run_id='openaistuff')

	def nextGameCompleted(self, score):
		self.scores.append(score)
		self.gameMemory = []

	def move(self, observation, store, list):
		# rand = random.randrange(4,100)
		# rand = int((100 / rand))
		# rand = random.randrange(1,4)
		observation = np.array(observation)
		self.observation = observation
		self.observation = np.reshape(observation, (-1, len(observation), 1))
		self.prediction = self.model.predict(self.observation)[0]
		return self.prediction

	def store(self, observation, action):
			self.gameMemory.append([observation, action])
