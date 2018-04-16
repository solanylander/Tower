import math, random, sys, pygame
from pygame.locals import *
from objects import Object

# Individual Ant part (leg, torso, head)
class Part(Object):

	# Initialise a body part
	def __init__(self, rotation, radius, weight=0, position=(0,0)):
		Object.__init__(self, rotation, position)
		# Set parts radius and weight
		self.radius = radius
		self.weight = weight

	# Return the images pivot
	def get_pivot(self):
		# Since all images are square this is half it's width + the position
		pivot = (self.position[0] + self.radius, self.position[1] + self.radius)
		return pivot
		
	# Get parts constraint 
	def get_constraint(self):
		return self.constraint

	# Set parts constraint
	def set_constraint(self, constraint):
		self.constraint = constraint

	# Set parts weight
	def set_weight(self, weight):
		self.weight = weight

	# Get parts weight 
	def get_weight(self):
		return self.weight


	# Rotate the body part by the value of amount with consideration to the body parts constraints
	def rotate(self, amount, ignore=False):

		# Current rotation + the amount the part is being rotated by
		r = (self.rotation + amount) % 360.0
		# -1 implies the part has no constraint
		# if ignore then skip constraint check
		if self.constraint > -1 and not ignore:
			# Distance the part is from the centre of the allowed area
			distance_from = (self.constraint - r) % 360
			# If the part is outside the allowed area set it to the closest constraint
			if distance_from > 90 and distance_from < 180:
				r = (self.constraint - 90) % 360
			elif distance_from > 180 and distance_from < 270:
				r = (self.constraint + 90) % 360

		amount = (r - self.rotation) % 360
		if amount > 180:
			amount -= 360
		# Rotate the and get the image mask
		self.rotation = r;