import math, random, sys, pygame, os, time, argparse
from pygame.locals import *
from agent import Agent
from part import Part
from block import Block
from network import Network
from random import *


parser = argparse.ArgumentParser()
parser.add_argument('--hidden_layer_size', type=int, default=200)
parser.add_argument('--learning_rate', type=float, default=0.01)
parser.add_argument('--batch_size_episodes', type=int, default=1)
parser.add_argument('--checkpoint_every_n_episodes', type=int, default=2)
parser.add_argument('--load_checkpoint', action='store_true')
parser.add_argument('--discount_factor', type=int, default=0.9998)
args = parser.parse_args()


# define display surface			
W, H = 1080, 600
episode_num = 13
HW, HH = W / 2, H / 2
AREA = W * H

# define some colors
BLUE = (0, 153, 255, 221)

network = Network(args.load_checkpoint)
# Place window in the center of the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (150,80)
# initialise display
pygame.init()
CLOCK = pygame.time.Clock()
DS = pygame.display.set_mode((W, H))
pygame.display.set_caption("Ant Tower Project")
FPS = 120
trainingNum = 20000
duration = 400
switch = True
# Get the image resources for the world
pointers = [None, None, None]
pointers[0] = pygame.image.load("image_resources/pointer.png").convert_alpha()
pointers[1] = pygame.image.load("image_resources/pointerTwo.png").convert_alpha()

block_distance = 300

blocks, agents = [],[]
# Adds agents into the world
blocks.append(Block(0, (0, 400)))
blocks[0].loadImage("image_resources/flat_floor.png")

goal = Block(0, (0, 400))
goal.loadImage("image_resources/goal.png")

block_move_u, block_move_r = 0,0
wall_height = 350
lock = False
angle = 0
ag_num = 0
done = False
last_cog = 0
diff_cog = 0
cog_threshold = 800

# wall pos, next wall, decrement
target_counters = [2,3,-1]








blocks.append(Block(0, (block_distance, 150)))
blocks[1].loadImage("image_resources/wall.png")
agents.append(Agent((390,200), blocks[1], network, 0, goal, 25))
print("Target: Wall")
# Tell all agents about the objects within the world so they can detect collisions
for i in range(len(agents)):
	for j in range(len(agents)):
		if i is not j:
			agents[i].addOtherAgent(agents[j])


timer = duration
counter = 0
show = False
reset = False
pause = False
resetCounter = 0
nextRound = False
agent_number = 0


blocks[1].setRotation(randint(-10,10))
blocks[1].setPosition((block_distance, randint(50,150)))
lock = True
wall_rotation = (-math.sin(blocks[1].getRotation() * math.pi / 180) * 300, -math.cos(blocks[1].getRotation() * math.pi / 180)* 300)
wall_rotation_increased = (-math.sin(blocks[1].getRotation() * math.pi / 180) * 320, -math.cos(blocks[1].getRotation() * math.pi / 180)* 320)
wall_position = blocks[1].getPosition()
corner_pos = (-math.cos(blocks[1].getRotation() * math.pi / 180) * 100, math.sin(blocks[1].getRotation() * math.pi / 180)* 100)
goal_xy = (wall_rotation_increased[0] + wall_position[0] + 488, wall_rotation_increased[1] + wall_position[1] + 488)
corner_xy = (wall_rotation[0] + wall_position[0] + 500 + corner_pos[0], wall_rotation[1] + wall_position[1] + 500 + corner_pos[1])
wall_corner = 400 - corner_xy[1]
print("Wall Height: ", wall_corner)
print("Wall Rotation: ", blocks[1].getRotation())
goal.setPosition(goal_xy)

block_move_u = 0
block_move_r = 0
for i in range(len(agents)):
	for j in range(len(blocks)):
		agents[i].addObject((blocks[j].getMask(), blocks[j].getPosition()[0], blocks[j].getPosition()[1]))


focus = Block(0, (800, 150))
focus.loadImage("image_resources/pointer.png")
won = 0
lost = 0
# main loop
while True:
	# Key Listeners for movement and quitting
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_q:
				counter = trainingNum - 1
			elif event.key == K_r:
				switch = not switch
			elif event.key == K_p:
				pause = not pause
			elif event.key == K_s:
				counter = counter - 1
				timer = -1
			elif event.key == K_v:
				show = 2
			elif event.key == K_b:
				show = 1
			elif event.key == K_n:
				pause = False
				show = 0
			elif event.key == K_m:
				pause = True
				show = 0
				print("stop")

			if not lock:
				if event.key == K_UP:
					block_move_u -= 1
				elif event.key == K_DOWN:
					block_move_u += 1
				elif event.key == K_LEFT:
					block_move_r += 1
				elif event.key == K_RIGHT:
					block_move_r -= 1
				elif event.key == K_RETURN:
					lock = True
					wall_rotation = (-math.sin(blocks[1].getRotation() * math.pi / 180) * 312, -math.cos(blocks[1].getRotation() * math.pi / 180)* 312)
					wall_position = blocks[1].getPosition()
					#corner_pos = (-math.cos(blocks[1].getRotation() * math.pi / 180) * 100, -math.sin(blocks[1].getRotation() * math.pi / 180)* 100)
					goal_xy = (wall_rotation[0] + wall_position[0] + 488, wall_rotation[1] + wall_position[1] + 488)
					goal.setPosition(goal_xy)

					block_move_u = 0
					block_move_r = 0
					for i in range(len(agents)):
						for j in range(len(blocks)):
							agents[i].addObject((blocks[j].getMask(), blocks[j].getPosition()[0], blocks[j].getPosition()[1]))

		elif event.type == KEYUP:
			if not lock:
				if event.key == K_UP:
					block_move_u += 1
				elif event.key == K_DOWN:
					block_move_u -= 1
				elif event.key == K_LEFT:
					block_move_r -= 1
				elif event.key == K_RIGHT:
					block_move_r += 1
	if not pause:

		wall_height = blocks[1].getPosition()[1] + block_move_u
		if wall_height > 0 and wall_height < 300:
			blocks[1].move((0, block_move_u))
		rotation = blocks[1].getRotation() + block_move_r
		if rotation < 15 or rotation > 345:
			blocks[1].rotate(block_move_r)







		if lock:


			if nextRound:
				nextRound = False
				timer = duration
				counter = counter + 1
				for k in range(len(agents)):
					if counter % 20 == 0 and not reset:#and agents[0].won > 0:
						agents[0].finishEpisode()
					score = agents[k].getCog()[0]
					agents[k].reset(counter < trainingNum, score)
					agents[k].randomAgent.nextGame()
				prev = counter
				print("----")
				reset = False
			else:
				timer = timer - 1


			# Control specific agents
			agents[agent_number].move()



			if timer < 0:
				timer = duration
				agents[agent_number].next()

			#	if agents[agent_number].button and counter % 20 > 1:
			#		counter = counter - 1
				#nextRound = True

		if  (counter >= trainingNum) or switch:
			# Draw world
			DS.fill(BLUE)
			for i in range(len(blocks)):
				DS.blit(blocks[i].getImage(), blocks[i].getPosition())
			# Draw agents
			for i in range(len(agents)):
				markers = agents[i].getBox()
				for j in range(len(markers)):
					DS.blit(pointers[0], (int(markers[j][0]), int(markers[j][1])))
				if lock:
					DS.blit(goal.getImage(), goal.getPosition())
					agents[i].parts.run(DS)
					agents[i].sensors.run(DS)
				# Pointer for agents center of gravity
				cog = agents[i].cog
				DS.blit(pointers[0], (int(cog[0]), int(cog[1])))
				# Pointer for collision points
			pygame.display.update()
			CLOCK.tick(FPS)


		if agents[agent_number].restart:


			for i in range(agent_number + 1):
				if agents[i].won:
					won += 1
				else:
					lost += 1
			print("Won:", won, "Lost:", lost)
			if len(network.batch_state_action_reward_tuples) > 50000:
				episode_num += 1
				print("Episode Num:", episode_num)
				#network.update_learn_rate(success_rate)
				network.finishEpisode()
				won = 0
				lost = 0
			else:
				print("Episode Finished:", len(network.batch_state_action_reward_tuples))
			print(agents[agent_number].episode_reward_sum)
			print("=================")
			cog_threshold = 800
			diff_cog = 0



			agent_number = 0
			ag_num += 1
			agents = []
			training = (randint(0,100) < 80)
			agents.append(Agent((390,200), blocks[1], network, ag_num, goal, 25))
			target_counters = [2,3,-1]
			#lock = False

			blocks[1].setRotation(randint(-10,10))
			blocks[1].setPosition((block_distance, randint(50,150)))





			wall_rotation = (-math.sin(blocks[1].getRotation() * math.pi / 180) * 300, -math.cos(blocks[1].getRotation() * math.pi / 180)* 300)
			wall_rotation_increased = (-math.sin(blocks[1].getRotation() * math.pi / 180) * 320, -math.cos(blocks[1].getRotation() * math.pi / 180)* 320)
			wall_position = blocks[1].getPosition()
			corner_pos = (-math.cos(blocks[1].getRotation() * math.pi / 180) * 100, math.sin(blocks[1].getRotation() * math.pi / 180)* 100)
			goal_xy = (wall_rotation_increased[0] + wall_position[0] + 488, wall_rotation_increased[1] + wall_position[1] + 488)
			corner_xy = (wall_rotation[0] + wall_position[0] + 500 + corner_pos[0], wall_rotation[1] + wall_position[1] + 500 + corner_pos[1])
			wall_corner = 400 - corner_xy[1]
			goal.setPosition(goal_xy)

			print("Wall Height: ", wall_corner)
			print("Wall Rotation: ", blocks[1].getRotation())
			for j in range(len(blocks)):
				agents[agent_number].addObject((blocks[j].getMask(), blocks[j].getPosition()[0], blocks[j].getPosition()[1]))
		
		if agents[agent_number].stop == 2:

			print(agents[agent_number].episode_reward_sum)

			last_cog = 400 - agents[agent_number].cog[1]


			agent_number += 1



			boundary = 25
			boundary_counters = [1,0]
			for i in range(agent_number):
				boundary_counters[1] += 1
				if boundary_counters[0] == boundary_counters[1]:
					boundary_counters[0] += 1
					boundary_counters[1] = 0

			#print("Boundary Counter:", boundary_counters)
			for j in range(boundary_counters[1]):
				boundary += 30 + (j * 5)


			if (wall_corner - last_cog) < 30:
				agents.append(Agent((400 - (agent_number * 80),200), focus, network, agent_number, goal, boundary))
				print("Target: Focus")
			elif agent_number == target_counters[0]:
				agents.append(Agent((400 - (agent_number * 80),200), blocks[1], network, agent_number, goal, boundary))
				target_counters = [target_counters[0] + target_counters[1], target_counters[1] + 1, target_counters[2] - 1]
				print("Target: Wall")
			else:
				agents.append(Agent((400 - (agent_number * 80),200), agents[agent_number + target_counters[2]].parts.parts[0], network, agent_number, goal, boundary))
				print("Target:", agent_number + target_counters[2])


			for j in range(len(agents)):
				if agent_number is not j:
					agents[agent_number].addOtherAgent(agents[j])
			for j in range(len(blocks)):
				agents[agent_number].addObject((blocks[j].getMask(), blocks[j].getPosition()[0], blocks[j].getPosition()[1]))

