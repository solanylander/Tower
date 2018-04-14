import math, random, sys, pygame
from pygame.locals import *
from tab import Tab
from button import Button

# Object within the world the agent may collide with
class Options(Tab):


	# Initialise an object
	def __init__(self, tab_option, parent):
		Tab.__init__(self, tab_option)
		self.buildOptions()
		self.parent = parent
		self.target_decay_rate = 0


	def click(self, press):
		for i in range(len(self.world_building)):
			pressed = self.world_building[i].checkPress(press)
			if pressed:
				if i > 1:
					self.parent.custom_build = (i == 3)
					self.parent.resetWorld()
					if i == 2:
						self.parent.generateWorld()
				else:
					self.parent.continuous = (i == 0)


		for i in range(len(self.agent_modifiers)):
			pressed = self.agent_modifiers[i].checkPress(press)
			if pressed:
				if i > 1:
					choices = [0,5,10,20]
					self.parent.randomness = choices[i - 2]
				else:
					self.parent.subsumption = (i == 0)
		for i in range(len(self.spawn_object)):
			pressed = self.spawn_object[i].checkPress(press)
			if pressed:
				self.parent.worldBuilding(i)
		for i in range(len(self.network_modifiers)):
			pressed = self.network_modifiers[i].checkPress(press)
			if pressed:
				if i < 2:
					self.parent.training = (i == 0)
					self.parent.resetWorld()
				elif i > 1 and i < 6:
					self.parent.reference = (i - 2) * 10
					for j in range(2,6):
						if i == j:
							self.network_modifiers[j].initial_image = False
						else:
							self.network_modifiers[j].initial_image = True
				elif i > 5 and i < 10:
					self.target_decay_rate = i - 6
					value = self.parent.network_collection.get_decay_rate(i - 6)
					values = [0.99, 0.999, 0.9999, 0.99999]
					print(value)
					for j in range(10,14):
						if value == values[j - 10]:
							self.network_modifiers[j].initial_image = False
						else:
							self.network_modifiers[j].initial_image = True

				elif i == 10:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.99)
				elif i == 11:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.999)
				elif i == 12:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.9999)
				elif i == 13:
					self.parent.network_collection.set_decay_rate(self.target_decay_rate, 0.99999)
				elif i == 14:
					self.wolf = True
				elif i == 15:
					self.parent.network_collection.update_learn_rate(0.1)
					self.parent.wolf = False
				elif i == 16:
					self.parent.network_collection.update_learn_rate(0.01)
					self.parent.wolf = False
				elif i == 17:
					self.parent.network_collection.update_learn_rate(0.001)
					self.parent.wolf = False
				elif i == 18:
					self.parent.network_collection.new_network()
				elif i > 18:
					self.parent.network_collection.load_checkpoint((i == 18))


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



	def buildOptions(self):
		self.loadImage("image_resources/options.png")
		self.position = (-326,65)
		self.initial_position = (-326,65)
		self.hide_left = True
		self.hidden = True
		self.width = 336
		self.hiding = False
		self.showing = False

		self.unclickable.append(Button(self.position, (10,40), (129,57), "image_resources/world_building.png"))
		self.unclickable.append(Button(self.position, (10,108), (129,57), "image_resources/move_selection.png"))
		self.unclickable.append(Button(self.position, (10,176), (129,27), "image_resources/training.png"))
		self.unclickable.append(Button(self.position, (10,206), (129,27), "image_resources/reference.png"))
		self.unclickable.append(Button(self.position, (10,243), (129,27), "image_resources/decay.png"))
		self.unclickable.append(Button(self.position, (10,311), (129,57), "image_resources/learning.png"))
		self.unclickable.append(Button(self.position, (10,348), (129,27), "image_resources/randomness.png"))
		self.unclickable.append(Button(self.position, (10,385), (129,27), "image_resources/network.png"))

		self.world_building.append(Button(self.position, (142,40), (123,27), "image_resources/continuous.png"))
		self.world_building[0].loadSecondImage("image_resources/continuous_green.png")
		self.world_building.append(Button(self.position, (142,70), (123,27), "image_resources/single.png"))
		self.world_building[1].loadSecondImage("image_resources/single_green.png")
		self.world_building.append(Button(self.position, (267,40), (81,27), "image_resources/random.png", True))
		self.world_building[2].loadSecondImage("image_resources/random_green.png")
		self.world_building.append(Button(self.position, (267,70), (81,27), "image_resources/custom.png", True))
		self.world_building[3].loadSecondImage("image_resources/custom_green.png")

		self.agent_modifiers.append(Button(self.position, (142,108), (135,27), "image_resources/subsumption.png"))
		self.agent_modifiers[0].loadSecondImage("image_resources/subsumption_green.png")
		self.agent_modifiers.append(Button(self.position, (142,138), (135,27), "image_resources/neural.png"))
		self.agent_modifiers[1].loadSecondImage("image_resources/neural_green.png")

		self.spawn_object.append(Button(self.position, (10,425), (51,57), "image_resources/300x200_picture.png"))
		self.spawn_object.append(Button(self.position, (70,425), (51,57), "image_resources/200x600_picture.png"))
		self.spawn_object.append(Button(self.position, (130,425), (51,57), "image_resources/400x400_picture.png"))
		self.spawn_object.append(Button(self.position, (190,425), (51,57), "image_resources/200x200_picture.png"))

		self.network_modifiers.append(Button(self.position, (142,176), (33,27), "image_resources/on.png"))
		self.network_modifiers[0].loadSecondImage("image_resources/on_green.png")
		self.network_modifiers.append(Button(self.position, (177,176), (39,27), "image_resources/off.png"))
		self.network_modifiers[1].loadSecondImage("image_resources/off_green.png")
		self.network_modifiers.append(Button(self.position, (142,206), (33,27), "image_resources/0.png"))
		self.network_modifiers[2].loadSecondImage("image_resources/0_green.png")
		self.network_modifiers.append(Button(self.position, (178,206), (39,27), "image_resources/10.png"))
		self.network_modifiers[3].loadSecondImage("image_resources/10_green.png")
		self.network_modifiers.append(Button(self.position, (220,206), (33,27), "image_resources/20.png"))
		self.network_modifiers[4].loadSecondImage("image_resources/20_green.png")
		self.network_modifiers.append(Button(self.position, (268,206), (39,27), "image_resources/30.png"))
		self.network_modifiers[5].loadSecondImage("image_resources/30_green.png")








		self.network_modifiers.append(Button(self.position, (142,243), (21,27), "image_resources/1.png"))
		self.network_modifiers[6].loadSecondImage("image_resources/1_green.png")
		self.network_modifiers.append(Button(self.position, (166,243), (21,27), "image_resources/2.png"))
		self.network_modifiers[7].loadSecondImage("image_resources/2_green.png")
		self.network_modifiers.append(Button(self.position, (190,243), (21,27), "image_resources/3.png"))
		self.network_modifiers[8].loadSecondImage("image_resources/3_green.png")
		self.network_modifiers.append(Button(self.position, (214,243), (21,27), "image_resources/4.png"))
		self.network_modifiers[9].loadSecondImage("image_resources/4_green.png")

		self.network_modifiers.append(Button(self.position, (10,273), (51,27), "image_resources/0_99.png"))
		self.network_modifiers[10].loadSecondImage("image_resources/0_99_green.png")
		self.network_modifiers.append(Button(self.position, (64,273), (63,27), "image_resources/0_999.png"))
		self.network_modifiers[11].loadSecondImage("image_resources/0_999_green.png")
		self.network_modifiers.append(Button(self.position, (130,273), (75,27), "image_resources/0_9999.png"))
		self.network_modifiers[12].loadSecondImage("image_resources/0_9999_green.png")
		self.network_modifiers.append(Button(self.position, (208,273), (87,27), "image_resources/0_99999.png"))
		self.network_modifiers[13].loadSecondImage("image_resources/0_99999_green.png")

		self.network_modifiers.append(Button(self.position, (142,311), (54,27), "image_resources/wolf.png"))
		self.network_modifiers[14].loadSecondImage("image_resources/wolf_green.png")
		self.network_modifiers.append(Button(self.position, (199,311), (33,27), "image_resources/0_1.png"))
		self.network_modifiers[15].loadSecondImage("image_resources/0_1_green.png")
		self.network_modifiers.append(Button(self.position, (235,311), (45,27), "image_resources/0_01.png"))
		self.network_modifiers[16].loadSecondImage("image_resources/0_01_green.png")
		self.network_modifiers.append(Button(self.position, (283,311), (57,27), "image_resources/0_001.png"))
		self.network_modifiers[17].loadSecondImage("image_resources/0_001_green.png")

		self.agent_modifiers.append(Button(self.position, (142,348), (33,27), "image_resources/0.png"))
		self.agent_modifiers[2].loadSecondImage("image_resources/0_green.png")
		self.agent_modifiers.append(Button(self.position, (178,348), (33,27), "image_resources/5.png"))
		self.agent_modifiers[3].loadSecondImage("image_resources/5_green.png")
		self.agent_modifiers.append(Button(self.position, (214,348), (39,27), "image_resources/10.png"))
		self.agent_modifiers[4].loadSecondImage("image_resources/10_green.png")
		self.agent_modifiers.append(Button(self.position, (256,348), (45,27), "image_resources/20.png"))
		self.agent_modifiers[5].loadSecondImage("image_resources/20_green.png")

		self.network_modifiers.append(Button(self.position, (142,385), (45,27), "image_resources/new.png"))
		self.network_modifiers.append(Button(self.position, (190,385), (54,27), "image_resources/load.png"))
		self.network_modifiers.append(Button(self.position, (247,385), (81,27), "image_resources/preset.png"))

		self.open = Button(self.position, (365,227), (30,39), "image_resources/right.png")
		self.open.loadSecondImage("image_resources/left.png")

		self.world_building[0].radioButtons(self.world_building[1])
		self.world_building[1].radioButtons(self.world_building[0])
		self.world_building[2].radioButtons(self.world_building[3])
		self.world_building[3].radioButtons(self.world_building[2])

		self.agent_modifiers[0].radioButtons(self.agent_modifiers[1])
		self.agent_modifiers[1].radioButtons(self.agent_modifiers[0])

		self.network_modifiers[0].radioButtons(self.network_modifiers[1])
		self.network_modifiers[1].radioButtons(self.network_modifiers[0])
		self.network_modifiers[2].radioButtons(self.network_modifiers[3])
		self.network_modifiers[3].radioButtons(self.network_modifiers[2])

		for i in range(0, 3):
			for j in range(6 + (i * 4), 10 + (i * 4)):
				for k in range(6 + (i * 4), 10 + (i * 4)):
					if not (j == k):
						self.network_modifiers[j].radioButtons(self.network_modifiers[k])


		for i in range(2, 6):
			for j in range(2, 6):
				if not (i == j):
					self.agent_modifiers[i].radioButtons(self.agent_modifiers[j])

		self.world_building[0].initial_image = False
		self.world_building[2].initial_image = False
		self.agent_modifiers[0].initial_image = False
		self.network_modifiers[1].initial_image = False
		self.network_modifiers[4].initial_image = False
		self.network_modifiers[6].initial_image = False
		self.network_modifiers[10].initial_image = False
		self.network_modifiers[14].initial_image = False
		self.agent_modifiers[3].initial_image = False