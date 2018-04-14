import math, random, sys, pygame
from pygame.locals import *
from part import Part
from random import *

# Groups together all the individual parts for one agent
class Parts:
	# Initialize class
	def __init__(self, backup, position, step):
		self.array = []
		self.training_step = step + 1
		self.init = False
		self.given = False
		self.net = []
		# If this is an agents backup store default values for all parts
		if backup:
			for k in range(0,15):
				self.array.append(Part(0, 0))
		# Otherwise spawn agent in a random position
		else:
			# Initialise the body and head of the agent
			random = randint(-30, 30)
			# The back of the agent is the heaviest so that it does ot topple forwards
			if self.training_step == 1:
				self.array.append(Part(random + randint(-89,89), 50, 23.44, position))
				self.array.append(Part(random, 50, 11.72))
				self.array.append(Part(random + randint(-89,89), 50, 8.24))
			else:
				self.array.append(Part(0, 50, 23.44, position))
				self.array.append(Part(0, 50, 11.72))
				self.array.append(Part(0, 50, 8.24))
			# Load the head and bodies image files
			self.array[0].loadImage("image_resources/body.png")
			self.array[1].loadImage("image_resources/body.png")
			self.array[2].loadImage("image_resources/head.png")

			# Initialise the legs of the agent
			for i in range(0, 2):
				random_values = [randint(0, 360),randint(-90, 90)]
				# The legs on each side of the agent should have matching rotations
				# The weight of each leg is 0.66 * 2 (Since each leg is made of 2 parts)
				self.array.append(Part(random_values[0], 12, 0.66))
				self.array.append(Part(random_values[0], 12, 0.66))
				self.array.append(Part(random_values[0], 12, 0.66))
				self.array.append(Part(random_values[0] + random_values[1], 12, 0.66))
				self.array.append(Part(random_values[0] + random_values[1], 12, 0.66))
				self.array.append(Part(random_values[0] + random_values[1], 12, 0.66))

			# Load the image files for the legs
			for j in range(3, 15):
				self.array[j].loadImage("image_resources/leg.png")
			# Set each parts position and constraints
			self.setPositions(position)
			self.setConstraints()


	# Link a backup to the actual agents parts and vice-versa
	def load_pair(self, pair):
		self.pair = pair

	# Replaces values with values from backup
	def duplicate(self):
		array = self.array
		pair = self.pair
		for i in range(0,15):
			array[i].setPosition(pair.array[i].getPosition())
			array[i].setConstraint(pair.array[i].getConstraint())
			array[i].setRotation(pair.array[i].getRotation())

	# Sets all the parts positions with regards to the agents pivot
	def setPositions(self, pivot):
		# This method finds the distance each part should be from its pivot and uing the rotation of the agents other parts
		# Calculates where it should be
		array = self.array
		# Rotation of the agents abdominal segments
		backRotation = (math.cos(array[0].getRotation() / 180 * math.pi), math.sin((180.0 + array[0].getRotation()) / 180 * math.pi))
		frontRotation = (math.cos(array[1].getRotation() / 180 * math.pi), math.sin((180.0 + array[1].getRotation()) / 180 * math.pi))
		# Set Back abdominal segments position to the pivot
		array[0].setPosition(pivot)
		# Front abdominal segment
		array[1].setPosition((pivot[0] + (backRotation[0] * 39.0), pivot[1] + (backRotation[1] * 39.0)))
		# Head
		array[2].setPosition((pivot[0] + (backRotation[0] * 39.0) + (frontRotation[0] * 39.0), pivot[1] + (backRotation[1] * 39.0) + (frontRotation[1] * 39.0)))
		for i in range(0,2):
			offset = i * 6
			# Back leg (top)
			array[3 + offset].setPosition((pivot[0] + 38 + (backRotation[0] * 12), pivot[1] + 40 + (backRotation[1] * 12)))
			legRotation = (math.sin(array[3 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + array[3 + offset].getRotation()) / 180 * math.pi))
			# Back leg (bottom)
			array[6 + offset].setPosition((pivot[0] + 38 + (backRotation[0] * 12) + (legRotation[0] * 11.5), pivot[1] + 40 + (backRotation[1] * 12) + (legRotation[1] * 11.5)))
			# Middle leg (top)
			array[4 + offset].setPosition((pivot[0] + 38 + (backRotation[0] * 39), pivot[1] + 40 + (backRotation[1] * 39)))
			legRotation = (math.sin(array[4 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + array[4 + offset].getRotation()) / 180 * math.pi))
			# Middle leg (bottom)
			array[7 + offset].setPosition((pivot[0] + 38 + (backRotation[0] * 39) + (legRotation[0] * 11.5), pivot[1] + 40 + (backRotation[1] * 39) + (legRotation[1] * 11.5)))
			# Front leg (top)
			array[5 + offset].setPosition((pivot[0] + 38 + (backRotation[0] * 39) + (frontRotation[0] * 27), pivot[1] + 40 + (backRotation[1] * 39) + (frontRotation[1] * 27)))
			# Front leg (bottom)
			legRotation = (math.sin(array[5 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + array[5 + offset].getRotation()) / 180 * math.pi))
			array[8 + offset].setPosition((pivot[0] + 38 + (backRotation[0] * 39) + (legRotation[0] * 11.5) + (frontRotation[0] * 27), pivot[1] + 40 + (backRotation[1] * 39)  + (legRotation[1] * 11.5)+ (frontRotation[1] * 27)))


	# Draw the images for each part
	def run(self, DS):
		array = self.array
		for i in range(9,15):
			DS.blit(array[i].getImage(), array[i].getPosition())
		for i in range(0,9):
			DS.blit(array[i].getImage(), array[i].getPosition())



	# Calculate the agents center of gravity
	def centerOfGravity(self, pivot):
		array = self.array
		cog = (0,0)
		centers = []
		# Agents co-ordinate
		# Convert each parts current angle to a 2D vector
		partRotations = []
		for q in range(0,15):
			# Since the body parts and the legs initially start at different rotations the calculations for them are different
			if q < 3:
				partRotations.append((math.cos(array[q].getRotation() / 180 * math.pi), math.sin((180.0 + array[q].getRotation()) / 180 * math.pi)))
			else:
				partRotations.append((math.cos((array[q].getRotation() - 90) / 180 * math.pi), math.sin((180.0 + (array[q].getRotation() - 90)) / 180 * math.pi)))

		# 1/2 the length of each part
		distances = [18,18,9,5,5,5,5,5,5,5,5,5,5,5,5]

		# Find the center points of each part
		# Calculated (1/2 parts length * angle) + pivot
		for i in range(0,15):
			centers.append((array[i].getPivot()[0] + (partRotations[i][0] * distances[i]), array[i].getPivot()[1] + (partRotations[i][1] * distances[i])))

		# Multiply the position of each agent by its weight to find the agents total center of gravity
		weight = 0
		for i in range(0,15):
			cog = (cog[0] + (centers[i][0] * array[i].getWeight()), cog[1] + (centers[i][1] * array[i].getWeight()))
			weight += array[i].getWeight()
		# Divide by the total weight of the agent
		cog = (cog[0] / weight, cog[1] / weight)
		return cog


	# Set the constraint of each part
	def setConstraints(self):
		array = self.array
		# The constraints of the body parts and head and related to the rotation
		# of the next part the agent is connected to
		array[0].setConstraint(array[1].getRotation())
		array[1].setConstraint(array[0].getRotation())
		array[2].setConstraint(array[1].getRotation())
		for i in range(0,2):
			offset = i * 6
			# The top parts of the agents legs have no constraint (shown by the -1)
			array[3 + offset].setConstraint(-1)
			array[4 + offset].setConstraint(-1)
			array[5 + offset].setConstraint(-1)
			# The bottom part of each leg has its constraint tied to the rotation of the top part
			array[6 + offset].setConstraint(array[3 + offset].getRotation())
			array[7 + offset].setConstraint(array[4 + offset].getRotation())
			array[8 + offset].setConstraint(array[5 + offset].getRotation())


	# When the agent moves a leg and it collides with the environment instead of cancelling the move
	# the agent should push off with the leg and move the rest of its body to compensate
	# this allows the agent to move around the environment
	def interactiveMove(self, part_num, direction_top, direction_bottom, colliding):
		array = self.array
		# Get the pivot of the part that is attempting to move
		initialPos = array[part_num].getPivot()
		# Get the distance between the pivot and where the agent collided with the environment
		distance = (initialPos[0] - colliding[0][0], initialPos[1] - colliding[0][1])
		hypD = math.sqrt(distance[0] * distance[0] + distance[1] * distance[1])

		# Get the x,y distance between the pivot and the point on the agent where it will collide after rotating
		# So hypontenuese distance is be the same as distance but the x,y values are slightly different
		rotation = (math.atan(distance[0] / distance[1]) * 180.0 / math.pi) - direction_top
		oldPos = (hypD * math.sin(rotation * math.pi / 180.0), hypD * math.cos(rotation * math.pi / 180.0))
		# If the collision point is above the pivot reverse the values since they will all be negative
		if distance[1] > 0:
			oldPos = (-oldPos[0], -oldPos[1])
		# Find the diffence between where the part will be and where it is currently
		# Minus 1 from the height since the parts dont have smooth edges (Pixels are squares)
		# This is added back later
		oldPos = (oldPos[0] + distance[0], oldPos[1] + distance[1] - 1.0)

		# Rotate both parts of the leg since they were reset when the agent colldied with the environment
		array[part_num].rotate(direction_top)
		array[part_num + 3].rotate(direction_bottom)

		# Recalibrate the parts of the agent so they are in the correct position
		self.setPositions(array[0].getPosition())
		# Return the difference between where the agent is an where is should be
		return oldPos

	# Rotate entire agent
	def rotateAll(self, amount):
		for iterate in range(0,15):
			# Since the entire agent is being rotated by the same amount ignore the constraint check
			self.array[iterate].rotate(amount, True)



	# Set the inputs for the agents neural network
	def inputs(self, pivot, sensors, target):
		array = self.array
		# Array of input values to be returned
		net_inputs = []
		# Rotation of the back abdominal section of the agent
		# By adding 180 it means the point at which the value change from 0 to 1 is in a less used location
		net_inputs.append(((180 + array[0].getRotation()) % 360) / 360.0)
		# The difference between the agent back and middle segments
		second_rotation = (array[1].getRotation() - array[0].getRotation() + 90)
		if abs(second_rotation) == 180:
			second_rotation = 1
		else:
			second_rotation = second_rotation % 180
		# The difference between the agent middle and head segments
		third_rotation = (array[2].getRotation() - array[1].getRotation() + 90) % 180
		if abs(third_rotation) == 180:
			third_rotation = 1
		else:
			third_rotation = third_rotation % 180

		# Scale between 0 and 1
		net_inputs.append(second_rotation / 180.0)
		net_inputs.append(third_rotation / 180.0)

		# top segment of the front set of legs
		# Since they all legs on the same side have the same rotation we only the need the value of one
		front_rotation = array[3].getRotation()
		net_inputs.append(front_rotation / 360.0)
		# Difference in rotation between the top of the leg and the bottom. Scaled to between 0 and 1
		front_rotation = (front_rotation - array[6].getRotation() + 90) % 181
		net_inputs.append(front_rotation / 180.0)

		# top segment of the back set of legs
		# Since they all legs on the same side have the same rotation we only the need the value of one
		back_rotation = array[9].getRotation()
		net_inputs.append(back_rotation / 360.0)
		# Difference in rotation between the top of the leg and the bottom. Scaled to between 0 and 1
		back_rotation = (back_rotation - array[12].getRotation() + 90) % 181
		net_inputs.append(back_rotation / 180.0)


		# Sensor values
		net_inputs.append(sensors[0])
		net_inputs.append(sensors[1])
		# If the sensor can see the target the value of this input is 1
		if target:
			net_inputs.append(1)
		else:
			net_inputs.append(0)

		if self.init < 3:
			self.init += 1
			self.net.append(net_inputs)

		return net_inputs

	def rewards(self, inputs, moves, last_score, turn):
		rotations = [abs(inputs[1] - 0.5), abs(inputs[2] - 0.5)]
		if self.training_step == 1:
			if rotations[0] < 0.1 and rotations[1] < 0.1:
				return 1.00, True
			elif rotations[0] == 0.5 or rotations[1] == 0.5 or turn > 3:
				return -1.00, True
		elif self.training_step == 2:
			if rotations[0] > 0.1 or rotations[1] > 0.1 or last_score <= 0 or turn > 5:
				return -1.00, True
			elif last_score > 20:
				return 1.00, True
		elif self.training_step == 3:
			if inputs[7] >= 0.65 or inputs[8] >= 0.65:
				if inputs[0] >= 0.62 and inputs[0] <= 0.65:
					if inputs[1] >= 0.24 and inputs[1] <= 0.40:
						if inputs[2] == 0:
							return 1.00, True
			if (inputs[7] == 0 and inputs[8] == 0) or turn == 5 or last_score <= 0:
				return -1.00, True
		elif self.training_step == 4:
			if not self.given and self.array[0].getPosition()[0] > 600:
				self.given = True
				return 1.00, False
			if (inputs[7] == 0 and inputs[8] == 0):
				if self.array[0].getPosition()[0] > 600:
					return 1.00, True
				else:
					return -1.00, True
			if turn == 11 or last_score <= 0:
				return -1.00, True

		return 0.00, False

	def setRotations(self, rotations):
		for i in range(0,len(rotations)):
			self.array[i].setRotation(rotations[i])
		self.setPositions(self.array[0].getPosition())
