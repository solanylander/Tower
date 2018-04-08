import math, random, sys, pygame
from pygame.locals import *
from part import Part
from random import *

# self.backup self.parts
class Parts:

	def __init__(self, backup, additional, position):
		parts = []
		self.backup = backup
		if backup:
			for k in range(0,15):
				parts.append(Part(0, 0, 0, False, 0, 0))
		else:
			rand_one = randint(-30, 30) 
			rand_two = rand_one - additional[0]
			rand_three = rand_one + additional[1]
			parts.append(Part(rand_two, position[0], position[1], True, 50, 0))
			parts.append(Part(rand_one, 0, 0, False, 50, 1))
			parts.append(Part(rand_three, 0, 0, False, 50, 2))

			for i in range(0, 2):
				rands = [randint(0, 360),randint(-90, 90)]
				parts.append(Part(rands[0], 0, 0, False, 12, 3 + i * 6))
				parts.append(Part(rands[0], 0, 0, False, 12, 4 + i * 6))
				parts.append(Part(rands[0], 0, 0, False, 12, 5 + i * 6))
				parts.append(Part(rands[0] + rands[1], 0, 0, False, 12, 6 + i * 6))
				parts.append(Part(rands[0] + rands[1], 0, 0, False, 12, 7 + i * 6))
				parts.append(Part(rands[0] + rands[1], 0, 0, False, 12, 8 + i * 6))

			parts[0].loadImage("image_resources/body.png")
			parts[1].loadImage("image_resources/body.png")
			parts[2].loadImage("image_resources/head.png")
			# Body parts and heads weight
			parts[0].setWeight(23.44)
			parts[1].setWeight(11.72)
			parts[2].setWeight(8.24)

			for j in range(3, 15):
				# Load the image files and set the constraints
				parts[j].loadImage("image_resources/leg.png")
				parts[j].setWeight(0.66)
			for j in range(9, 15):
				# Load the image files and set the constraints
				#parts[j].loadImage("image_resources/leg_yellow.png")
				parts[j].loadImage("image_resources/leg.png")
		self.parts = parts

		self.legcounter = 0

	def load_pair(self, pair):
		self.pair = pair

	def duplicate(self):
		parts = self.parts
		pair = self.pair
		for i in range(0,15):
			parts[i].setPosition(self.pair.parts[i].getPosition())
			parts[i].setConstraint(self.pair.parts[i].getConstraint())
			parts[i].setRotation(self.pair.parts[i].getRotation(), False)
			if not self.backup:
				parts[i].rotation(0, False)

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




	def getParts(self):
		return self.parts


	# Draw all the images
	def run(self, DS):
		parts = self.parts
		for i in range(9,15):
			DS.blit(parts[i].getImage(), parts[i].getPosition())
		for i in range(0,9):
			DS.blit(parts[i].getImage(), parts[i].getPosition())



	# Calculate the agents center of gravity
	def centerOfGravity(self, pivot):
		parts = self.parts
		cog = (0,0)
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
			cog = (cog[0] + (centers[i][0] * parts[i].getWeight()), cog[1] + (centers[i][1] * parts[i].getWeight()))
			weight += parts[i].getWeight()
		# Divide by the total weight of the agent
		cog = (cog[0] / weight, cog[1] / weight)
		return cog


	# Set the constraints of each part
	def setConstraints(self):
		parts = self.parts
		parts[0].setConstraint(parts[1].getRotation())
		parts[1].setConstraint(parts[0].getRotation())
		parts[2].setConstraint(parts[1].getRotation())
		for i in range(0,2):
			offset = i * 6
			parts[3 + offset].setConstraint(-1)
			parts[4 + offset].setConstraint(-1)
			parts[5 + offset].setConstraint(-1)
			parts[6 + offset].setConstraint(parts[3 + offset].getRotation())
			parts[7 + offset].setConstraint(parts[4 + offset].getRotation())
			parts[8 + offset].setConstraint(parts[5 + offset].getRotation())


	# Rotate entire agent
	def rotateAll(self, amount):
		for iterate in range(0,15):
			self.parts[iterate].rotation(amount, True)

	# When the agent pushes off with a leg the rest of its body should follow
	def interactiveMove(self, part_num, direction_top, direction_bottom, cog, colliding):
		parts = self.parts
		initialPos = parts[part_num].getPivot()
		distance = (initialPos[0] - colliding[0][0], initialPos[1] - colliding[0][1])
		hypD = math.sqrt(distance[0] * distance[0] + distance[1] * distance[1])

		rotation = (math.atan(distance[0] / distance[1]) * 180.0 / math.pi) - direction_top
		newPos = (hypD * math.sin(rotation * math.pi / 180.0), hypD * math.cos(rotation * math.pi / 180.0))
		if distance[1] > 0:
			newPos = (-newPos[0], -newPos[1])
		newPos = (newPos[0] + distance[0], newPos[1] + distance[1] - 1.0)


		parts[part_num].rotation(direction_top, False)
		parts[part_num + 3].rotation(direction_bottom, False)

		pivot = parts[0].getPosition()
		self.setPositions(pivot)

		return newPos


	def inputs(self, pivot, turn, sensors, target):
		parts = self.parts

		netInputs = []
		netInputs.append(((180 + parts[0].getRotation()) % 360) / 360.0)
		secondRotation = (parts[1].getRotation() - parts[0].getRotation() + 90) % 181
		thirdRotation = (parts[2].getRotation() - parts[1].getRotation() + 90) % 181



		netInputs.append(secondRotation / 180.0)
		netInputs.append(thirdRotation / 180.0)

		greenRotation = parts[3].getRotation()
		netInputs.append(greenRotation / 360.0)
		greenRotation = (greenRotation - parts[6].getRotation() + 90) % 181
		netInputs.append(greenRotation / 180.0)



		yellowRotation = parts[9].getRotation()
		netInputs.append(yellowRotation / 360.0)
		yellowRotation = (yellowRotation - parts[12].getRotation() + 90) % 181
		netInputs.append(yellowRotation / 180.0)

		netInputs.append(sensors[0])
		netInputs.append(sensors[1])
		
		if target:
			netInputs.append(1)
		else:
			netInputs.append(0)


		for j in range(7):
			if j == turn:
				netInputs.append(1)
			else:
				netInputs.append(0)
		return netInputs

	def training_move_body(self, inputs):
		parts = self.parts
		move = 1


		# Fix climb over other agent
		# fix collisions

		if inputs[13] == 1:
			if inputs[7] < 0.05 and inputs[8] < 0.05:
				difference = (inputs[0] - inputs[1]) % 1
				if difference > 0.003 and difference < 0.5:
					move = 0
				elif difference > 0.5:
					move = 2
			else:
				if inputs[5] < 0.3 and inputs[3] <= 0.3:
					if (inputs[0] < 0.12 or inputs[0] > 0.75):
						move = 2
					elif inputs[0] > 0.15:
						move = 0
		elif inputs[14] == 1:
			if (inputs[7] >= 0.6 or inputs[8] >= 0.6) and inputs[0] > 0.12 and inputs[0] < 0.15 and inputs[16] == 1:
				if inputs[1] > 0.5:
					move = 2
				elif inputs[1] > 0.03:
					move = 0
			elif inputs[16] == 0 and (inputs[7] > 0.1 or inputs[8] > 0.1):
				difference = (inputs[0] - inputs[1] + 0.12) % 1
				if inputs[8] == 0 and inputs[7] > 0.75:
					difference = (inputs[0] - inputs[1] - 0.05) % 1
				if difference > 0.003 and difference < 0.5:
					move = 2
				elif difference > 0.5:
					move = 0
		elif inputs[15] == 1:
			if inputs[7] == 0 and inputs[8] == 0:
				difference = (inputs[2] - inputs[1]) % 1
				if difference > 0.003 and difference < 0.5:
					move = 0
				elif difference > 0.5:
					move = 2
			if (inputs[7] >= 0.6 or inputs[8] >= 0.6) and inputs[16] == 1:
				difference = (inputs[2] - inputs[1]) % 1
				if difference > 0.75 or difference < 0.5:
					move = 0
		return move

	def training_move_leg(self, inputs):
		move = 1
		decide = (inputs[3] - inputs[5] - 0.5) % 1
		if inputs[9] == 1:


			if (inputs[7] > 0 or inputs[8] > 0) and inputs[16] == 0:
				move = 0
			elif (inputs[7] < 0.5 and inputs[8] < 0.5):
				difference = ((inputs[0] - inputs[1]) % 1) + ((inputs[2] - inputs[1]) % 1)
				if difference < 0.012 and decide < 0.5 :
					move = 0
			elif ((inputs[7] >= 0.5 and inputs[7] < 0.6) or (inputs[8] >= 0.5 and inputs[8] < 0.6)) and inputs[0] > 0.12 and inputs[0] < 0.15 and inputs[16] == 1:
				move = 0
			else:
				if inputs[16] == 0:
					difference = ((inputs[0] - inputs[1] + 0.1) % 1) + ((inputs[2] - inputs[1]) % 1)
					if difference < 0.012 and decide < 0.5:
						move = 0
				elif inputs[3] > 0.25:
					move = 0

		elif inputs[10] == 1:
			if (inputs[7] < 0.5 and inputs[8] < 0.5) or inputs[16] == 0 and inputs[4] < 1:
				move = 0
		elif inputs[11] == 1:
			if (inputs[7] > 0 or inputs[8] > 0) and inputs[16] == 0:
				move = 0
			elif (inputs[7] < 0.5 and inputs[8] < 0.5):
				difference = ((inputs[0] - inputs[1]) % 1) + ((inputs[2] - inputs[1]) % 1)
				if difference < 0.012 and (decide < 0.003 or decide >= 0.5):
					move = 0
			elif ((inputs[7] >= 0.5 and inputs[7] < 0.6) or (inputs[8] >= 0.5 and inputs[8] < 0.6)) and inputs[0] > 0.12 and inputs[0] < 0.15 and inputs[16] == 1:
				move = 0
			else:
				if inputs[16] == 0:
					difference = ((inputs[0] - inputs[1] + 0.1) % 1) + ((inputs[2] - inputs[1]) % 1)
					if difference < 0.012 and decide < 0.5:
						move = 0
				elif inputs[5] > 0.25:
					move = 0
		elif inputs[12] == 1:
			if (inputs[7] < 0.5 and inputs[8] < 0.5) or inputs[16] == 0 and inputs[4] < 1:
				move = 0
		return move

