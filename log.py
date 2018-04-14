import math, random, sys, pygame
from pygame.locals import *
from tab import Tab
from button import Button

# Object within the world the agent may collide with
class Log(Tab):


	# Initialise an object
	def __init__(self, tab_option, font):
		Tab.__init__(self, tab_option)
		self.buildLog()
		self.history = []
		self.history.append("Program Started Successfully")
		self.tracker = 0
		self.font = font


	def click(self, press):
		for i in range(len(self.log_scroll)):
			pressed = self.log_scroll[i].checkPress(press)
			if pressed:
				if i == 0:
					self.tracker -= 1
					if self.tracker < 0:
						self.tracker = 0
				else:
					self.tracker += 1
					if self.tracker > len(self.history) - 12:
						self.tracker = len(self.history) - 12

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

	def writeLog(self, DS):
		if len(self.history) < 12:
			for i in range(len(self.history)):

				log = self.font.render(self.history[i], False, (0, 0, 0))
				DS.blit(log,(self.position[0] + 10,self.position[1] + 30 + (12 * (i + 1))))
		else:
			counter = 1
			for i in range(self.tracker, self.tracker + 12):
				log = self.font.render(self.history[i], False, (0, 0, 0))
				DS.blit(log,(self.position[0] + 10,self.position[1] + 30 + (12 * counter)))
				counter += 1

	def writeMessage(self, message):
		self.history.append(message)
		self.tracker = len(self.history) - 12
		if self.tracker < 0:
			self.tracker = 0

	def buildLog(self):
		self.loadImage("image_resources/log.png")
		self.position = (1060,300)
		self.initial_position = (860,300)
		self.log_scroll.append(Button(self.position, (170, 40), (20,30), "image_resources/up.png"))
		self.log_scroll.append(Button(self.position, (170, 160), (20,30), "image_resources/down.png"))

		self.width = 200
		self.hide_left = False
		self.hidden = True
		self.hiding = False
		self.showing = False

		self.open = Button(self.position, (-40, 80), (30,39), "image_resources/left.png")
		self.open.loadSecondImage("image_resources/right.png")

