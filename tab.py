import math, random, sys, pygame
from pygame.locals import *
from button import Button

# Object within the world the agent may collide with
class Tab():


	# Initialise an object
	def __init__(self, tab_option):
		self.unclickable = []
		self.world_building = []
		self.agent_modifiers = []
		self.spawn_object = []
		self.network_modifiers = []
		self.log_scroll = []
		self.feedback = []
		if tab_option > 1:
			self.build_tab(tab_option)

	# Initialize tab
	def build_tab(self, tab_option):
		# Load image
		self.load_image("image_resources/controls.png")
		# Initialize variables
		self.position = (1060,65)
		self.initial_position = (860,65)

		self.width = 200
		self.hide_left = False
		self.hidden = True
		self.left = False
		self.right = False
		# Initialize buttons
		self.open = Button(self.position, (-40, 80), (30,39), "image_resources/left.png")
		self.open.load_second_image("image_resources/right.png")

	# Load tab sprite
	def load_image(self, image):
		self.image = pygame.image.load(image).convert_alpha()

	# Check if the tab is moving on screen
	def move(self):
		# If currently hiding or revealing move left or right
		amount = 0
		if self.right:
			amount = 5
		elif self.left:
			amount = -5
		if not self.hide_left:
			amount = -amount
		if not (amount == 0):
			# Move sprite along with all buttons attached to tab
			self.position = (self.position[0] + amount, self.position[1])
			for i in range(len(self.unclickable)):
				self.unclickable[i].move(amount)
			for i in range(len(self.world_building)):
				self.world_building[i].move(amount)
			for i in range(len(self.agent_modifiers)):
				self.agent_modifiers[i].move(amount)
			for i in range(len(self.network_modifiers)):
				self.network_modifiers[i].move(amount)
			for i in range(len(self.spawn_object)):
				self.spawn_object[i].move(amount)
			for i in range(len(self.log_scroll)):
				self.log_scroll[i].move(amount)
			for i in range(len(self.feedback)):
				self.feedback[i].move(amount)
			self.open.move(amount)

			# Once it reaches the desired position stop moving
			if self.hide_left:
				if self.position[0] >= (self.width + self.initial_position[0]):
					self.right = False
					self.hidden = True
				if self.position[0] <= self.initial_position[0]:
					self.left = False
					self.hidden = False
			else:
				if self.position[0] <= (self.initial_position[0]):
					self.right = False
					self.hidden = False
				if self.position[0] >= self.width + self.initial_position[0]:
					self.left = False
					self.hidden = True

	# Draw all sprites including buttons
	def run(self, canvas):
		canvas.blit(self.image, self.position)
		for i in range(len(self.unclickable)):
			self.unclickable[i].run(canvas)
		for i in range(len(self.world_building)):
			self.world_building[i].run(canvas)
		for i in range(len(self.agent_modifiers)):
			self.agent_modifiers[i].run(canvas)
		for i in range(len(self.spawn_object)):
			self.spawn_object[i].run(canvas)
		for i in range(len(self.network_modifiers)):
			self.network_modifiers[i].run(canvas)
		for i in range(len(self.log_scroll)):
			self.log_scroll[i].run(canvas)
		for i in range(len(self.feedback)):
			self.feedback[i].run(canvas)
		self.open.run(canvas)

	# Check which button was pressed. Take the appropriate action
	def click(self, press):
		if self.open.check_press(press):
			self.toggle_seen()

	# Hide/Show tab
	def toggle_seen(self):
		# If user tells tab to move left move left
		if self.position[0] >= (self.width + self.initial_position[0]):
			if self.hide_left:
				self.left = True
			else:
				self.right = True
		# If user tells tab to move right move right
		if self.position[0] <= self.initial_position[0]:
			if self.hide_left:
				self.right = True
			else:
				self.left = True