import math, sys, pygame
from pygame.locals import *
from part import Part
from agent_parts import Parts
from sensors import Sensors
import random
from random import randint
import pickle
import time
import numpy as np

class Agent:

	def __init__(self, xy, target, networks, agent_num, goal, boundary, training, randomness, subsumption):
		print("Sub",subsumption, "Randomness",randomness)
		print("Agent Num:", agent_num)
		# store initial parameters
		self.agent_num = agent_num
		self.boundary = boundary
		self.networks = networks
		self.target = target
		self.goal = goal

		self.training = training
		self.randomness = randomness
		self.subsumption = subsumption

		self.finished = False

		# Initialize variables
		self.stop = 0
		self.restart = False	
		self.colliding = []
		self.objects = []
		self.agents = []
		self.batch_state_action_reward_tuples = []
		self.networkInput = []
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		self.prevMoves = []
		self.total = 0
		self.won = False
		self.interactive_dist = 0
		self.turn = 0
		self.start_reached = False
		if self.networks.get_turn() < 2:
			self.start_reached = True

		self.next()

		# Initialise agents parts and backup
		self.parts = Parts(False, xy, self.networks.get_turn())
		self.backup = Parts(True, None, 0)	
		self.parts.load_pair(self.backup)
		self.backup.load_pair(self.parts)
		self.array = self.parts.array
		self.cog = self.parts.centerOfGravity(xy)
		self.score_tracker = self.cog[0]
		self.last_score = 0.5


		# Initialise agents sensors
		self.sensors = Sensors()
		self.sensors.setPositions(self.array[0].getPivot(), self.array[2].getPivot())

	def next(self):
		self.timer = 400
		if not (self.turn == 0):
			parts = self.array
			score = self.cog[0] - self.score_tracker
			if score == 0:
				percent = 1
			else:
				percent = (self.interactive_dist / score)
			self.last_score = self.interactive_dist
			print("Step:", self.turn, "Score:", score, self.interactive_dist)
			if self.last_score <= 0:
				if ((self.networkInput[7] > 0.5 or self.networkInput[8] > 0.5) and self.networkInput[2] < 0.01):
					self.finished = 1
				else:
					self.finished = -1
			self.score_tracker = self.cog[0]
			self.interactive_dist = 0
		self.turn += 1



	# Handles movement calculations
	def move(self):
		self.round_tuples = []
		if self.start_reached:
			self.timer -= 1
			if self.timer == 0:
				self.next()
		parts = self.array
		# Reset variables
		pivot = self.array[0].getPosition()
		self.moves = []
		# Update the position of the sensors and then check their value
		self.sensors.setPositions(self.array[0].getPivot(), self.array[2].getPivot())
		self.sensors.collisions(self.objects, self.agents, self.target)
		self.networkInput = self.parts.inputs(pivot, self.sensors.sensor_values, self.sensors.target)
		if not self.start_reached:
			if self.sensors.sensor_values[0] > 0.1 or self.sensors.sensor_values[1] > 0.1:
				self.start_reached = True
		# Gravity
		pivot = self.gravity(pivot, 30)
		# Move the agents body then legs
		pivot = self.bodyMove(pivot)
		pivot = self.legMove(pivot)

		self.cog = self.parts.centerOfGravity(pivot)
		self.backup.duplicate()
		# After movement check where the agent is colliding with the world so that it knows whether to fall
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		# Lower the agent by 1.5 pixels, check for collisions then raise it back up
		pivot = (pivot[0], pivot[1] + 1.5)
		self.parts.setPositions(pivot)
		self.collide()
		pivot = (pivot[0], pivot[1] - 1.5)
		self.parts.duplicate()
		extra = 0
		# If the agents center of gravity is not between 2 collision points then it should fall over
		if self.box[0][0] != -1 and (self.box[0][0] > self.cog[0] or self.box[1][0] < self.cog[0]):
			pivot, extra = self.fallRotation(pivot)
			self.parts.setConstraints()
			if extra != 0:
				pivot = self.gravity(pivot, (extra) * 10)

		



	# Updates the network and checks to see if the run has ended
	def updateNetwork(self, move, partNum, turn):
		if self.start_reached:
			array = self.array
			reward = 0
			# If the agent reaches the goal the agent wins the round
			if turn == 3:
				reward, self.restart = self.parts.rewards(self.networkInput, self.moves, self.last_score, self.turn)

				# Set the output to match the move
				for i in range(7):
					output = [0,0,0]
					output[self.moves[i]] = 1
					# Add result to the set of tuples that will train the network
					tup = (self.networkInput, output, reward)
					self.networks.append_tuple(tup, i)


			# If the agent succeeds/fails print log
			if self.restart:
				if reward < 0:
					print("Reward: %0.3f,  lost..." % (reward))
				elif reward > 0:
					print("Reward: %0.3f, won!" % (reward))
					self.won = True
					self.next()
					self.last_score = 0.5

	# When the agents center of gravity is not between 2 points of contact with the environment
	# then it should fall over
	def fallRotation(self, pivot):
		parts = self.parts
		# Find the closest point of contact with the environment
		# so that when the agent falls they can pivot from there
		pointOfContact = (self.box[0][0], self.box[0][1])

		# The agent falls using the point of contact and its center of gravity so it needs the distance between
		distanceXY = (self.cog[0] - pointOfContact[0], pointOfContact[1] - self.cog[1])
		# The speed at which the agent falls (amount the agent will be rotated by)
		torque = distanceXY[0] / 25

		# Actual distance between the agents point of contact with the world and the agents main pivot point
		distanceH = math.sqrt(distanceXY[0] * distanceXY[0] + distanceXY[1] * distanceXY[1])

		# The angle between the collision point being used and the agents pivot point.
		currentAngle = None
		if(distanceXY[0] == 0):
			currentAngle = 90
		else:
			currentAngle = math.atan(distanceXY[1]/distanceXY[0]) * 180.0 / math.pi
		if currentAngle < 0:
			currentAngle = 180 + currentAngle
		# the new angle is the current angle minus torque
		newAngle = currentAngle - torque

		# The X,Y distances between the agents point of contact with the world and where the agents main pivot point will be after the rotation
		newXY = (distanceH * math.cos(newAngle / 180 * math.pi), (distanceH * math.sin(newAngle / 180 * math.pi)))
		if pointOfContact[1] < self.cog[1]:
			newXY = (-newXY[0], -newXY[1])
		newCog = (pointOfContact[0] + newXY[0], pointOfContact[1] - newXY[1])

		# Store a backup
		self.backup.duplicate()
		# Rotate all parts of the agent
		self.parts.rotateAll(-torque)
		# Reposition agent parts
		self.parts.setPositions(pivot)
		# Get the agents new center of gravity
		self.cog = self.parts.centerOfGravity(pivot)
		# Find the difference between the current cog and where it should be
		cogDiff = (newCog[0] - self.cog[0], newCog[1] - self.cog[1])

		# Add the difference and raise it by 2
		newPivot = (pivot[0] + cogDiff[0], pivot[1] + cogDiff[1] - 2)
		self.parts.setPositions(newPivot)

		# If it fails reset the agent
		if self.collide():
			self.parts.duplicate()
			return pivot, 0
		# Else return the new pivot and since we raised it by 2 before tell
		# the program to lower it by 2
		else:
			return newPivot, 20

	# Agent is affected by gravity
	def gravity(self, pivot, amount):
		# Decrement multiple times instead of just lowering once soif it collides in the middle it will go as close as possible
		for i in range(0,amount):
			# Store a copy of the agent
			self.backup.duplicate()
			# Lower the agent by 1
			pivot = (pivot[0], pivot[1] + 0.1)
			self.parts.setPositions(pivot)
			# If the agent collides with the world revert the move
			if self.collide():
				self.parts.duplicate()
				# Reset the pivot if the agent is reset
				pivot = (pivot[0], pivot[1] - 0.1)
				break
		return pivot

	# Handles Collisions between the ant and the world
	def collide(self):
		array = self.array
		objects = [self.objects, self.agents]
		self.colliding = []
		ret = False
		for z in range(2):
			# Check for collisions for every part of the agent
			for position in range(0,15):
				# Check collisions against all the other objects in the world which exclude itself
				for k in range(len(objects[z])):
					# Find the position difference between the agent part and the external object
					offset = (int(objects[z][k][1] - array[position].getPosition()[0]), int(objects[z][k][2] - array[position].getPosition()[1]))
					result = array[position].getMask().overlap(objects[z][k][0], offset)
					# If there is a collision add it to the collision list
					if result:
						self.collisionBox((array[position].getPosition()[0] + result[0], array[position].getPosition()[1] + result[1]))
						self.colliding.append((array[position].getPosition()[0] + result[0], array[position].getPosition()[1] + result[1]))
						ret = True

		return ret

	# Add an object in the environment so the ant is aware of the world
	def addObject(self, obj):
		self.objects.append(obj)

	# Add another agent so the ant is aware of the world
	def addOtherAgent(self, agent):
		for j in range(0,3):
			part = agent.parts.array[j]
			self.agents.append((part.getMask(), part.getPosition()[0], part.getPosition()[1]))


	# Creates a parallelogram around the agent with the corners being the collision points with the highest and lowest x and y values
	# used for calculating gravity and if the agents center of gravity is over an edge (in which case it will fall)
	def collisionBox(self, point):
		# Bottom left corner
		if self.box[0][0] == -1 or point[0] < self.box[0][0]:
			self.box[0] = point
		# Bottom right corner
		if self.box[1][0] == -1 or (point[0] > self.box[1][0] and self.box[1][0] != -1):
			self.box[1] = point
		# Top left corner
		if self.box[2][1] == -1 or point[1] < self.box[2][1]:
			self.box[2] = point
		# Top right corner
		if self.box[3][1] == -1 or (point[1] > self.box[3][1] and self.box[3][1] != -1):
			self.box[3] = point

	# Return the collision points box that should be drawn on screen
	def getBox(self):
		return self.box

	# Choose a move depending on the probabilities given by the neural network
	def getMove(self, probabilities, banned):
		highest = 0
		for i in range(1,3):
			if probabilities[i] > probabilities[highest]:
				highest = i

		move = 0
		move = highest
		# 90% chance of best move otherwise pick a random move
		while True:
			probability_random = random.uniform(0, 100)
			if probability_random >= self.randomness:
				move = highest
			else:
				move = randint(0, 2)

			if not(move == banned):
				break
		# Return the chosen move
		return move

	# Move the agents legs
	def legMove(self, pivot):
		parts = self.parts
		array = self.array
		prevMoves = []
		# Front legs then back legs
		for i in range(0,2):
			cog = self.cog[0]
			# Get the inputs for the top part of the legs then the bottom part
			# Get the probabilities for each move
			probabilities_top = self.networks.forward_pass(self.networkInput, (i * 2))
			probabilities_bottom = self.networks.forward_pass(self.networkInput, (i * 2) + 1)
			# Pick a move based of the networks probabilities
			move_top = self.getMove(probabilities_top, -1)
			move_bottom = self.getMove(probabilities_bottom, -1)


			if not self.start_reached or self.subsumption:
				if randint(0, 100) >= self.randomness:
					move_top = self.presetMove(i)
				else:
					move_top = randint(0,2)
				if randint(0, 100) >= self.randomness:
					move_bottom = self.presetMove(i)
				else:
					move_bottom = randint(0,2)



			# Rotate the bottom by the same amount as the top + its own values
			rotation_amount_top = move_top - 1
			rotation_amount_bottom = move_bottom - 1 + rotation_amount_top
			# Append moves
			self.moves.append(move_top)
			self.moves.append(move_bottom)
			for j in range(3):
				# Store initial pivot and calculate part number
				oldPivot = (pivot[0], pivot[1])
				partNum = (i * 6) + j + 3
				# Store a back up
				self.backup.duplicate()
				self.parts.setConstraints()
				# rotate a leg by the correct amount
				array[partNum].rotate(rotation_amount_top)
				array[partNum + 3].rotate(rotation_amount_bottom)

				self.parts.setPositions(pivot)
				resetGravity = 0
				# If the leg collides with the environment the entire agent should move. (How the agent walks)
				if self.collide():
					# Restore backup
					self.parts.duplicate()
					# Add the distance the agent should move by
					distChange = self.parts.interactiveMove(partNum, rotation_amount_top, rotation_amount_bottom, self.colliding)
					pivot = (pivot[0] + distChange[0], pivot[1] + distChange[1])
					# If the agent still collides with the world try raising it more
					if self.collide():
						pivot = (pivot[0], pivot[1] - 2)
						self.parts.setPositions(pivot)

						if self.collide():
							self.parts.duplicate()
							pivot = (oldPivot[0], oldPivot[1])
						else:
							resetGravity = 30
					else:
						resetGravity = 10
					# If the agent was raised to stop a collision lower it back down
					if resetGravity is not 0:
						pivot = self.gravity(pivot, resetGravity)
						prevMoves.append((partNum, distChange[0], move_top))
						self.interactive_dist += distChange[0]

				# It's possible for the agent to vibrate along the floor. This reduces the amount a lot by cancelling out
				# moves when the agent is twitching
				if resetGravity == 0:
					for z in range(len(self.prevMoves)):
						if self.prevMoves[z][0] == partNum and abs(move_top - self.prevMoves[z][2]) == 2:
							pivot = (pivot[0] - self.prevMoves[z][1], pivot[1] - 1.0)
							self.parts.setPositions(pivot)
							# If the move cannot be reverted accept it
							if self.collide():
								self.parts.duplicate()
								pivot = (pivot[0] + self.prevMoves[z][1], pivot[1] + 1.0)
								print("Fail, Previous move could not be reverted")
							else:
								pivot = self.gravity(pivot, 10)

			# Send the agents move information to the network
			if self.training:
				self.updateNetwork(move_top, partNum, (i * 2))
				self.updateNetwork(move_bottom, partNum + 3, (i * 2) + 1)
		self.prevMoves = prevMoves
		return pivot

	# Move the agents body
	def bodyMove(self, pivot):
		parts = self.array
		# Currently no banned moves
		banned_move = -1
		for i in range(4,7):
			# Initialise variables
			oldPivot = (pivot[0], pivot[1])
			partNum = i - 4
			move = None
			# Get the networks input data and then get the probabilities from the network
			probabilities = self.networks.forward_pass(self.networkInput, i)
			# The middle part of the agent cannot rotate in the same direction as the back since they share the same pivot
			if i == 5:
				move = self.getMove(probabilities, banned_move)
			else:
				move = self.getMove(probabilities, -1)




			if not self.start_reached or self.subsumption:
				if randint(0, 100) >= self.randomness:
					move = self.presetMove(i)
				else:
					move = randint(0,2)






			# Rotation amount  -1-anticlockwise 0-stationary 1-clockwise
			self.moves.append(move)
			rotation_amount = move - 1
			# Store a backup and then rotate part
			self.backup.duplicate()
			self.parts.setConstraints()
			parts[partNum].rotate(rotation_amount)
			# Since the agent builds off the back piece, when that rotates the agent should reposition so that all other parts
			# stay in the same place
			if i == 4:
				torso_position = parts[1].getPosition()
				self.parts.setPositions(pivot)
				new_torso_position = parts[1].getPosition()
				new_torso_position = (new_torso_position[0] - torso_position[0], new_torso_position[1] - torso_position[1])
				pivot = (pivot[0] - new_torso_position[0], pivot[1] - new_torso_position[1])
				# if the back of the agent rotated ban that move for the middle section of the agent
				if move is not 1 and new_torso_position[0] is not 0:
					banned_move = move
			# When the middle part of the agent rotates so does the head
			elif i == 5:
				parts[2].rotate(rotation_amount)

			self.parts.setPositions(pivot)
			resetGravity = 0

			# If the agent collides with its environment reposition it slightly
			if self.collide():
				pivot = (pivot[0], pivot[1] - 2)
				self.parts.setPositions(pivot)

				if self.collide():

					pivot = (pivot[0] - 1, pivot[1])
					self.parts.setPositions(pivot)

					if self.collide():
						pivot = (pivot[0] - 1, pivot[1])
						self.parts.setPositions(pivot)

						if self.collide():
							self.parts.duplicate()
							pivot = (oldPivot[0], oldPivot[1])
						else:
							resetGravity = 30
					else:
						resetGravity = 30
				else:
					resetGravity = 30
			elif move is not 1:
				resetGravity = 10

			if resetGravity is not 0:
				pivot = self.gravity(pivot, resetGravity)
			# Send the agents move information to the network
			if self.training:
				self.updateNetwork(move, partNum, i)
		return pivot

	def presetMove(self, i):
		move = 0
		if i < 4:
			if (self.networkInput[7] > 0.5 or self.networkInput[8] > 0.5) and self.networkInput[2] < 0.01:
				move = 1
		else:
			move = 1
			if i == 4:
				if self.networkInput[7] > 0.5 or self.networkInput[8] > 0.5:
					if self.networkInput[9] == 1:
						if self.networkInput[0] < 0.62:
							move = 2
						elif self.networkInput[0] > 0.65:
							move = 0
				else:	
					if self.networkInput[1] > 0.51:
						move = 2
					elif self.networkInput[1] < 0.49:
						move = 0
			elif i == 5:
				if self.networkInput[8] == 0 and self.networkInput[7] > 0.2:
						if self.networkInput[1] > 0.43:
							move = 0
						elif self.networkInput[1] < 0.37:
							move = 2
				elif self.networkInput[7] > 0.5 or self.networkInput[8] > 0.5:
					if self.networkInput[9] == 1:
						if self.networkInput[0] >= 0.62 and self.networkInput[0] <= 0.65:
							if self.networkInput[1] < 0.24:
								move = 2
							elif self.networkInput[1] > 0.30:
								move = 0
					else:
						if self.networkInput[1] < 0.76:
							move = 2
						elif self.networkInput[1] > 0.70:
							move = 0
			elif i == 6:
				if (self.networkInput[7] > 0.5 or self.networkInput[8] > 0.5) and self.networkInput[9] == 1:
					if self.networkInput[0] >= 0.62 and self.networkInput[0] <= 0.65:
						move = 0
				else:
					if self.networkInput[2] > 0.51:
						move = 0
					elif self.networkInput[2] < 0.49:
						move = 2
		return move

