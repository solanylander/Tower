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

	def __init__(self, xy, target, network, agent_num, goal, boundary):
		print("Agent Num:", agent_num)
		# store initial parameters
		self.agent_num = agent_num
		self.boundary = boundary
		self.network = network
		self.target = target
		self.goal = goal

		# Initialize variables
		self.stop = 0
		self.restart = False	
		self.colliding = []
		self.objects = []
		self.batch_state_action_reward_tuples = []
		self.networkInput = []
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		self.prevMoves = []
		self.total = 0
		self.won = False
		self.interactive_dist = 0
		self.turn = 0

		self.next()

		# Initialise agents parts and backup
		self.parts = Parts(False, xy)
		self.backup = Parts(True, None)	
		self.parts.load_pair(self.backup)
		self.backup.load_pair(self.parts)
		self.array = self.parts.array
		self.cog = self.parts.centerOfGravity(xy)
		self.score_tracker = self.cog[0]


		# Initialise agents sensors
		self.sensors = Sensors()
		self.sensors.setPositions(self.array[0].getPivot(), self.array[2].getPivot())

	def next(self):
		if not (self.turn == 0):
			parts = self.array
			score = self.cog[0] - self.score_tracker
			if score == 0:
				percent = 1
			else:
				percent = (self.interactive_dist / score)
			print("Step:", self.turn, "Score:", score, self.interactive_dist)
			self.score_tracker = self.cog[0]
			self.interactive_dist = 0
		self.turn += 1



	# Handles movement calculations
	def move(self):
		parts = self.array
		# Reset variables
		pivot = self.array[0].getPosition()
		self.moves = []
		# Update the position of the sensors and then check their value
		self.sensors.setPositions(self.array[0].getPivot(), self.array[2].getPivot())
		self.sensors.collisions(self.objects, self.target)
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
	def updateNetwork(self, move, partNum):
		array = self.array
		reward = 0
		# If the agent reaches the goal the agent wins the round
		if partNum == 14:
			offset = (int(array[2].getPosition()[0] - self.goal.getPosition()[0]), int(array[2].getPosition()[1] - self.goal.getPosition()[1]))
			result = self.goal.getMask().overlap(array[2].getMask(), offset)
			if result:
				reward = 1.00

		# Set the output to match the move
		output = [0,0,0]
		output[move] = 1

		# Add result to the set of tuples that will train the network
		tup = None
		if ((partNum - 3) % 6) < 3:
			tup = (self.networkInput_top, output, reward)
		else:
			tup = (self.networkInput, output, reward)
		self.network.batch_state_action_reward_tuples.append(tup)

		# If the agent succeeds/fails print log
		if reward < 0:
			print("Training Step %d; Score: %0.3f, Reward: %0.3f,  lost..." % (self.training_step, score, reward))
		elif reward > 0:
			print("Training Step %d: Score: %0.3f, Reward: %0.3f, won!" % (self.training_step, score, reward))


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
		objects = self.objects
		self.colliding = []
		ret = False
		# Check for collisions for every part of the agent
		for position in range(0,15):
			# Check collisions against all the other objects in the world which exclude itself
			for k in range(len(objects)):
				# Find the position difference between the agent part and the external object
				offset = (int(objects[k][1] - array[position].getPosition()[0]), int(objects[k][2] - array[position].getPosition()[1]))
				result = array[position].getMask().overlap(objects[k][0], offset)
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
			self.objects.append((part.getMask(), part.getPosition()[0], part.getPosition()[1]))


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
		probability_addition = probabilities[0] + probabilities[1] + probabilities[2]

		move = 0
		while True:
			probability_random = random.uniform(0, probability_addition)
			# If random is less than the probability of 0 choose 0
			if probability_random < probabilities[0]:
				move = 0
			# Elif random is less the probability of 0 + 1 choose 1
			elif probability_random < probabilities[0] + probabilities[1]:
				move = 1
			# Else choose move 2
			else:
				move = 2
			# If the move is banned pick another one
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
			self.networkInput_top = self.parts.inputs(pivot, i * 2, self.sensors.sensor_values, self.sensors.target)
			self.networkInput = self.parts.inputs(pivot, (i * 2) + 1, self.sensors.sensor_values, self.sensors.target)
			# Get the probabilities for each move
			probabilities_top = self.network.forward_pass(self.networkInput_top)[0]
			probabilities_bottom = self.network.forward_pass(self.networkInput)[0]
			# Pick a move based of the networks probabilities
			move_top = self.getMove(probabilities_top, -1)
			move_bottom = self.getMove(probabilities_bottom, -1)
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
			self.updateNetwork(move_top, partNum)
			self.updateNetwork(move_bottom, partNum + 3)
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
			self.networkInput = self.parts.inputs(pivot, i, self.sensors.sensor_values, self.sensors.target)
			probabilities = self.network.forward_pass(self.networkInput)[0]
			# The middle part of the agent cannot rotate in the same direction as the back since they share the same pivot
			if i == 5:
				move = self.getMove(probabilities, banned_move)
			else:
				move = self.getMove(probabilities, -1)

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
			self.updateNetwork(move, partNum)
		return pivot