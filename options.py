import math, random, sys, pygame
from pygame.locals import *
from tab import Tab
from button import Button

# Object within the world the agent may collide with
class Options(Tab):


	# Initialise an object
	def __init__(self, tab_option, parent):
		Tab.__init__(self, tab_option)
		self.build_options()
		self.parent = parent
		self.target_decay_rate = 0

	# Check which button was pressed
	def click(self, press):
		# World building buttons
		for i in range(len(self.world_building)):
			if self.world_building[i].check_press(press):
				# Custom build or randomly generated environment
				if i > 1:
					self.parent.custom_build = (i == 3)
					self.parent.reset_environment()
					if i == 2:
						self.parent.generate_world()
				# Single round or continuous runs
				else:
					self.parent.continuous = (i == 0)

		# Agent modifiers
		for i in range(len(self.agent_modifiers)):
			if self.agent_modifiers[i].check_press(press):
				# Agents level of randomness
				if i > 1:
					choices = [0,5,10,20]
					self.parent.randomness = choices[i - 2]
					self.parent.tabs[1].write_message("Randomness %: " + str(choices[i - 2]))
				# Does the agent recieve moves from the neural network or the subsumption rules
				elif i == 0:
					self.parent.subsumption = True
					self.parent.tabs[1].write_message("Rule Based Move Selection")
				elif i == 1:
					self.parent.subsumption = False
					self.parent.tabs[1].write_message("Neural Network Selection")

		# Object spawners
		for i in range(len(self.spawn_object)):
			if self.spawn_object[i].check_press(press):
				# Spawn corresponding object
				self.parent.world_building(i)

		# User visual feedback
		for i in range(len(self.feedback)):
			if self.feedback[i].check_press(press):
				# Toggle on/off collisions, centre of gravitys and sensor images
				self.parent.display[i] = not self.parent.display[i]
				if not self.parent.display[i]:
					self.feedback[i].off = True

		# Network Modifiers
		for i in range(len(self.network_modifiers)):
			if self.network_modifiers[i].check_press(press):
				# Training mode or free mode
				if i < 2:
					self.parent.training = (i == 0)
					self.parent.reset_environment()
					if i == 0: 
						self.parent.tabs[1].write_message("Training Mode")
					elif i == 1: 
						self.parent.tabs[1].write_message("Free Mode")
				# How often to use the reference move
				elif i > 1 and i < 6:
					self.parent.reference = (i - 2) * 10
					self.parent.tabs[1].write_message("Reference Motion %: " + str((i - 2) * 10))
					for j in range(2,6):
						if i == j:
							self.network_modifiers[j].off = False
						else:
							self.network_modifiers[j].off = True
				# Check the decay rate for a specific training stage
				elif i > 5 and i < 10:
					self.target_decay_rate = i - 6
					value = self.parent.network_collection.get_decay_rate(i - 6)
					values = [0.99, 0.999, 0.9999, 0.99999]
					for j in range(10,14):
						if value == values[j - 10]:
							self.network_modifiers[j].off = False
						else:
							self.network_modifiers[j].off = True
				# Network decay rates
				elif i == 10:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.99)
					self.parent.tabs[1].write_message("Decay Rate Is Now Set To 0.99")
				elif i == 11:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.999)
					self.parent.tabs[1].write_message("Decay Rate Is Now Set To 0.999")
				elif i == 12:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.9999)
					self.parent.tabs[1].write_message("Decay Rate Is Now Set To 0.9999")
				elif i == 13:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.99999)
					self.parent.tabs[1].write_message("Decay Rate Is Now Set To 0.99999")
				# Win or Learn Fast learning rate
				elif i == 14:
					self.wolf = True
					self.parent.tabs[1].write_message("WoLF Learning Rate Selected")
				# Update networks learning rate
				elif i > 14 and i < 18:
					values = [0.1, 0.01, 0.001]
					value = values[i - 15]
					self.parent.tabs[1].write_message(str(value) + " Learning Rate Selected")
					self.parent.tabs[1].write_message("This May Take A While")
					self.parent.draw_sprites()
					self.parent.network_collection.update_learn_rate(value)
					self.parent.tabs[1].write_message("Learning Rate Updated")
					self.parent.wolf = False
				# Reset network
				elif i == 18:
					self.parent.network_collection.new_network()
					self.parent.tabs[1].write_message("New Network Created")
				# Load checkpoint, either preset one or users own
				elif i == 19:
					self.parent.network_collection.load_checkpoint(False)
					self.parent.tabs[1].write_message("Saved Network Loaded")
				elif i == 20:
					self.parent.network_collection.load_checkpoint(True)
					self.parent.tabs[1].write_message("Preset Network Loaded")

		# If the user wants to show / hide options menu do so
		if self.open.check_press(press):
			self.toggle_seen()


	# Initialize options menu and place buttons in the correct position
	def build_options(self):
		# Load image
		self.load_image("image_resources/options.png")
		# Initial position
		self.position = (-326,55)
		self.initial_position = (-326,55)
		# Hide tab to the left of the screen
		self.hide_left = True
		self.hidden = True
		self.width = 336
		self.left = False
		self.right = False

		# Unclickable buttons.
		self.unclickable.append(Button(self.position, (10,40), (129,57), "image_resources/world_building.png"))
		self.unclickable.append(Button(self.position, (10,108), (129,57), "image_resources/move_selection.png"))
		self.unclickable.append(Button(self.position, (10,176), (129,27), "image_resources/training.png"))
		self.unclickable.append(Button(self.position, (10,206), (129,27), "image_resources/reference.png"))
		self.unclickable.append(Button(self.position, (10,243), (129,27), "image_resources/decay.png"))
		self.unclickable.append(Button(self.position, (10,311), (129,57), "image_resources/learning.png"))
		self.unclickable.append(Button(self.position, (10,348), (129,27), "image_resources/randomness.png"))
		self.unclickable.append(Button(self.position, (10,385), (129,27), "image_resources/network.png"))

		# Buttons that change aspects of environment construction
		self.world_building.append(Button(self.position, (142,40), (123,27), "image_resources/continuous.png"))
		self.world_building[0].load_second_image("image_resources/continuous_green.png")
		self.world_building.append(Button(self.position, (142,70), (123,27), "image_resources/single.png"))
		self.world_building[1].load_second_image("image_resources/single_green.png")
		self.world_building.append(Button(self.position, (267,40), (81,27), "image_resources/random.png", True))
		self.world_building[2].load_second_image("image_resources/random_green.png")
		self.world_building.append(Button(self.position, (267,70), (81,27), "image_resources/custom.png", True))
		self.world_building[3].load_second_image("image_resources/custom_green.png")

		# Agent modifiers
		self.agent_modifiers.append(Button(self.position, (142,108), (135,27), "image_resources/subsumption.png"))
		self.agent_modifiers[0].load_second_image("image_resources/subsumption_green.png")
		self.agent_modifiers.append(Button(self.position, (142,138), (135,27), "image_resources/neural.png"))
		self.agent_modifiers[1].load_second_image("image_resources/neural_green.png")
		self.agent_modifiers.append(Button(self.position, (142,348), (33,27), "image_resources/0.png"))
		self.agent_modifiers[2].load_second_image("image_resources/0_green.png")
		self.agent_modifiers.append(Button(self.position, (178,348), (33,27), "image_resources/5.png"))
		self.agent_modifiers[3].load_second_image("image_resources/5_green.png")
		self.agent_modifiers.append(Button(self.position, (214,348), (39,27), "image_resources/10.png"))
		self.agent_modifiers[4].load_second_image("image_resources/10_green.png")
		self.agent_modifiers.append(Button(self.position, (256,348), (45,27), "image_resources/20.png"))
		self.agent_modifiers[5].load_second_image("image_resources/20_green.png")

		# Spawn objects into the environment
		self.spawn_object.append(Button(self.position, (10,460), (51,57), "image_resources/300x200_picture.png"))
		self.spawn_object.append(Button(self.position, (70,460), (51,57), "image_resources/200x600_picture.png"))
		self.spawn_object.append(Button(self.position, (130,460), (51,57), "image_resources/400x400_picture.png"))
		self.spawn_object.append(Button(self.position, (190,460), (51,57), "image_resources/200x200_picture.png"))
		self.spawn_object.append(Button(self.position, (250,460), (41,57), "image_resources/flag_1_picture.png"))
		self.spawn_object.append(Button(self.position, (300,460), (41,57), "image_resources/flag_2_picture.png"))

		# Modify values of the neural network
		self.network_modifiers.append(Button(self.position, (142,176), (33,27), "image_resources/on.png"))
		self.network_modifiers[0].load_second_image("image_resources/on_green.png")
		self.network_modifiers.append(Button(self.position, (177,176), (39,27), "image_resources/off.png"))
		self.network_modifiers[1].load_second_image("image_resources/off_green.png")
		self.network_modifiers.append(Button(self.position, (142,206), (33,27), "image_resources/0.png"))
		self.network_modifiers[2].load_second_image("image_resources/0_green.png")
		self.network_modifiers.append(Button(self.position, (178,206), (39,27), "image_resources/10.png"))
		self.network_modifiers[3].load_second_image("image_resources/10_green.png")
		self.network_modifiers.append(Button(self.position, (220,206), (33,27), "image_resources/20.png"))
		self.network_modifiers[4].load_second_image("image_resources/20_green.png")
		self.network_modifiers.append(Button(self.position, (268,206), (39,27), "image_resources/30.png"))
		self.network_modifiers[5].load_second_image("image_resources/30_green.png")
		self.network_modifiers.append(Button(self.position, (142,243), (21,27), "image_resources/1.png"))
		self.network_modifiers[6].load_second_image("image_resources/1_green.png")
		self.network_modifiers.append(Button(self.position, (166,243), (21,27), "image_resources/2.png"))
		self.network_modifiers[7].load_second_image("image_resources/2_green.png")
		self.network_modifiers.append(Button(self.position, (190,243), (21,27), "image_resources/3.png"))
		self.network_modifiers[8].load_second_image("image_resources/3_green.png")
		self.network_modifiers.append(Button(self.position, (214,243), (21,27), "image_resources/4.png"))
		self.network_modifiers[9].load_second_image("image_resources/4_green.png")
		self.network_modifiers.append(Button(self.position, (10,273), (51,27), "image_resources/0_99.png"))
		self.network_modifiers[10].load_second_image("image_resources/0_99_green.png")
		self.network_modifiers.append(Button(self.position, (64,273), (63,27), "image_resources/0_999.png"))
		self.network_modifiers[11].load_second_image("image_resources/0_999_green.png")
		self.network_modifiers.append(Button(self.position, (130,273), (75,27), "image_resources/0_9999.png"))
		self.network_modifiers[12].load_second_image("image_resources/0_9999_green.png")
		self.network_modifiers.append(Button(self.position, (208,273), (87,27), "image_resources/0_99999.png"))
		self.network_modifiers[13].load_second_image("image_resources/0_99999_green.png")
		self.network_modifiers.append(Button(self.position, (142,311), (54,27), "image_resources/wolf.png"))
		self.network_modifiers[14].load_second_image("image_resources/wolf_green.png")
		self.network_modifiers.append(Button(self.position, (199,311), (33,27), "image_resources/0_1.png"))
		self.network_modifiers[15].load_second_image("image_resources/0_1_green.png")
		self.network_modifiers.append(Button(self.position, (235,311), (45,27), "image_resources/0_01.png"))
		self.network_modifiers[16].load_second_image("image_resources/0_01_green.png")
		self.network_modifiers.append(Button(self.position, (283,311), (57,27), "image_resources/0_001.png"))
		self.network_modifiers[17].load_second_image("image_resources/0_001_green.png")
		self.network_modifiers.append(Button(self.position, (142,385), (45,27), "image_resources/new.png"))
		self.network_modifiers.append(Button(self.position, (190,385), (54,27), "image_resources/load.png"))
		self.network_modifiers.append(Button(self.position, (247,385), (81,27), "image_resources/preset.png"))

		# Provide visual feedback to the user
		self.feedback.append(Button(self.position, (10,422), (111,27), "image_resources/collisions.png"))
		self.feedback[0].load_second_image("image_resources/collisions_green.png")
		self.feedback.append(Button(self.position, (124,422), (93,27), "image_resources/sensors.png"))
		self.feedback[1].load_second_image("image_resources/sensors_green.png")
		self.feedback.append(Button(self.position, (220,422), (45,27), "image_resources/cog.png"))
		self.feedback[2].load_second_image("image_resources/cog_green.png")

		# Hide/Show options tab
		self.open = Button(self.position, (365,227), (30,39), "image_resources/right.png")
		self.open.load_second_image("image_resources/left.png")

		# Link radio buttons. Only 1 of each set can be on at a time
		self.world_building[0].radio_buttons(self.world_building[1])
		self.world_building[1].radio_buttons(self.world_building[0])

		self.world_building[2].radio_buttons(self.world_building[3])
		self.world_building[3].radio_buttons(self.world_building[2])

		self.agent_modifiers[0].radio_buttons(self.agent_modifiers[1])
		self.agent_modifiers[1].radio_buttons(self.agent_modifiers[0])

		self.network_modifiers[0].radio_buttons(self.network_modifiers[1])
		self.network_modifiers[1].radio_buttons(self.network_modifiers[0])

		self.network_modifiers[2].radio_buttons(self.network_modifiers[3])
		self.network_modifiers[3].radio_buttons(self.network_modifiers[2])

		for i in range(0, 3):
			for j in range(6 + (i * 4), 10 + (i * 4)):
				for k in range(6 + (i * 4), 10 + (i * 4)):
					if not (j == k):
						self.network_modifiers[j].radio_buttons(self.network_modifiers[k])

		for i in range(2, 6):
			for j in range(2, 6):
				if not (i == j):
					self.agent_modifiers[i].radio_buttons(self.agent_modifiers[j])

		# Set some buttons to start already on
		self.world_building[0].off = False
		self.world_building[2].off = False
		self.agent_modifiers[0].off = False
		self.network_modifiers[1].off = False
		self.network_modifiers[4].off = False
		self.network_modifiers[6].off = False
		self.network_modifiers[10].off = False
		self.network_modifiers[14].off = False
		self.agent_modifiers[3].off = False