import math, random, sys, pygame
from pygame.locals import *

# Object within the world the agent may collide with
class Button():


	# Initialise an object
	def __init__(self, parent_position, position, dimensions, image, mc=False):
		# If true then the button does not change sprite
		self.static = True
		# Can be pressed even when on
		self.multi_click = mc
		# Position and dimensions
		self.position = (parent_position[0] + position[0], parent_position[1] + position[1])
		self.width = dimensions[0]
		self.height = dimensions[1]
		# Load button sprite
		self.off = True
		self.load_image(image)
		self.deselect = []

	# Load buttons sprite
	def load_image(self, image):
		self.image = pygame.image.load(image).convert_alpha()

	# Load buttons second sprite. Used for visual feedback when pressed
	def load_second_image(self, image):
		self.second_image = pygame.image.load(image).convert_alpha()
		self.static = False

	# Draw buttons sprite
	def run(self, canvas):
		if self.off:
			canvas.blit(self.image, self.position)
		else:
			canvas.blit(self.second_image, self.position)

	# Move button
	def move(self, amount):
		self.position = (self.position[0] + amount, self.position[1])


	# Checks if they button was pressed
	def check_press(self, press):
		# If the button is off or can be pressed when on
		if self.off or len(self.deselect) == 0 or self.multi_click:
			# if the position of the mouse click aligns with the buttons placement
			if press[0] > self.position[0] and press[0] < (self.position[0] + self.width):
				if press[1] > self.position[1] and press[1] < (self.position[1] + self.height):
					# When pressed turn on the button and turn off all adjoining radio buttons
					if not self.static and self.off:
						self.off = False
						for j in range(len(self.deselect)):
							self.deselect[j].off = True
					# Return true if the button was pressed
					return True
		return False

	# Add adjoining radio buttons. If this button turns on
	# the other buttons turn off automatically
	def radio_buttons(self, button):
		self.deselect.append(button)