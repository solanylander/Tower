import math, random, sys, pygame
from pygame.locals import *

# Object within the world the agent may collide with
class Block:

	# Rotate image (Only works for square images)
	def rotImage(self, image, angle):
	    rect = image.get_rect()
	    rotatedImage = pygame.transform.rotate(image, angle)
	    rect.center = rotatedImage.get_rect().center
	    rotatedImage = rotatedImage.subsurface(rect).copy()
	    return rotatedImage

	# Initialise an object
	def __init__(self, rotate, x, y):
		self.rotate = rotate
		self.position = (x, y)

	# Load an objects image and save it
	def loadImage(self, image):
		# Image unrotated. Saves the program having to repeated call the file the image is saved in
		self.imageLoad = pygame.image.load(image).convert_alpha()
		# Rotate the image and take its mask (Used to calculate collisions)
		self.image = self.rotImage(self.imageLoad, self.rotate)
		self.mask = pygame.mask.from_surface(self.image)

	# Get objects position
	def getPosition(self):
		return self.position

	# Rotate the object by the value of amount
	def rotation(self, amount):
		# Rotate the and get the image mask
		self.rotate = r;
		self.image = self.rotImage(self.imageLoad, self.rotate)
		self.mask = pygame.mask.from_surface(self.image)

	# Get the objects rotation
	def getRotation(self):
		return self.rotate

	# Get the objects image rotated
	def getImage(self):
		return self.image

	# Get the objects mask
	def getMask(self):
		return self.mask
