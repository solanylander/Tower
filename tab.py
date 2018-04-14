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
		if tab_option > 1:
			self.buildTab(tab_option)

	# Rotate the object by the value of amount
	def loadImage(self, image):
		self.image = pygame.image.load(image).convert_alpha()

	def hideShow(self):
		amount = 0
		if self.showing:
			amount = 5
		elif self.hiding:
			amount = -5
		if not self.hide_left:
			amount = -amount
		if not (amount == 0):
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
			self.open.move(amount)
			if self.hide_left:
				if self.position[0] >= (self.width + self.initial_position[0]):
					self.showing = False
				if self.position[0] <= self.initial_position[0]:
					self.hiding = False
			else:
				if self.position[0] <= (self.initial_position[0]):
					self.showing = False
				if self.position[0] >= self.width + self.initial_position[0]:
					self.hiding = False

	def run(self, DS):
		DS.blit(self.image, self.position)
		for i in range(len(self.unclickable)):
			self.unclickable[i].run(DS)
		for i in range(len(self.world_building)):
			self.world_building[i].run(DS)
		for i in range(len(self.agent_modifiers)):
			self.agent_modifiers[i].run(DS)
		for i in range(len(self.spawn_object)):
			self.spawn_object[i].run(DS)
		for i in range(len(self.network_modifiers)):
			self.network_modifiers[i].run(DS)
		for i in range(len(self.log_scroll)):
			self.log_scroll[i].run(DS)
		self.open.run(DS)

	def click(self, press):
		if self.open.checkPress(press):
			if self.position[0] >= (self.width + self.initial_position[0]):
				if self.hide_left:
					self.hiding = True
				else:
					self.showing = True
			if self.position[0] <= self.initial_position[0]:
				if self.hide_left:
					self.showing = True
				else:
					self.hiding = True

	def buildTab(self, tab_option):
		self.loadImage("image_resources/controls.png")
		self.position = (1060,65)
		self.initial_position = (860,65)

		self.width = 200
		self.hide_left = False
		self.hidden = True
		self.hiding = False
		self.showing = False

		self.open = Button(self.position, (-40, 80), (30,39), "image_resources/left.png")
		self.open.loadSecondImage("image_resources/right.png")