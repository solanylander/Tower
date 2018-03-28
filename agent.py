import math, random, sys, pygame
from pygame.locals import *
from part import Part
from agent_parts import Parts
from sensor import Sensor
from random import *
import pickle
import time
import numpy as np

MAX_BODY_ROTATION = 90
RANDOM_ELEMENT = False
TRAINER_COUNTER = 5

class Agent:

	def __init__(self, xy, args, wall, network, random_agent, agent_num):
		# Which body parts are currently colliding
		self.wall = wall
		self.agent_num = agent_num
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
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
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
		self.boundary = 40000
		# Valid run
		self.button = True
		self.max = 0
		# Reset Agent
		self.sensor = Sensor()
		self.other_agents = []
		self.other_agents_info = []
		self.random = [False, False, False, False, False, False, False]	
		self.backup = Parts(True, None, None)	
		self.reset(True, 0)
		# Initialise the backup storage for the parts information with 0 values

	def randomize(self, limit):
		self.limit = limit
		print("Random", self.random, limit)
		if not (self.limit == 0):
			score = self.cog[0] - self.score_tracker
			print("Agent Num:", self.agent_num, "Score:", score)
			self.score_tracker = self.cog[0]


			if score < 1:
				print("ended")
				self.stop = True





	# Reset agent
	def reset(self, stage, score):
		self.interactive_dist = 0
		for i in range(7):
			if randint(0,100) > 60:
				self.random[i] = True
			else:
				self.random[i] = False
		self.failed = False
		self.randomize(0)
		self.randomAgent.nextGame()
		self.additional_random = [randint(-90,90), randint(-90, 90), 0]
		self.parts = Parts(False, self.additional_random, self.xy)
		self.array = self.parts.parts
		self.parts.load_pair(self.backup)
		self.backup.load_pair(self.parts)
		self.parts.setPositions(self.xy)
		self.cog = self.parts.centerOfGravity(self.xy)
		self.score_tracker = self.cog[0]

		self.parts.setConstraints()

		if self.button == False:
			score = score - self.c[0]
			self.total = self.total + score

		self.sensor.setPositions(self.parts.parts[0].getPivot(), self.parts.parts[2].getPivot())
		self.button = True
		return self.collide(0)



	# Handles movement calculations
	def move(self, show):
		self.show = show
		parts = self.array
		run_finished = False
		if not self.stop:
			self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
			self.otherAgents()
			self.target = False
			self.sensor_values = (0,0)
			for i in range(len(self.other_agents_info)):
				agent_part_pos = (self.other_agents_info[i][1], self.other_agents_info[i][2])
				agent_sensor_values = self.sensor.collisionCheck(agent_part_pos, self.other_agents_info[i][0])
				if (agent_sensor_values[0] > self.sensor_values[0]):
					self.sensor_values = (agent_sensor_values[0], self.sensor_values[1])
				if (agent_sensor_values[1] > self.sensor_values[1]):
					self.sensor_values = (self.sensor_values[0], agent_sensor_values[1])


			sensor_values = self.sensor.collisionCheck(self.wall.getPosition(), self.wall.getMask())
			if (sensor_values[0] >= self.sensor_values[0]) and not (sensor_values[0] == 0):
				self.target = True
				self.sensor_values = (sensor_values[0], self.sensor_values[1])
			if (sensor_values[1] >= self.sensor_values[1]) and not (sensor_values[1] == 0):
				self.target = True
				self.sensor_values = (self.sensor_values[0], sensor_values[1])
			self.moves = []
			pivot = self.parts.parts[0].getPosition()
			pivot = self.gravity(pivot, 30)
			pivot = self.body_move(pivot)
			self.cog = self.parts.centerOfGravity(pivot)
			interactive_cog = self.cog[0]
			pivot, run_finished = self.leg_move(pivot)

			rotation = ((self.parts.parts[3].getRotation() -  self.parts.parts[9].getRotation()) % 360 - 179)
			self.cog = self.parts.centerOfGravity(pivot)
			self.interactive_dist += self.cog[0] - interactive_cog
			self.backup.duplicate()
			self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
			pivot = (pivot[0], pivot[1] + 1.5)
			self.parts.setPositions(pivot)
			self.collide(1)
			pivot = (pivot[0], pivot[1] - 1.5)
			self.parts.duplicate()
			extra = 0
			# If the agents center of gravity is to the left of all its points of contacts fall to the left

			if self.box[0][0] != -1 and self.box[0][0] > self.cog[0]:
				pivot, extra = self.fallRotation(pivot, True)
			# If the agents center of gravity is to the right of all its points of contacts fall to the right
			elif self.box[1][0] != -1 and self.box[1][0] < self.cog[0]:
				pivot, extra = self.fallRotation(pivot, False)
			elif self.box[0][0] <= self.cog[0] + 1 and self.box[1][0] >= self.cog[0] - 1 and self.button:
				self.c = self.cog
				print("click")
				self.button = False

			self.parts.setConstraints()
			if extra != 0:
				pivot = self.gravity(pivot, (extra) * 10)
			if show == 2:		
				print(self.moves)
			self.sensor.setPositions(self.parts.parts[0].getPivot(), self.parts.parts[2].getPivot())
		return run_finished

	def otherAgents(self):
		self.other_agents_info = []
		for i in range(len(self.other_agents)):
			for j in range(0,3):
				part = self.other_agents[i].parts.parts[j]
				self.other_agents_info.append((part.getMask(), part.getPosition()[0], part.getPosition()[1]))

	def leg_move(self, pivot):
		parts = self.parts
		prevMoves = []
		move_top, move_bottom = None, None

		for i in range(0,2):

			oldCog = self.cog[0]
			cog = self.cog[0]

			self.networkInput = self.parts.inputs(pivot, i * 2, self.sensor_values, self.target)
			if False:
				probabilities_top = None
				probabilities_bottom = None

				if (self.random[i * 2] and RANDOM_ELEMENT) or self.round_n % 20 > 17:
					probabilities_top = self.randomAgent.move(self.networkInput)
				else:
					probabilities_top = self.network.forward_pass(self.networkInput)[0]

				self.networkInput = self.parts.inputs(pivot, (i * 2) + 1, self.sensor_values, self.target)
				if (self.random[(i * 2) + 1] and RANDOM_ELEMENT) or self.round_n % 20 > 17:
					probabilities_bottom = self.randomAgent.move(self.networkInput)
				else:
					probabilities_bottom = self.network.forward_pass(self.networkInput)[0]

				move_top = np.argmax(probabilities_top)
				move_bottom = np.argmax(probabilities_bottom)
			else:
				move_top = self.parts.training_move_leg(self.networkInput)
				self.networkInput = self.parts.inputs(pivot, (i * 2) + 1, self.sensor_values, self.target)
				move_bottom = self.parts.training_move_leg(self.networkInput)

			rotation_amount_top = move_top - 1
			rotation_amount_bottom = move_bottom - 1 + rotation_amount_top

			self.moves.append(move_top)
			self.moves.append(move_bottom)
			for j in range(3):
				oldPivot = (pivot[0], pivot[1])
				partNum = (i * 6) + j + 3

				self.backup.duplicate()
				self.parts.setConstraints()
				parts.parts[partNum].rotation(rotation_amount_top, False)
				parts.parts[partNum + 3].rotation(rotation_amount_bottom, False)

				self.parts.setPositions(pivot)
				resetGravity = 0

				if self.collide(1):
					self.parts.duplicate()
					distChange = self.parts.interactiveMove(partNum, rotation_amount_top, rotation_amount_bottom, self.cog, self.colliding)
					self.cog = self.parts.centerOfGravity(pivot)
					pivot = (pivot[0] + distChange[0], pivot[1] + distChange[1])



					if self.collide(1):
						pivot = (pivot[0], pivot[1] - 2)
						self.parts.setPositions(pivot)

						if self.collide(1):
							self.parts.duplicate()
							pivot = (oldPivot[0], oldPivot[1])
						else:
							resetGravity = 30
					else:
						resetGravity = 10

					if resetGravity is not 0:
						pivot = self.gravity(pivot, resetGravity)
						prevMoves.append((partNum, distChange[0], move_top))

				if resetGravity == 0:
					for z in range(len(self.prevMoves)):
						if self.prevMoves[z][0] == partNum and abs(move_top - self.prevMoves[z][2]) == 2:
							pivot = (pivot[0] - self.prevMoves[z][1], pivot[1] - 1.0)
							self.parts.setPositions(pivot)
							if self.collide(1):
								self.parts.duplicate()
								pivot = (pivot[0] + self.prevMoves[z][1], pivot[1] + 1.0)
								print("Fail, Previous move could not be reverted")
							else:
								pivot = self.gravity(pivot, 10)

				run_finished = self.ended(move_top, self.button, partNum)
				run_finished = self.ended(move_bottom, self.button, partNum + 3)
		self.prevMoves = prevMoves
		return pivot, run_finished

	def body_move(self, pivot):
		parts = self.array
		banned = None
		for i in range(4,7):
			move = None
			self.networkInput = self.parts.inputs(pivot, i, self.sensor_values, self.target)
			if False:
				probabilities = None
				if (self.random[i] and RANDOM_ELEMENT) or self.round_n % 20 > 17:
					probabilities = self.randomAgent.move(self.networkInput)
				else:
					probabilities = self.network.forward_pass(self.networkInput)[0]

				move = np.argmax(probabilities)
			else:
				move = self.parts.training_move_body(self.networkInput)

			self.moves.append(move)
			rotation_amount = move - 1

			oldPivot = (pivot[0], pivot[1])
			partNum = i - 4

			self.backup.duplicate()
			self.parts.setConstraints()
			parts[partNum].rotation(rotation_amount, False)
			if i == 4:
				torso_position = parts[1].getPosition()
				self.parts.setPositions(pivot)
				new_torso_position = parts[1].getPosition()
				new_torso_position = (new_torso_position[0] - torso_position[0], new_torso_position[1] - torso_position[1])
				pivot = (pivot[0] - new_torso_position[0], pivot[1] - new_torso_position[1])
				if move is not 1 and new_torso_position[0] is not 0:
					banned = move
			elif i == 5:
				parts[2].rotation(rotation_amount, False)

			self.parts.setPositions(pivot)
			resetGravity = 0
			if self.collide(1):
				pivot = (pivot[0], pivot[1] - 2)
				self.parts.setPositions(pivot)

				if self.collide(1):

					pivot = (pivot[0] - 1, pivot[1])
					self.parts.setPositions(pivot)

					if self.collide(1):
						pivot = (pivot[0] - 1, pivot[1])
						self.parts.setPositions(pivot)

						if self.collide(1):
							self.parts.duplicate()
							pivot = (oldPivot[0], oldPivot[1])
						else:
							resetGravity = 30
					else:
						resetGravity = 30
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
			score = self.cog[0] - self.c[0]
			reward = 0
			if partNum == 14 and self.interactive_dist > self.boundary:
				rotation_constraint_one = abs((self.parts.parts[0].getRotation() + 15) % 180)
				rotation_constraint_two = abs((self.parts.parts[2].getRotation() + 15) % 180)
				print("Constraints: ", rotation_constraint_one)
				if rotation_constraint_one < 30 and rotation_constraint_two < 30:
					reward = 0.999
					self.won += 1
				else:
					reward = -0.999
					self.lost += 1

			elif partNum == 14 and (self.interactive_dist < -20 or self.limit >= 40000):
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

	# When the agent is hanging on an edge over its center of gravity it should tip in that direction
	def fallRotation(self, pivot, left):

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

		self.backup.duplicate()
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		pivot = (pivot[0], pivot[1] + 3)
		self.parts.setPositions(pivot)
		self.collide(1)
		pivot = (pivot[0], pivot[1] - 3)
		self.parts.duplicate()
		# X,Y distances between the agents point of contact with the world and the agents main pivot point.
		# (The pivot is where the agent bases all calculations from and is the rotation point for its back)
		# Torque is the distance the agents center of gravity is from the collision point being used
		# If the agent is falling to the left use the left most collision point otherwise use the rightmost

		# Actual distance between the agents point of contact with the world and the agents main pivot point
		distanceH = math.sqrt(distanceXY[0] * distanceXY[0] + distanceXY[1] * distanceXY[1])
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

		# The X,Y distances between the agents point of contact with the world and where the agents main pivot point will be after the rotation
		newXY = (distanceH * math.cos(newAngle / 180 * math.pi), (distanceH * math.sin(newAngle / 180 * math.pi)))
		if pointOfContact[1] < self.cog[1]:
			newXY = (-newXY[0], -newXY[1])
		newCog = (pointOfContact[0] + newXY[0], pointOfContact[1] - newXY[1])
		self.backup.duplicate()
		self.parts.rotateAll(-torque)
		self.parts.setPositions(pivot)
		self.cog = self.parts.centerOfGravity(pivot)
		cogDiff = (newCog[0] - self.cog[0], newCog[1] - self.cog[1])

		newPivot = (pivot[0] + cogDiff[0], pivot[1] + cogDiff[1] - 2)
		self.parts.setPositions(newPivot)

		if self.collide(1):
			self.parts.duplicate()
			return pivot, 0
		else:
			return newPivot, 20


	# Agent is affected by gravity
	def gravity(self, pivot, amount):
		# Decrement multiple times instead of just lowering once since this way if it collides in the middle it will go as close as possible
		for i in range(0,amount):
			# Store a copy of the agent
			self.backup.duplicate()
			# Lower the agent by 1
			pivot = (pivot[0], pivot[1] + 0.1)
			self.parts.setPositions(pivot)
			# If the agent collides with the world revert the move
			if self.collide(1):
				self.parts.duplicate()
				# Reset the pivot if the agent is reset
				pivot = (pivot[0], pivot[1] - 0.1)
				break
		return pivot

	# Handles Collisions between the ant and the world
	def collide(self, ignore):
		parts = self.array
		objects = []
		for i in range(len(self.objects)):
			objects.append(self.objects[i])
		for j in range(len(self.other_agents_info)):
			objects.append(self.other_agents_info[j])

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
			self.selfCollide = selfCollide
			self.colliding = colliding
		return ret

	# Add an object in the environment so the ant is aware of the world
	def addObject(self, obj):
		self.objects.append(obj)

	# Add an object in the environment so the ant is aware of the world
	def addOtherAgent(self, agent):
		self.other_agents.append(agent)

	# Return an array of all the individual ant parts
	def getParts(self):
		return self.parts.getParts()

	# Retrun any markers that should be drawn on screen
	def getMarkers(self):
		return self.box

	def setRotations(self, rotations):
		for i in range(len(rotations)):
			self.parts[i].setRotation(rotations[i], True)

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