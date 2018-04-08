import math, random, sys, pygame, os, time, argparse
from pygame.locals import *
from agent import Agent
from part import Part
from block import Block


parser = argparse.ArgumentParser()
parser.add_argument('--hidden_layer_size', type=int, default=200)
parser.add_argument('--learning_rate', type=float, default=0.0005)
parser.add_argument('--batch_size_episodes', type=int, default=1)
parser.add_argument('--checkpoint_every_n_episodes', type=int, default=2)
parser.add_argument('--load_checkpoint', action='store_true')
parser.add_argument('--discount_factor', type=int, default=0.9995)
args = parser.parse_args()

# define display surface			
W, H = 1080, 600
HW, HH = W / 2, H / 2
AREA = W * H

# define some colors
BLUE = (0, 153, 255, 221)

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (250,80)


pygame.init()
CLOCK = pygame.time.Clock()
DS = pygame.display.set_mode((W, H))
pygame.display.set_caption("Ant Tower Project")
FPS = 120

pointers = [None, None, None]
pointers[0] = pygame.image.load("image_resources/big_pointer.png").convert_alpha()
pointers[1] = pygame.image.load("image_resources/pointerTwo.png").convert_alpha()
pointers[2] = pygame.image.load("image_resources/big_pointer_2.png").convert_alpha()

blocks, agents = [],[]

blocks.append(Block(0, (0, 560)))
blocks[0].loadImage("image_resources/flat_floor.png")
blocks.append(Block(0, (980, 350)))
blocks[1].loadImage("image_resources/wall.png")

agents.append(Agent((816,448), args))
agents[0].setRotations([90,0,-90,0,0,20,0,0,0,0,0,20,0,0,0])
agents[0].setPositions(agents[0].parts[0].getPosition())
agents.append(Agent((866,393), args))
agents[1].setRotations([50,50,90,340,340,60,340,340,90,340,340,60,340,340,90])
agents[1].setPositions(agents[1].parts[0].getPosition())
agents.append(Agent((753,455), args))
agents[2].setRotations([230,180,240,0,0,0,0,0,0,0,0,0,0,0,0])
agents[2].setPositions(agents[2].parts[0].getPosition())
agents.append(Agent((854,445), args))
agents[3].setRotations([-90,180,90,0,0,0,90,0,0,0,0,0,90,0,0])
agents[3].setPositions(agents[3].parts[0].getPosition())
agents.append(Agent((713,460), args))
agents[4].setRotations([50,10,10,300,60,350,0,0,355,300,60,350,0,0,355])
agents[4].setPositions(agents[4].parts[0].getPosition())
agents.append(Agent((543,487), args))
agents[5].setRotations([0,50,0,310,50,50,0,0,0,310,50,50,0,0,0])
agents[5].setPositions(agents[5].parts[0].getPosition())
agents.append(Agent((933,278), args))
agents[6].setRotations([0,0,0,310,50,50,0,0,0,310,50,50,0,0,0])
agents[6].setPositions(agents[6].parts[0].getPosition())
agents.append(Agent((773,394), args))
agents[7].setRotations([20,20,40,310,70,10,0,0,0,310,70,10,0,0,0])
agents[7].setPositions(agents[7].parts[0].getPosition())

block_move = (0,0)
wall_height = 350
pointer_position = (blocks[1].getPosition()[0] - 5, blocks[1].getPosition()[1] - 5)
mouse_position = (-10,-10)
track_mouse = False
lock = False
distance = (0,0)
support_distance = [0,0]
angle = 0

while True:
	# Key Listeners for movement and quitting
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_UP:
				block_move -= 1
			elif event.key == K_DOWN:
				block_move += 1
			elif event.key == K_RETURN and mouse_position[1] == 560:
				distance = (blocks[1].getPosition()[0] - mouse_position[0], mouse_position[1] - blocks[1].getPosition()[1])
				angle = math.atan(distance[1]/distance[0])
				support_distance = (math.cos(angle) * 100, math.sin(angle) * 100)
				print(distance)
				print(support_distance)
				print("----------------")
				lock = True
			elif event.key == K_l:
				lock = False
				track_mouse = False

		elif event.type == KEYUP:
			if event.key == K_UP:
				block_move[0] += 1
			elif event.key == K_DOWN:
				block_move[0] -= 1
			elif event.key == K_LEFT:
				block_move[1] += 1
			elif event.key == K_RIGHT:
				block_move[1] -= 1
		elif event.type == pygame.MOUSEBUTTONDOWN and not lock:
			track_mouse = True
		elif event.type == pygame.MOUSEBUTTONUP and not lock:
			mouse_position = (-10,-10)
			track_mouse = False

	if track_mouse and not lock:
		mouse_position = pygame.mouse.get_pos()
		if mouse_position[1] > 560:
			mouse_position = (mouse_position[0], 560)

	wall_height = blocks[1].getPosition()[1] + block_move[0]
	if wall_height > 200 and wall_height < 500:
		blocks[1].moveBlock(0, block_move[0])

	blocks[1].rotation(block_move[1])

	pointer_position = (blocks[1].getPosition()[0] - 5, blocks[1].getPosition()[1] - 5)

	# Draw world
	DS.fill(BLUE)
	for i in range(len(blocks)):
		DS.blit(blocks[i].getImage(), blocks[i].getPosition())
	if track_mouse:
		pygame.draw.line(DS, (0, 0, 255), mouse_position, blocks[i].getPosition())
		#DS.blit(pointers[0], (mouse_position[0] - 5, mouse_position[1] - 5))
		#if lock:
		#	for i in range(1, int(distance[0]/support_distance[0]) + 1):
				#DS.blit(pointers[2], (support_distance[0] * i + mouse_position[0], (support_distance[1] * -i) + mouse_position[1]))

	#DS.blit(pointers[0], pointer_position)

	for i in range(len(agents)):
		agents[i].run(DS)

	pygame.display.update()
	CLOCK.tick(FPS)