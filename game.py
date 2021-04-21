import pygame
import enum
import copy
import math

class Team(enum.Enum):
	BLUE = 0
	RED = 1

pygame.init()

canvas = pygame.display.set_mode((1000,800))

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

pygame.display.set_caption('Brick Dominance')

def check_collision(ball, brick):
	pass

class Player:
	def __init__(self, team):
		self.gold = 0
		self.hp = 100
		self.team = team

class Brick:
	def __init__(self, xy, hp, size = (1,1), hit_gold = 1, death_gold = 5): # xy => (x,y), size => (size_x, size_y)
		self.xy = xy
		self.hp = hp
		self.size = size
		self.color = (255,255,255)
		self.hit_gold = hit_gold
		self.death_gold = death_gold

		bricks.append(self)

	def draw(self):
		x,y = self.xy
		l,h = self.size
		pygame.draw.rect(canvas, self.color, (x,y,l*20,h*10), 1)

class Paddle:
	def __init__(self, xy, length):
		self.xy = xy
		self.length = length
		self.color = (0, 0, 0)

	def draw(self):
		x,y = self.xy
		pygame.draw.rect(canvas, self.color, (x, y, self.length, 10))




# class BluePaddle(Paddle):
# 	def __init__(self, xy, length):
# 		Paddle.__init__(self, xy, length)
# 		self.color = (0, 163, 255) # nice blue color


class Ball:
	def __init__(self, xy, power, size = 1, speed = 1.0, color = (200,200,200)):
		self.xy = xy
		self.power = power
		self.size = size
		self.color = color
		self.speed = speed
		self.velo = self.normalize([1.0,10]) # normalized vector

		balls.append(self)

	def normalize(self, velo):
		xc, yc = velo
		mag = math.sqrt(xc**2 + yc**2)
		return [xc/mag,yc/mag]


	def move(self):
		x,y = self.xy
		dx, dy = self.velo
		nx, ny = x + dx * self.speed, y + dy * self.speed

		if nx < 0 or nx+self.size*10 > screen_width:
			self.velo[0] = -self.velo[0]


		if ny < 0 or ny+self.size*10 > screen_height:
			self.velo[1] = -self.velo[1]

		dx, dy = self.velo
		nx, ny = x + dx * self.speed, y + dy * self.speed
		self.xy = (nx,ny)

	def draw(self):
		x,y = self.xy
		pygame.draw.ellipse(canvas, (200,200,200), (x, y, 10*self.size, 10*self.size))


# global lists
balls = []
default_ball = Ball((screen_width//3, screen_height//2), Team.BLUE, speed=2.5, size=10)

bricks = []
test_brick = Brick((500, 500), 1)

# instantiating objects




running = True
while running:

	canvas.fill((0,0,0)) # clear frame


	pygame.time.delay(1000//120)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		#if event.type == pygame.key:


	for ball in balls:
		ball.move()
		ball.draw()

	for brick in bricks:
		brick.draw()

	pygame.display.update()
