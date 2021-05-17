

import pygame
import enum
import time
import math
import random

# constants / settings

delay = 180


class Screen:
	START = 0
	SELECT = 1
	GAME = 2
	END = 3

	@staticmethod
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

	@staticmethod
	def draw_select():
		pass





class Team(enum.Enum): # (UP, DOWN, POWERUP)
	BLUE = (pygame.K_w, pygame.K_s, pygame.K_x)
	RED = (pygame.K_UP, pygame.K_DOWN, pygame.K_KP0)
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
font18 = pygame.font.Font('valorant.ttf', 19)

def reset_ball_and_brick():
	for sector in balls:
		sector.clear()

	for sector in bricks:
		sector.clear()

def instantiate_start():
	Brick(545, 430, Team.NONE, 1, (831, 141), color=(20, 20, 20))

	Ball(200, 300, Team.NONE, 0, 16, 2)
	Ball(200, 1080-300, Team.NONE, 0, 16, 2)
	Ball(1920-200, 1080-300, Team.NONE, 0, 16, 2)
	Ball(1920-200, 300, Team.NONE, 0, 16, 2)

def instantiate_select():
	reset_ball_and_brick()




def instantiate_game():
	global balls, paddles, zones, bricks, flagged_bricks, blue_player, red_player, blue_paddle, red_paddle

	# BALLS
	balls = [[], [], []]
	Ball(screen_width // 2, screen_height // 2, Team.NONE, 1, speed=4, diameter=16)

	Ball(screen_width // 2, screen_height // 2, Team.BLUE, 1, speed=3, diameter=10)
	Ball(screen_width // 2, screen_height // 2, Team.RED, 1, speed=3, diameter=10)

	# PADDLES

	blue_paddle = Paddle(400, screen_height // 2, Team.BLUE)
	red_paddle = Paddle(1502, screen_height // 2, Team.RED)

	# ZONES
	zones = []

	PlayerZone(0, 0, (100, 1080), blue_player)
	PlayerZone(1820, 0, (100, 1080), red_player)

	# BRICKS
	bricks = [[], [], []]  # 2d list, [0] index is list of blue bricks, [1] is red, [2] is neutral (interacted by both teams)
	flagged_bricks = []  # bricks flagged for removal

	for i in range(5):
		for j in range(18):
			Brick(i * 30 + 200, j * 60, Team.BLUE, 10, size=(28, 58))
			Brick(i * 30 + 1560, j * 60, Team.RED, 10, size=(28, 58))



	blue_player.powerup = Hex()
	red_player.powerup = Clone()


def normalize(velo):
	xc, yc = velo
	mag = math.sqrt(xc ** 2 + yc ** 2)
	return [xc / mag, yc / mag]

def velo_to_angle(velo):
	"""returns angle of velocity in radians"""
	return math.atan2(velo[1], velo[0])

def angle_to_velo(radians):
	"""returns normalized velocity vector of given angle in radians"""
	return [math.cos(radians), math.sin(radians)]


def brick_collision(ball, brick, allies=False):
	if ball.get_rect().colliderect(brick.get_rect()):

		if not allies:
			brick.on_hit(ball)

		if not ball.already_hit:

			ball_center_x = ball.x + ball.diameter / 2

			if brick.x <= ball_center_x and ball_center_x <= brick.x + brick.size[0]:
				if not ball.effects["ghost"]:
					ball.bounce(1)
			else:
				if not ball.effects["ghost"]:
					ball.bounce(0)

			ball.already_hit = True


def paddle_collision(ball, paddle):
	if ball.get_rect().colliderect(paddle.get_rect()):
		paddle.on_hit(ball)

		ball_center_y = ball.y + ball.diameter / 2

		if paddle.y <= ball_center_y and ball_center_y <= paddle.y + paddle.size[1]:
			paddle_center_y = paddle.y + paddle.size[1] / 2

			df = ball_center_y - paddle_center_y

			if not ball.effects["ghost"]:
				ball.bounce(0, df)

		else:
			if not ball.effects["ghost"]:
				ball.bounce(1)



def zone_collision(ball, zone):
	return ball.get_rect().colliderect(zone.get_rect()) and ball.team != zone.player.team



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

		self.powerup = None


	def can_purchase(self):
		if self.gold >= self.powerup.cost:
			self.gold -= self.powerup.cost

			self.display_gold()
			return True
		return False

	def gain_gold(self, amount):
		if self.powerup == None:
			self.gold += amount
			return

		self.gold = min(self.gold + amount, self.powerup.charges * self.powerup.cost)
		#self.display_gold()

	def get_percentage_gold(self):
		return self.gold / (self.powerup.charges * self.powerup.cost)

	def display_gold(self):
		content = f"{self.gold}/{self.powerup.charges * self.powerup.cost}"

		text = font24.render(content, True, TeamColor.NONE.value)
		text_rect = text.get_rect()

		if self.team == Team.BLUE:
			text = font24.render(content, True, TeamColor.BLUE.value)

			px, py, pw, ph = 500, 1059, 200, 16

			text_rect.x = px - text_rect.width - 10
			text_rect.y = 1080 - text_rect.height

			# (30, 72, 153)


			pygame.draw.rect(canvas, (20, 20, 20), (px-5, py-5, pw+10, ph+10))
			pygame.draw.rect(canvas, (50, 50, 50), (px, py, pw, ph))
			if self.gold != 0:
				pygame.draw.rect(canvas, (61, 122, 255), (px, py, pw * self.get_percentage_gold(), ph))

			for i in range(1,self.powerup.charges):
				pygame.draw.rect(canvas, (30, 30, 30), (px + pw- i * (pw/self.powerup.charges), py, 5, ph))

		elif self.team == Team.RED:
			text = font24.render(content, True, TeamColor.RED.value)


			px, py, pw, ph = 1220, 1059, 200, 16

			text_rect.x = px - text_rect.width - 10
			text_rect.y = 1080 - text_rect.height

			# (30, 72, 153)


			pygame.draw.rect(canvas, (20, 20, 20), (px-5, py-5, pw+10, ph+10))
			pygame.draw.rect(canvas, (50, 50, 50), (px, py, pw, ph))
			if self.gold != 0:
				pygame.draw.rect(canvas, (255, 61, 61), (px, py, pw * self.get_percentage_gold(), ph))

			for i in range(1,self.powerup.charges):
				pygame.draw.rect(canvas, (30, 30, 30), (px + pw- i * (pw/self.powerup.charges), py, 5, ph))


		canvas.blit(text, text_rect)

class Ball(Object):
	def __init__(self, x, y, team, power, diameter=1, speed=1.0, color=(200, 200, 200), velo=(888, 888)):
		Object.__init__(self, x, y, (diameter, diameter))
		self.diameter = diameter
		self.power = power
		self.team = team
		self.color = color
		self.speed = speed

		if velo == (888,888):
			self.velo = normalize((random.random()-0.5, random.random()-0.5))  # normalized vector
		else:
			self.velo = normalize(velo)

		self.already_hit = False
		self.damage_cooldown = 0.3 # seconds in the zone before taking damage
		self.damage_timer = 0 # timer to keep track of when last took damage

		self.effects = {"ghost": False, "hex": False,}

		if team == Team.BLUE:
			balls[0].append(self)
		elif team == Team.RED:
			balls[1].append(self)
		else:  # neutral
			balls[2].append(self)

		self.set_default_color()

	def set_default_color(self):
		if self.team == Team.BLUE:
			self.color = (60, 120, 255)
		elif self.team == Team.RED:
			self.color = (255, 60, 60)
		else:  # neutral
			self.color = (230, 230, 230)



	def move(self):
		nx, ny = self.x + self.velo[0] * self.speed * dtf, self.y + self.velo[1] * self.speed * dtf

		if nx < 0 or nx + self.size[0] > screen_width:
			ball.bounce(0)

		if ny < 0 or ny + self.size[1] > screen_height:
			ball.bounce(1)

		self.x, self.y = self.x + self.velo[0] * self.speed * dtf, self.y + self.velo[1] * self.speed * dtf

		if self.speed >= 4:
			Particle(
				self.x+self.diameter/2,
				self.y+self.diameter/2,
				6,
				velo=( -(self.velo[0]+ 0.5*(random.random()*2-1)), -(self.velo[1]+ 0.5*(random.random()*2-1)) ),
				color=(60,60,60),
				speed=1
			)



	def bounce(self, ix, df = 0):
		noise = 1 / 50
		df_noise = 1 / 400
		adjustment_noise = 1 / 8

		self.velo[ix] = -self.velo[ix]
		self.velo[ix] += noise * (random.random() - 0.5)
		self.velo[1 - ix] += noise * (random.random() - 0.5)


		if df == 0:
			self.velo = normalize(self.velo)
		else:
			radians = velo_to_angle(self.velo)
			if self.x < 960:
				radians = radians + df_noise * df  # add negative if on LS, subtract positive on RS
			else:
				radians = radians - df_noise * df  # subtract negative if on LS, subtract positive on RS
			self.velo = angle_to_velo(radians)

		if abs(self.velo[0]) < abs(self.velo[1]):
			if self.velo[1] < 0:
				self.velo[1] += adjustment_noise
			else:
				self.velo[1] -= adjustment_noise

		self.velo = normalize(self.velo)

	def draw(self):
		pygame.draw.ellipse(canvas, self.color, (self.x, self.y, self.diameter, self.diameter))
		#draw_circle(canvas, int(self.x), int(self.y), self.size//2, (200, 200, 200))

class Brick(Object):
	def __init__(self, x, y, team, hp=1, size=(20, 10), hit_gold=1, death_gold=5, color=(255,255,255)):
		Object.__init__(self, x, y, size)
		self.hp = hp
		self.maxhp = hp
		self.color = color
		self.hit_gold = hit_gold
		self.death_gold = death_gold
		self.team = team

		self.effects = {"hex": False,}
		self.hex_timer = 0; self.hex_cooldown = 1

		if team == Team.BLUE:
			bricks[0].append(self)
		elif team == Team.RED:
			bricks[1].append(self)
		else:  # neutral
			bricks[2].append(self)

		self.set_default_color()


	def set_default_color(self):
		if self.team == Team.BLUE:
			self.color = (60, 120, 255)
		elif self.team == Team.RED:
			self.color = (255, 60, 60)


	def draw(self):
		w, h = self.size
		hp_indicator = (self.hp / self.maxhp)

		if self.effects["hex"]:
			self.color = (143, 255, 9)

		r, g, b = self.color

		if self.team == Team.BLUE or self.team == Team.RED:
			pygame.draw.rect(canvas, (r * hp_indicator, g * hp_indicator, b * hp_indicator), (self.x, self.y, w, h))
		else:
			pygame.draw.rect(canvas, self.color, (self.x, self.y, w, h))

	def on_hit(self, ball):
		self.take_damage_from_ball(ball)

		if ball.effects["hex"] and not self.effects["hex"]:
			self.effects["hex"] = True

	# print(f"COLLISION: {self.x},{self.y}")

	def death_particles(self):
		for _ in range(40):
			FadeParticle(
				self.x + self.size[0] / 2,
				self.y + self.size[1] / 2,
				6,
				velo=normalize((random.random() * 2 - 1, random.random() * 2 - 1)),
				color=self.color,
				speed=0.7,
				lifetime=0.8,
			)

	def take_damage(self, damage):
		self.hp -= damage

		if self.hp <= 0:
			self.death_particles()
			if self.team == Team.BLUE:
				flagged_bricks.append((self, 0))
				red_player.gain_gold(self.death_gold)
			elif self.team == Team.RED:
				flagged_bricks.append((self, 1))
				blue_player.gain_gold(self.death_gold)
			else:
				flagged_bricks.append((self, 2))
		else:
			if self.team == Team.BLUE:
				red_player.gain_gold(self.hit_gold)
			elif self.team == Team.RED:
				blue_player.gain_gold(self.hit_gold)

	def take_damage_from_ball(self, ball):

		self.hp -= ball.power


		if self.hp <= 0:
			self.death_particles()
			if self.team == Team.BLUE:
				flagged_bricks.append((self, 0))
				red_player.gain_gold(self.death_gold)
			elif self.team == Team.RED:
				flagged_bricks.append((self, 1))
				blue_player.gain_gold(self.death_gold)
			else:
				flagged_bricks.append((self, 2))
		else:
			if self.team == Team.BLUE:
				red_player.gain_gold(self.hit_gold)
			elif self.team == Team.RED:
				blue_player.gain_gold(self.hit_gold)

	def hex(self):
		if time.time() > self.hex_timer + self.hex_cooldown:
			print("TOOK DAMAGE FROM HEX")
			self.take_damage(1)

			self.hex_timer = time.time()








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

	def set_default_color(self):
		if self.team == Team.BLUE:
			self.color = (60, 120, 255)
		elif self.team == Team.RED:
			self.color = (255, 60, 60)

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


class Particle(Object):
	def __init__(self, x, y, diameter, velo=(888,888), color=(255,255,255), speed=1.0, lifetime=0.2):
		Object.__init__(self, x, y, (diameter, diameter))
		self.diameter = diameter

		if velo == (888,888):
			self.velo = (random.random()*2-1, random.random()*2-1)
		else:
			self.velo = velo


		self.color = color
		self.speed = speed

		self.lifetime = lifetime

		self.timer = time.time()

		particles.append(self)


	def move(self):
		self.x, self.y = self.x + self.velo[0] * self.speed * dtf, self.y + self.velo[1] * self.speed * dtf

	def draw(self):
		pygame.draw.ellipse(canvas, self.color, (int(self.x), int(self.y), self.diameter//2, self.diameter//2))

	def auto_remove(self):
		if time.time() > self.timer + self.lifetime:
			flagged_particles.append(self)

class FadeParticle(Particle):
	def __init__(self, x, y, diameter, velo=(888,888), color=(255,255,255), speed=1.0, lifetime=0.2):
		Particle.__init__(self, x, y, diameter, velo, color, speed, lifetime)

		if velo == (888,888):
			self.velo = (random.random()*2-1, random.random()*2-1)
		else:
			self.velo = velo

		particles.append(self)


	def move(self):
		self.x, self.y = self.x + self.velo[0] * self.speed * dtf, self.y + self.velo[1] * self.speed * dtf

	def draw(self):
		time_left = max(self.timer + self.lifetime - time.time(), 0)

		new_color = []
		for v in self.color:
			new_color.append(
				int(v * (time_left/self.lifetime)**(1/50) )
			)

		self.color = tuple(new_color)
		pygame.draw.ellipse(canvas, self.color, (int(self.x), int(self.y), self.diameter//2, self.diameter//2))

	def auto_remove(self):
		if time.time() > self.timer + self.lifetime:
			flagged_particles.append(self)


# Particle(
# 	800,
# 	800,
# 	6,
# 	velo=(random.random() * 2 - 1, random.random() * 2 - 1),
# 	color=(250, 250, 250),
# 	speed=3,
# 	lifetime=5.0,
# )




class PowerUp:
	def __init__(self, cost, charges, duration):
		self.cost = cost
		self.charges = charges # maximum charges that are intended to store
		self.duration = duration

		self.symbol = '?'
		self.description = "DEFAULT POWERUP"

		self.timer = 0
		self.called = 0


	# to be implemented by subclass
	def execute(self, team, **kwargs):
		ix = 0 if team == Team.BLUE else 1
		if self not in ticking_powerups[ix]:

			ticking_powerups[ix].append(self)
			self.called = 0
		self.timer = time.time() + max(self.timer + self.duration - time.time(), 0)
		self.called += 1

	# to be implemented by subclass
	def reset(self, team, **kwargs):
		ix = 0 if team == Team.BLUE else 1
		ticking_powerups[ix].remove(self)

	def tick(self, **kwargs):
		pass

	def is_finished(self):
		return time.time() > self.timer + self.duration

class Accelerate(PowerUp):
	def __init__(self):
		PowerUp.__init__(self, cost=25, charges=5, duration=2)
		self.name = "Accelerate"
		self.symbol = 'A'
		self.description = "Activating the ability will consume a charge: Increases all allied ball speed by 30% and damage by +2. This effect lasts for 2s, reactivating the ability again within its duration will extend and add to the existing bonuses. Costs -15."


	def execute(self, ball, team, **kwargs):
		print("fasttt")
		PowerUp.execute(self, team)
		ball.speed += 0.9
		ball.power += 2



	def reset(self, ball, team, **kwargs):
		print("normal")
		PowerUp.reset(self, team)
		for _ in range(self.called):
			ball.speed -= 0.9
			ball.power -= 2

class Obfuscate(PowerUp):
	def __init__(self):
		PowerUp.__init__(self, cost=10, charges=3, duration=2)
		self.name = "Obfuscate"
		self.symbol = 'O'
		self.description = "Activating the ability will consume a charge: Grant invisibility to all allied balls. This effect lasts for 2s, reactivating the ability again within 2s will extend the invisibility duration. Costs -18."



	def execute(self, ball, team, **kwargs):
		print("goodbye")
		PowerUp.execute(self, team)
		ball.color = (0,0,0)



	def reset(self, ball, team, **kwargs):
		print("normal")
		PowerUp.reset(self, team)
		ball.set_default_color()

class Explosive(PowerUp):
	def __init__(self):
		PowerUp.__init__(self, cost=60, charges=1, duration=0.5)
		self.name = "Explosive"
		self.symbol = 'X'
		self.description = "Activating the ability will, cause the ball will explode after 0.5s. Enemy bricks will take damage based on proximity to the explosion; explosion damage will scale with ball damage. Costs -120."


	def calc_damage(self, ball, brick):
		dx = (brick.x + brick.size[0] / 2) - (ball.x + ball.diameter / 2)
		dy = (brick.y + brick.size[1] / 2) - (ball.y + ball.diameter / 2)

		dist = math.sqrt(dx ** 2 + dy ** 2)
		amp = max(500 - dist, 0) / 500

		return round(8 * amp**2 * ball.power)

	def explosion_particles(self, ball):
		for _ in range(60):
			Particle(
				ball.x + ball.diameter / 2,
				ball.y + ball.diameter / 2,
				8,
				velo=normalize((random.random()*2-1, random.random()*2-1)),
				color=(60, 60, 60),
				speed=5,
				lifetime=0.3,
			)

	def execute(self, team, **kwargs):
		PowerUp.execute(self, team)
		ball.color = (255,255,255)

	def reset(self, ball, team, **kwargs):
		PowerUp.reset(self, team)
		if ball.team == Team.BLUE:
			for brick in bricks[1] + bricks[2]:
				brick.take_damage(self.calc_damage(ball, brick))

		elif ball.team == Team.RED:
			for brick in bricks[0] + bricks[2]:
				brick.take_damage(self.calc_damage(ball, brick))
		else:
			for brick in bricks[0] + bricks[1] + bricks[2]:
				brick.take_damage(self.calc_damage(ball, brick))

		ball.set_default_color()
		self.explosion_particles(ball)

class Ghost(PowerUp):
	def __init__(self):
		PowerUp.__init__(self, cost=100, charges=2, duration=0.5)
		self.name = "Ghost"
		self.symbol = 'G'
		self.description = "Activating the ability will consume a charge: Allied balls will be able to pass through bricks for 0.5s, all bricks in contact with the ball will be destroyed. Balls gain 20du. Costs -100."


	def execute(self, ball, team, **kwargs):
		PowerUp.execute(self, team)
		ball.power += 10
		ball.effects["ghost"] = True
		ball.color = (80, 80, 80)

	def reset(self, ball, team, **kwargs):
		PowerUp.reset(self, team)

		for _ in range(self.called):
			ball.power -= 10

		ball.effects["ghost"] = False
		ball.set_default_color()

class Hex(PowerUp):
	def __init__(self):
		PowerUp.__init__(self, cost=40, charges=4, duration=12)
		self.name = "Hex"
		self.symbol = 'H'
		self.description = "Activating the ability will consume a charge: When an allied ball collides withs an enemy brick, the brick will lost -1 health every 1s. Costs -40."


	def execute(self, ball, team, **kwargs):
		PowerUp.execute(self, team)
		ball.effects["hex"] = True
		ball.color = (143, 255, 9)


	def reset(self, ball, team, **kwargs):
		PowerUp.reset(self, team)
		ball.effects["hex"] = False
		ball.set_default_color()

class Clone(PowerUp):
	def __init__(self):
		PowerUp.__init__(self, cost=60, charges=4, duration=0)
		self.name = "Clone"
		self.symbol = 'C'
		self.description = "Activating the ability will consume a charge: The original ball clones itself, each clone is stronger than the previous, gaining +1 damage."

		self.times_cloned = 0

	def execute(self, team, **kwargs):
		PowerUp.execute(self, team)
		Ball(ball.x, ball.y, ball.team, power=1 + self.times_cloned, speed=ball.speed, diameter=ball.diameter)
		self.times_cloned += 1

		if team == Team.BLUE:
			ball.color = (0,50,255)
		elif team == Team.RED:
			ball.color = (255,50,0)

class Wither(PowerUp):
	def __init__(self):
		PowerUp.__init__(self, cost=80, charges=3, duration=8)
		self.name = "Hex"
		self.symbol = 'H'
		self.description = "Activating the ability will consume a charge: Slow the enemy paddle by 30% / 60% / 90% for 8s."

	def execute(self, team, enemy_paddle, **kwargs):
		PowerUp.execute(self, team)
		enemy_paddle.speed = max(enemy_paddle.speed - 0.9, 0.3)
		enemy_paddle.color = (90, 90, 90)



	def reset(self, team, enemy_paddle, **kwargs):
		PowerUp.reset(self, team)
		enemy_paddle.speed = 3
		enemy_paddle.set_default_color()






# ROOK BOBBY ROOK














# global lists & instantiating objects

balls = [[], [], []]
paddles = []
zones = []

bricks = [[], [], []]
flagged_bricks = []

ticking_powerups = [[],[]]

particles = []
flagged_particles = []

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



	# for _ in range(1):
	# 	FadeParticle(
	# 		500,
	# 		500,
	# 		8,
	# 		velo=normalize((random.random() * 2 - 1, random.random() * 2 - 1)),
	# 		color=(255,255,255),
	# 		speed=0.75,
	# 		lifetime=0.8,
	# 	)

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

		# draw particles
		for particle in particles:
			particle.move()
			particle.draw()
			particle.auto_remove()

		for particle in flagged_particles:
			particles.remove(particle)

		flagged_particles.clear()



	elif screen == Screen.GAME:

		keys = pygame.key.get_pressed()
		for paddle in paddles:
			direction = 0
			if keys[paddle.team.value[0]]:
				direction -= 1
			if keys[paddle.team.value[1]]:
				direction += 1

			paddle.move(direction)

		#print(ticking_powerups)

		for event in events:
			if event.type == pygame.KEYUP:
				if event.key == blue_player.team.value[2] and blue_player.can_purchase():
					for ball in balls[0]:
						blue_player.powerup.execute(ball=ball, team=Team.BLUE, enemy_paddle=red_paddle)

						if type(blue_player.powerup) == Clone:
							break

				elif event.key == red_player.team.value[2] and red_player.can_purchase():
					for ball in balls[1]:
						red_player.powerup.execute(ball=ball, team=Team.RED, enemy_paddle=blue_paddle)

						if type(red_player.powerup) == Clone:
							break



		print(ticking_powerups)

		for powerup in ticking_powerups[0]:
			if powerup.is_finished():
				for ball in balls[0]:
					try:
						blue_player.powerup.reset(ball=ball, team=Team.BLUE, enemy_paddle=red_paddle)
					except ValueError:
						if type(powerup) == Clone:
							pass
						else:
							raise ValueError

		for powerup in ticking_powerups[1]:
			if powerup.is_finished():
				for ball in balls[1]:
					try:
						red_player.powerup.reset(ball=ball, team=Team.RED, enemy_paddle=blue_player)
					except ValueError:
						if type(powerup) == Clone:
							pass
						else:
							raise ValueError


		# draw particles
		for particle in particles:
			particle.move()
			particle.draw()
			particle.auto_remove()

		for particle in flagged_particles:
			particles.remove(particle)

		flagged_particles.clear()

		# neutral ball
		for sector in balls:
			for ball in sector:

				ball.already_hit = False
				for brick in bricks[0] + bricks[1] + bricks[2]:
					brick_collision(ball, brick, allies=(brick.team == ball.team))

				for target, team_id in flagged_bricks:
					bricks[team_id].remove(target)

				flagged_bricks.clear()

				for paddle in paddles:
					paddle_collision(ball, paddle)

		for zone in zones:
			zone.testfor()
			zone.draw()

		# draw on to canvas
		for layer in bricks:
			for brick in layer:

				for effect in brick.effects:
					if brick.effects[effect]:
						print(effect)
						if effect == "hex":
							brick.hex()

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
