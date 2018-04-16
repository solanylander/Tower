import math, random, sys, pygame, os, time, argparse
from pygame.locals import *
from agent import Agent
from part import Part
from objects import Object
from network_collection import NetworkCollection
from tab import Tab
from options import Options
from log import Log
from random import *

# Main Class. This runs the application and updates the UI
class Main():

	def __init__(self):
		# Initialise variables and randomly generate ane nvironment
		self.initialize_variables()
		self.generate_world()
		# Update display
		self.update_display = True

		# main loop
		while True:
			# Check for inputs
			self.check_inputs()
			# If not paused
			if not self.paused:
				# If a run is ongoing
				if self.running:
					# Different modes
					if self.training:
						self.training_mode()
					else:
						self.free_mode()
				# Update environment objects positions
				self.move_environment()
				# Update the display if the user chooses too
				# Program runs faster when it is off
				if self.update_display:
					self.draw_sprites()

	def initialize_variables(self):
		# define display surface			
		self.dimensions = (1080, 600)
		# Initial parameters
		self.subsumption = True
		self.episode_num = 0
		self.extra = False
		self.agent_num = 0
		self.placing_object = False
		self.rotate_unplaced = 0
		self.continuous = True
		self.draw_goal = False
		self.wolf = True
		self.randomness = 5
		self.reference = 20
		self.draw_scaleable = False
		self.display = [False, False, False]
		self.training = False
		self.running = False
		self.custom_build = False
		self.paused = False
		self.agents_to_be_added = []

		# Backgrounds colour
		self.background = (0, 153, 255, 221)

		# Keeps track of the winrate across training stages
		self.win_counter = 0
		self.network_collection = NetworkCollection()
		# Place window in the center of the screen
		os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (150,80)
		# initialise display
		pygame.init()
		self.clock = pygame.time.Clock()
		self.canvas = pygame.display.set_mode(self.dimensions)
		pygame.display.set_caption("Intelligent Agent Structures")
		# Create a font used to write on the screen
		pygame.font.init()
		self.font = pygame.font.SysFont('arial', 12)
		self.font.set_bold(True)


		# Get the image resources for the world
		self.pointers = [None, None]
		self.pointers[0] = pygame.image.load("image_resources/pointer_alt.png").convert_alpha()
		self.pointers[1] = pygame.image.load("image_resources/pointer.png").convert_alpha()

		# array containing the environments current blocks and agents
		self.blocks, self.agents = [],[]
		# Adds agents into the world
		self.floor = Object(0, (0, 400))
		self.floor.load_image("image_resources/flat_floor.png")

		# File paths for the block images
		self.block_images = ["300x200","200x600","400x400","200x200","goal","goal_flipped"]

		# UI Tabs for environment modification, output log and controls
		self.tabs = []
		self.tabs.append(Options(0, self))
		self.tabs.append(Log(1, self.font, self))
		self.tabs.append(Tab(2))

		# Static agents used in the final training stage
		self.scaleable_agents = []
		preset_rotations = [44,0,270,90,90,90,0,0,0,90,90,90,0,0,0]
		self.scaleable_agents.append(Agent((582,339), self.network_collection, 0, None, 25, False, self.randomness, self.subsumption))
		self.scaleable_agents.append(Agent((667,339), self.network_collection, 0, None, 25, False, self.randomness, self.subsumption))
		self.scaleable_agents.append(Agent((667,304), self.network_collection, 0, None, 25, False, self.randomness, self.subsumption))
		for i in range(3):
			self.scaleable_agents[i].parts.set_rotations(preset_rotations)
		# Rounds won/lost
		self.won = 0
		self.lost = 0

	# Check computer inputs
	def check_inputs(self):
		# Event Listener
		for event in pygame.event.get():
			# On quit event quit game
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				# Start run
				if event.key == K_RETURN:
					self.running = True
				# End run / Reset environment
				elif event.key == K_ESCAPE:
					self.reset_environment()
				# Rotate block clockwise and anti clockwise
				elif event.key == K_q:	
					self.rotate_unplaced += 1
				elif event.key == K_e:	
					self.rotate_unplaced += -1
				# Update display
				elif event.key == K_u:	
					self.update_display = not self.update_display
				# Play / Pause
				elif event.key == K_p:	
					self.paused = not self.paused
			elif event.type == KEYUP:
				# Stop rotating block
				if event.key == K_e:	
					self.rotate_unplaced += 1
				elif event.key == K_q:	
					self.rotate_unplaced += -1
			# On mouse click check which button was pressed
			elif event.type == pygame.MOUSEBUTTONDOWN and not self.paused:
				self.pos = pygame.mouse.get_pos()
				# If an object is being held by the user place it
				if self.placing_object:
					self.place_object()
				# Check buttons
				for i in range(3):
					self.tabs[i].click(self.pos)

	# Draw sprites
	def draw_sprites(self):
		# Draw background
		self.canvas.fill(self.background)
		# Draw the goal if there is one
		if self.draw_goal:
			self.canvas.blit(self.goal.get_image(), self.goal.get_position())
		# Draw sensors if user chooses
		if self.display[1]:
			for i in range(len(self.agents)):
				self.agents[i].sensors.run(self.canvas)
		# Draw any blocks within the environment including any the user is holding
		if self.placing_object:
			self.canvas.blit(self.unplaced.get_image(), self.unplaced.get_position())
		for i in range(len(self.blocks)):
			self.canvas.blit(self.blocks[i].get_image(), self.blocks[i].get_position())
		# Draw the agents used in the final training stage
		if self.draw_scaleable:
			for i in range(len(self.scaleable_agents)):
				self.scaleable_agents[i].parts.run(self.canvas)
		# Draw the agents
		for i in range(len(self.agents)):
			self.agents[i].parts.run(self.canvas)
		# Draw the floor
		self.canvas.blit(self.floor.get_image(), self.floor.get_position())
		# Draw the agents collision points with the environment if the request it
		if self.display[0]:
			for i in range(len(self.agents)):
				markers = self.agents[i].get_box()
				for j in range(len(markers)):
					self.canvas.blit(self.pointers[1], (int(markers[j][0]), int(markers[j][1])))
		# Draw the agents center of gravity if the request it
		if self.display[2]:
			for i in range(len(self.agents)):
				cog = self.agents[i].cog
				self.canvas.blit(self.pointers[0], (int(cog[0]), int(cog[1])))
		# Draw tabs
		for i in range(3):
			self.tabs[i].run(self.canvas)
		pygame.display.update()
		# Max FPS
		self.clock.tick(120)

	# Place an object the user is holding
	def place_object(self):
		# It must overlap with the environment (No freefloating structures)
		if (self.check_environmental_overlap()):
			# Place new goal
			if self.unplaced_goal:
					self.goal = self.unplaced
					self.draw_goal = True
			# Place block
			else:
				self.blocks.append(self.unplaced)
		self.placing_object = False

	# Check if a block is overlapping with the environment (No free floating structures)
	def check_environmental_overlap(self, goal=False):
		# Compare either the goal or the block the user is currently holding
		checking = self.unplaced
		if goal:
			checking = self.goal
		# Compare against every block including the floor
		for k in range(len(self.blocks) + 1):
			comparison = None
			if k == len(self.blocks):
				comparison = [self.floor.get_position(), self.floor.get_mask()]
			else:
				comparison = [self.blocks[k].get_position(), self.blocks[k].get_mask()]

			# Find the position difference between the agent part and the external object
			offset = (int(comparison[0][0] - checking.get_position()[0]), int(comparison[0][1] - checking.get_position()[1]))
			result = checking.get_mask().overlap(comparison[1], offset)
			# If there was a collision return the collision position
			if result:
				return result[1]
		# Else return false
		return False

	# Randomly generate a new environment
	def generate_world(self):
		# Reset environment
		self.blocks = []
		self.agents = []
		self.agent_num = 0
		# Randomly place 3 blocks.
		while len(self.blocks) < 3:
			self.unplaced = Object(0, (randint(500,800), randint(0,200)))
			self.unplaced.load_image("image_resources/"+self.block_images[randint(0,3)]+".png")
			self.unplaced.rotate(randint(0,180))
			# Only keep the block if it touches the environment
			if self.check_environmental_overlap():
				self.blocks.append(self.unplaced)
		# Place goal
		self.set_goal()

	# Move an item in the environment. Either what the user it holding or a tab
	def move_environment(self):
		# User holding item
		if self.placing_object:
			self.pos = pygame.mouse.get_pos()
			if self.unplaced_goal:
				self.unplaced.set_position((self.pos[0] - 25, self.pos[1] - 25))
			else:
				self.unplaced.set_position((self.pos[0] - 200, self.pos[1] - 200))
				self.unplaced.rotate(self.rotate_unplaced)
		# Update tabs
		for i in range(3):
			self.tabs[i].move()

	# Automatically place goal in the environment
	def set_goal(self):
		# Goal is shapped like a flag. Keep trying to place goal until the attaches to the ground by the flag pole
		for i in range(10):
			# Randomly position
			x_pos = randint(850,900)
			self.goal = Object(0, (x_pos, 0))
			# Pick a direction for the goal to face. When placing on a slope means it can attach to the ground by the pole
			flipped = False
			if randint(0, 100) > 50:
				self.goal.load_image("image_resources/goal.png")
			else:
				self.goal.load_image("image_resources/goal_flipped.png")
				flipped = True
			counter = 0
			# Start the goal in the air. Keep lowering until it touches the ground
			while(not self.check_environmental_overlap(True)):
				counter += 1
				self.goal.set_position((x_pos,counter))
			# Lower the goal by 2 pixels to plant it firmly in the ground
			self.goal.set_position((x_pos,counter + 2))
			# If planted by the flag pole break otherwise try a maximum of 10 times
			if self.check_environmental_overlap(True) > 40:
				break
		self.draw_goal = True

	# Reset environment
	def reset_environment(self,  clear_world=False):
		# Reset variables
		self.running = False
		self.placing_object = False
		self.network_collection.reset_training()
		# Clear blocks and agents
		self.agents = []
		self.agent_num = 0
		self.episode_num = 0
		self.draw_scaleable = False
		if not clear_world:
			self.blocks = []
			self.draw_goal = False
		# If not custom built environments generate a new one
		if not self.custom_build:
			self.generate_world()
		self.tabs[1].write_message("Environment Reset")

	# When the user requests a block give them one
	def world_building(self, object_num):
		if not self.running and (object_num < 4 or self.draw_goal == False):
			if self.custom_build or object_num > 3:
				self.placing_object = True
				# Centered so cursor is in the middle of the image
				self.unplaced = Object(0, (self.pos[0] - 200, self.pos[1] - 200))
				self.unplaced.load_image("image_resources/"+self.block_images[object_num]+".png")
				self.unplaced_goal = (object_num > 3)

	# Training mode. Here the user performs several subtasks to train the neural network
	def training_mode(self):
		# If no agents exist create one
		if len(self.agents) == 0:
			if self.reference > 0:
				self.create_agent(290, True, True)
			else:
				self.create_agent(290, True, False)

		# Get agent
		agent = self.agents[0]
		# Get collection of neural networks
		network_collection = self.network_collection
		# Move agent
		agent.move()

		# If the agent finishes its run reset environment
		if agent.restart:
			# Did the agent win
			if agent.won:
				self.won += 1
				if self.extra:
					self.tabs[1].write_message("WON")
			else:
				self.lost += 1
				if self.extra:
					self.tabs[1].write_message("LOST")

					
			# Run the first 2 training stages until the networks have 20000 pieces of data.
			# Run the last 2 training stages until the networks have 50000 pieces of data.
			comparator = 50000
			if network_collection.get_turn() < 2:
				comparator = 20000

			difference = (network_collection.get_length() - (comparator * self.reference / 100))

			# If the network has enough data
			if network_collection.get_length() > comparator:
				# Move to the next step
				self.tabs[1].write_message("Training Stage " + str(network_collection.get_turn() + 1) + "/4 Complete")
				network_collection.increment_turn()
				# Generate new environment
				self.generate_world()
				# Average of the averages from each stage of training
				self.win_counter += (self.won/(self.won + self.lost))/4
				# Finish episode
				if network_collection.get_turn() == 0:
					self.tabs[1].write_message("Episode " + str(self.episode_num + 1) + " Finished")
					self.tabs[1].write_message("Training, This may take a while")
					self.draw_scaleable = False
					self.draw_sprites()
					# If using Win or Learn Fast update the learning rate
					learn_rate = network_collection.get_learn_rate()
					if self.wolf:
						learn_rate = 0.1 - (self.win_counter * 0.099)
						network_collection.update_learn_rate(learn_rate)
					# Finish episode and save network
					network_collection.finish_episode()
					network_collection.save_checkpoint()
					self.tabs[1].write_message("Network Trained With LR: " + str("%.3f" % learn_rate))

					# Reset variables
					self.episode_num += 1
					self.win_counter = 0
					preset = False

					# End run
					self.run_ended()

				# Empty environment except on the 3rd stage
				elif network_collection.get_turn() == 3:
					self.blocks = []
					self.draw_goal = False
				# Reset win/loss count
				self.won = 0
				self.lost = 0
			elif self.extra:
				self.tabs[1].write_message(str(network_collection.get_length()) + " / " + str(comparator))

			# Reset agent
			self.agents = []
			self.create_agent(290, True, (network_collection.get_length() < (comparator * self.reference / 100)))

			# On the 3rd training step spawn static training agents
			if network_collection.get_turn() == 3:
				for j in range(len(self.scaleable_agents)):
					self.agents[self.agent_num].add_other_agent(self.scaleable_agents[j])
				self.draw_scaleable = True









	# Free mode. Environment are built and agents attempt to work together to scale them
	def free_mode(self):
		# If no agents currently exist create one
		if len(self.agents) == 0:
			# If there is no goal make one
			if not self.draw_goal:
				self.set_goal()
			self.create_agent(390, False)

		# Move all the agents
		for i in range(self.agent_num + 1):
			self.agents[i].move()
			# Once an agent is confirmed to be finished add its mask to the next agent
			if self.agents[i].finished_completely:
				self.agents[i].finished_completely = False
				self.agents[self.agent_num].add_other_agent(self.agents[i])
		# If an agent requests another then spawn another agent
		if self.agents[self.agent_num].finished == 1:
			self.agents_to_be_added = [self.agent_num]
			self.agent_num += 1
			self.create_agent(100, False)
		# If the agent declares a run finished, end run
		elif self.agents[self.agent_num].finished == -1:
			if self.agents[self.agent_num].won:
				self.tabs[1].write_message("Run Finished Successfully")
			else:
				self.tabs[1].write_message("Run Failed")
			self.run_ended()

	# Run ended.
	def run_ended(self):
		# If it's in continuous create a new run otherwise reset environment and wait for user input
		if self.continuous:
			self.agents = []
			# If the environment is custom keep it otherwise reset the environment
			if self.custom_build:
				self.agent_num = 0
			else:
				self.reset_environment()
				self.running = True
		else:
			self.reset_environment(self.custom_build)

	# Create a new agent
	def create_agent(self, x_pos, training, reference=False):
		# Append to agent array
		if self.training:
			# Choose if the run is a reference of the neural network
			if self.extra:
				if reference:
					self.tabs[1].write_message("Reference")
				else:
					self.tabs[1].write_message("Neural Network")
			self.agents.append(Agent((x_pos,200), self.network_collection, 0, None, 25, True, self.randomness, reference))
		else:
			self.agents.append(Agent((x_pos,200), self.network_collection, 0, self.goal, 25, False, self.randomness, self.subsumption))
		if self.extra:
			self.tabs[1].write_message("New Agent Created")
		# Inform agent of the other agents positions
		for j in range(len(self.agents) - 2):
			self.agents[self.agent_num].add_other_agent(self.agents[j])
		self.agents[self.agent_num].add_object((self.floor.get_mask(), self.floor.get_position()[0], self.floor.get_position()[1]))
		# Inform agent of the environmental objects positions
		for j in range(len(self.blocks)):
			self.agents[self.agent_num].add_object((self.blocks[j].get_mask(), self.blocks[j].get_position()[0], self.blocks[j].get_position()[1]))


Main()