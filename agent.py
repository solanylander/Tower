import math, random, sys, pygame
from pygame.locals import *
from part import Part
from policy_network import Network
from network import random_network
from random import *
import pickle
import time
import numpy as np

class Agent:

	def __init__(self, xy, args):
		# Which body parts are currently colliding
		self.colliding = []
		# Objects within the world
		self.objects = []

		self.args = args
		# Neural network
		self.network = Network(args.hidden_layer_size, args.learning_rate, checkpoints_dir='checkpoints')
		if args.load_checkpoint:
			self.network.load_checkpoint()
		self.batch_state_action_reward_tuples = []
		self.smoothed_reward = None
		self.episode_n = 1
		self.episode_reward_sum = 0
		self.round_n = 1
		self.randomAgent = random_network()
		# Center of gravity
		self.cog = (0,0)
		# Run counter
		self.counter = 0
		# Total distance counter
		self.total = 0
		# Initial position
		self.c = None
		# Spawn position
		self.xy = xy
		# Valid run
		self.button = True
		# Reset Agent
		self.reset(True, 0, True)
		# Initialise the backup storage for the parts information with 0 values
		self.backup = []
		for k in range(0,15):
			self.backup.append(Part(0, 0, 0, False, 0))

	# Reset agent
	def reset(self, stage, score, init):
		parts = []
		# add the head and body parts
		if True:
			parts.append(Part(randint(0, 360), self.xy[0], self.xy[1], True, 50))
			parts.append(Part(randint(0, 360), 0, 0, False, 50))
			parts.append(Part(randint(0, 360), 0, 0, False, 50))
		else:
			# Normal Spawn
			parts.append(Part(0, self.xy[0], self.xy[1], True, 50))
			parts.append(Part(0, 0, 0, False, 50))
			parts.append(Part(0, 0, 0, False, 50))
		# Load the image files
		parts[0].loadImage("image_resources/body.png")
		parts[1].loadImage("image_resources/body.png")
		parts[2].loadImage("image_resources/head.png")
		# Body parts and heads weight
		parts[0].setWeight(23.44)
		parts[1].setWeight(11.72)
		parts[2].setWeight(8.24)

		if True:
			for i in range(0, 2):
				parts.append(Part(randint(0, 360), 0, 0, False, 12))
				parts.append(Part(randint(0, 360), 0, 0, False, 12))
				parts.append(Part(randint(0, 360), 0, 0, False, 12))
				parts.append(Part(randint(0, 360), 0, 0, False, 12))
				parts.append(Part(randint(0, 360), 0, 0, False, 12))
				parts.append(Part(randint(0, 360), 0, 0, False, 12))
		else:
			# Normal Spawn
			for i in range(0, 2):
				parts.append(Part(310, 0, 0, False, 12))
				parts.append(Part(50, 0, 0, False, 12))
				parts.append(Part(50, 0, 0, False, 12))
				parts.append(Part(0, 0, 0, False, 12))
				parts.append(Part(0, 0, 0, False, 12))
				parts.append(Part(0, 0, 0, False, 12))
		# Add the leg parts
		for l in range(3, 15):
			# Load the image files and set the constraints
			parts[l].loadImage("image_resources/leg_green.png")
			parts[l].setWeight(0.66)
		for l in range(9, 15):
			# Load the image files and set the constraints
			parts[l].loadImage("image_resources/leg_yellow.png")
		self.parts = parts
		self.setConstraints()
		self.setPositions(self.xy)
		self.prevMove = -1
		if self.button == False:
			score = score - self.c[0]
			self.total = self.total + score
		self.button = True
		return self.collide(0)


	# Handles movement calculations
	def move(self, timer, show):
		parts = self.parts
		pos = parts[0].getPosition()
		cog = self.getCog()[0]
		self.stored(True)
		amountOfMoves = 0
		moveTracker = []
		failures = 0
		double = False

		pivot = (pos[0], pos[1])
		pivot = self.gravity(pivot, 30)
		usedMoves = []
		for i in range(4):
			self.stored(True)
			self.inputs(pivot, i)
			up_probability = self.network.forward_pass(self.networkInput)[0]
			self.new = True
			# Pick a move
			count = True
			zd = 0



			random = False
			if (randint(0,100) < 20):
				up_probability = self.randomAgent.move(self.networkInput, self.button, moveTracker)
				random = True
			move = np.argmax(up_probability)
			if show:
				if random:
					print("yes")
				else:
					print("no")
			while move is not 30 and (move % 15) in usedMoves:

				up_probability[move] = 0
				move = np.argmax(up_probability)
				zd += 1

			if np.max(up_probability) == 0:
				move = 30

			movement = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			if move != 30:
				for k in range(len(movement)):
					if k == move:
						movement[k] = 1
						break
					elif k == move - 15:
						movement[k] = -1
						break

				self.setConstraints()

				backMove = parts[k].rotation(movement[k])
				if k == 0:
					pivot = (pivot[0] + backMove[0], pivot[1] + backMove[1])
				if(k > 2 and k < 6 or k > 8 and k < 12):
					parts[k + 3].rotation(movement[k])

				self.setPositions(pivot)

				if self.collide(2):
					count = False
					self.stored(False)
				elif self.collide(1):
					self.stored(False)
					amountOfMoves = amountOfMoves + 1
					distChange = self.interactiveMove(move % 15, movement[k])
					pivot = (pivot[0] + distChange[0], pivot[1] + distChange[1])
					self.setPositions(pivot)

					if self.collide(1):
						self.stored(False)
						print("Fail 2", distChange)

						pivot = (pivot[0], pivot[1] - 2)

						parts[move % 15].rotation(movement[k])
						if (((move % 15) - 3) % 6) < 3:
							parts[(move % 15) + 3].rotation(movement[k])
						self.setPositions(pivot)
						double = True
						xDiff = self.getCog()[0] - cog
						pivot = (pivot[0] - xDiff, pivot[1])
						self.setPositions(pivot)

						if self.collide(1):
							self.stored(False)
							print("Fail 3")
							double = False
						else:
							pivot = self.gravity(pivot, 20)

			if show:
				print(move, count, zd)

			self.centerOfGravity(pivot, double)
			# If the agents center of gravity is to the left of all its points of contacts fall to the left
			if self.box[0][0] != -1 and self.box[0][0] > self.cog[0]:
				passed = self.fallRotation(pivot, True)
			# If the agents center of gravity is to the right of all its points of contacts fall to the right
			elif self.box[1][0] != -1 and self.box[1][0] < self.cog[0]:
				passed = self.fallRotation(pivot, False)
			elif self.box[0][0] <= self.cog[0] and self.box[1][0] >= self.cog[0] and self.button:
				self.c = self.cog
				print("click")
				self.button = False

			self.setConstraints()
			if move != 30:
				usedMoves.append(move % 15)

			if self.collide(2):
				self.tweak(pivot)

			x = self.ended(move, timer, self.button, i)
			if i == 3:
				if show:
					print("----------------")
				return x


	def ended(self, move, timer, button, turn):
		if not button:
			score = self.getCog()[0] - self.c[0]
			reward = 0
			if timer < 0 and score < 6 and turn == 3:
				reward = (score - 6) / 120
			elif timer < 0 and score < 30 and turn == 3:
				reward = score / 200
			elif timer < 0 and turn == 3:
				reward = score / 120

			output = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			output[move] = 1

			self.episode_reward_sum += reward

			tup = (self.networkInput, output, reward)
			self.batch_state_action_reward_tuples.append(tup)
			if turn == 3:
				if reward < 0:
					print("Round %d; Score: %0.3f, Reward: %0.3f,  lost..." % (self.round_n, score, reward))
				elif reward > 0:
					print("Round %d: Score: %0.3f, Reward: %0.3f, won!" % (self.round_n, score, reward))
				if reward != 0:
					self.round_n += 1
					self.n_steps = 0
					return True
		return False

	def finishEpisode(self):
		print("Episode %d finished after %d rounds" % (self.episode_n, self.round_n))

		# exponentially smoothed version of reward
		if self.smoothed_reward is None:
			self.smoothed_reward = self.episode_reward_sum
		else:
			self.smoothed_reward = self.smoothed_reward * 0.99 + self.episode_reward_sum * 0.01
		print("Reward total was %.3f; discounted moving average of reward is %.3f" \
			% (self.episode_reward_sum, self.smoothed_reward))

		if self.episode_n % self.args.batch_size_episodes == 0:
			states, actions, rewards = zip(*self.batch_state_action_reward_tuples)
			rewards = self.network.discount_rewards(rewards, self.args.discount_factor)
			rewards -= np.mean(rewards)
			rewards /= np.std(rewards)
			self.batch_state_action_reward_tuples = list(zip(states, actions, rewards))
			self.network.train(self.batch_state_action_reward_tuples)
			self.batch_state_action_reward_tuples = []

		if self.episode_n % self.args.checkpoint_every_n_episodes == 0:
			self.network.save_checkpoint()

		self.episode_n += 1
		self.episode_reward_sum = 0






	def legalMove(self, move, pivot, show):
		if move == -1:
			return True
		elif randint(0,100) < 10:
			return False

		self.prevMove = move

		parts = self.parts
		valid = None
		partNum = move % 15
		direction = -1

		if move < 15:
			direction = 1
		valid = parts[partNum].checkRotation(direction)

		if valid == False:
			return False

		parts[partNum].rotation(direction)
		
		if ((partNum - 3) % 6) < 3:
			parts[partNum + 3].rotation(direction)
		self.setPositions(pivot)

		if self.collide(2):
			valid = False

		self.stored(False)
		return valid

	def inputs(self, pivot, turn):
		parts = self.parts
		objects = self.objects
		netInputs = []
		for i in range(len(parts)):
				netInputs.append(parts[i].getRotation() / 360.0)
		#		for j in range(0,2):
		#			parts[i].rotation(-1 + (j * 2))
		#			if(i > 2 and i < 6 or i > 8 and i < 12):
		#				parts[i + 3].rotation(-1 + (j * 2))
		#			self.setPositions(pivot)
		#			boolToInt = 0
		#			if self.collide(1):
		#				boolToInt = 1
		#			netInputs.append(boolToInt)
		#			self.stored(False)
		for j in range(4):
			if j == turn:
				netInputs.append(1)
			else:
				netInputs.append(0)
		self.networkInput = netInputs

	# When the agent pushes off with a leg the rest of its body should follow
	def interactiveMove(self, move, direction):
		colliding = self.colliding
		parts = self.parts
		initialPos = parts[move % 15].getPivot()
		distance = (initialPos[0] - colliding[0][0], initialPos[1] - colliding[0][1])
		hypD = math.sqrt(distance[0] * distance[0] + distance[1] * distance[1])

		rotation = (math.atan(distance[0] / distance[1]) * 180.0 / math.pi) - direction
		newPos = (hypD * math.sin(rotation * math.pi / 180.0), hypD * math.cos(rotation * math.pi / 180.0))
		newPos = (newPos[0] + distance[0], newPos[1] + distance[1] - 1.0)

		parts[move].rotation(direction)
		if ((move - 3) % 6) < 3:
			parts[move + 3].rotation(direction)

		return newPos


		#print("final", self.collide(False))
	# When the agent is hanging on an edge over its center of gravity it should tip in that direction
	def fallRotation(self, pivot, left):



		parts = self.parts
		# X,Y distances between the agents point of contact with the world and the agents main pivot point.
		# (The pivot is where the agent bases all calculations from and is the rotation point for its back)
		distanceXY = None
		# Torque is the distance the agents center of gravity is from the collision point being used
		torque = None
		# If the agent is falling to the left use the left most collision point otherwise use the rightmost
		if left:
			distanceXY = (self.box[0][0] - parts[0].getPivot()[0], self.box[0][1] - parts[0].getPivot()[1])
			torque = (self.cog[0] - self.box[0][0]) / 25
		else:
			distanceXY = (self.box[1][0] - parts[0].getPivot()[0], self.box[1][1] - parts[0].getPivot()[1])
			torque = (self.cog[0] - self.box[1][0]) / 25

		# Actual distance between the agents point of contact with the world and the agents main pivot point
		distanceH = math.sqrt(distanceXY[0] * distanceXY[0] + distanceXY[1] * distanceXY[1])

		# The angle between the collision point being used and the agents pivot point. The agent will be rotated around the point of collision
		# since when you fall you fall around the last place you were touching the ground
		currentAngle = None
		if(distanceXY[0] == 0):
			currentAngle = 90
		else:
			currentAngle = math.atan(distanceXY[1]/distanceXY[0]) * 180.0 / math.pi


		# The X,Y distances between the agents point of contact with the world and where the agents main pivot point will be after the rotation
		newXY = (math.cos((180.0 + currentAngle + torque) / 180 * math.pi), -math.sin((currentAngle + torque) / 180 * math.pi))
		newXY = (-abs(newXY[0] * distanceH), -abs(newXY[1] * distanceH))
		# Difference between where the pivot point is and where it will be after the rotation
		if(distanceXY[0] < 0):	
			newXY = (distanceXY[0] - newXY[0], newXY[1])
		else:
			newXY = (distanceXY[0] + newXY[0], newXY[1])
		if(distanceXY[1] < 0):
			newXY = (newXY[0], newXY[1] - distanceXY[1])
		else:
			newXY = (newXY[0], newXY[1] + distanceXY[1])
		# Once the agent has successfully rotated without colliding with the world passed = True
		passed = False
		# Store a backup of the agent
		self.stored(True)
		# Keep attempting to rotate the agent whilst moving it slightly away from the point of contact. Since the agents legs do not have rounded edges sometimes its
		# corner will get stuck in the ground so this gives it a little room to work with
		for horizontal in range(0,1):
			# Move vertically first since this will be negated by gravity and only move horizontally if necessary
			for vertical in range(0,5):
				# Move slightly left if the agent is falling to the left otherwise move slightly right, also move up
				if left:
					newPivot = (pivot[0] + newXY[0] - (0.3 * horizontal), pivot[1] + newXY[1] - (0.5 * vertical))
				else:
					newPivot = (pivot[0] + newXY[0] + (0.3 * horizontal), pivot[1] + newXY[1] - (0.5 * vertical))
				# Move and rotate the agent
				self.rotateAll(-torque)
				self.setPositions(newPivot)
				# If the agent collides with the world reset it with the stored values otherwise finish iterating and break
				if self.collide(1):
					self.stored(False)
				else:
					passed = True
					break
			if passed:
				break
		return (newXY, passed)

	# Rotate entire agent
	def rotateAll(self, amount):
		for iterate in range(0,15):
			self.parts[iterate].rotation(amount)

	# Agent is affected by gravity
	def gravity(self, pivot, amount):
		# Decrement multiple times instead of just lowering once since this way if it collides in the middle it will go as close as possible
		for i in range(0,amount):
			# Store a copy of the agent
			self.stored(True)
			# Lower the agent by 1
			pivot = (pivot[0], pivot[1] + 0.1)
			self.setPositions(pivot)
			# If the agent collides with the world revert the move
			if self.collide(1):
				self.stored(False)
				# Reset the pivot if the agent is reset
				pivot = (pivot[0], pivot[1] - 0.1)
				break
		return pivot

	# Calculate the agents center of gravity
	def centerOfGravity(self, pivot, double):
		parts = self.parts
		self.cog = (0,0)
		centers = []
		weight = 0
		# Agents co-ordinate
		pos = parts[0].getPosition()
		# Convert each parts current angle to a 2D vector
		partRotations = []
		for q in range(0,15):
			if q < 3:
				partRotations.append((math.cos(parts[q].getRotation() / 180 * math.pi), math.sin((180.0 + parts[q].getRotation()) / 180 * math.pi)))
			else:
				partRotations.append((math.cos((parts[q].getRotation() - 90) / 180 * math.pi), math.sin((180.0 + (parts[q].getRotation() - 90)) / 180 * math.pi)))

		# Find the center points of each part
		# Calculated by finding the connecting part to the body which is the center point (find top left of image then add half the image width)
		# then calculate the parts rotation and multiply it by the number of pixels away the center of the part is from the images center
		centers.append((pos[0] + (partRotations[0][0] * 17.0) + 50, pos[1] + (partRotations[0][1] * 17.0) + 50))
		centers.append((pos[0] + (partRotations[0][0] * 39.0) + (partRotations[1][0] * 17.0) + 50, pos[1] + (partRotations[0][1] * 39.0) + (partRotations[1][1] * 17.0) + 50))
		centers.append((pos[0] + (partRotations[0][0] * 39.0) + (partRotations[1][0] * 39.0) + (partRotations[2][0] * 9.0) + 50, pos[1] + (partRotations[0][1] * 39.0) + (partRotations[1][1] * 39.0) + (partRotations[2][1] * 9.0) + 50))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[3][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[3][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[4][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[4][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[5][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[5][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[3][0] * 12) + (partRotations[6][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[3][1] * 12) + (partRotations[6][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[4][0] * 12) + (partRotations[7][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[4][1] * 12) + (partRotations[7][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[5][0] * 12) + (partRotations[8][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[5][1] * 12) + (partRotations[8][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[9][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[9][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[10][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[10][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[11][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[11][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[9][0] * 12) + (partRotations[12][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[9][1] * 12) + (partRotations[12][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[10][0] * 12) + (partRotations[13][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[10][1] * 12) + (partRotations[13][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[11][0] * 12) + (partRotations[14][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[11][1] * 12) + (partRotations[14][1] * 5) + 13))
		
		# Add all parts center of gravity multiplied by there specific weight
		for i in range(0,15):
			self.cog = (self.cog[0] + (centers[i][0] * parts[i].getWeight()), self.cog[1] + (centers[i][1] * parts[i].getWeight()))
			weight += parts[i].getWeight()
		# Divide by the total weight of the agent
		self.cog = (self.cog[0] / weight, self.cog[1] / weight)

		self.stored(True)
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		pivot = (pivot[0], pivot[1] + 1.5)
		self.setPositions(pivot)
		self.collide(1)
		self.stored(False)




	# If setup is true store a copy of the agent otherwise replace the current agents details with the stored copy
	def stored(self, setup):
		one = []
		two = []
		if setup:
			two = self.parts
			one = self.backup
		else:
			two = self.backup
			one = self.parts
		for k in range(0,15):
			one[k].setPosition(two[k].getPosition())
			one[k].setConstraint(two[k].getConstraint())
			one[k].setRotation(two[k].getRotation())
			if not setup:
				one[k].rotation(0)
	
	# Set the constraints of each part
	def setConstraints(self):
		parts = self.parts
		parts[0].setConstraint(((parts[1].getRotation() - 90) % 360, (parts[1].getRotation() + 90) % 360))
		parts[1].setConstraint(((parts[0].getRotation() - 90) % 360, (parts[0].getRotation() + 90) % 360))
		parts[2].setConstraint(((parts[1].getRotation() - 90) % 360, (parts[1].getRotation() + 90) % 360))
		for i in range(0,2):
			offset = i * 6
			parts[3 + offset].setConstraint((0, 360))
			parts[4 + offset].setConstraint((0, 360))
			parts[5 + offset].setConstraint((0, 360))
			parts[6 + offset].setConstraint(((parts[3 + offset].getRotation() - 90) % 360, (parts[3 + offset].getRotation() + 90) % 360))
			parts[7 + offset].setConstraint(((parts[4 + offset].getRotation() - 90) % 360, (parts[4 + offset].getRotation() + 90) % 360))
			parts[8 + offset].setConstraint(((parts[5 + offset].getRotation() - 90) % 360, (parts[5 + offset].getRotation() + 90) % 360))

	# Sets all the parts positions with regards to the agents pivot
	def setPositions(self, pivot):
		parts = self.parts
		# Rotation of the agents abdominal segments
		backRotation = (math.cos(parts[0].getRotation() / 180 * math.pi), math.sin((180.0 + parts[0].getRotation()) / 180 * math.pi))
		frontRotation = (math.cos(parts[1].getRotation() / 180 * math.pi), math.sin((180.0 + parts[1].getRotation()) / 180 * math.pi))
		# Back abdominal segment
		parts[0].setPosition(pivot)
		pos = parts[0].getPosition()
		# Front abdominal segment
		parts[1].setPosition((pos[0] + (backRotation[0] * 39.0), pos[1] + (backRotation[1] * 39.0)))
		# Head
		parts[2].setPosition((pos[0] + (backRotation[0] * 39.0) + (frontRotation[0] * 39.0), pos[1] + (backRotation[1] * 39.0) + (frontRotation[1] * 39.0)))
		for i in range(0,2):
			offset = i * 6
			# Back leg (top)
			parts[3 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 12), pos[1] + 40 + (backRotation[1] * 12)))
			legRotation = (math.sin(parts[3 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + parts[3 + offset].getRotation()) / 180 * math.pi))
			# Back leg (bottom)
			parts[6 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 12) + (legRotation[0] * 11.5), pos[1] + 40 + (backRotation[1] * 12) + (legRotation[1] * 11.5)))
			# Middle leg (top)
			parts[4 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39), pos[1] + 40 + (backRotation[1] * 39)))
			legRotation = (math.sin(parts[4 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + parts[4 + offset].getRotation()) / 180 * math.pi))
			# Middle leg (bottom)
			parts[7 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39) + (legRotation[0] * 11.5), pos[1] + 40 + (backRotation[1] * 39) + (legRotation[1] * 11.5)))
			# Front leg (top)
			parts[5 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39) + (frontRotation[0] * 27), pos[1] + 40 + (backRotation[1] * 39) + (frontRotation[1] * 27)))
			# Front leg (bottom)
			legRotation = (math.sin(parts[5 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + parts[5 + offset].getRotation()) / 180 * math.pi))
			parts[8 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39) + (legRotation[0] * 11.5) + (frontRotation[0] * 27), pos[1] + 40 + (backRotation[1] * 39)  + (legRotation[1] * 11.5)+ (frontRotation[1] * 27)))

	# Handles Collisions between the ant and the world
	def collide(self, ignore):
		parts = self.parts
		objects = self.objects
		colliding = []
		selfCollide = []
		ret = False
		# For legs check if they are colliding with other legs from the same ant. Body parts are behind the legs so they can overlap
		# But an agent cannot cross its legs
		for position in range(0,15):
			# HERE
			if ignore % 2 == 0:
				if position > 2 and position < 9:
					for j in range(3,9):
						# Dont check collisions when the 2 parts are from the same leg. E.g "Thigh" and "Calf"
						if (position % 3) != (j % 3):			
							offset = (int(parts[position].getPosition()[0] - parts[j].getPosition()[0]), int(parts[position].getPosition()[1] - parts[j].getPosition()[1]))
							result = parts[j].getMask().overlap(parts[position].getMask(), offset)
							# If they collide return true
							if result:
								ret = True
								if position < j:
									selfCollide.append((position, j))
				elif position > 8:
					for j in range(9,15):
						# Dont check collisions when the 2 parts are from the same leg. E.g "Thigh" and "Calf"
						if (position % 3) != (j % 3):			
							offset = (int(parts[position].getPosition()[0] - parts[j].getPosition()[0]), int(parts[position].getPosition()[1] - parts[j].getPosition()[1]))
							result = parts[j].getMask().overlap(parts[position].getMask(), offset)
							# If they collide return true
							if result:
								ret = True
								if position < j:
									selfCollide.append((position, j))
			# TO HERE
			if ignore < 2:
				# Check collisions against all the other objects in the world which exclude itself
				for k in range(len(objects)):
					offset = (int(objects[k][1] - parts[position].getPosition()[0]), int(objects[k][2] - parts[position].getPosition()[1]))
					result = parts[position].getMask().overlap(objects[k][0], offset)
					if result:
						self.collisionBox((parts[position].getPosition()[0] + result[0], parts[position].getPosition()[1] + result[1]))
						colliding.append((parts[position].getPosition()[0] + result[0], parts[position].getPosition()[1] + result[1]))
						ret = True
		self.selfCollide = selfCollide
		self.colliding = colliding
		return ret

	def tweak(self, pivot):
		parts = self.parts
		colliders = []
		for i in range (0,2):
			start = 3 + (i * 6)
			for position in range(start, start + 6):
				for j in range(position + 1,start + 6):
					# Dont check collisions when the 2 parts are from the same leg. E.g "Thigh" and "Calf"
					if (position % 3) != (j % 3):			
						offset = (int(parts[position].getPosition()[0] - parts[j].getPosition()[0]), int(parts[position].getPosition()[1] - parts[j].getPosition()[1]))
						result = parts[j].getMask().overlap(parts[position].getMask(), offset)
						# If they collide return true
						if result:
							colliders.append((position, j))

		for i in range(len(colliders)):
			self.collide(2)
			colliderLen = len(self.selfCollide)
			x = colliders[i][0]
			y = colliders[i][1]
			if x % 6 < 3:
				x = x - 3
			if y % 6 < 3:
				y = y - 3
			self.stored(True)
			max = (0,360)
			#when you fix one rotation but not another then it will stick on 360
			for z in range(0, 8):
				count = 0
				while len(self.selfCollide) >= colliderLen and count < 10:
					if z == 0:
						self.parts[x].rotation(-1)
						self.parts[y].rotation(1)
					elif z == 1:
						self.parts[x].rotation(-1)
					elif z == 2:
						self.parts[x].rotation(-1)
						self.parts[y].rotation(-1)
					elif z == 3:
						self.parts[x].rotation(1)
						self.parts[y].rotation(1)
					elif z == 4:
						self.parts[x].rotation(1)
					elif z == 5:
						self.parts[x].rotation(1)
						self.parts[y].rotation(-1)
					elif z == 6:
						self.parts[y].rotation(1)
					elif z == 7:
						self.parts[y].rotation(-1)

					self.setPositions(pivot)
					self.collide(2)
					count = count + 1
				if count < max[1]:
					max = (z, count)
				self.stored(False)
				self.collide(2)
				if count < 3:
					break
			z = max[0]
			count = 0
			while len(self.selfCollide) >= colliderLen and count < 10:

				if z == 0:
					self.parts[x].rotation(-1)
					self.parts[y].rotation(1)
				elif z == 1:
					self.parts[x].rotation(-1)
				elif z == 2:
					self.parts[x].rotation(-1)
					self.parts[y].rotation(-1)
				elif z == 3:
					self.parts[x].rotation(1)
					self.parts[y].rotation(1)
				elif z == 4:
					self.parts[x].rotation(1)
				elif z == 5:
					self.parts[x].rotation(1)
					self.parts[y].rotation(-1)
				elif z == 6:
					self.parts[y].rotation(1)
				elif z == 7:
					self.parts[y].rotation(-1)
				self.setPositions(pivot)
				self.collide(2)
				count = count + 1
		count = 0
		while self.collide(0) and count < 5:
			pivot = (pivot[0], pivot[1] - 1.0)
			self.setPositions(pivot)
			count = count + 1
		if count == 5:
			pivot = (pivot[0], pivot[1] + 5.0)
			self.setPositions(pivot)
		

	# Creates a parallelogram around the agent with the corners being the collision points with the highest and lowest x and y values
	# used for calculating gravity and if the agents center of gravity is over an edge (in which case it will fall)
	def collisionBox(self, point):
		# Lowest x value
		if self.box[0][0] == -1 or point[0] < self.box[0][0]:
			self.box[0] = point
		# Highest x value
		if self.box[1][0] == -1 or (point[0] > self.box[1][0] and self.box[1][0] != -1):
			self.box[1] = point
		# Lowest y value
		if self.box[2][1] == -1 or point[1] < self.box[2][1]:
			self.box[2] = point
		# Highest y value
		if self.box[3][1] == -1 or (point[1] > self.box[3][1] and self.box[3][1] != -1):
			self.box[3] = point

	# Add an object in the environment so the ant is aware of the world
	def addObject(self, obj):
		self.objects.append(obj)

	# Draw all the images
	def run(self, DS):
		parts = self.parts
		for i in range(0,9):
			DS.blit(parts[i].getImage(), parts[i].getPosition())
		for i in range(9,15):
			DS.blit(parts[i].getImage(), parts[i].getPosition())

	# Return an array of all the individual ant parts
	def getParts(self):
		return self.parts

	# Return the agents center of gravity
	def getCog(self):
		return self.cog

	# Retrun any markers that should be drawn on screen
	def getMarkers(self):
		return self.box
