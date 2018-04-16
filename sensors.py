import math, random, sys, pygame
from pygame.locals import *
from objects import Object

# Stores an agents sensors
class Sensors:

	# Initialise all sensors
	def __init__(self):
		self.sensor_array = []
		self.sensor_values = [0,0]
		# Has the sensor can seen the target?
		self.target = False

		# Forward facing sensory inputs.
		for i in range(0,2):
			self.sensor_array.append(Object(0, (0,0)))
			self.sensor_array[i].load_image("image_resources/sensor.png")
		# Upward facing sensor
		self.sensor_array.append(Object(0, (0,0)))
		self.sensor_array[2].load_image("image_resources/sensor_two.png")


	# Sets the position of both sensors
	def set_positions(self, back, head):
		# Set the x co-ordinate of both forward sensors to be inline
		front = head[0]
		if head[0] < back[0]:
			front = back[0]

		# Set the position of all sensors
		self.sensor_array[0].position = (front, back[1])
		self.sensor_array[1].position = (front, head[1] - 15)
		self.sensor_array[2].position = (front + 10, head[1] - 70)



	# Update the sensors information
	def collisions(self, environment, objective):
		# Reset sensor values
		self.sensor_values = [0,0]

		# Check to see if either sensor can see any of the objects within the environment
		# Including other agents
		for i in range(len(environment)):

			mask = environment[i][0]
			part_pos = (environment[i][1], environment[i][2])
			# Check for each sensor
			for j in range(2):
				self.collision_check(part_pos, mask, j)

			if self.collision_check(part_pos, mask, 2):
				self.target = True




	# Check if a sensor is colliding with an object
	def collision_check(self, position, mask, sensor_num):
		# Get the position of the sensor
		sensor = self.sensor_array[sensor_num]
		# Find the distance between a sensors position and the object
		x = int(position[0] - sensor.position[0])
		y = int(position[1] - sensor.position[1])
		offset = (x,y)

		# Find amount of overlap between sensor and the object
		result = sensor.mask.overlap(mask, offset)
		if result:
			if sensor_num == 2:
				return True
			value = 1 - ((result[0] + 1) / 70)
			# If the new object is closer than all previous objects update the values
			if value >= self.sensor_values[sensor_num]:
				# The closer the sensor is the greater the value ranging between 0 and 1
				self.sensor_values[sensor_num] = value
				return True
		return False


	# Draw the sensor images
	def run(self, DS):
		for i in range(0,3):
			DS.blit(self.sensor_array[i].image, self.sensor_array[i].position)