import math, random, sys, pygame
from pygame.locals import *

# Object within the world the agent may collide with
class Button():


	# Initialise an object
	def __init__(self, parent_position, position, dimensions, image, mc=False):
		self.static = True
		self.multi_click = mc
		self.position = (parent_position[0] + position[0], parent_position[1] + position[1])
		self.width = dimensions[0]
		self.height = dimensions[1]
		self.initial_image = True
		self.loadImage(image)
		self.deselect = []

	# Rotate the object by the value of amount
	def loadImage(self, image):
		self.image = pygame.image.load(image).convert_alpha()

	# Rotate the object by the value of amount
	def loadSecondImage(self, image):
		self.second_image = pygame.image.load(image).convert_alpha()
		self.static = False

	def run(self, DS):
		if self.initial_image:
			DS.blit(self.image, self.position)
		else:
			DS.blit(self.second_image, self.position)

	def move(self, amount):
		self.position = (self.position[0] + amount, self.position[1])


	def checkPress(self, press):
		if self.initial_image or len(self.deselect) == 0 or self.multi_click:
			if press[0] > self.position[0] and press[0] < (self.position[0] + self.width):
				if press[1] > self.position[1] and press[1] < (self.position[1] + self.height):
					if not self.static and self.initial_image:
						self.initial_image = not self.initial_image
						for j in range(len(self.deselect)):
							self.deselect[j].initial_image = True
					return True
		return False

	def radioButtons(self, button):
		self.deselect.append(button)