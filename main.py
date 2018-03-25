import math, random, sys, pygame, os, time, argparse
from pygame.locals import *
from agent import Agent
from part import Part
from block import Block
from policy_network import Network
from network import random_network


parser = argparse.ArgumentParser()
parser.add_argument('--hidden_layer_size', type=int, default=200)
parser.add_argument('--learning_rate', type=float, default=0.0005)
parser.add_argument('--batch_size_episodes', type=int, default=1)
parser.add_argument('--checkpoint_every_n_episodes', type=int, default=2)
parser.add_argument('--load_checkpoint', action='store_true')
parser.add_argument('--discount_factor', type=int, default=0.9998)
args = parser.parse_args()


# define display surface			
W, H = 1080, 600
HW, HH = W / 2, H / 2
AREA = W * H

# define some colors
BLUE = (0, 153, 255, 221)

network = Network(args.hidden_layer_size, args.learning_rate, checkpoints_dir='checkpoints')
random_agent = random_network()
random_agent.initialiseNetwork()
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
pointers[2] = pygame.image.load("image_resources/pointerThree.png").convert_alpha()

blocks, agents = [],[]
agentNumber = 1
# Adds agents into the world
blocks.append(Block(0, 000, 400))
blocks[0].loadImage("image_resources/flat_floor.png")



block_move_u, block_move_r = 0,0
wall_height = 350
lock = False
angle = 0









blocks.append(Block(0, 200, 150))
blocks[1].loadImage("image_resources/wall.png")
agents.append(Agent((390,200), args, blocks[1], network, random_agent))
agents.append(Agent((170,200), args, agents[0].parts[0], network, random_agent))
agents.append(Agent((0,200), args, blocks[1], network, random_agent))
# Tell all agents about the objects within the world so they can detect collisions
for i in range(len(agents)):
	for j in range(len(agents)):
		if i is not j:
			agents[i].addOtherAgent(agents[j])


timer = duration
epTimer = 0
counter = 0
show = False
reset = False
pause = False
resetCounter = 0
nextRound = False
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
			blocks[1].moveBlock(0, block_move_u)
		rotation = blocks[1].getRotation() + block_move_r
		if rotation < 15 or rotation > 345:
			blocks[1].rotation(block_move_r)

		if lock:


			if nextRound:
				epTimer = 0
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
				epTimer += 1

			if timer < 0:
				timer = duration
				agents[0].randomize(int(epTimer/400))
				#if timer == 333 or timer == 666:
				#	agents[0].randomAgent.nextGame()


			# Control specific agents
			for j in range(len(agents)):
				if agents[j].move(show):
					if agents[j].button and counter % 20 > 1:
						counter = counter - 1
					nextRound = True
		if  (counter >= trainingNum) or switch:
			# Draw world
			DS.fill(BLUE)
			for i in range(len(blocks)):
				DS.blit(blocks[i].getImage(), blocks[i].getPosition())
			# Draw agents
			for i in range(len(agents)):
				markers = agents[i].getMarkers()
				for j in range(len(markers)):
					DS.blit(pointers[0], (int(markers[j][0]), int(markers[j][1])))
				if lock:
					agents[i].run(DS)
					DS.blit(agents[i].sensor.getImage(), agents[i].sensor.getPosition(True))
					DS.blit(agents[i].sensor.getImage(), agents[i].sensor.getPosition(False))
				# Pointer for agents center of gravity
				cog = agents[i].getCog()
				DS.blit(pointers[1], (int(cog[0]), int(cog[1])))
				# Pointer for collision points
			pygame.display.update()
			CLOCK.tick(FPS)