import math, random, sys, pygame
from pygame.locals import *

# Object within the world the agent may collide with
class Sensor:

	# Initialise an object
	def __init__(self):
		self.image = pygame.image.load("image_resources/sensor.png").convert_alpha()
		self.mask = pygame.mask.from_surface(self.image)
		self.step = 0

	# Get objects position
	def getPosition(self, top):
		if top:
			return self.position_top
		else:
			return self.position_bottom

	# Set objects position
	def setPositions(self, top, bottom):
		front = top[0]
		if bottom[0] > top[0]:
			front = bottom[0]
		if bottom[1] > top[1]:
			self.position_bottom = (front, top[1])
			self.position_top = (front, bottom[1])
		else:
			self.position_top = (front, top[1])
			self.position_bottom = (front, bottom[1])

	def moveSensor(self, top, xy):
		if top:
			self.position_top = (self.position_top[0] + xy[0], self.position_top[1] + xy[0])
		else:
			self.position_bottom = (self.position_bottom[0] + xy[0], self.position_bottom[1] + xy[0])

	# Get the objects image rotated
	def getImage(self):
		return self.image

	# Get the objects mask
	def getMask(self):
		return self.mask

	def collisionCheck(self, position, mask):
		amount_one, amount_two = 0.0, 0.0
		x = int(self.position_top[0] - position[0])
		offset = (-x, -int(self.position_top[1] - position[1]))
		result = self.mask.overlap(mask, offset)
		if result:
			amount_one = 1 - ((result[0] + 1) / 70)
		else:
			amount_one = 0

		offset = (-x, -int(self.position_bottom[1] - position[1]))
		result = self.mask.overlap(mask, offset)
		if result:
			amount_two = 1 - ((result[0] + 1) / 70)
		else:
			amount_two = 0
		return (amount_one, amount_two)