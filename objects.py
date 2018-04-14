import math, random, sys, pygame
from pygame.locals import *

# Superclass for all objects within the environment (Agent parts, sensors and blocks)
class Object:

	# Initialise an object
	def __init__(self, rotation, xy):
		self.rotation = rotation
		self.position = (xy[0], xy[1])
		self.loaded_image = False

	# Rotate image (Only works for square images)
	def rotImage(self, image, angle):
		rect = image.get_rect()
		rotated_image = pygame.transform.rotate(image, angle)
		rect.center = rotated_image.get_rect().center
		self.image = rotated_image.subsurface(rect).copy()
		self.mask = pygame.mask.from_surface(self.image)

	# Load an objects image and save it
	def loadImage(self, image):
		# Image unrotated. Saves the program having to repeated call the file the image is saved in
		self.image_load = pygame.image.load(image).convert_alpha()
		# Rotate the image and take its mask (Used to calculate collisions)
		self.rotImage(self.image_load, self.rotation)
		self.mask = pygame.mask.from_surface(self.image)
		self.loaded_image = True

	# Get objects position
	def getPosition(self):
		return self.position

	# set objects position
	def setPosition(self, position):
		self.position = position

	# Rotate the object by the value of amount
	def setRotation(self, amount):
		# Rotate the and get the image mask
		self.rotation = amount % 360
		if self.loaded_image:
			self.rotImage(self.image_load, self.rotation)
			self.mask = pygame.mask.from_surface(self.image)

	# Get the objects rotation
	def getRotation(self):
		return self.rotation

	# Get the objects image rotated
	def getImage(self):
		return self.image

	# Get the objects mask
	def getMask(self):
		return self.mask

	# Move object
	def move(self, xy):
		self.position = (self.position[0] + xy[0], self.position[1] + xy[1])