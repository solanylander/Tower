import math, random, sys, pygame
from pygame.locals import *
from objects import Object

# Object within the world the agent may collide with
class Block(Object):


	# Initialise an object
	def __init__(self, rotation, xy):
		Object.__init__(self, rotation, xy)


	# Rotate the object by the value of amount
	def rotate(self, amount):
		# Rotate the block and get the new image mask
		self.rotation = (self.rotation + amount) % 360
		self.rotImage(self.image_load, self.rotation)
