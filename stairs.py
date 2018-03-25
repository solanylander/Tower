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
parser.add_argument('--discount_factor', type=int, default=1)
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

blocks.append(Block(0, 0, 560))
blocks[0].loadImage("image_resources/flat_floor.png")
blocks.append(Block(0, 585, 150))
blocks[1].loadImage("image_resources/wall.png")

block_move_u, block_move_r = 0,0
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
				block_move_u -= 1
			elif event.key == K_DOWN:
				block_move_u += 1
			elif event.key == K_LEFT:
				block_move_r += 1
			elif event.key == K_RIGHT:
				block_move_r -= 1
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
				block_move_u += 1
			elif event.key == K_DOWN:
				block_move_u -= 1
			elif event.key == K_LEFT:
				block_move_r -= 1
			elif event.key == K_RIGHT:
				block_move_r += 1
		elif event.type == pygame.MOUSEBUTTONDOWN and not lock:
			track_mouse = True
		elif event.type == pygame.MOUSEBUTTONUP and not lock:
			mouse_position = (-10,-10)
			track_mouse = False

	if track_mouse and not lock:
		mouse_position = pygame.mouse.get_pos()
		if mouse_position[1] > 560:
			mouse_position = (mouse_position[0], 560)

	wall_height = blocks[1].getPosition()[1] + block_move_u
	if wall_height > 0 and wall_height < 300:
		blocks[1].moveBlock(0, block_move_u)
	rotation = blocks[1].getRotation() + block_move_r
	if rotation < 15 or rotation > 345:
		blocks[1].rotation(block_move_r)

	pointer_position = (blocks[1].getPosition()[0] - 10, blocks[1].getPosition()[1] - 5)

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