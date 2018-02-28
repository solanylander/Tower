import math, random, sys, pygame, os, time, argparse
from pygame.locals import *
from agent import Agent
from part import Part
from block import Block


parser = argparse.ArgumentParser()
parser.add_argument('--hidden_layer_size', type=int, default=200)
parser.add_argument('--learning_rate', type=float, default=0.0005)
parser.add_argument('--batch_size_episodes', type=int, default=1)
parser.add_argument('--checkpoint_every_n_episodes', type=int, default=10)
parser.add_argument('--load_checkpoint', action='store_true')
parser.add_argument('--discount_factor', type=int, default=1.00)
args = parser.parse_args()


# define display surface			
W, H = 1080, 600
HW, HH = W / 2, H / 2
AREA = W * H

# define some colors
BLUE = (0, 255, 200, 255)

# Place window in the center of the screen
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (700,80)
# initialise display
pygame.init()
CLOCK = pygame.time.Clock()
DS = pygame.display.set_mode((W, H))
pygame.display.set_caption("Ant Tower Project")
FPS = 120
trainingNum = 10000
duration = 1000
switch = 0

# Get the image resources for the world
pointers = [None, None, None]
pointers[0] = pygame.image.load("image_resources/pointer.png").convert_alpha()
pointers[1] = pygame.image.load("image_resources/pointerTwo.png").convert_alpha()
pointers[2] = pygame.image.load("image_resources/pointerThree.png").convert_alpha()

blocks, agents = [],[]
agentNumber = 1
# Adds agents into the world
for p in range(0,agentNumber):
	agents.append(Agent((300,200 + 175 * p), args))
	agents[p].randomAgent.initialiseNetwork()
	blocks.append(Block(0, 0, 400 + p * 175))
	# agents.append(Agent((50,-25 + 175 * p)))
	# blocks.append(Block(0, 0, 55 + p * 175))
	blocks[p].loadImage("image_resources/flat_floor.png")
# Tell all agents about the objects within the world so they can detect collisions
for i in range(len(agents)):
	for j in range(len(blocks)):
		agents[i].addObject((blocks[j].getMask(), blocks[j].getPosition()[0], blocks[j].getPosition()[1]))

timer = duration
counter = 0
show = False
reset = False
pause = False
resetCounter = 0
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
			elif event.key == K_b:
				show = 2
			elif event.key == K_n:
				show = 1
			elif event.key == K_m:
				show = 0
				print("stop")
	if not pause:
		if timer < 0:
			timer = duration
			counter = counter + 1
			x = (trainingNum - counter) / 4.48
			for k in range(len(agents)):
				if counter % 20 == 0 and not reset:
					agents[k].finishEpisode()
				score = agents[k].getCog()[0]
				if counter % 5 == 0 or resetCounter == 3:
					agents[k].reset(counter < trainingNum, score, False, True)
				else:
					agents[k].reset(counter < trainingNum, score, False, False)
				agents[k].randomAgent.nextGame()
			prev = counter
			print("----")
			reset = False
		else:
			timer = timer - 1
			if timer == 333 or timer == 666:
				agents[0].randomAgent.nextGame()


		if timer == duration - 2:
			if agents[0].collide(False):
				timer = -1
				counter = counter - 1
				print("Reset")
				reset = True
				resetCounter += 1
			else:
				resetCounter = 0

		# Control specific agents
		for j in range(len(agents)):
			if agents[j].move(timer, show):
				timer = -1
		if  (counter >= trainingNum) or switch:
			# Draw world
			DS.fill(BLUE)
			for i in range(len(blocks)):
				DS.blit(blocks[i].getImage(), blocks[i].getPosition())
			# Draw agents
			for i in range(len(agents)):
				agents[i].run(DS)
				# Pointer for agents center of gravity
				cog = agents[i].getCog()
				DS.blit(pointers[1], (int(cog[0]), int(cog[1])))
				markers = agents[i].getMarkers()
				# Pointer for collision points
				for j in range(len(markers)):
					DS.blit(pointers[0], (int(markers[j][0]), int(markers[j][1])))
			pygame.display.update()
			CLOCK.tick(FPS)