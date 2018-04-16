import math, random, sys, pygame
from pygame.locals import *

# Superclass for all objects within the environment (Agent parts, sensors and environmental objects)
class Object:

	# Initialise an object
	def __init__(self, rotation, xy):
		self.rotation = rotation
		self.position = (xy[0], xy[1])
		self.loaded_image = False

	# Rotate image (Only works for square images)
	def rot_image(self, image, angle):
		rect = image.get_rect()
		rotated_image = pygame.transform.rotate(image, angle)
		rect.center = rotated_image.get_rect().center
		self.image = rotated_image.subsurface(rect).copy()
		self.mask = pygame.mask.from_surface(self.image)

	# Load an objects image and save it
	def load_image(self, image):
		# Image unrotated. Saves the program having to repeated call the file the image is saved in
		self.image_load = pygame.image.load(image).convert_alpha()
		# Rotate the image and take its mask (Used to calculate collisions)
		self.rot_image(self.image_load, self.rotation)
		self.mask = pygame.mask.from_surface(self.image)
		self.loaded_image = True

	# Get objects position
	def get_position(self):
		return self.position

	# set objects position
	def set_position(self, position):
		self.position = position

	# Rotate the object by the value of amount
	def set_rotation(self, amount):
		# Rotate the and get the image mask
		self.rotation = amount % 360
		if self.loaded_image:
			self.rot_image(self.image_load, self.rotation)
			self.mask = pygame.mask.from_surface(self.image)

	# Get the objects rotation
	def get_rotation(self):
		return self.rotation

	# Get the objects image rotated
	def get_image(self):
		return self.image

	# Get the objects mask
	def get_mask(self):
		return self.mask

	# Move object
	def move(self, xy):
		self.position = (self.position[0] + xy[0], self.position[1] + xy[1])

	# Rotate an object by the value of amount
	def rotate(self, amount):
		self.rotation = (self.rotation + amount) % 360
		self.rot_image(self.image_load, self.rotation)