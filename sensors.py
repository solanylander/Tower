import math, random, sys, pygame
from pygame.locals import *
from objects import Object

# Stores an agents sensors
class Sensors:

	# Initialise both sensors
	def __init__(self):
		self.sensor_array = []
		self.sensor_values = [0,0]
		# Can the sensor can see the target?
		self.target = False

		for i in range(0,2):
			self.sensor_array.append(Object(0, (0,0)))
			self.sensor_array[i].loadImage("image_resources/sensor.png")


	# Sets the position of both sensors
	def setPositions(self, back, head):
		# Set the x co-ordinate of both sensors to the greater of the 2
		front = head[0]
		if head[0] < back[0]:
			front = back[0]

		# Set the position of both sensors
		self.sensor_array[0].position = (front, back[1])
		self.sensor_array[1].position = (front, head[1])



	# Update the sensors information
	def collisions(self, environment, objective):
		# Reset sensor values
		self.target = False
		self.sensor_values = [0,0]

		# Check to see if either sensor can see any of the objects within the environment
		# Including other agents
		for i in range(len(environment)):

			mask = environment[i][0]
			part_pos = (environment[i][1], environment[i][2])
			# Check for each sensor
			for j in range(2):
				self.collisionCheck(part_pos, mask, j)

		# Check to see if the sensor can see the agents target. If it can set target to True and update sensor values
		for k in range(2):
			if not self.target:
				self.target = self.collisionCheck(objective.position, objective.mask, k)




	# Check if a sensor is colliding with an object
	def collisionCheck(self, position, mask, sensor):
		# Get the position of the sensor
		sensor = self.sensor_array[sensor]
		# Find the distance between a sensors position and the object
		x = int(position[0] - sensor.position[0])
		y = int(position[1] - sensor.position[1])
		offset = (x,y)

		# Find amount of overlap between sensor and the object
		result = sensor.mask.overlap(mask, offset)
		if result:
			# If the new object is closer than all previous objects update the values
			if result[0] >= self.sensor_values[sensor]:
				# The closer the sensor is the greater the value ranging between 0 and 1
				self.sensor_values[sensor] = 1 - ((result[0] + 1) / 70)
				return True
		return False


	# Draw the sensor images
	def run(self, DS):
		for i in range(0,2):
			DS.blit(self.sensor_array[i].image, self.sensor_array[i].position)