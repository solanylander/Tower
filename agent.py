import math, sys, pygame
from pygame.locals import *
from part import Part
from agent_parts import Parts
from sensors import Sensors
import random
from random import randint
import pickle
import time
import numpy as np

class Agent:

	def __init__(self, xy, networks, agent_num, goal, boundary, training, randomness, subsumption):
		# store initial parameters
		self.agent_num = agent_num
		self.boundary = boundary
		self.finished_completely = False
		self.networks = networks
		self.target = False
		self.goal = goal

		self.training = training
		self.randomness = randomness
		self.subsumption = subsumption

		self.finished_counter = -1
		self.finished = 0

		# Initialize variables
		self.stop = 0
		self.restart = False	
		self.colliding = []
		self.objects = []
		self.batch_state_action_reward_tuples = []
		self.network_input = []
		self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]
		self.prev_moves = []
		self.total = 0
		self.won = False
		self.interactive_dist = 0
		self.turn = 0
		self.start_reached = False
		if self.networks.get_turn() < 2:
			self.start_reached = True

		self.next()

		# Initialise agents parts and backup
		self.parts = Parts(False, xy, self.networks.get_turn())
		self.backup = Parts(True, None, 0)	
		self.parts.load_pair(self.backup)
		self.backup.load_pair(self.parts)
		self.array = self.parts.array
		self.cog = self.parts.center_of_gravity(xy)
		self.initial_position = self.cog[0]
		self.last_score = 0.5
		self.last_interactive = 0.5


		# Initialise agents sensors
		self.sensors = Sensors()
		self.sensors.set_positions(self.array[0].get_pivot(), self.array[2].get_pivot())

	# Checks the agents distance travelled periodically so it can tell when it is no longer progressing
	def next(self):
		# 400 frames between each check
		self.timer = 400
		if not (self.turn == 0):
			self.last_score = self.cog[0] - self.initial_position
			self.last_interactive = self.interactive_dist

			# If the agent reached its target call the next agent otherwise reset the environment
			if self.last_score <= 0 and not self.training:
				# Agent hasn't flipped over and has found its target
				if ((self.network_input[7] > 0.2 or self.network_input[8] > 0.2) and (self.network_input[9] == 1 or (((self.network_input[0] + 0.325) % 1) < 0.15))):
					self.finished = 1
				# Otherwise reset environment
				else:
					self.finished = -1
			# Agents initial position 
			self.initial_position = self.cog[0]
			self.interactive_dist = 0
		# Number of checks the agent has done
		self.turn += 1



	# Handles movement calculations
	def move(self):
		# After an agent has finished progressive keep checking their physics for a while
		# Stop after 100 frames however to maintain the applications performance
		if not (self.finished_counter == 0):
			if not (self.finished == 0) and self.finished_counter == -1:
				self.finished_counter = 100
			if self.finished_counter > 0:
				self.finished_counter -= 1
				# Update the agents position for new agents now its completely finished
				if self.finished_counter == 0:
					self.finished_completely = True


			# Agents gravity
			pivot = self.array[0].get_position()
			pivot = self.gravity(pivot, 30)

			# If the agent is still progressing
			if self.finished == 0:

				# check agents progress if they have begun moving
				if self.start_reached:
					self.timer -= 1
					if self.timer == 0:
						self.next()
				parts = self.array
				# Reset variables
				self.moves = []
				# Update the position of the sensors and then check their value
				self.sensors.set_positions(self.array[0].get_pivot(), self.array[2].get_pivot())
				self.sensors.collisions(self.objects, self.target)
				self.network_input = self.parts.inputs(pivot, self.sensors.sensor_values, self.sensors.target)
				if not self.start_reached:
					if self.sensors.sensor_values[0] > 0.1 or self.sensors.sensor_values[1] > 0.1:
						self.start_reached = True
				# Move the agents body then legs
				pivot = self.body_move(pivot)
				pivot = self.leg_move(pivot)

				self.cog = self.parts.center_of_gravity(pivot)
				self.backup.duplicate()
				# After movement check where the agent is colliding with the world so that it knows whether to fall
				self.box = [(-1,-1), (-1,-1), (-1,-1), (-1,-1)]

			# Lower the agent by 1.5 pixels, check for collisions then raise it back up
			pivot = (pivot[0], pivot[1] + 1.5)
			self.parts.set_positions(pivot)
			self.collide()
			pivot = (pivot[0], pivot[1] - 1.5)
			self.parts.duplicate()
			extra = 0

			# If the agents center of gravity is not between 2 collision points then it should fall over
			if self.box[0][0] != -1 and (self.box[0][0] > self.cog[0] or self.box[1][0] < self.cog[0]):
				pivot, extra = self.fall_rotation(pivot)
				self.parts.set_constraints()
				if extra != 0:
					pivot = self.gravity(pivot, (extra) * 10)

			# If the agent reaches the goal reset environment
			if self.finished == 0 and not self.training:
				offset = (int(parts[2].get_position()[0] - self.goal.get_position()[0]), int(parts[2].get_position()[1] - self.goal.get_position()[1]))
				result = self.goal.get_mask().overlap(parts[2].get_mask(), offset)
				if not (result == None):
					self.finished = -1
					self.won = True

		



	# Updates the network and checks to see if the run has ended
	def update_network(self, move, turn):
		if self.start_reached:
			array = self.array
			reward = 0
			# If the agent reaches the goal the agent wins the round
			if turn == 3:
				reward, self.restart = self.parts.rewards(self.network_input, self.moves, self.last_score, self.turn, self.last_interactive)

				# Set the output to match the move
				for i in range(7):
					output = [0,0,0]
					output[self.moves[i]] = 1
					# Add result to the set of tuples that will train the network
					tup = (self.network_input, output, reward)
					self.networks.append_tuple(tup, i)


			# If the agent succeeds/fails print log
			if self.restart:
				if reward > 0:
					self.won = True

	# When the agents center of gravity is not between 2 points of contact with the environment
	# then it should fall over
	def fall_rotation(self, pivot):
		parts = self.parts
		# Find the closest point of contact with the environment
		# so that when the agent falls they can pivot from there
		point_of_contact = (self.box[0][0], self.box[0][1])

		# The agent falls using the point of contact and its center of gravity so it needs the distance between
		distance_xy = (self.cog[0] - point_of_contact[0], point_of_contact[1] - self.cog[1])
		# The speed at which the agent falls (amount the agent will be rotated by)
		torque = distance_xy[0] / 25

		# Actual distance between the agents point of contact with the world and the agents main pivot point
		distance_h = math.sqrt(distance_xy[0] * distance_xy[0] + distance_xy[1] * distance_xy[1])

		# The angle between the collision point being used and the agents pivot point.
		current_angle = None
		if(distance_xy[0] == 0):
			current_angle = 90
		else:
			current_angle = math.atan(distance_xy[1]/distance_xy[0]) * 180.0 / math.pi
		if current_angle < 0:
			current_angle = 180 + current_angle
		# the new angle is the current angle minus torque
		new_angle = current_angle - torque

		# The X,Y distances between the agents point of contact with the world and where the agents main pivot point will be after the rotation
		newXY = (distance_h * math.cos(new_angle / 180 * math.pi), (distance_h * math.sin(new_angle / 180 * math.pi)))
		if point_of_contact[1] < self.cog[1]:
			newXY = (-newXY[0], -newXY[1])
		new_cog = (point_of_contact[0] + newXY[0], point_of_contact[1] - newXY[1])

		# Store a backup
		self.backup.duplicate()
		# Rotate all parts of the agent
		self.parts.rotate_all(-torque)
		# Reposition agent parts
		self.parts.set_positions(pivot)
		# Get the agents new center of gravity
		self.cog = self.parts.center_of_gravity(pivot)
		# Find the difference between the current cog and where it should be
		cog_diff = (new_cog[0] - self.cog[0], new_cog[1] - self.cog[1])

		# Add the difference and raise it by 2
		new_pivot = (pivot[0] + cog_diff[0], pivot[1] + cog_diff[1] - 2)
		self.parts.set_positions(new_pivot)

		# If it fails reset the agent
		if self.collide():
			self.parts.duplicate()
			return pivot, 0
		# Else return the new pivot and since we raised it by 2 before tell
		# the program to lower it by 2
		else:
			return new_pivot, 20

	# Agent is affected by gravity
	def gravity(self, pivot, amount):
		# Decrement multiple times instead of just lowering once soif it collides in the middle it will go as close as possible
		for i in range(0,amount):
			# Store a copy of the agent
			self.backup.duplicate()
			# Lower the agent by 1
			pivot = (pivot[0], pivot[1] + 0.1)
			self.parts.set_positions(pivot)
			# If the agent collides with the world revert the move
			if self.collide():
				self.parts.duplicate()
				# Reset the pivot if the agent is reset
				pivot = (pivot[0], pivot[1] - 0.1)
				break
		return pivot

	# Handles Collisions between the ant and the world
	def collide(self):
		array = self.array
		objects = self.objects
		self.colliding = []
		ret = False
		# Check for collisions for every part of the agent
		for position in range(0,15):
			# Check collisions against all the other objects in the world which exclude itself
			for k in range(len(objects)):
				# Find the position difference between the agent part and the external object
				offset = (int(objects[k][1] - array[position].get_position()[0]), int(objects[k][2] - array[position].get_position()[1]))
				result = array[position].get_mask().overlap(objects[k][0], offset)
				# If there is a collision add it to the collision list
				if result:
					self.collision_box((array[position].get_position()[0] + result[0], array[position].get_position()[1] + result[1]))
					self.colliding.append((array[position].get_position()[0] + result[0], array[position].get_position()[1] + result[1]))
					ret = True

		return ret

	# Add an object in the environment so the ant is aware of the world
	def add_object(self, obj):
		self.objects.append(obj)

	# Add another agent so the ant is aware of it
	def add_other_agent(self, agent):
		for j in range(0,3):
			part = agent.parts.array[j]
			self.objects.append((part.get_mask(), part.get_position()[0], part.get_position()[1]))


	# Creates a parallelogram around the agent with the corners being the collision points with the highest and lowest x and y values
	# used for calculating gravity and if the agents center of gravity is over an edge (in which case it will fall)
	def collision_box(self, point):
		# Bottom left corner
		if self.box[0][0] == -1 or point[0] < self.box[0][0]:
			self.box[0] = point
		# Bottom right corner
		if self.box[1][0] == -1 or (point[0] > self.box[1][0] and self.box[1][0] != -1):
			self.box[1] = point
		# Top left corner
		if self.box[2][1] == -1 or point[1] < self.box[2][1]:
			self.box[2] = point
		# Top right corner
		if self.box[3][1] == -1 or (point[1] > self.box[3][1] and self.box[3][1] != -1):
			self.box[3] = point

	# Return the collision points box that should be drawn on screen
	def get_box(self):
		return self.box

	# Choose a move depending on the probabilities given by the neural network
	def get_move(self, probabilities, banned):
		highest = 0
		for i in range(1,3):
			if probabilities[i] > probabilities[highest]:
				highest = i

		move = 0
		move = highest
		# 90% chance of best move otherwise pick a random move
		while True:
			probability_random = random.uniform(0, 100)
			if probability_random >= self.randomness:
				move = highest
			else:
				move = randint(0, 2)

			if not(move == banned):
				break
		# Return the chosen move
		return move

	# Move the agents legs
	def leg_move(self, pivot):
		parts = self.parts
		array = self.array
		prev_moves = []
		# Front legs then back legs
		for i in range(0,2):
			cog = self.cog[0]
			# Get the inputs for the top part of the legs then the bottom part
			# Get the probabilities for each move
			probabilities_top = self.networks.forward_pass(self.network_input, (i * 2))
			probabilities_bottom = self.networks.forward_pass(self.network_input, (i * 2) + 1)
			# Pick a move based of the networks probabilities
			move_top = self.get_move(probabilities_top, -1)
			move_bottom = self.get_move(probabilities_bottom, -1)


			if not self.start_reached or self.subsumption:
				if randint(0, 100) >= self.randomness:
					move_top = self.parts.preset_moves(i, self.network_input)
				else:
					move_top = randint(0,2)
				if randint(0, 100) >= self.randomness:
					move_bottom = self.parts.preset_moves((i + 1), self.network_input)
				else:
					move_bottom = randint(0,2)



			# Rotate the bottom by the same amount as the top + its own values
			rotation_amount_top = move_top - 1
			rotation_amount_bottom = move_bottom - 1 + rotation_amount_top
			# Append moves
			self.moves.append(move_top)
			self.moves.append(move_bottom)
			for j in range(3):
				# Store initial pivot and calculate part number
				old_pivot = (pivot[0], pivot[1])
				part_num = (i * 6) + j + 3
				# Store a back up
				self.backup.duplicate()
				self.parts.set_constraints()
				# rotate a leg by the correct amount
				array[part_num].rotate(rotation_amount_top)
				array[part_num + 3].rotate(rotation_amount_bottom)

				self.parts.set_positions(pivot)
				reset_gravity = 0
				# If the leg collides with the environment the entire agent should move. (How the agent walks)
				if self.collide():
					# Restore backup
					self.parts.duplicate()
					# Add the distance the agent should move by
					dist_change = self.parts.interactive_move(part_num, rotation_amount_top, rotation_amount_bottom, self.colliding)
					pivot = (pivot[0] + dist_change[0], pivot[1] + dist_change[1])
					# If the agent still collides with the world try raising it more
					if self.collide():
						pivot = (pivot[0], pivot[1] - 2)
						self.parts.set_positions(pivot)

						if self.collide():
							self.parts.duplicate()
							pivot = (old_pivot[0], old_pivot[1])
							break
						else:
							reset_gravity = 30
					else:
						reset_gravity = 10
					# If the agent was raised to stop a collision lower it back down
					if reset_gravity is not 0:
						pivot = self.gravity(pivot, reset_gravity)
						prev_moves.append((part_num, dist_change[0], move_top))
						self.interactive_dist += dist_change[0]

				# It's possible for the agent to vibrate along the floor. This reduces the amount a lot by cancelling out
				# moves when the agent is twitching
				if reset_gravity == 0:
					for z in range(len(self.prev_moves)):
						if self.prev_moves[z][0] == part_num and abs(move_top - self.prev_moves[z][2]) == 2:
							pivot = (pivot[0] - self.prev_moves[z][1], pivot[1] - 1.0)
							self.parts.set_positions(pivot)
							# If the move cannot be reverted accept it
							if self.collide():
								self.parts.duplicate()
								pivot = (pivot[0] + self.prev_moves[z][1], pivot[1] + 1.0)
							else:
								pivot = self.gravity(pivot, 10)

			# Send the agents move information to the network
			if self.training:
				self.update_network(move_top, (i * 2))
				self.update_network(move_bottom, (i * 2) + 1)
		self.prev_moves = prev_moves
		return pivot

	# Move the agents body
	def body_move(self, pivot):
		parts = self.array
		# Currently no banned moves
		banned_move = -1
		for i in range(4,7):
			# Initialise variables
			old_pivot = (pivot[0], pivot[1])
			part_num = i - 4
			move = None
			# Get the networks input data and then get the probabilities from the network
			probabilities = self.networks.forward_pass(self.network_input, i)
			# The middle part of the agent cannot rotate in the same direction as the back since they share the same pivot
			if i == 5:
				move = self.get_move(probabilities, banned_move)
			else:
				move = self.get_move(probabilities, -1)



			# Whilst moving into position of in the subsumption architecture pick a preset move
			if not self.start_reached or self.subsumption:
				# Potentially pick a random move. Randomness determined by user
				if randint(0, 100) >= self.randomness:
					move = self.parts.preset_moves(i, self.network_input)
				else:
					move = randint(0,2)


			# Rotation amount  -1-anticlockwise 0-stationary 1-clockwise
			self.moves.append(move)
			rotation_amount = move - 1
			# Store a backup and then rotate part
			self.backup.duplicate()
			self.parts.set_constraints()
			parts[part_num].rotate(rotation_amount)
			# Since the agent builds off the back piece, when that rotates the agent should reposition so that all other parts
			# stay in the same place
			if i == 4:
				torso_position = parts[1].get_position()
				self.parts.set_positions(pivot)
				new_torso_position = parts[1].get_position()
				new_torso_position = (new_torso_position[0] - torso_position[0], new_torso_position[1] - torso_position[1])
				pivot = (pivot[0] - new_torso_position[0], pivot[1] - new_torso_position[1])
				# if the back of the agent rotated ban that move for the middle section of the agent
				if move is not 1 and new_torso_position[0] is not 0:
					banned_move = move
			# When the middle part of the agent rotates so does the head
			elif i == 5:
				parts[2].rotate(rotation_amount)

			self.parts.set_positions(pivot)
			reset_gravity = 0

			# If the agent collides with its environment reposition it slightly
			if self.collide():
				# Move 2 pixels up
				pivot = (pivot[0], pivot[1] - 2)
				self.parts.set_positions(pivot)

				if self.collide():
					# Move 1 pixel left
					pivot = (pivot[0] - 1, pivot[1])
					self.parts.set_positions(pivot)

					if self.collide():
						# Move 1  more pixel left
						pivot = (pivot[0] - 1, pivot[1])
						self.parts.set_positions(pivot)

						# If it still collides revert move
						if self.collide():
							self.parts.duplicate()
							pivot = (old_pivot[0], old_pivot[1])
						else:
							reset_gravity = 30
					else:
						reset_gravity = 30
				else:
					reset_gravity = 30
			elif move is not 1:
				reset_gravity = 10
			# If the agent was respositioned lower it back to the ground
			if reset_gravity is not 0:
				pivot = self.gravity(pivot, reset_gravity)
			# Send the agents move information to the network
			if self.training:
				self.update_network(move, i)
		return pivot
