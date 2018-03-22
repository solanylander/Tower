import math, random, sys, pygame
from pygame.locals import *
from part import Part
from policy_network import Network
from network import random_network
from random import *
import pickle
import time
import numpy as np

MAX_BODY_ROTATION = 90

class Agent:

	def __init__(self, xy, args):
		# Which body parts are currently colliding
		self.colliding = []
		self.history = []
		# Objects within the world
		self.objects = []
		self.reward = 1
		self.args = args
		# Neural network
		self.network = Network(args.hidden_layer_size, args.learning_rate, checkpoints_dir='checkpoints')
		if args.load_checkpoint:
			self.network.load_checkpoint()
		self.batch_state_action_reward_tuples = []
		self.smoothed_reward = None
		self.episode_n = 1
		self.episode_reward_sum = 0
		self.round_n = 1
		self.randomAgent = random_network()
		self.networkInput = []
		for i in range(81):
			self.networkInput.append(0)
		# Center of gravity
		self.cog = (0,0)
		self.rotations = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		self.prevMoves = [(-1,0),(-1,0),(-1,0),(-1,0),(-1,0),(-1,0)]
		# Run counter
		self.counter = 0
		# Total distance counter
		self.total = 0
		# Initial position
		self.c = None
		# Spawn position
		self.xy = xy

		self.won = 0
		self.lost = 0
		self.boundary = 40
		# Valid run
		self.button = True
		self.max = 0
		# Reset Agent
		self.random = [0,0,0,0,0,0]		
		self.reset(True, 0, True, True)
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		# Initialise the backup storage for the parts information with 0 values
		self.backup = []
		for k in range(0,15):
			self.backup.append(Part(0, 0, 0, False, 0, 0))
		self.backupTwo = []
		for k in range(0,15):
			self.backupTwo.append(Part(0, 0, 0, False, 0, 0))

	def randomize(self, limit):
		if limit > 100:
			limit = 100
		self.limit = limit
		moveChoices = [3,4,5,9,10,11]
		rand = randint(0,5)
		self.allowedMoves = [moveChoices[rand]]
		rand = randint(0,5)
		while moveChoices[rand] not in self.allowedMoves:
			self.allowedMoves.append(moveChoices[rand])
			rand = randint(0,5)

		for i in range(len(self.allowedMoves)):
			self.allowedMoves.append(self.allowedMoves[i] + 3)
		self.randomAgent.nextGame()


		for i in range(6):
			self.random[i] = randint(10,100)

		#print("Move tracker", self.allowedMoves)
		print("Random", self.random, limit)

	# Reset agent
	def reset(self, stage, score, init, hardReset):
		parts = []
		self.legsFixLocks = [0,0,0,0,0,0]

		self.randomParts = [False,False,False,False,False,False,False,False,False,False,False,False]
		randomCounter = 0
		while randint(0,100) < 90:
			self.randomParts[randint(0,11)] = True
			randomCounter += 1

		print("RandomPartsG", self.randomParts[0], self.randomParts[1], self.randomParts[2], self.randomParts[3], self.randomParts[4], self.randomParts[5])
		print("RandomPartsY", self.randomParts[6], self.randomParts[7], self.randomParts[8], self.randomParts[9], self.randomParts[10], self.randomParts[11])
		self.randomize(0)
		boundary = self.boundary * len(self.allowedMoves) / 12
			#elif randint(0, 100) < 40 and self.reward <= 0:
			#	self.random
		# add the head and body parts
		if hardReset:
			if True:
				z = randint(0, 360)
				parts.append(Part(z, self.xy[0], self.xy[1], True, 50, 0))
				z = (z + randint(-0, 0 + 1)) % 360
				parts.append(Part(z, 0, 0, False, 50, 1))
				z = (z + randint(-0, 0 + 1)) % 360
				parts.append(Part(z, 0, 0, False, 50, 2))
			else:
				# Normal Spawn
				print("Trying Again")
				parts.append(Part(self.rotations[0], self.xy[0], self.xy[1], True, 50))
				parts.append(Part(self.rotations[1], 0, 0, False, 50))
				parts.append(Part(self.rotations[2], 0, 0, False, 50))
			# Load the image files
			parts[0].loadImage("image_resources/body.png")
			parts[1].loadImage("image_resources/body.png")
			parts[2].loadImage("image_resources/head.png")
			# Body parts and heads weight
			parts[0].setWeight(23.44)
			parts[1].setWeight(11.72)
			parts[2].setWeight(8.24)

			if True:
				for i in range(0, 2):
					rands = [randint(0, 360),randint(0, 360),randint(0, 360)]
					parts.append(Part(rands[0], 0, 0, False, 12, 3 + i * 6))
					parts.append(Part(rands[1], 0, 0, False, 12, 4 + i * 6))
					parts.append(Part(rands[2], 0, 0, False, 12, 5 + i * 6))
					parts.append(Part(rands[0], 0, 0, False, 12, 6 + i * 6))
					parts.append(Part(rands[1], 0, 0, False, 12, 7 + i * 6))
					parts.append(Part(rands[2], 0, 0, False, 12, 8 + i * 6))
			else:
				# Normal Spawn
				for i in range(0, 2):
					parts.append(Part(self.rotations[(i * 6) + 3], 0, 0, False, 12))
					parts.append(Part(self.rotations[(i * 6) + 4], 0, 0, False, 12))
					parts.append(Part(self.rotations[(i * 6) + 5], 0, 0, False, 12))
					parts.append(Part(self.rotations[(i * 6) + 6], 0, 0, False, 12))
					parts.append(Part(self.rotations[(i * 6) + 7], 0, 0, False, 12))
					parts.append(Part(self.rotations[(i * 6) + 8], 0, 0, False, 12))

			for i in range(15):
				self.rotations[i] = parts[i].getRotation()
			# Add the leg parts
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
		self.button = True
		self.interactiveCounter = 0
		self.interactiveTotalCounter = 0
		self.timer = 0
		return self.collide(0)

	# Handles movement calculations
	def move(self, timer, show):
		prevMoves = []
		self.show = show
		self.timer += 1
		parts = self.parts
		pos = parts[0].getPosition()
		self.stored(True)
		amountOfMoves = 0
		moveTracker = []
		failures = 0
		#print(parts[0].getRotation())
		pivot = (pos[0], pos[1])
		if show == 1:
			print(pivot)
			print("-------------")
		pivot = self.gravity(pivot, 30)
		usedMoves = []
		usedRotations = []
		bottomPart = False
		i = -1
		while True:
			i += 1
			oldCog = self.getCog()[0]
			cog = self.getCog()[0]
			self.stored(True)
			self.storedTwo(True)
			self.inputs(pivot, i)
			self.new = True
			# Pick a move
			count = True
			zd = 0

			if self.random[i] > randint(0,100) and (timer % 900 >= 500):
				up_probability = self.randomAgent.trulyRandom()
				random = True
			else:
				up_probability = self.network.forward_pass(self.networkInput)[0]
				random_probability = self.randomAgent.constantRandom()
				for h in range(len(self.randomParts)):
					if self.randomParts[h] == True:
						up_probability[h + 3] = random_probability[h + 3]
						up_probability[h + 18] = random_probability[h + 18]
				random = False
			move = np.argmax(up_probability)

			while True:
				if move == 30 or ((move % 15) not in usedMoves and self.legalMove(move, pivot, usedRotations, usedMoves, bottomPart)):
					break

				up_probability[move] = 0
				move = np.argmax(up_probability)
				if np.max(up_probability) == 0:
					move = 30
			zd += 1
			if show == 1:
				print("Initial Rotation", parts[move%15].getRotation())
				print("Initial Constraint", parts[move%15].getConstraint())
			movement = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			if move != 30:
				#print("Before Movement", pivot)
				interMoved = False
				for k in range(len(movement)):
					if k == move:
						movement[k] = 1
						break
					elif k == move - 15:
						movement[k] = -1
						break
				self.setConstraints()
				backMove = parts[k].rotation(movement[k])
				oldPivot = (pivot[0], pivot[1])

				if k == 0:
					pivot = (pivot[0] + backMove[0], pivot[1] + backMove[1])
				if(k > 2 and k < 6 or k > 8 and k < 12):
					parts[k + 3].rotation(movement[k])
				if show == 1:
					print("After Backmove:", pivot)

				self.setPositions(pivot)

				resetGravity = 0

				if self.collide(2):
					count = False
					self.stored(False)
					if k == 0 and backMove[0] != 0:
						#print("used to slide")
						pivot = (oldPivot[0], oldPivot[1])
						self.setPositions(pivot)
						if show == 1:
							print("Collide 2", pivot)

				elif self.collide(1):
					self.stored(False)

					amountOfMoves = amountOfMoves + 1
					self.centerOfGravity(pivot)
					q = self.getCog()
					distChange = self.interactiveMove(move % 15, movement[k], q)
					pivot = (pivot[0] + distChange[0], pivot[1] + distChange[1])
					if show == 1:
						print("After Interactive move:", pivot)
					if self.collide(1):
						pivot = (pivot[0], pivot[1] - 2)

						parts[move % 15].rotation(movement[k])
						if (((move % 15) - 3) % 6) < 3:
							parts[(move % 15) + 3].rotation(movement[k])
						self.setPositions(pivot)
						#xDiff = self.getCog()[0] - cog
						#pivot = (pivot[0] - xDiff, pivot[1])
						#print(xDiff)
						#self.setPositions(pivot)

						if self.collide(1):
							self.stored(False)
							pivot = (oldPivot[0], oldPivot[1])
							reverted = True
						else:
							resetGravity = 30
					else:
						resetGravity = 10
					if resetGravity is not 0:
						interMoved = True
						pivot = self.gravity(pivot, resetGravity)
						if move < 15:
							prevMoves.append((move + 15, distChange[0]))
						else:
							prevMoves.append((move - 15, distChange[0]))
				elif backMove[0] is not 0:
					interMoved = True

				prevMoveNumber = -1
				for z in range(len(self.prevMoves)):
					if self.prevMoves[z][0] == move and self.prevMoves[z][1] is not 0:
						prevMoveNumber = z
						break


				if prevMoveNumber is not -1 and not interMoved:
					self.stored(True)
					oldPivot = (pivot[0], pivot[1])

					pivot = (pivot[0] -self.prevMoves[prevMoveNumber][1], pivot[1] - 3.0)
					self.setPositions(pivot)
					if self.collide(1):
						self.stored(False)
						print("Fail, Previous move could not be reverted")
					else:
						pivot = self.gravity(pivot, 30)





			self.centerOfGravity(pivot)

			self.stored(True)
			self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
			pivot = (pivot[0], pivot[1] + 1.5)
			self.setPositions(pivot)
			self.collide(1)
			pivot = (pivot[0], pivot[1] - 1.5)
			self.stored(False)
			if show == 1:
				print("Before Fall", pivot)
				print("Box 1:", self.box[0])
				print("Cog:", self.getCog())
				print("Box 2:", self.box[1])
			extra = 0
			# If the agents center of gravity is to the left of all its points of contacts fall to the left
			if self.box[0][0] != -1 and self.box[0][0] > self.cog[0] + 1:
				pivot, extra = self.fallRotation(pivot, True, move)
			# If the agents center of gravity is to the right of all its points of contacts fall to the right
			elif self.box[1][0] != -1 and self.box[1][0] < self.cog[0] - 1:
				pivot, extra = self.fallRotation(pivot, False, move)
			elif self.box[0][0] <= self.cog[0] + 1 and self.box[1][0] >= self.cog[0] - 1 and self.button:
				self.c = self.cog
				print("click")
				self.button = False

			if show == 1:
				print("After Fall", pivot)
			if extra != 0:
				pivot = self.gravity(pivot, (extra) * 10)

			self.setConstraints()
			if move != 30:
				usedMoves.append(move % 15)
			usedRotations.append(move)
			fail = False
			if self.collide(2):
				extra = self.tweak(pivot)
				if self.collide(2):
					if not self.button:
						self.storedTwo(False)
					else:
						fail = True
					print("Tweak")
				pivot = (pivot[0] - extra, pivot[1])
				if extra != 0:
					pivot = self.gravity(pivot, (extra) * 10)

			#angle = (self.parts[0].getRotation() - self.parts[1].getRotation()) % 360
			#if angle > 89 and angle < 271:
			#	print("90 Degrees")
			#	fail = True
			#angle = (self.parts[2].getRotation() - self.parts[1].getRotation()) % 360
			#if angle > 89 and angle < 271:
			#	print("90 Degrees")
			#	fail = True
			x = self.ended(move, timer, self.button, i, fail)
			if not self.button and (move % 15) in self.allowedMoves:
				self.interactiveCounter += self.cog[0] - oldCog
			if not self.button and (move % 15) > 2:
				self.interactiveTotalCounter += self.cog[0] - oldCog



			if show == 2 and i == 5:
				print("Rotations:", usedRotations)
				print("Random Allowed:", timer % 900 >= 500)
			if show == 1:
				print("Moves:", usedRotations)
				print("Final Rotation", parts[move%15].getRotation())
				print("After Tweak:", pivot)
				if i == 5:
					print("=============")
				else:
					print("-------------")
			if i == 5 or fail:
				self.prevMoves = prevMoves
				self.history = usedRotations
				for j in range(0,6):
					if self.legsFixLocks[j] == 1:
						self.legsFixLocks[j] = 2
				if fail:
					return True
				#print(self.legsFixLocks, usedRotations)
				return x


	def ended(self, move, timer, button, turn, fail):
		if not button and (move < 30 or fail):
			score = self.getCog()[0] - self.c[0]
			reward = 0
			boundary = self.boundary * len(self.allowedMoves) / 12

			if turn == 5 and self.interactiveTotalCounter > self.boundary:
				#if abs(score - self.interactiveTotalCounter) < 20:
				reward = 0.999
				self.won += 1
				#else:
				#	reward = -1.000
				#	self.lost += 1					
			elif (turn == 5 and self.interactiveTotalCounter < -10) or fail:
				reward = -0.999
				self.lost += 1				
			elif (turn == 5 and self.limit == 11):
				print("Limit Reached")
				reward = -0.999
				self.lost += 1


			if move == 30:
				move = 3

			output = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			output[move] = 1

			self.episode_reward_sum += reward
			tup = (self.networkInput, output, reward)
			self.batch_state_action_reward_tuples.append(tup)
			if (turn == 5 or fail):
				if reward < 0:
					print("Round %d; Score: %0.3f, Reward: %0.3f,  lost..." % (self.round_n, score, reward))
				elif reward > 0:
					print("Round %d: Score: %0.3f, Reward: %0.3f, won!" % (self.round_n, score, reward))
				if reward != 0:
					print("Boundary:", self.boundary)
					#print("Interactive:", self.interactiveCounter)
					print("Total Interactive:", self.interactiveTotalCounter)
					print("============================")
					if score > self.max:
						self.max = score
					self.reward = reward
					self.round_n += 1
					self.n_steps = 0
					return True
		return False

	def finishEpisode(self):
		#if self.won > 25:
		#	self.boundary += 40
		#if self.lost == 30 and self.boundary > 100:
		#	self.boundary -= 20
		print("Self Boundary", self.boundary)
		print("Episode %d finished after %d rounds" % (self.episode_n, self.round_n))
		print("Current max score:", self.max)
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






	def legalMove(self, move, pivot, usedRotations, usedMoves, bottomPart):
		if move == 30:
			return True
		elif (move % 15) < 3:
			return False
		parts = self.parts
		valid = None
		partNum = move % 15
		direction = -1
		if move < 15:
			direction = 1
		valid = parts[partNum].checkRotation(direction)

		if valid == False:
			return False

		parts[partNum].rotation(direction)

		
		if ((partNum - 3) % 6) < 3:
			parts[partNum + 3].rotation(direction)
		self.setPositions(pivot)

		if self.collide(2):
			valid = False
		if self.collide(1) and (move % 15) == 0:
			valid = False

		self.stored(False)


		if False:#not bottomPart:


			thighMove = (move % 15) % 6



			if len(usedRotations) > 0 and valid == True and thighMove > 2:

				#3,4,5 18,19,20
				pivot = [(move % 15) - 1, move % 15, (move % 15) + 1, (move % 15) + 14, (move % 15) + 15, (move % 15) + 16]
				offset = 0
				if pivot[1] > 8:
					offset = 2
				if thighMove == 5:
					offset = offset + 1



				if thighMove > 3 and pivot[0] in usedMoves:
					if (self.values[offset][0] is not 0 and self.values[offset][3] is not 0) or (self.values[offset][1] is not 0 and self.values[offset][2] is not 0):
						#print("USED ROTATIONS", usedRotations)
						#print(move, 1)
						if (pivot[3] in usedRotations and move == pivot[1]) or (pivot[0] in usedRotations and move == pivot[4]):
							#print("false")
							valid = False
							amount = thighMove - 3
							if move % 15 > 8:
								amount += 3
							if self.legsFixLocks[amount] == 0:
								self.legsFixLocks[amount] = 1
								self.legsFixLocks[amount - 1] = 1
					if valid:
						if (self.values[offset][0] is not 0 and self.values[offset][1] is not 0) or (self.values[offset][2] is not 0 and self.values[offset][3] is not 0):
							#print("USED ROTATIONS", usedRotations)
							#print(move, 2)
							if (pivot[0] in usedRotations and move == pivot[1]) or (pivot[3] in usedRotations and move == pivot[4]):
								#print("false")
								valid = False
								amount = thighMove - 3
								if move % 15 > 8:
									amount += 3
								if self.legsFixLocks[amount] == 0:
									self.legsFixLocks[amount] = 1
									self.legsFixLocks[amount - 1] = 1

				if thighMove == 4:
					offset = offset + 1



				if thighMove < 5 and pivot[2] in usedMoves:
					if (self.values[offset][0] is not 0 and self.values[offset][3] is not 0) or (self.values[offset][1] is not 0 and self.values[offset][2] is not 0):
						#print("USED ROTATIONS", usedRotations)
						#print(move, 3)
						if (pivot[5] in usedRotations and move == pivot[1]) or (pivot[2] in usedRotations and move == pivot[4]):
							#print("false")
							valid = False
							amount = thighMove - 3
							if move % 15 > 8:
								amount += 3
							if self.legsFixLocks[amount] == 0:
								self.legsFixLocks[amount] = 1
								self.legsFixLocks[amount + 1] = 1

					if valid:
						if (self.values[offset][0] is not 0 and self.values[offset][1] is not 0) or (self.values[offset][2] is not 0 and self.values[offset][3] is not 0):
							#print("USED ROTATIONS", usedRotations)
							#print(move, 4)
							if (pivot[3] in usedRotations and move == pivot[1]) or (pivot[5] in usedRotations and move == pivot[4]):
								#print("false")
								valid = False
								amount = thighMove - 3
								if move % 15 > 8:
									amount += 3
								if self.legsFixLocks[amount] == 0:
									self.legsFixLocks[amount] = 1
									self.legsFixLocks[amount + 1] = 1



			#HERE SOMEWHERE
			if thighMove > 2:
				lastLeg = [(((move % 15) - 1) * 5 + 2), (((move % 15) - 1) * 5 + 4)]
				currentLeg = [((move % 15) * 5 + 2), ((move % 15) * 5 + 4)]
				nextLeg = [(((move % 15) + 1) * 5 + 2), (((move % 15) + 1) * 5 + 4)]


				if (self.networkInput[currentLeg[0]] > 0) or (self.networkInput[currentLeg[1]] > 0):
					if move not in self.history:
						amount = thighMove - 3
						if move % 15 > 8:
							amount += 3
						if thighMove < 5 and ((self.networkInput[nextLeg[0]] > 0) or (self.networkInput[nextLeg[1]] > 0)):		
							# IF 2 then do it
							if self.legsFixLocks[amount] == 2:
								#print(move, "Top")
								valid = False
							#print(move, amount, "locked")
							#print(thighMove, self.legsFixLocks)
						elif thighMove > 3 and ((self.networkInput[lastLeg[0]] > 0) or (self.networkInput[lastLeg[1]] > 0)):				
							if self.legsFixLocks[amount] == 2:
								#print(move, "Bottom")
								valid = False
							#print(move, amount, "locked")
						else:
							amount = thighMove - 3
							if move % 15 > 8:
								amount += 3
							self.legsFixLocks[amount] = 0
				else:
					amount = thighMove - 3
					if move % 15 > 8:
						amount += 3
					self.legsFixLocks[amount] = 0


		return valid

	def inputs(self, pivot, turn):
		parts = self.parts
		objects = self.objects
		if turn == 0:
			netInputs = []
			for i in range(len(parts)):
				netInputs.append(parts[i].getRotation() / 360.0)
				for j in range(0,2):
					parts[i].rotation(-1 + (j * 2))
					if(i > 2 and i < 6 or i > 8 and i < 12):
						parts[i + 3].rotation(-2 + (j * 4))
					self.setPositions(pivot)
					boolToIntWorld = 0
					boolToIntSelf = 0
					if self.collide(1):
						boolToIntWorld = 1
					if self.collide(2):
						boolToIntSelf = 1
					if boolToIntWorld is 0 and self.networkInput[len(netInputs)] > 0.25:
						boolToIntWorld = self.networkInput[len(netInputs)] - 0.25
					netInputs.append(boolToIntWorld)
					if boolToIntSelf is 0 and self.networkInput[len(netInputs)] > 0.25:
						boolToIntSelf = self.networkInput[len(netInputs)] - 0.25
					netInputs.append(boolToIntSelf)
					self.stored(False)
			for j in range(6):
				if j == turn:
					netInputs.append(1)
				else:
					netInputs.append(0)
			self.networkInput = netInputs
			#if self.show == 1:
				#print(netInputs)




			self.values = [[0 for x in range(4)] for y in range(4)]
			# Green vs Yellow legs
			for i in range(2):
				# Front 2 vs Back 2
				for j in range(2):
					# Rotate left vs Rotate Right
					for k in range(2):
						offset = 15 + (i * 30) + (j * 5)
						self.values[(i * 2) + j][(k * 2)] = self.networkInput[offset + 2 + (k * 2)]
						self.values[(i * 2) + j][(k * 2) + 1] = self.networkInput[offset + 7 + (k * 2)]
			
			for z in range(4):
				for y in range(2):
					if self.values[z][y] > 0 and self.values[z][y + 2] > 0:
						if self.values[z][y] > self.values[z][y + 2]:
							self.values[z][y + 2] = 0
						elif self.values[z][y] < self.values[z][y + 2]:
							self.values[z][y] = 0


			#print("-----------")
			#print(self.values)
		else:
			for i in range(len(parts)):
				self.networkInput[i * 5]  = parts[i].getRotation() / 360.0
			self.networkInput[74 + turn] = 0
			self.networkInput[75 + turn] = 1


	# When the agent pushes off with a leg the rest of its body should follow
	def interactiveMove(self, move, direction, cog):
		colliding = self.colliding
		parts = self.parts
		initialPos = parts[move % 15].getPivot()

		distance = (initialPos[0] - colliding[0][0], initialPos[1] - colliding[0][1])
		hypD = math.sqrt(distance[0] * distance[0] + distance[1] * distance[1])

		rotation = (math.atan(distance[0] / distance[1]) * 180.0 / math.pi) - direction
		newPos = (hypD * math.sin(rotation * math.pi / 180.0), hypD * math.cos(rotation * math.pi / 180.0))

		newPos = (newPos[0] + distance[0], newPos[1] + distance[1] - 1.0)


		parts[move].rotation(direction)
		if ((move - 3) % 6) < 3:
			parts[move + 3].rotation(direction)

		pivot = parts[0].getPosition()
		self.setPositions(pivot)
		self.centerOfGravity(pivot)
		cog = cog[0] - self.getCog()[0]
		if (move % 15) < 3:
			newPos = (0, newPos[1])

		return newPos


		#print("final", self.collide(False))
	# When the agent is hanging on an edge over its center of gravity it should tip in that direction
	def fallRotation(self, pivot, left, move):
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
		if (move % 15) < 3:
			newPivot = (pivot[0], pivot[1] + cogDiff[1] - 2)
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
			self.parts[iterate].rotation(amount)

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
			one[k].setRotation(two[k].getRotation())
			if not setup:
				one[k].rotation(0)

	def storedTwo(self, setup):
		one = []
		two = []
		if setup:
			two = self.parts
			one = self.backupTwo
		else:
			two = self.backupTwo
			one = self.parts
		for k in range(0,15):
			one[k].setPosition(two[k].getPosition())
			one[k].setConstraint(two[k].getConstraint())
			one[k].setRotation(two[k].getRotation())
			if not setup:
				one[k].rotation(0)
	
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
		objects = self.objects
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

	def tweak(self, pivot):
		parts = self.parts
		colliders = []
		for i in range (0,2):
			start = 3 + (i * 6)
			for position in range(start, start + 6):
				for j in range(position + 1,start + 6):
					# Dont check collisions when the 2 parts are from the same leg. E.g "Thigh" and "Calf"
					if (position % 3) != (j % 3):			
						offset = (int(parts[position].getPosition()[0] - parts[j].getPosition()[0]), int(parts[position].getPosition()[1] - parts[j].getPosition()[1]))
						result = parts[j].getMask().overlap(parts[position].getMask(), offset)
						# If they collide return true
						if result:
							colliders.append((position, j))
		#print(colliders)
		for i in range(len(colliders)):
			self.collide(2)
			colliderLen = len(self.selfCollide)
			if colliderLen == 0:
				#print("0 count")
				break
			#print(colliderLen, self.selfCollide)
			x = colliders[i][0]
			y = colliders[i][1]
			if x % 6 < 3:
				x = x - 3
			if y % 6 < 3:
				y = y - 3
			self.stored(True)
			max = (0,360)
			#when you fix one rotation but not another then it will stick on 360
			for z in range(0, 8):
				count = 0
				while len(self.selfCollide) >= colliderLen and count < 10:
					if z == 0:
						self.parts[x].rotation(-1)
						self.parts[y].rotation(1)
					elif z == 1:
						self.parts[x].rotation(-1)
					elif z == 2:
						self.parts[x].rotation(-1)
						self.parts[y].rotation(-1)
					elif z == 3:
						self.parts[x].rotation(1)
						self.parts[y].rotation(1)
					elif z == 4:
						self.parts[x].rotation(1)
					elif z == 5:
						self.parts[x].rotation(1)
						self.parts[y].rotation(-1)
					elif z == 6:
						self.parts[y].rotation(1)
					elif z == 7:
						self.parts[y].rotation(-1)

					self.setPositions(pivot)
					self.collide(2)
					count = count + 1
				if count < max[1]:
					max = (z, count)
				self.stored(False)
				self.collide(2)
				if count < 3:
					break
			z = max[0]
			count = 0
			while len(self.selfCollide) >= colliderLen and count < 10:

				if z == 0:
					self.parts[x].rotation(-1)
					self.parts[y].rotation(1)
				elif z == 1:
					self.parts[x].rotation(-1)
				elif z == 2:
					self.parts[x].rotation(-1)
					self.parts[y].rotation(-1)
				elif z == 3:
					self.parts[x].rotation(1)
					self.parts[y].rotation(1)
				elif z == 4:
					self.parts[x].rotation(1)
				elif z == 5:
					self.parts[x].rotation(1)
					self.parts[y].rotation(-1)
				elif z == 6:
					self.parts[y].rotation(1)
				elif z == 7:
					self.parts[y].rotation(-1)
				self.setPositions(pivot)
				self.collide(2)
				count = count + 1
			if count == 10:
				#print("10 count")
				self.stored(False)
		count = 0
		while self.collide(0) and count < 5:
			pivot = (pivot[0], pivot[1] - 1.0)
			self.setPositions(pivot)
			count = count + 1
		if count == 5:
			pivot = (pivot[0], pivot[1] + 5.0)
			self.setPositions(pivot)
		return count
		

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
