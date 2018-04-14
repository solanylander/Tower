import math, random, sys, pygame, os, time, argparse
from pygame.locals import *
from agent import Agent
from part import Part
from block import Block
from network_collection import NetworkCollection
from tab import Tab
from options import Options
from log import Log
from random import *

class Main():

	def __init__(self):
		self.initializeVariables()
		self.generateWorld()
		# main loop
		while True:
			self.checkInputs()
			if self.running:
				if self.training:
					self.trainingMode()
				else:
					self.freeMode()

			if self.placing_object:
				self.pos = pygame.mouse.get_pos()
				self.unplaced.setPosition((self.pos[0] - 200, self.pos[1] - 200))
				self.unplaced.rotate(self.rotate_unplaced)
			self.moveTabs()

			self.drawSprites()

	def checkInputs(self):
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_RETURN:
					self.running = True
				elif event.key == K_q:
					self.resetWorld()
				elif event.key == K_o:	
					self.rotate_unplaced += 1
				elif event.key == K_p:	
					self.rotate_unplaced += -1
			elif event.type == KEYUP:
				if event.key == K_p:	
					self.rotate_unplaced += 1
				elif event.key == K_o:	
					self.rotate_unplaced += -1



			elif event.type == pygame.MOUSEBUTTONDOWN:
				self.pos = pygame.mouse.get_pos()
				if self.placing_object:
					self.placeObject()
				for i in range(3):
					self.tabs[i].click(self.pos)

	def drawSprites(self):
		# Draw world
		self.DS.fill(self.background)
		if self.draw_goal:
			self.DS.blit(self.goal.getImage(), self.goal.getPosition())
		self.DS.blit(self.floor.getImage(), self.floor.getPosition())
		if self.placing_object:
			self.DS.blit(self.unplaced.getImage(), self.unplaced.getPosition())
		for i in range(len(self.blocks)):
			self.DS.blit(self.blocks[i].getImage(), self.blocks[i].getPosition())
		if self.draw_scaleable:
			for i in range(len(self.scaleable_agents)):
				self.scaleable_agents[i].parts.run(self.DS)
		for i in range(len(self.agents)):
			self.agents[i].parts.run(self.DS)

		for i in range(3):
			self.tabs[i].run(self.DS)

		self.tabs[1].writeLog(self.DS)
		pygame.display.update()
		# Max FPS
		self.CLOCK.tick(120)

	def placeObject(self):
		if self.checkEnvironmentOverlap:
			self.blocks.append(self.unplaced)
		self.placing_object = False

	def checkEnvironmentOverlap(self, goal=False):
		checking = self.unplaced
		if goal:
			checking = self.goal
		for k in range(len(self.blocks) + 1):
			comparison = None
			if k == len(self.blocks):
				comparison = [self.floor.getPosition(), self.floor.getMask()]
			else:
				comparison = [self.blocks[k].getPosition(), self.blocks[k].getMask()]

			# Find the position difference between the agent part and the external object
			offset = (int(comparison[0][0] - checking.getPosition()[0]), int(comparison[0][1] - checking.getPosition()[1]))
			result = checking.getMask().overlap(comparison[1], offset)
			if result:
				return True, result[0]
		return False, False

	def generateWorld(self):
		self.blocks = []
		self.agents = []
		self.agent_num = 0
		while len(self.blocks) < 3:
			self.unplaced = Block(0, (randint(500,800), randint(0,200)))
			self.unplaced.loadImage("image_resources/"+self.block_images[randint(0,3)]+".png")
			self.unplaced.rotate(randint(0,180))
			if self.checkEnvironmentOverlap()[0]:
				self.blocks.append(self.unplaced)


	def moveTabs(self):
		for i in range(3):
			self.tabs[i].hideShow()

	def trainingMode(self):
		if len(self.agents) == 0:
			self.agents.append(Agent((290,200), -1, self.network_collection, 0, None, 25, True, self.randomness, (randint(0,80) < self.reference)))
			self.agents[self.agent_num].addObject((self.floor.getMask(), self.floor.getPosition()[0], self.floor.getPosition()[1]))
			for j in range(len(self.blocks)):
				self.agents[self.agent_num].addObject((self.blocks[j].getMask(), self.blocks[j].getPosition()[0], self.blocks[j].getPosition()[1]))
		agent = self.agents[self.agent_num]
		network_collection = self.network_collection

		agent.move()


		if agent.restart:
			if agent.won:
				self.won += 1
			else:
				self.lost += 1
			print("Won:", self.won, "Lost:", self.lost)
			comparator = 50000
			if network_collection.get_turn() < 2:
				comparator = 20000
			if network_collection.get_length() > comparator:

				network_collection.increment_turn()

				self.generateWorld()
				self.win_counter += (self.won/(self.won + self.lost))/4
				if network_collection.get_turn() == 0:
					self.draw_scaleable = False
					print("Episode Num:", self.episode_num)
					learn_rate = 0.1 - (self.win_counter * 0.099)
					network_collection.update_learn_rate(learn_rate)
					self.win_counter = 0
					network_collection.finish_episode()
					network_collection.save_checkpoint()
					self.episode_num += 1
					preset = False





					if self.continuous:
						self.agents = []
						if self.custom_build:
							self.agent_num = 0
						else:
							self.resetWorld()
							self.running = True
					else:
						self.resetWorld()



				elif network_collection.get_turn() == 3:
					self.blocks = []
				self.won = 0
				self.lost = 0
			else:
				print("Episode Finished:", network_collection.get_length())
			print("=================")



			self.agent_num = 0
			self.agents = []
			self.agents.append(Agent((290,200), -1, self.network_collection, 0, None, 25, True, self.randomness, (randint(0,80) < self.reference)))
			self.agents[self.agent_num].addObject((self.floor.getMask(), self.floor.getPosition()[0], self.floor.getPosition()[1]))
			for j in range(len(self.blocks)):
				self.agents[self.agent_num].addObject((self.blocks[j].getMask(), self.blocks[j].getPosition()[0], self.blocks[j].getPosition()[1]))

			if network_collection.get_turn() == 3:
				for j in range(len(self.scaleable_agents)):
					self.agents[self.agent_num].addOtherAgent(self.scaleable_agents[j])
				self.draw_scaleable = True










	def freeMode(self):
		if len(self.agents) == 0:
			self.setGoal()
			self.agents.append(Agent((390,200), -1, self.network_collection, 0, self.goal, 25, False, self.randomness, self.subsumption))
			for j in range(len(self.agents) - 1):
				self.agents[self.agent_num].addOtherAgent(self.agents[j])
			self.agents[self.agent_num].addObject((self.floor.getMask(), self.floor.getPosition()[0], self.floor.getPosition()[1]))
			for j in range(len(self.blocks)):
				self.agents[self.agent_num].addObject((self.blocks[j].getMask(), self.blocks[j].getPosition()[0], self.blocks[j].getPosition()[1]))

		self.agents[self.agent_num].move()
		if self.agents[self.agent_num].finished == 1:
			self.agent_num += 1
			self.agents.append(Agent((390,200), -1, self.network_collection, 0, self.goal, 25, False, self.randomness, self.subsumption))
			for j in range(len(self.agents) - 1):
				self.agents[self.agent_num].addOtherAgent(self.agents[j])
			self.agents[self.agent_num].addObject((self.floor.getMask(), self.floor.getPosition()[0], self.floor.getPosition()[1]))
			for j in range(len(self.blocks)):
				self.agents[self.agent_num].addObject((self.blocks[j].getMask(), self.blocks[j].getPosition()[0], self.blocks[j].getPosition()[1]))
		elif self.agents[self.agent_num].finished == -1:
			if self.continuous:
				self.agents = []
				if self.custom_build:
					self.agent_num = 0
				else:
					self.resetWorld()
					self.running = True
			else:
				self.resetWorld()



	def setGoal(self):
		for i in range(10):
			x_pos = randint(850,900)
			self.goal = Block(0, (x_pos, 0))
			self.goal.loadImage("image_resources/goal.png")
			counter = 0
			while(not self.checkEnvironmentOverlap(True)[0]):
				counter += 1
				self.goal.setPosition((x_pos,counter))
			self.goal.setPosition((x_pos,counter + 2))
			if (self.checkEnvironmentOverlap(True)[1]) > 20:
				break
		self.draw_goal = True

	def resetWorld(self):
		self.running = False
		self.placing_object = False
		self.network_collection.reset_training()
		self.blocks = []
		self.agents = []
		self.agent_num = 0
		self.episode_num = 0
		self.draw_goal = False
		if not self.custom_build:
			self.generateWorld()

	def worldBuilding(self, object_num):
		if self.custom_build and not self.running:
			self.placing_object = True
			self.unplaced = Block(0, (self.pos[0] - 200, self.pos[1] - 200))
			self.unplaced.loadImage("image_resources/"+self.block_images[object_num]+".png")

	def initializeVariables(self):
		# define display surface			
		self.dimensions = (1080, 600)
		self.subsumption = True
		self.episode_num = 0
		self.agent_num = 0
		self.placing_object = False
		self.rotate_unplaced = 0
		self.continuous = True
		self.draw_goal = False
		self.wolf = True
		self.randomness = 5
		self.reference = 20
		self.draw_scaleable = False

		# Backgrounds colour
		self.background = (0, 153, 255, 221)

		# Keeps track of the winrate across training stages
		self.win_counter = 0
		self.network_collection = NetworkCollection()
		# Place window in the center of the screen
		os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (150,80)
		# initialise display
		pygame.init()
		self.CLOCK = pygame.time.Clock()
		self.DS = pygame.display.set_mode(self.dimensions)
		pygame.display.set_caption("Intelligent Agent Structures")

		pygame.font.init()
		self.font = pygame.font.SysFont('arial', 12)
		self.font.set_bold(True)

		self.training = False
		self.running = False
		self.custom_build = False

		# Get the image resources for the world
		self.pointers = [None, None, None]
		self.pointers[0] = pygame.image.load("image_resources/pointer.png").convert_alpha()
		self.pointers[1] = pygame.image.load("image_resources/pointerTwo.png").convert_alpha()
		self.pointers[2] = pygame.image.load("image_resources/pointerThree.png").convert_alpha()

		self.blocks, self.agents = [],[]
		# Adds agents into the world
		self.floor = Block(0, (0, 400))
		self.floor.loadImage("image_resources/flat_floor.png")

		self.block_images = ["300x200","200x600","400x400","200x200"]

		self.tabs = []
		self.tabs.append(Options(0, self))
		self.tabs.append(Log(1, self.font))
		self.tabs.append(Tab(2))

		self.scaleable_agents = []
		preset_rotations = [44,0,270,90,90,90,0,0,0,90,90,90,0,0,0]
		self.scaleable_agents.append(Agent((582,339), True, self.network_collection, 0, None, 25, False, self.randomness, self.subsumption))
		self.scaleable_agents.append(Agent((667,339), True, self.network_collection, 0, None, 25, False, self.randomness, self.subsumption))
		self.scaleable_agents.append(Agent((667,304), True, self.network_collection, 0, None, 25, False, self.randomness, self.subsumption))
		for i in range(3):
			self.scaleable_agents[i].parts.setRotations(preset_rotations)

		self.won = 0
		self.lost = 0

Main()