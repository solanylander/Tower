import math, random, sys, pygame
from pygame.locals import *
from part import Part
from sensor import Sensor
from random import *
import pickle
import time
import numpy as np

MAX_BODY_ROTATION = 90
RANDOM_ELEMENT = False
TRAINER_COUNTER = 5

class Agent:

	def __init__(self, xy, args, wall, network, random_agent):
		# Which body parts are currently colliding
		self.wall = wall
		self.colliding = []
		self.history = []
		self.stop = False
		# Objects within the world
		self.objects = []
		self.reward = 1
		self.args = args
		# Neural network
		self.network = network
		if args.load_checkpoint:
			self.network.load_checkpoint()
		self.batch_state_action_reward_tuples = []
		self.smoothed_reward = None
		self.episode_n = 1
		self.episode_reward_sum = 0
		self.round_n = 1
		self.randomAgent = random_agent

		self.networkInput = []
		# Center of gravity
		self.cog = (0,0)
		self.rotations = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		self.prevMoves = []
		# Run counter
		self.counter = 0
		self.legcounter = 0
		# Total distance counter
		self.total = 0
		# Initial position
		self.c = None
		# Spawn position
		self.xy = xy
		self.won = 0
		self.lost = 0
		self.boundary = 400
		self.wait_lock = randint(0,1)
		# Valid run
		self.button = True
		self.max = 0
		# Reset Agent
		self.sensor = Sensor()
		self.other_agents = []
		self.other_agents_info = []
		self.random = [False, False, False, False, False, False, False]		
		self.reset(True, 0)
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		# Initialise the backup storage for the parts information with 0 values
		self.backup = []
		for k in range(0,15):
			self.backup.append(Part(0, 0, 0, False, 0, 0))
		self.step = 0
		self.counter_six = 0

	def randomize(self, limit):
		self.limit = limit
		print("Random", self.random, limit)


	# Reset agent
	def reset(self, stage, score):
		self.wait_lock = randint(0,1)
		self.interactive_dist = 0
		for i in range(7):
			if randint(0,100) > 60:
				self.random[i] = True
			else:
				self.random[i] = False
		parts = []
		self.failed = False
		self.randomize(0)
		self.randomAgent.nextGame()
		rand = randint(-30, 30) 
		parts.append(Part(rand, self.xy[0], self.xy[1], True, 50, 0))
		self.additional_random = [randint(-90, 90), randint(-90, 90), 0]
		rand += self.additional_random[0]
		parts.append(Part(rand, 0, 0, False, 50, 1))
		rand += self.additional_random[1]
		parts.append(Part(rand, 0, 0, False, 50, 2))
		for i in range(0, 2):
			rands = [randint(0, 360),randint(-90, 90)]
			parts.append(Part(rands[0], 0, 0, False, 12, 3 + i * 6))
			parts.append(Part(rands[0], 0, 0, False, 12, 4 + i * 6))
			parts.append(Part(rands[0], 0, 0, False, 12, 5 + i * 6))
			parts.append(Part(rands[0] + rands[1], 0, 0, False, 12, 6 + i * 6))
			parts.append(Part(rands[0] + rands[1], 0, 0, False, 12, 7 + i * 6))
			parts.append(Part(rands[0] + rands[1], 0, 0, False, 12, 8 + i * 6))


		parts[0].loadImage("image_resources/body.png")
		parts[1].loadImage("image_resources/body.png")
		parts[2].loadImage("image_resources/head.png")
		# Body parts and heads weight
		parts[0].setWeight(23.44)
		parts[1].setWeight(11.72)
		parts[2].setWeight(8.24)

		for l in range(3, 15):
			# Load the image files and set the constraints
			parts[l].loadImage("image_resources/leg_green.png")
			parts[l].setWeight(0.66)
		for l in range(9, 15):
			# Load the image files and set the constraints
			parts[l].loadImage("image_resources/leg_yellow.png")
		self.parts = parts
		self.setPositions(self.xy)
		self.setConstraints()

		if self.button == False:
			score = score - self.c[0]
			self.total = self.total + score

		self.sensor.setPositions(parts[0].getPivot(), parts[2].getPivot())
		self.button = True
		return self.collide(0)



	# Handles movement calculations
	def move(self, show):
		self.show = show
		run_finished = False
		if not self.stop:
			self.otherAgents()
			self.sensor_values, self.step = self.sensor.collisionCheck(self.wall.getPosition(), self.wall.getMask(), self.step)
			self.moves = []
			parts = self.parts
			pivot = parts[0].getPosition()
			pivot = self.gravity(pivot, 30)
			pivot = self.body_move(pivot)
			self.centerOfGravity(pivot)
			interactive_cog = self.getCog()[0]
			pivot, run_finished = self.leg_move(pivot)
			rotation = ((parts[3].getRotation() -  parts[9].getRotation()) % 360 - 179)


			if rotation < 2 and rotation > 0:
				self.wait_lock = 2


			self.centerOfGravity(pivot)
			self.interactive_dist += self.getCog()[0] - interactive_cog
			self.stored(True)
			self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
			pivot = (pivot[0], pivot[1] + 1.5)
			self.setPositions(pivot)
			self.collide(1)
			pivot = (pivot[0], pivot[1] - 1.5)
			self.stored(False)

			extra = 0
			# If the agents center of gravity is to the left of all its points of contacts fall to the left
			if self.box[0][0] != -1 and self.box[0][0] > self.cog[0] + 1:
				pivot, extra = self.fallRotation(pivot, True)
			# If the agents center of gravity is to the right of all its points of contacts fall to the right
			elif self.box[1][0] != -1 and self.box[1][0] < self.cog[0] - 1:
				pivot, extra = self.fallRotation(pivot, False)
			elif self.box[0][0] <= self.cog[0] + 1 and self.box[1][0] >= self.cog[0] - 1 and self.button:
				self.c = self.cog
				print("click")
				self.button = False
			self.setConstraints()
			if extra != 0:
				pivot = self.gravity(pivot, (extra) * 10)
			if show == 2:		
				print(self.moves)
			self.sensor.setPositions(parts[0].getPivot(), parts[2].getPivot())
		return run_finished

	def otherAgents(self):
		self.other_agents_info = []
		for i in range(len(self.other_agents)):
			for j in range(0,1):
				part = self.other_agents[i].parts[j]
				self.other_agents_info.append((part.getMask(), part.getPosition()[0], part.getPosition()[1]))

	def leg_move(self, pivot):
		parts = self.parts
		prevMoves = []
		for i in range(0,2):

			oldCog = self.getCog()[0]
			cog = self.getCog()[0]
			probabilities_top = None
			probabilities_bottom = None

			self.inputs(pivot, i * 2)
			if (self.random[i * 2] and RANDOM_ELEMENT) or self.round_n % 20 > 17:
				probabilities_top = self.randomAgent.move(self.networkInput)
			else:
				probabilities_top = self.network.forward_pass(self.networkInput)[0]


			self.inputs(pivot, (i * 2) + 1)
			if (self.random[(i * 2) + 1] and RANDOM_ELEMENT) or self.round_n % 20 > 17:
				probabilities_bottom = self.randomAgent.move(self.networkInput)
			else:
				probabilities_bottom = self.network.forward_pass(self.networkInput)[0]


			move_top = np.argmax(probabilities_top)
			move_top = 1
			if self.won < TRAINER_COUNTER:
				if self.additional_random[0] == 0 and self.additional_random[1] == 0 and not i == self.wait_lock:
					move_top = 0
				else:
					move_top = 1
			part_rotation = (parts[3 + (i * 6)].getRotation() + 90) % 360
			if self.step == 2:
				move_top = 0
			if self.step == 2:
				move_top = 1
			if self.step == 3 and part_rotation > 180:
				move_top = 0
			if self.step == 3 and part_rotation > 45 and part_rotation < 135:
				move_top = 1
			rotation_amount_top = move_top - 1

			move_bottom = np.argmax(probabilities_bottom)
			if self.won < TRAINER_COUNTER:
				if self.additional_random[0] == 0 and self.additional_random[1] == 0:
					move_bottom = 0
				else:
					move_bottom = 1

			if self.step == 3 and self.legcounter < 180:
				move_bottom = 2
				self.legcounter += 1
			elif self.step == 3:
				move_bottom = 1
			rotation_amount_bottom = move_bottom - 1 + rotation_amount_top
			self.moves.append(move_top)
			self.moves.append(move_bottom)
			for j in range(3):
				oldPivot = (pivot[0], pivot[1])
				partNum = (i * 6) + j + 3

				self.stored(True)
				self.setConstraints()
				parts[partNum].rotation(rotation_amount_top, False)
				parts[partNum + 3].rotation(rotation_amount_bottom, False)

				self.setPositions(pivot)
				resetGravity = 0

				if self.collide(1):
					self.stored(False)
					distChange = self.interactiveMove(partNum, rotation_amount_top, rotation_amount_bottom, self.getCog())
					pivot = (pivot[0] + distChange[0], pivot[1] + distChange[1])



					if self.collide(1):
						pivot = (pivot[0], pivot[1] - 2)
						self.setPositions(pivot)

						if self.collide(1):
							self.stored(False)
							pivot = (oldPivot[0], oldPivot[1])
						else:
							resetGravity = 30
					else:
						resetGravity = 10

					if resetGravity is not 0:
						pivot = self.gravity(pivot, resetGravity)
						prevMoves.append((partNum, distChange[0]))

				if resetGravity == 0:
					for z in range(len(self.prevMoves)):
						if self.prevMoves[z][0] == partNum:
							pivot = (pivot[0] - self.prevMoves[z][1], pivot[1] - 1.0)
							self.setPositions(pivot)
							if self.collide(1):
								self.stored(False)
								pivot = (pivot[0] + self.prevMoves[z][1], pivot[1] + 1.0)
								print("Fail, Previous move could not be reverted")
							else:
								pivot = self.gravity(pivot, 10)

				run_finished = self.ended(move_top, self.button, partNum)
				run_finished = self.ended(move_bottom, self.button, partNum + 3)
		self.prevMoves = prevMoves
		return pivot, run_finished




	def body_move(self, pivot):
		parts = self.parts
		banned = None
		for i in range(4,7):

			probabilities = None
			self.inputs(pivot, i)
			if (self.random[i] and RANDOM_ELEMENT) or self.round_n % 20 > 17:
				probabilities = self.randomAgent.move(self.networkInput)
			else:
				probabilities = self.network.forward_pass(self.networkInput)[0]

			move = np.argmax(probabilities)
			if self.won < TRAINER_COUNTER:
				move = 1
				if self.additional_random[0] == 0 and self.additional_random[1] == 0 and self.additional_random[2] < 60:
					if i == 5:
						move = 2
					elif i == 6:
						move = 2
						self.additional_random[2] += 1
				else:
					if i == 5:
						if self.additional_random[0] > 0:
							self.additional_random[0] -= 1
							move = 0
						elif self.additional_random[0] < 0:
							self.additional_random[0] += 1
							move = 2
					elif i == 6:
						if self.additional_random[1] > 0:
							self.additional_random[1] -= 1
							move = 0
						elif self.additional_random[1] < 0:
							self.additional_random[1] += 1
							move = 2


			if i == 5 and move == banned:
				probabilities[move] = 0
				move = np.argmax(probabilities)
			if self.step == 1 and i == 5 and parts[1].getRotation() > 10:
				move = 0
			if self.step == 1 and i == 6 and parts[2].getRotation() > 180:
				move = 2
			if parts[1].getRotation() <= 10 and self.step == 1 and (self.sensor_values[0] > 0.2 or self.sensor_values[1] > 0.2):
				self.step = 2
			if self.step == 2:
				move = 1
			if self.step == 2 and i == 4 and (self.parts[0].getRotation() - self.parts[1].getRotation() + 61) % 360 > 2:
				move = 2
			elif self.step == 2 and i == 5:
				move = 1
			elif self.step == 2 and i == 6:
				self.counter_six += 1
				if self.counter_six < 90:
					move = 0
			if self.step == 2 and (self.parts[0].getRotation() - self.parts[1].getRotation() + 5) % 360 < 10:
				self.step = 3
			if self.step == 3 and i == 4:
				if self.parts[0].getRotation() < 25 or self.parts[0].getRotation() > 240:
					move = 2
			elif self.step == 3 and i == 5:
				if self.parts[1].getRotation() < 180 and self.parts[1].getRotation() > 1:
					move = 0
				elif self.parts[1].getRotation() < 360 and self.parts[1].getRotation() > 180:
					move = 2
			elif self.step == 3 and i == 6:
				if self.parts[2].getRotation() < 180 and self.parts[2].getRotation() > 1:
					move = 0
				elif self.parts[2].getRotation() < 360 and self.parts[2].getRotation() > 180:
					move = 2
			if self.step == 3 and (parts[3].getRotation() + 90) % 360 < 180 and (parts[9].getRotation() + 90) % 360 < 180 and parts[0].getRotation() < 40:
				move = 2

			self.moves.append(move)
			rotation_amount = move - 1

			oldPivot = (pivot[0], pivot[1])
			partNum = i - 4

			self.stored(True)
			self.setConstraints()
			parts[partNum].rotation(rotation_amount, False)
			if i == 4:
				torso_position = parts[1].getPosition()
				self.setPositions(pivot)
				new_torso_position = parts[1].getPosition()
				new_torso_position = (new_torso_position[0] - torso_position[0], new_torso_position[1] - torso_position[1])
				pivot = (pivot[0] - new_torso_position[0], pivot[1] - new_torso_position[1])
				if move is not 1 and new_torso_position[0] is not 0:
					banned = move
			elif i == 5:
				parts[2].rotation(rotation_amount, False)

			self.setPositions(pivot)


			resetGravity = 0


			if self.collide(1):
				pivot = (pivot[0], pivot[1] - 2)
				self.setPositions(pivot)

				if self.collide(1):
					self.stored(False)
					pivot = (oldPivot[0], oldPivot[1])
				else:
					resetGravity = 30
			elif move is not 1:
				resetGravity = 10

			if resetGravity is not 0:
				pivot = self.gravity(pivot, resetGravity)
			self.ended(move, self.button, partNum)
		return pivot



	def ended(self, move, button, partNum):
		if not button and (move < 30 or fail):
			score = self.getCog()[0] - self.c[0]
			reward = 0
			if partNum == 14 and self.interactive_dist > self.boundary:
				rotation_constraint_one = abs((self.parts[0].getRotation() + 15) % 180)
				rotation_constraint_two = abs((self.parts[2].getRotation() + 15) % 180)
				print("Constraints: ", rotation_constraint_one)
				if rotation_constraint_one < 30 and rotation_constraint_two < 30:
					reward = 0.999
					self.won += 1
				else:
					reward = -0.999
					self.lost += 1

			elif partNum == 14 and (self.interactive_dist < -20 or self.limit >= 40):
				reward = -0.999
				self.lost += 1				

			output = [0,0,0]
			output[move] = 1

			self.episode_reward_sum += reward
			tup = (self.networkInput, output, reward)
			self.batch_state_action_reward_tuples.append(tup)
			if partNum == 14:
				if reward < 0:
					print("Round %d; Score: %0.3f, Reward: %0.3f,  lost..." % (self.round_n, score, reward))
				elif reward > 0:
					print("Round %d: Score: %0.3f, Reward: %0.3f, won!" % (self.round_n, score, reward))
				if reward != 0:
					print("Boundary:", self.boundary)
					print("Interactive:", self.interactive_dist)
					print("============================")
					if score > self.max:
						self.max = score
					self.reward = reward
					self.round_n += 1
					self.n_steps = 0
					return True
		return False

	def finishEpisode(self):
		#if self.won > 15:
		#	self.boundary += 40
		#if self.won == 0 and self.boundary > 100:
		#	self.boundary -= 20
		print("Self Boundary", self.boundary)
		print("Episode %d finished after %d rounds" % (self.episode_n, self.round_n))
		print("Current max score:", self.max)
		print("Won:", self.won, "Lost:", self.lost)
		# exponentially smoothed version of reward
		if self.smoothed_reward is None:
			self.smoothed_reward = self.episode_reward_sum
		else:
			self.smoothed_reward = self.smoothed_reward * 0.99 + self.episode_reward_sum * 0.01
		print("Reward total was %.3f; discounted moving average of reward is %.3f" \
			% (self.episode_reward_sum, self.smoothed_reward))

		if self.episode_n % self.args.batch_size_episodes == 0:
			states, actions, rewards = zip(*self.batch_state_action_reward_tuples)
			rewards = self.network.discount_rewards(rewards, self.args.discount_factor)
			rewards -= np.mean(rewards)
			rewards /= np.std(rewards)
			self.batch_state_action_reward_tuples = list(zip(states, actions, rewards))
			self.network.train(self.batch_state_action_reward_tuples)
			self.batch_state_action_reward_tuples = []

		if self.episode_n % self.args.checkpoint_every_n_episodes == 0:
			self.network.save_checkpoint()

		self.won = 0
		self.lost = 0
		self.episode_n += 1
		self.episode_reward_sum = 0


	def inputs(self, pivot, turn):
		parts = self.parts

		netInputs = []
		netInputs.append(parts[0].getRotation() / 360.0)
		netInputs.append(parts[1].getRotation() / 360.0)
		netInputs.append(parts[2].getRotation() / 360.0)

		greenRotation = parts[3].getRotation()
		netInputs.append(greenRotation / 360.0)
		greenRotation = (greenRotation - parts[6].getRotation() + 90) % 360
		netInputs.append(greenRotation / 180.0)



		yellowRotation = parts[9].getRotation()
		netInputs.append(yellowRotation / 360.0)
		yellowRotation = (yellowRotation - parts[12].getRotation() + 90) % 360
		netInputs.append(yellowRotation / 180.0)

		for j in range(7):
			if j == turn:
				netInputs.append(1)
			else:
				netInputs.append(0)

		self.networkInput = netInputs


	# When the agent pushes off with a leg the rest of its body should follow
	def interactiveMove(self, part_num, direction_top, direction_bottom, cog):
		colliding = self.colliding
		parts = self.parts
		initialPos = parts[part_num].getPivot()

		distance = (initialPos[0] - colliding[0][0], initialPos[1] - colliding[0][1])
		hypD = math.sqrt(distance[0] * distance[0] + distance[1] * distance[1])

		rotation = (math.atan(distance[0] / distance[1]) * 180.0 / math.pi) - direction_top
		newPos = (hypD * math.sin(rotation * math.pi / 180.0), hypD * math.cos(rotation * math.pi / 180.0))

		newPos = (newPos[0] + distance[0], newPos[1] + distance[1] - 1.0)


		parts[part_num].rotation(direction_top, False)
		parts[part_num + 3].rotation(direction_bottom, False)

		pivot = parts[0].getPosition()
		self.setPositions(pivot)
		self.centerOfGravity(pivot)
		cog = cog[0] - self.getCog()[0]

		return newPos


		#print("final", self.collide(False))
	# When the agent is hanging on an edge over its center of gravity it should tip in that direction
	def fallRotation(self, pivot, left):
		#print("--------------")
		parts = self.parts
		distanceXY = None
		torque = None
		pointOfContact = None
		if left:
			pointOfContact = (self.box[0][0], self.box[0][1])
		else:
			pointOfContact = (self.box[1][0], self.box[1][1])

		distanceXY = (self.cog[0] - pointOfContact[0] , pointOfContact[1] - self.cog[1])
		torque = distanceXY[0] / 25
		#print("Initial Pivot:", pivot)
		#print("Point of Contact:", pointOfContact)
		#print("Initial Center Of Gravity:", self.cog)
		#print("Initial Distance:", distanceXY)
		#print("Torque:", torque)


		self.stored(True)
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		pivot = (pivot[0], pivot[1] + 3)
		self.setPositions(pivot)
		self.collide(1)
		pivot = (pivot[0], pivot[1] - 3)
		self.stored(False)
		#if self.box[0][0] != self.box[1][0]:
		#	print(self.box[0][0] - self.box[1][0])
		#	print(torque)

		# X,Y distances between the agents point of contact with the world and the agents main pivot point.
		# (The pivot is where the agent bases all calculations from and is the rotation point for its back)
		# Torque is the distance the agents center of gravity is from the collision point being used
		# If the agent is falling to the left use the left most collision point otherwise use the rightmost

		# Actual distance between the agents point of contact with the world and the agents main pivot point
		distanceH = math.sqrt(distanceXY[0] * distanceXY[0] + distanceXY[1] * distanceXY[1])
		#print("Hypotenuse:", distanceH)
		# The angle between the collision point being used and the agents pivot point. The agent will be rotated around the point of collision
		# since when you fall you fall around the last place you were touching the ground
		currentAngle = None
		if(distanceXY[0] == 0):
			currentAngle = 90
		else:
			currentAngle = math.atan(distanceXY[1]/distanceXY[0]) * 180.0 / math.pi
		if currentAngle < 0:
			currentAngle = 180 + currentAngle
		newAngle = currentAngle - torque
		#print("CurrentAngle:", currentAngle)
		#print("newAnge:", newAngle)




		# The X,Y distances between the agents point of contact with the world and where the agents main pivot point will be after the rotation
		newXY = (distanceH * math.cos(newAngle / 180 * math.pi), (distanceH * math.sin(newAngle / 180 * math.pi)))
		newCog = (pointOfContact[0] + newXY[0], pointOfContact[1] - newXY[1])
		#print("newXY", newXY)
		#print("newCog", newCog)
		self.stored(True)
		self.rotateAll(-torque)
		self.setPositions(pivot)
		self.centerOfGravity(pivot)

		cogDiff = (newCog[0] - self.cog[0], newCog[1] - self.cog[1])
		#print("Middle Cog", self.cog)
		#print("Cog Diff", cogDiff)
		newPivot = (pivot[0] + cogDiff[0], pivot[1] + cogDiff[1] - 2)
		#print("newPivot", newPivot)
		self.setPositions(newPivot)

		if self.collide(1):
			self.stored(False)
			#print("Collided, Reseting")
			#print("==================")
			return pivot, 0
		else:
			#print("Did not collide")
			#print("==================")
			return newPivot, 20

	# Rotate entire agent
	def rotateAll(self, amount):
		for iterate in range(0,15):
			self.parts[iterate].rotation(amount, True)

	# Agent is affected by gravity
	def gravity(self, pivot, amount):
		# Decrement multiple times instead of just lowering once since this way if it collides in the middle it will go as close as possible
		for i in range(0,amount):
			# Store a copy of the agent
			self.stored(True)
			# Lower the agent by 1
			pivot = (pivot[0], pivot[1] + 0.1)
			self.setPositions(pivot)
			# If the agent collides with the world revert the move
			if self.collide(1):
				self.stored(False)
				# Reset the pivot if the agent is reset
				pivot = (pivot[0], pivot[1] - 0.1)
				break
		return pivot

	# Calculate the agents center of gravity
	def centerOfGravity(self, pivot):
		parts = self.parts
		self.cog = (0,0)
		centers = []
		weight = 0
		# Agents co-ordinate
		pos = parts[0].getPosition()
		# Convert each parts current angle to a 2D vector
		partRotations = []
		for q in range(0,15):
			if q < 3:
				partRotations.append((math.cos(parts[q].getRotation() / 180 * math.pi), math.sin((180.0 + parts[q].getRotation()) / 180 * math.pi)))
			else:
				partRotations.append((math.cos((parts[q].getRotation() - 90) / 180 * math.pi), math.sin((180.0 + (parts[q].getRotation() - 90)) / 180 * math.pi)))

		# Find the center points of each part
		# Calculated by finding the connecting part to the body which is the center point (find top left of image then add half the image width)
		# then calculate the parts rotation and multiply it by the number of pixels away the center of the part is from the images center
		centers.append((pos[0] + (partRotations[0][0] * 17.0) + 50, pos[1] + (partRotations[0][1] * 17.0) + 50))
		centers.append((pos[0] + (partRotations[0][0] * 39.0) + (partRotations[1][0] * 17.0) + 50, pos[1] + (partRotations[0][1] * 39.0) + (partRotations[1][1] * 17.0) + 50))
		centers.append((pos[0] + (partRotations[0][0] * 39.0) + (partRotations[1][0] * 39.0) + (partRotations[2][0] * 9.0) + 50, pos[1] + (partRotations[0][1] * 39.0) + (partRotations[1][1] * 39.0) + (partRotations[2][1] * 9.0) + 50))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[3][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[3][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[4][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[4][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[5][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[5][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[3][0] * 12) + (partRotations[6][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[3][1] * 12) + (partRotations[6][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[4][0] * 12) + (partRotations[7][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[4][1] * 12) + (partRotations[7][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[5][0] * 12) + (partRotations[8][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[5][1] * 12) + (partRotations[8][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[9][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[9][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[10][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[10][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[11][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[11][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 12) + (partRotations[9][0] * 12) + (partRotations[12][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 12) + (partRotations[9][1] * 12) + (partRotations[12][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[10][0] * 12) + (partRotations[13][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[10][1] * 12) + (partRotations[13][1] * 5) + 13))
		centers.append((pos[0] + 38 + (partRotations[0][0] * 39) + (partRotations[1][0] * 27) + (partRotations[11][0] * 12) + (partRotations[14][0] * 5) + 13, pos[1] + 40 + (partRotations[0][1] * 39) + (partRotations[1][1] * 27) + (partRotations[11][1] * 12) + (partRotations[14][1] * 5) + 13))
		
		# Add all parts center of gravity multiplied by there specific weight
		for i in range(0,15):
			self.cog = (self.cog[0] + (centers[i][0] * parts[i].getWeight()), self.cog[1] + (centers[i][1] * parts[i].getWeight()))
			weight += parts[i].getWeight()
		# Divide by the total weight of the agent
		self.cog = (self.cog[0] / weight, self.cog[1] / weight)




	# If setup is true store a copy of the agent otherwise replace the current agents details with the stored copy
	def stored(self, setup):
		one = []
		two = []
		if setup:
			two = self.parts
			one = self.backup
		else:
			two = self.backup
			one = self.parts
		for k in range(0,15):
			one[k].setPosition(two[k].getPosition())
			one[k].setConstraint(two[k].getConstraint())
			one[k].setRotation(two[k].getRotation(), False)
			if not setup:
				one[k].rotation(0, False)
	
	# Set the constraints of each part
	def setConstraints(self):
		parts = self.parts
		parts[0].setConstraint(parts[1].getRotation())
		parts[1].setConstraint(parts[0].getRotation())
		parts[2].setConstraint(parts[1].getRotation())
		for i in range(0,2):
			offset = i * 6
			parts[3 + offset].setConstraint(-1)
			parts[4 + offset].setConstraint(-1)
			parts[5 + offset].setConstraint(-1)
			parts[6 + offset].setConstraint(parts[3 + offset].getRotation())
			parts[7 + offset].setConstraint(parts[4 + offset].getRotation())
			parts[8 + offset].setConstraint(parts[5 + offset].getRotation())

	# Sets all the parts positions with regards to the agents pivot
	def setPositions(self, pivot):
		parts = self.parts
		# Rotation of the agents abdominal segments
		backRotation = (math.cos(parts[0].getRotation() / 180 * math.pi), math.sin((180.0 + parts[0].getRotation()) / 180 * math.pi))
		frontRotation = (math.cos(parts[1].getRotation() / 180 * math.pi), math.sin((180.0 + parts[1].getRotation()) / 180 * math.pi))
		# Back abdominal segment
		parts[0].setPosition(pivot)
		pos = parts[0].getPosition()
		# Front abdominal segment
		parts[1].setPosition((pos[0] + (backRotation[0] * 39.0), pos[1] + (backRotation[1] * 39.0)))
		# Head
		parts[2].setPosition((pos[0] + (backRotation[0] * 39.0) + (frontRotation[0] * 39.0), pos[1] + (backRotation[1] * 39.0) + (frontRotation[1] * 39.0)))
		for i in range(0,2):
			offset = i * 6
			# Back leg (top)
			parts[3 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 12), pos[1] + 40 + (backRotation[1] * 12)))
			legRotation = (math.sin(parts[3 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + parts[3 + offset].getRotation()) / 180 * math.pi))
			# Back leg (bottom)
			parts[6 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 12) + (legRotation[0] * 11.5), pos[1] + 40 + (backRotation[1] * 12) + (legRotation[1] * 11.5)))
			# Middle leg (top)
			parts[4 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39), pos[1] + 40 + (backRotation[1] * 39)))
			legRotation = (math.sin(parts[4 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + parts[4 + offset].getRotation()) / 180 * math.pi))
			# Middle leg (bottom)
			parts[7 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39) + (legRotation[0] * 11.5), pos[1] + 40 + (backRotation[1] * 39) + (legRotation[1] * 11.5)))
			# Front leg (top)
			parts[5 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39) + (frontRotation[0] * 27), pos[1] + 40 + (backRotation[1] * 39) + (frontRotation[1] * 27)))
			# Front leg (bottom)
			legRotation = (math.sin(parts[5 + offset].getRotation() / 180 * math.pi), -math.cos((180.0 + parts[5 + offset].getRotation()) / 180 * math.pi))
			parts[8 + offset].setPosition((pos[0] + 38 + (backRotation[0] * 39) + (legRotation[0] * 11.5) + (frontRotation[0] * 27), pos[1] + 40 + (backRotation[1] * 39)  + (legRotation[1] * 11.5)+ (frontRotation[1] * 27)))

	# Handles Collisions between the ant and the world
	def collide(self, ignore):
		parts = self.parts
		objects = []
		for i in range(len(self.objects)):
			objects.append(self.objects[i])
		for i in range(len(self.other_agents_info)):
			objects.append(self.other_agents_info[i])

		colliding = []
		selfCollide = []
		ret = False
		# For legs check if they are colliding with other legs from the same ant. Body parts are behind the legs so they can overlap
		# But an agent cannot cross its legs
		for position in range(0,15):
			# HERE
			if ignore % 2 == 0:
				if position > 2 and position < 9:
					for j in range(3,9):
						# Dont check collisions when the 2 parts are from the same leg. E.g "Thigh" and "Calf"
						if (position % 3) != (j % 3):			
							offset = (int(parts[position].getPosition()[0] - parts[j].getPosition()[0]), int(parts[position].getPosition()[1] - parts[j].getPosition()[1]))
							result = parts[j].getMask().overlap(parts[position].getMask(), offset)
							# If they collide return true
							if result:
								ret = True
								if position < j:
									selfCollide.append((position, j))
				elif position > 8:
					for j in range(9,15):
						# Dont check collisions when the 2 parts are from the same leg. E.g "Thigh" and "Calf"
						if (position % 3) != (j % 3):			
							offset = (int(parts[position].getPosition()[0] - parts[j].getPosition()[0]), int(parts[position].getPosition()[1] - parts[j].getPosition()[1]))
							result = parts[j].getMask().overlap(parts[position].getMask(), offset)
							# If they collide return true
							if result:
								ret = True
								if position < j:
									selfCollide.append((position, j))
			# TO HERE
			if ignore < 2:
				# Check collisions against all the other objects in the world which exclude itself
				for k in range(len(objects)):
					offset = (int(objects[k][1] - parts[position].getPosition()[0]), int(objects[k][2] - parts[position].getPosition()[1]))
					result = parts[position].getMask().overlap(objects[k][0], offset)
					if result:
						self.collisionBox((parts[position].getPosition()[0] + result[0], parts[position].getPosition()[1] + result[1]))
						colliding.append((parts[position].getPosition()[0] + result[0], parts[position].getPosition()[1] + result[1]))
						ret = True
						#if position < 3:
						#	self.failed = True
		self.selfCollide = selfCollide
		self.colliding = colliding
		return ret



	# Creates a parallelogram around the agent with the corners being the collision points with the highest and lowest x and y values
	# used for calculating gravity and if the agents center of gravity is over an edge (in which case it will fall)
	def collisionBox(self, point):
		# Lowest x value
		if self.box[0][0] == -1 or point[0] < self.box[0][0]:
			self.box[0] = point
		# Highest x value
		if self.box[1][0] == -1 or (point[0] > self.box[1][0] and self.box[1][0] != -1):
			self.box[1] = point
		# Lowest y value
		if self.box[2][1] == -1 or point[1] < self.box[2][1]:
			self.box[2] = point
		# Highest y value
		if self.box[3][1] == -1 or (point[1] > self.box[3][1] and self.box[3][1] != -1):
			self.box[3] = point

	# Add an object in the environment so the ant is aware of the world
	def addObject(self, obj):
		self.objects.append(obj)

	# Add an object in the environment so the ant is aware of the world
	def addOtherAgent(self, agent):
		self.other_agents.append(agent)

	# Draw all the images
	def run(self, DS):
		parts = self.parts
		for i in range(0,9):
			DS.blit(parts[i].getImage(), parts[i].getPosition())
		for i in range(9,15):
			DS.blit(parts[i].getImage(), parts[i].getPosition())

	# Return an array of all the individual ant parts
	def getParts(self):
		return self.parts

	# Return the agents center of gravity
	def getCog(self):
		return self.cog

	# Retrun any markers that should be drawn on screen
	def getMarkers(self):
		return self.box

	def setRotations(self, rotations):
		for i in range(len(rotations)):
			self.parts[i].setRotation(rotations[i], True)
