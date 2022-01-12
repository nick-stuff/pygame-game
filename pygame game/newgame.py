import pygame
import random
import os
import time
from worldData import worldData, world2data, world3data
from pygame.locals import *

pygame.init()
FPS =60

screenWidth = 1000
screenHeight = 1000
playerVel = 3

walkSound = pygame.mixer.Sound('walk.mp3')
walkSound.set_volume(0.20)

jumpSound = pygame.mixer.Sound('jump.mp3')
jumpSound.set_volume(0.15)

stompSound = pygame.mixer.Sound('stomp.mp3')
stompSound.set_volume(0.5)

coinSound = pygame.mixer.Sound('coin.mp3')
coinSound.set_volume(0.6)

pygame.mixer.music.load('bgm.mp3')
pygame.mixer.music.set_volume(0.3)
tile_size = 50
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("more pygame stuff")
font = pygame.font.SysFont('Arial',32)
sunImg = pygame.image.load("sun.png").convert_alpha()
sunImg = pygame.transform.scale(sunImg, (300,200))
skyImg = pygame.image.load("sky.png")

enemySprite = pygame.image.load("Run.png")
enemySpriteJump = pygame.image.load("jump.png")
enemySpriteHitGround = pygame.image.load("Ground.png")
enemySpriteDeath = pygame.image.load("Dead.png")
playerSprite = pygame.image.load("player.png")
stoneImg = pygame.image.load('floordeffuse.png')
coinImg = pygame.image.load('coins1.png')

winText = font.render('YOU WON!!! AND AS SUCH ARE', 1, (0,0,0) )
winText2 = font.render('APPOINTED THE TITLE EPIC GAMER!', 1, (0,0,0))

movingPlatformList = [] 
#playerSprite = pygame.transform.scale(playerSprite, (1500,75))
playerHIT = pygame.USEREVENT + 1
delay = pygame.USEREVENT + 2
loadNew = pygame.USEREVENT + 3 

world1Enemies = (500,500,45,45), (500,100,45,45), (700,800,45,45)
world2Enemies = (700,500,45,45), (500,100,45,45), (700,800,45,45), (300,500,45,45)
world3Enemies = (700,500,45,45), (100,100,45,45), (300,600,45,45)
class world():
	def __init__(self,data):
		self.tile_list = []
		self.positiveX = True
		self.movingPlatformList = []
		self.coinList = []
		self.spriteX = 1
		dirtImg = pygame.image.load('dirt.png')
		grassImg = pygame.image.load('grass.png')
		rowCount = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirtImg, (tile_size, tile_size))
					imgRect = img.get_rect()
					imgRect.x = col_count * tile_size
					imgRect.y = rowCount * tile_size
					tile = (img, imgRect,1)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grassImg, (tile_size, tile_size))
					imgRect = img.get_rect()
					imgRect.x = col_count * tile_size
					imgRect.y = rowCount * tile_size
					tile = (img, imgRect,2)
					self.tile_list.append(tile)
				if tile == 5:
					img = pygame.transform.scale(stoneImg, (tile_size, tile_size))
					imgRect = img.get_rect()
					imgRect.x = col_count * tile_size
					imgRect.y = rowCount * tile_size
					tile = (img,imgRect,5)
					self.tile_list.append(tile)
					moving = (tile, False)
					movingPlatformList.append(moving)
				if tile == 7:
					img = coinImg
					imgRect = pygame.Rect(0,0,32,36)
					imgRect.x = (col_count * tile_size) +9
					imgRect.y = rowCount * tile_size + 14
					tile = (img, imgRect,7)
					self.coinList.append(tile)
				col_count +=1
			rowCount +=1
	def draw(self, SpriteCtr):
		movingRight = None
		for tile in self.tile_list:
			if tile[2] == 5:
				testTile = tile[1]
				testTilePositive = tile[1].copy()
				testTilePositive.x+=2
				testTileNegative = tile[1].copy()
				for tiles in self.tile_list:
					if not rectangleEquals(testTile,tiles[1]):
						if testTilePositive.colliderect(tiles[1]):
							self.positiveX = False
						elif testTileNegative.colliderect(tiles[1]):
							self.positiveX = True
				if self.positiveX:
					for tiles in movingPlatformList:
						x,rect,y = tiles[0]
						if rectangleEquals(testTile,rect):
							img = pygame.transform.scale(stoneImg, (tile_size, tile_size))
							rect.x+=2
							tile = (img,rect,5)
							movingRight = True
							moving = tile,movingRight
							movingPlatformList.remove(tiles)
							movingPlatformList.append(moving)
							break
				else:
					for tiles in movingPlatformList:
						x,rect,y = tiles[0]
						if rectangleEquals(testTile,rect):
							img = pygame.transform.scale(stoneImg, (tile_size, tile_size))
							rect.x-=2
							tile = (img,rect,5)
							movingRight = False
							moving = tile, movingRight
							movingPlatformList.remove(tiles)
							movingPlatformList.append(moving)
							break
			screen.blit(tile[0],tile[1])
		if SpriteCtr % 5 == 0:
			self.spriteX+=18
		if self.spriteX > 76:
			self.spriteX = 1 
		for coin in self.coinList:
			subsurf = (self.spriteX,0,16,16)
			subsurfCoin= coin[0].subsurface(subsurf)
			subsurfCoin= pygame.transform.scale(subsurfCoin,(36, 36))
			screen.blit(subsurfCoin,coin[1])
	def returnCoinList(self):
		return self.coinList
	def returnList(self):
		return self.tile_list
def rectangleEquals(tile1,tile2):
	if tile1.x == tile2.x and tile1.y == tile2.y and tile1.width == tile2.width and tile1.height == tile2.height:
		return True
	return False
class enemy():
	def __init__(self, x,y,w,h):
		self.enemyRect= pygame.Rect(x,y,w,h)
		self.v = 0
		self.justJumped = False
		self.spriteX = 0
		self.radians = 0
		self.markedForDeletion = False
		self.positiveX = True
		self.jumped= False
	def update(self, objlist, playerLoc, SpriteCtr, playerInvulnerable):
		#collisionX(objlist,5)
		self.v+=1
		lower = self.collisionY(objlist,self.v, self.positiveX)
		self.collisionPlayer(playerLoc, playerInvulnerable)
		if lower[0] and self.v > 0:
			self.v = 0
			if self.jumped == True:
				self.JustLanded = True
			self.jumped = False
			dy = lower[1]- (self.enemyRect.y + self.enemyRect.height)
			self.enemyRect.y+=dy
		elif lower[0] and self.v <=0:
			self.enemyRect.y+=0
		else:
			self.enemyRect.y+=self.v

		if lower[2] and self.positiveX:
			self.positiveX = False
		elif lower[2] and not self.positiveX:
			self.positiveX = True
		if lower[3] and not self.jumped:
			self.v-=12
			self.jumped = True 
		if self.positiveX:
			if (self.collisionX(objlist, 3)):
				self.enemyRect.x+=0
			else:
				self.enemyRect.x+=3
		else:
			if(self.collisionX(objlist, -3)):
				self.enemyRect.x+=0
			else:
				self.enemyRect.x-=3
		#pygame.draw.rect(screen,(255,255,255), self.enemyRect, 2)
		#if self.markedForDeletion:
		#	self.draw(0)
		
		Image, location = self.draw(SpriteCtr)
		screen.blit(Image, location)


	def draw(self, SpriteCtr):
		if self.jumped:
			if self.markedForDeletion:
				cropped = (0,0,19,14)
				subsurf = enemySpriteDeath.subsurface(cropped)
				subsurf = pygame.transform.scale(subsurf, (42,42))
				subsurfCopy = pygame.transform.rotate(subsurf, self.radians)
				self.radians+=10
				if self.justJumped:
					self.enemyRect.y+=int(subsurfCopy.get_height()/2)
					self.enemyRect.x+=int(subsurfCopy.get_width()/2)
					self.justJumped = False
				return(subsurfCopy, (self.enemyRect.x - int(subsurfCopy.get_width()/2), self.enemyRect.y - int(subsurfCopy.get_height()/2)))
			else:
				cropped = (0,0,20,17)
				subsurf = enemySpriteJump.subsurface(cropped)
		else:
			self.jumpCounter= 0
			if self.spriteX > 156:
				self.spriteX = 0
			elif SpriteCtr % 5 == 0:
				self.spriteX += 27
			cropped = (self.spriteX,0,20,17)
			subsurf = enemySprite.subsurface(cropped)
		subsurf = pygame.transform.scale(subsurf, (45,45))
		if self.positiveX:
			subsurf = pygame.transform.flip(subsurf, True, False)
		return(subsurf, self.enemyRect)
	def collisionX(self, objlist,newloc):
		for obj in objlist:
			if obj[1].colliderect(self.enemyRect.x + newloc, self.enemyRect.y,45, 45):
				return True
		return False
	#test if entity is about to fall. if part of the rectangle has a different distance to the ground, we know this
	def collisionY(self, objlist,dy, positiveX):
		testRect = None
		testRectAdjacentUpper = None
		testRectAdjacentLower = None
		AdjUpper = None
		AdjLower = None
		noObjectFound = False
		for obj in objlist:
			if obj[1].colliderect(self.enemyRect.x, self.enemyRect.y + dy,45, 45):
				if positiveX:
					AdjUpper= pygame.Rect(obj[1].x+50, obj[1].y-50,50,50)
					AdjSide = pygame.Rect(obj[1].x+50, obj[1].y,50,50)
					AdjLower= pygame.Rect(obj[1].x+50, obj[1].y+50,50,50) 
				else:
					AdjUpper= pygame.Rect(obj[1].x-50, obj[1].y-50,50,50) 
					AdjSide = pygame.Rect(obj[1].x-50, obj[1].y,50,50) 
					AdjLower= pygame.Rect(obj[1].x-50, obj[1].y+50,50,50) 
				for objects in objlist:
					if objects[1].colliderect(AdjUpper):
						testRectAdjacentUpper = objects[1]
					elif objects[1].colliderect(AdjSide):
						testRect= objects[1]
					elif objects[1].colliderect(AdjLower):
						testRectAdjacentLower = objects[1]
				if self.enemyRect.x > 900:
					return(True, obj[1].y, True, False)
				elif self.enemyRect.x < 55:
					return(True, obj[1].y, True, False)
				if testRectAdjacentUpper != None:
					if not positiveX:
						if self.enemyRect.x <= obj[1].x+2:
							return(True, obj[1].y, False, True)
						else:
							return(True, obj[1].y, False, False)
					return(True, obj[1].y, False, True)
				elif testRectAdjacentLower != None:
					return(True, obj[1].y, False, False)
				elif testRect != None and (self.enemyRect.x + self.enemyRect.width) < 940:
					return(True, obj[1].y,False, False)
				else:
					if not positiveX:
						if self.enemyRect.x <= obj[1].x+1:
							return(True, obj[1].y, True, False)
						else:
							return(True, obj[1].y, False, False)
					return(True, obj[1].y, True, False)
		return(False, 0, False, False)
	def collisionPlayer(self, playerLoc, playerIsInvuln):
		#self.enemyRect.y < playerLoc.y +playerLoc.height and (playerLoc.y +playerLoc.height < self.enemyRect.y + self.enemyRect.height)
		if not playerIsInvuln:
			if self.enemyRect.y > playerLoc.y +playerLoc.height - 10 and self.enemyRect.y < playerLoc.y +playerLoc.height + 10:
				if (playerLoc.x > self.enemyRect.x and playerLoc.x < self.enemyRect.x + self.enemyRect.width):
					self.markedForDeletion = True
					stompSound.play()
				elif (playerLoc.x + playerLoc.width < self.enemyRect.x+self.enemyRect.width and playerLoc.x + playerLoc.width > self.enemyRect.x):
					self.markedForDeletion = True
					stompSound.play()
	def deathHandle(self):
		if not self.jumped:
			self.v-=11
			self.jumped = True
			self.justJumped = True
			self.enemyRect.y-=self.v 
		else:
			self.v+=1
			if self.v > 30:
				self.v = 30
			self.enemyRect.y+=self.v 
		if self.positiveX:
			self.enemyRect.x+=3
		else:
			self.enemyRect.x-=3
		Image, Location = self.draw(0)
		screen.blit(Image,Location)
		if self.enemyRect.y>1000:
			return True
		else:
			return False
	def returnLoc(self):
		return self.enemyRect
class player():
	def __init__(self):
		self.jumped = False
		self.v = 0
		self.counter=0
		self.Sprite = playerSprite
		self.playerRect = pygame.Rect(350, 700, 45, 45)
		self.spriteX = 4
		self.spriteY = 0
		self.flippedLeft = False
		self.flippedRight = False
		self.health = 10
		self.timer = 0
		self.auxilaryTimer = 0
	def collisionX(self,objlist, newloc, key):
		for obj in objlist:
			if obj[1].colliderect(self.playerRect.x + newloc[0], self.playerRect.y,45, 45) and key[pygame.K_d]:
				return (True, False, obj[1].x)
			elif obj[1].colliderect(self.playerRect.x - newloc[0], self.playerRect.y,45, 45) and key[pygame.K_a]:
				return (False, True, obj[1].x)
		return (False, False, 0)
	def collisionXMovingPlatform(self,objlist,movingRight):
		for obj in objlist:
			if obj[1].colliderect(self.playerRect.x + 5, self.playerRect.y,45, 45) and movingRight:
				return (True, False, obj[1].x)
			elif obj[1].colliderect(self.playerRect.x - 5, self.playerRect.y,45, 45) and not movingRight:
				return (False, True, obj[1].x)
		return (False, False, 0)	
	def collisionY(self, objlist,dy):
		for obj in objlist:
			if obj[1].colliderect(self.playerRect.x, self.playerRect.y + dy,45, 45):
				return(True, obj[1], obj[2])
		return(False, 0)
	def coinCollision(self, coinList, invuln):
		if not invuln:
			for coin in coinList:
				if self.playerRect.colliderect(coin[1]):
					coinSound.play()
					coinList.remove(coin)
	def update(self, key, frames,objlist, enemies, invuln, coinlist):
		
		#screen.blit(playerSprite, self.playerRect)
		self.collisionEnemy(enemies)
		self.coinCollision(coinlist, invuln)
		print(self.health)
		#spriteRect = Sprite.get_rect()
		cropped = (self.spriteX,self.spriteY,16,17)
		subsurf = playerSprite.subsurface(cropped)
		if (key[pygame.K_d] or key[pygame.K_a]):
			if self.auxilaryTimer%12 == 0 and not self.jumped:
				walkSound.play()
			if self.counter == 0:
				self.spriteX = 100
				self.counter+=1
			else:
				if (frames % 5 == 0):
					self.spriteX+=24
				if self.spriteX >= 244:
					self.spriteX = 100
			self.auxilaryTimer+=1
		else:
			self.auxilaryTimer = 0
			self.counter = 0
			if (frames % 10 == 0):
				self.spriteX+=24
			if self.spriteX > 91:
				self.spriteX = 4
		self.Sprite = pygame.transform.scale(subsurf, (45,45))

		xCollide = self.collisionX(objlist, (5,0), key)
		
		if key[pygame.K_d] and self.playerRect.x < 950 and not xCollide[0]:
			self.playerRect.x+=playerVel
			self.flippedLeft = False
		elif key[pygame.K_a] and self.playerRect.x > 0 and not xCollide[1]: 
			self.playerRect.x-=playerVel
			self.flippedLeft = True
		if (self.flippedLeft):
			self.Sprite = pygame.transform.flip(self.Sprite, True, False)
		
		

		if key[pygame.K_SPACE] and not self.jumped:
			if self.v > 0:
				self.v = 0
			self.v-=15
			jumpSound.play()
			self.jumped = True

		self.v +=1
		if self.v > 20:
			self.v = 20

		dy = self.v
		
		lower = self.collisionY(objlist, dy)
		if lower[0] and self.v > 0:
			self.jumped = False
			self.v = 0
			dy = lower[1].y - (self.playerRect.y + self.playerRect.height)
			if lower[2] == 5:
				for tile in movingPlatformList:
					drawInfo, rect, identifier = tile[0]
					if rectangleEquals(lower[1], rect):
						xCollide = self.collisionXMovingPlatform(objlist, tile[1])
						if tile[1]:
							if xCollide[0]:
								self.playerRect.x+=0
							else:
								self.playerRect.x+=2
						else:
							if xCollide[1]:
								self.playerRect.x-=0
							else:
								self.playerRect.x-=2
		elif lower[0] and self.v <= 0:
			self.v = 0 
			dy = 0
		self.playerRect.y+=dy

	
		#print(lower[0])
		#collision(objlist)
		#pygame.draw.rect(screen,(255,255,255), self.playerRect, 2)
		if invuln:
			self.timer+=1
			if not self.timer%5 == 0:
				screen.blit(self.Sprite, self.playerRect)
		else:
			self.timer=0
			screen.blit(self.Sprite, self.playerRect)
	#def movementX(self):
	def returnLoc(self):
		return self.playerRect
	def subtractHealth(self):
		self.health-=1
	def collisionEnemy(self, enemies):
		#self.enemyRect.y < playerLoc.y +playerLoc.height and (playerLoc.y +playerLoc.height < self.enemyRect.y + self.enemyRect.height)
		for en in enemies:
			enemyLoc = en.returnLoc()
			if not en.markedForDeletion:
				if self.playerRect.y + self.playerRect.height > enemyLoc.y and self.playerRect.y +self.playerRect.height <= enemyLoc.y + enemyLoc.height:
					if (self.playerRect.x > enemyLoc.x and self.playerRect.x < enemyLoc.x + enemyLoc.width):
						pygame.event.post(pygame.event.Event(playerHIT))
					elif (self.playerRect.x + self.playerRect.width < enemyLoc.x+enemyLoc.width and self.playerRect.x + self.playerRect.width > enemyLoc.x):
						pygame.event.post(pygame.event.Event(playerHIT))
def loadEnemies(worldID):
	if worldID == 1:
		worldEnemies = world1Enemies
	elif worldID == 2:
		worldEnemies = world2Enemies
	elif worldID == 3:
		worldEnemies = world3Enemies
	enemyList = []
	for enemyData in worldEnemies:
		x,y,w,h = enemyData
		enemyList.append(enemy(x,y,w,h))
	return enemyList
def main():
	theWorld = world(worldData)
	worldID = 1
	player1 = player()
	SpriteCount = 0
	clock = pygame.time.Clock()
	run = True	
	enemies = loadEnemies(worldID)
	invuln = False
	pygame.mixer.music.play(10000)
	while run:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == playerHIT:
				if not invuln:
					player1.subtractHealth()
					pygame.time.set_timer(pygame.USEREVENT + 2, 5000, True)
					invuln = True
			if event.type == delay:
				invuln = False
			if event.type == loadNew:
				worldID+=1
				if worldID == 2:
					theWorld = world(world2data)
					player1 = player()
					enemies = loadEnemies(worldID)
				elif worldID == 3:
					theWorld = world(world3data)
					player1 = player()
					enemies = loadEnemies(worldID)
				elif worldID == 4:
					screen.blit(skyImg, (0,0))
					screen.blit(sunImg, (250,50))
					#screen.fill((255,255,255))
					screen.blit(winText, (250,500))
					screen.blit(winText2, (215,550))
					pygame.display.update()
					pygame.time.delay(5000)
					theWorld = world(worldData)
					player1 = player()
					worldID = 1
					enemies = loadEnemies(worldID)



		keys_pressed = pygame.key.get_pressed()
		screen.blit(skyImg, (0,0))
		screen.blit(sunImg, (250,50))
		
		SpriteCount+=1
		theWorld.draw(SpriteCount)

		for en in enemies:
			if en.markedForDeletion:
				dead = en.deathHandle()
				if dead:
					enemies.remove(en)
			else:
				en.update(theWorld.returnList(), player1.returnLoc(), SpriteCount, invuln)
		
		player1.update(keys_pressed, SpriteCount, theWorld.returnList(), enemies,invuln, theWorld.returnCoinList())
		
		if not theWorld.returnCoinList():
			pygame.event.post(pygame.event.Event(loadNew))
			


		#x,y = pygame.mouse.get_pos()
		#print(x,y)
		pygame.display.update()

	pygame.quit()

if __name__ == "__main__":
	main()