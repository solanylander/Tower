import math, random, sys, pygame
from pygame.locals import *
from tab import Tab
from button import Button


MESSAGE_DISPLAY_NUM = 10

# Object within the world the agent may collide with
class Log(Tab):

	# Number of messages displayed

	# Initialise Output Log
	def __init__(self, tab_option, font, parent):
		Tab.__init__(self, tab_option)
		self.build_log()
		# Logs history
		self.history = []
		self.history.append("Program Started Successfully")
		self.parent = parent
		self.tracker = 0
		# Set font
		self.font = font
		# Automatically open when a message is sent to the log
		self.auto = True 

	# On click check if a button was pressed
	def click(self, press):
		# Scroll through log messages
		for i in range(len(self.log_scroll)):
			if self.log_scroll[i].check_press(press):
				if i == 0:
					self.tracker -= 1
					if self.tracker < 0:
						self.tracker = 0
				elif i == 1:
					self.tracker += 1
					if self.tracker > len(self.history) - MESSAGE_DISPLAY_NUM:
						self.tracker = len(self.history) - MESSAGE_DISPLAY_NUM
				elif i == 2:
					self.auto = not self.auto
					if not self.auto:
						self.log_scroll[2].off = True
				else:
					self.parent.extra = not self.parent.extra
					if not self.parent.extra:
						self.log_scroll[3].off = True

		# If the user wants to show / hide the log tab do so
		if self.open.check_press(press):
			self.toggle_seen()

	# Write the current log to screen
	def write_log(self, canvas):
		# If there are less thab MESSAGE_DISPLAY_NUM entries show them all
		if len(self.history) < MESSAGE_DISPLAY_NUM:
			for i in range(len(self.history)):

				log = self.font.render(self.history[i], False, (0, 0, 0))
				canvas.blit(log,(self.position[0] + 10,self.position[1] + 30 + (12 * (i + 1))))
		# Otherwise display 10 messages. User can scroll through them
		else:
			counter = 1
			for i in range(self.tracker, self.tracker + MESSAGE_DISPLAY_NUM):
				log = self.font.render(self.history[i], False, (0, 0, 0))
				canvas.blit(log,(self.position[0] + 10,self.position[1] + 30 + (12 * counter)))
				counter += 1

	# Add a message to the log
	def write_message(self, message):
		self.history.append(message)
		self.tracker = len(self.history) - MESSAGE_DISPLAY_NUM
		if self.tracker < 0:
			self.tracker = 0
		# If auto open display log tab
		if self.auto and self.hidden == True:
			self.toggle_seen()
			self.hidden = False
			self.open.off = False



	# Draw all sprites including buttons
	def run(self, canvas):
		canvas.blit(self.image, self.position)
		for i in range(len(self.unclickable)):
			self.unclickable[i].run(canvas)
		# Update Log
		self.write_log(canvas)
		for i in range(len(self.log_scroll)):
			self.log_scroll[i].run(canvas)
		self.open.run(canvas)


	# Build log tab
	def build_log(self):
		# Load image
		self.load_image("image_resources/log.png")
		# Initialize variables
		self.position = (1060,300)
		self.initial_position = (860,300)
		self.width = 200
		self.hide_left = False
		self.hidden = True
		self.left = False
		self.right = False

		# Log buttons
		self.log_scroll.append(Button(self.position, (170, 40), (20,30), "image_resources/up.png"))
		self.log_scroll.append(Button(self.position, (170, 160), (20,30), "image_resources/down.png"))
		self.log_scroll.append(Button(self.position, (10, 166), (57,27), "image_resources/auto.png"))
		self.log_scroll[2].load_second_image("image_resources/auto_green.png")
		self.log_scroll.append(Button(self.position, (70, 166), (57,27), "image_resources/extra.png"))
		self.log_scroll[3].load_second_image("image_resources/extra_green.png")
		# Auto open is initially open
		self.log_scroll[2].off = False

		# Show/Hide tab button
		self.open = Button(self.position, (-40, 80), (30,39), "image_resources/left.png")
		self.open.load_second_image("image_resources/right.png")

