import pygame
from pygame import gfxdraw

import enum
import time
import math
import random

# constants / settings

delay = 180


class Screen:
	START = 0
	GAME = 1
	END = 2

	def draw_start():

		text1 = font80.render("Brick", True, TeamColor.BLUE.value)
		text_rect1 = text1.get_rect()

		text2 = font80.render("Dominance", True, TeamColor.RED.value)
		text_rect2 = text2.get_rect()


		total_rect = pygame.Rect(0, 0, text_rect1.w + text_rect2.w, text_rect1.h)
		total_rect.move_ip(1920//2-total_rect.w//2, 500-total_rect.h//2)

		text_rect1.move_ip(total_rect.x, total_rect.y)
		text_rect2.move_ip(total_rect.x + text_rect1.w, total_rect.y)


		canvas.blit(text1, text_rect1)
		canvas.blit(text2, text_rect2)


		text3 = font24.render("< Click Anywhere to Continue >", True, (80, 80, 80))
		text_rect3 = text3.get_rect()
		text_rect3.move_ip(1920//2-text_rect3.w//2, 1080//2-text_rect3.h//2)

		canvas.blit(text3, text_rect3)





class Team(enum.Enum):
	BLUE = (pygame.K_w, pygame.K_s)
	RED = (pygame.K_UP, pygame.K_DOWN)
	NONE = ()


class TeamColor(enum.Enum):
	BLUE = (50, 120, 255)
	RED = (255, 50, 50)
	NONE = (255, 255, 255)



pygame.init()

canvas = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

pygame.display.set_caption('Brick Dominance')

font80 = pygame.font.Font('valorant.ttf', 80)
font50 = pygame.font.Font('valorant.ttf', 50)
font30 = pygame.font.Font('valorant.ttf', 30)
font24 = pygame.font.Font('valorant.ttf', 24)

def instantiate_start():
	global balls, paddles, zones, bricks, flagged

	Brick(545, 430, Team.NONE, 1, (831, 141), color=(20, 20, 20))

	for i in range(5):
		Ball(1920//2, 1080//3, Team.NONE, 0, 16, 2)

def instantiate_game():
	global balls, paddles, zones, bricks, flagged, blue_player, red_player

	# BALLS
	balls = [[], [], []]
	Ball(screen_width // 2, screen_height // 2, Team.NONE, 1, speed=4, diameter=16)

	Ball(screen_width // 2, screen_height // 2, Team.BLUE, 1, speed=3, diameter=10)
	Ball(screen_width // 2, screen_height // 2, Team.RED, 1, speed=3, diameter=10)

	# PADDLES

	Paddle(400, screen_height // 2, Team.BLUE)
	Paddle(1502, screen_height // 2, Team.RED)

	# ZONES
	zones = []

	PlayerZone(0, 0, (100, 1080), blue_player)
	PlayerZone(1820, 0, (100, 1080), red_player)

	# BRICKS
	bricks = [[], [],
			  []]  # 2d list, [0] index is list of blue bricks, [1] is red, [2] is neutral (interacted by both teams)
	flagged = []  # bricks flagged for removal

	for i in range(5):
		for j in range(21):
			Brick(i * 32 + 200, j * 52, Team.BLUE, 3, size=(30, 50))
			Brick(i * 32 + 1560, j * 52, Team.RED, 3, size=(30, 50))

def velo_to_angle(velo):
	"""returns angle of velocity in radians"""
	return math.atan2(velo[1], velo[0])

def angle_to_velo(radians):
	"""returns normalized velocity vector of given angle in radians"""
	return [math.cos(radians), math.sin(radians)]


def brick_collision(ball, brick):
	if ball.get_rect().colliderect(brick.get_rect()):
		brick.on_hit(ball)

		if not ball.already_hit:

			ball_center_y = ball.y + ball.diameter / 2

			if brick.y <= ball_center_y and ball_center_y <= brick.y + brick.size[1]:
				ball.bounce(0)
			else:
				ball.bounce(1)

			ball.already_hit = True


def paddle_collision(ball, paddle):
	if ball.get_rect().colliderect(paddle.get_rect()):
		paddle.on_hit(ball)

		ball_center_y = ball.y + ball.diameter / 2

		if paddle.y <= ball_center_y and ball_center_y <= paddle.y + paddle.size[1]:
			paddle_center_y = paddle.y + paddle.size[1] / 2

			df = ball_center_y - paddle_center_y

			ball.bounce(0, df)

		else:
			ball.bounce(1)



def zone_collision(ball, zone):
	return ball.get_rect().colliderect(zone.get_rect())



class Object:
	def __init__(self, x, y, size):
		self.x = x
		self.y = y
		self.size = size

	def get_rect(self):
		return pygame.Rect(self.x, self.y, self.size[0], self.size[1])


class Player:
	def __init__(self, team):
		self.gold = 0
		self.hp = 100
		self.team = team

	def display_gold(self):
		content = f"+{self.gold}"

		text = font30.render(content, True, TeamColor.NONE.value)
		text_rect = text.get_rect()

		if self.team == Team.BLUE:
			text = font30.render(content, True, TeamColor.BLUE.value)

			text_rect.x = 0
			text_rect.y = 1050
		elif self.team == Team.RED:
			text = font30.render(content, True, TeamColor.RED.value)

			text_rect.x = 1820
			text_rect.y = 1050


		canvas.blit(text, text_rect)



class Brick(Object):
	def __init__(self, x, y, team, hp=1, size=(20, 10), hit_gold=1, death_gold=5, color=(255,255,255)):
		Object.__init__(self, x, y, size)
		self.hp = hp
		self.maxhp = hp
		self.color = (255, 255, 255)
		self.hit_gold = hit_gold
		self.death_gold = death_gold
		self.team = team

		if team == Team.BLUE:
			bricks[0].append(self)
			self.color = TeamColor.BLUE.value
		elif team == Team.RED:
			bricks[1].append(self)
			self.color = TeamColor.RED.value
		else:  # neutral
			bricks[2].append(self)
			self.color = color

	def draw(self):
		l, h = self.size
		hp_indicator = (self.hp / self.maxhp)

		r, g, b = self.color

		if self.team == Team.BLUE:
			pygame.draw.rect(canvas, (r * hp_indicator, g * hp_indicator, b * hp_indicator), (self.x, self.y, l, h))
		elif self.team == Team.RED:
			pygame.draw.rect(canvas, (r * hp_indicator, g * hp_indicator, b * hp_indicator), (self.x, self.y, l, h))
		else:
			pygame.draw.rect(canvas, self.color, (self.x, self.y, l, h))

	def on_hit(self, ball):
		self.take_damage(ball)

	# print(f"COLLISION: {self.x},{self.y}")

	def take_damage(self, ball):

		self.hp -= ball.power


		if self.hp <= 0:


			if self.team == Team.BLUE:
				flagged.append((self, 0))
				red_player.gold += self.death_gold
			elif self.team == Team.RED:
				flagged.append((self, 1))
				blue_player.gold += self.death_gold
			else:
				flagged.append((self, 2))
		else:
			if self.team == Team.BLUE:
				red_player.gold += self.hit_gold
			elif self.team == Team.RED:
				blue_player.gold += self.hit_gold




class Paddle(Object):
	def __init__(self, x, y, team, length=180, speed=3, refresh=0.02):
		Object.__init__(self, x, y, (18, length))
		self.team = team
		self.speed = speed
		self.refresh = refresh
		self.color = TeamColor.RED.value if team == Team.RED else TeamColor.BLUE.value

		self.past = 0

		paddles.append(self)

	def move(self, direction):
		# if time.time() > self.past + self.refresh:
		if True:
			if direction == -1:
				self.y -= self.speed * dtf
			elif direction == 1:
				self.y += self.speed * dtf
			self.past = time.time()

	def on_hit(self, ball):
		#print("hit by paddle")
		pass

	def draw(self):
		pygame.draw.rect(canvas, self.color, (self.x, self.y, self.size[0], self.size[1]))


class Zone(Object):
	def __init__(self, x, y, size):
		Object.__init__(self, x, y, size)

		zones.append(self)

	def testfor(self):
		for sector in balls:
			for ball in sector:
				if zone_collision(ball, self):
					self.execute(ball)

	def execute(self, ball):  # abstract function
		pass

	def draw(self):
		pass



class PlayerZone(Zone):
	def __init__(self, x, y, size, player):
		Zone.__init__(self, x, y, size)
		self.player = player

	def execute(self, ball):

		if time.time() > ball.damage_timer + ball.damage_cooldown:
			self.player.hp -= ball.power
			ball.damage_timer = time.time()




	def draw(self):

		text = font50.render(f"{self.player.hp}", True, TeamColor.NONE.value)
		text_rect = text.get_rect()

		l,h = self.size
		if self.player.team == Team.BLUE:
			pygame.draw.rect(canvas, (10, 24, 51), (self.x, self.y, l, h))
			text = font50.render(f"{self.player.hp}", True, TeamColor.BLUE.value)

			text_rect.x = 0
		elif self.player.team == Team.RED:
			pygame.draw.rect(canvas, (51, 10, 10), (self.x, self.y, l, h))
			text = font50.render(f"{self.player.hp}", True, TeamColor.RED.value)

			text_rect.x = 1820


		canvas.blit(text, text_rect)




class Upgrade:
	def __init__(self):
		pass


# IMPLEMENT EXPLOSION :)

# class BluePaddle(Paddle):
# 	def __init__(self, xy, length):
# 		Paddle.__init__(self, xy, length)
# 		self.color = (0, 163, 255) # nice blue color


class Ball(Object):
	def __init__(self, x, y, team, power, diameter=1, speed=1.0, color=(200, 200, 200), velo=(888, 888)):
		Object.__init__(self, x, y, (diameter, diameter))
		self.diameter = diameter
		self.power = power
		self.color = color
		self.speed = speed

		if velo == (888,888):
			self.velo = self.normalize((random.random()*2-1, 0.5*random.random()*2-1))  # normalized vector
		else:
			self.velo = self.normalize(velo)

		self.already_hit = False
		self.damage_cooldown = 0.3 # seconds in the zone before taking damage
		self.damage_timer = 0 # timer to keep track of when last took damage

		if team == Team.BLUE:
			balls[0].append(self)
			self.color = (60, 120, 255)
		elif team == Team.RED:
			balls[1].append(self)
			self.color = (255, 60, 60)
		else:  # neutral
			balls[2].append(self)
			self.color = (230, 230, 230)

	def normalize(self, velo):
		xc, yc = velo
		mag = math.sqrt(xc ** 2 + yc ** 2)
		return [xc / mag, yc / mag]

	def move(self):
		nx, ny = self.x + self.velo[0] * self.speed * dtf, self.y + self.velo[1] * self.speed * dtf

		if nx < 0 or nx + self.size[0] > screen_width:
			ball.bounce(0)

		if ny < 0 or ny + self.size[1] > screen_height:
			ball.bounce(1)

		self.x, self.y = self.x + self.velo[0] * self.speed * dtf, self.y + self.velo[1] * self.speed * dtf

	def bounce(self, ix, df = 0):
		noise = 1 / 50
		df_noise = 1 / 400

		self.velo[ix] = -self.velo[ix]
		self.velo[ix] += noise * (random.random() - 0.5)
		self.velo[1 - ix] += 1/5 * noise * (random.random() - 0.5)


		if df == 0:
			self.velo = self.normalize(self.velo)
		else:
			radians = velo_to_angle(self.velo)
			if self.x < 960:
				radians = radians + df_noise * df  # add negative if on LS, subtract positive on RS
			else:
				radians = radians - df_noise * df  # subtract negative if on LS, subtract positive on RS
			self.velo = angle_to_velo(radians)

	def draw(self):
		pygame.draw.ellipse(canvas, self.color, (self.x, self.y, self.diameter, self.diameter))
		#draw_circle(canvas, int(self.x), int(self.y), self.size//2, (200, 200, 200))


# global lists & instantiating objects

balls = [[], [], []]
paddles = []
zones = []
bricks = [[], [], []]
flagged = []

screen = Screen.START

# PLAYERS
blue_player = Player(Team.BLUE)
red_player = Player(Team.RED)



instantiate_start()






clock = pygame.time.Clock()

dt = clock.tick(delay)
dtfc = dt

running = True
while running:

	canvas.fill((0, 0, 0))  # clear frame

	# attempts to maintain constant framerate (180fps)
	dt = clock.tick(delay)
	dtf = dt / dtfc

	events = pygame.event.get()

	for event in events:
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			pass

	if screen == Screen.START:

		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:

				screen = Screen.GAME
				instantiate_game()

		for brick in bricks[2]:
			brick.draw()

		for ball in balls[2]:

			ball.already_hit = False
			for brick in bricks[2]:
				brick_collision(ball, brick)

		for sector in balls:
			for ball in sector:
				ball.move()
				ball.draw()

		Screen.draw_start()





	elif screen == Screen.GAME:

		keys = pygame.key.get_pressed()
		for paddle in paddles:
			direction = 0
			if keys[paddle.team.value[0]]:
				direction -= 1
			if keys[paddle.team.value[1]]:
				direction += 1

			paddle.move(direction)

		# blue team balls
		for ball in balls[0]:

			ball.already_hit = False
			for brick in bricks[1] + bricks[2]:
				brick_collision(ball, brick)

			for target, team_id in flagged:
				bricks[team_id].remove(target)

			flagged.clear()

			for paddle in paddles:
				paddle_collision(ball, paddle)

		# red team balls
		for ball in balls[1]:

			ball.already_hit = False
			for brick in bricks[0] + bricks[2]:
				brick_collision(ball, brick)

			for target, team_id in flagged:
				bricks[team_id].remove(target)

			flagged.clear()

			for paddle in paddles:
				paddle_collision(ball, paddle)

		# neutral ball
		for ball in balls[2]:

			ball.already_hit = False
			for brick in bricks[0] + bricks[1] + bricks[2]:
				brick_collision(ball, brick)

			for target, team_id in flagged:
				bricks[team_id].remove(target)

			flagged.clear()

			for paddle in paddles:
				paddle_collision(ball, paddle)

		for zone in zones:
			zone.testfor()
			zone.draw()

		# draw on to canvas
		for layer in bricks:
			for brick in layer:
				brick.draw()

		for paddle in paddles:
			paddle.draw()

		for sector in balls:
			for ball in sector:
				ball.move()
				ball.draw()

		red_player.display_gold()
		blue_player.display_gold()







	pygame.display.update()
