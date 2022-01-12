import pygame
import os
import random
import ctypes
import numpy 
pygame.init()

font = pygame.font.SysFont('Arial',32)
font_smaller = pygame.font.SysFont('Arial',24)
text = font.render('Level Editor', True, (255,255,255), (0,0,0) )

screenWidth = 1200
screenHeight = 1000
white = (255, 255, 255)
dirtImg = pygame.image.load('dirt.png')
grassImg = pygame.image.load('grass.png')

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("level editor")
savebtn = pygame.image.load('save_btn.png')

sunImg = pygame.image.load("sun.png").convert_alpha()
sunImg = pygame.transform.scale(sunImg, (300,200))
skyImg = pygame.image.load("sky.png")
coinImg = pygame.image.load('coins1.png')
dumpText = font_smaller.render('Dump to Console', True, (255,255,255), (0,0,0) )
coinText = font_smaller.render('Place Coin [on]', True, (255,255,255), (0,0,0) )
coinTextOff = font_smaller.render('Place Coin [off]', True, (255,255,255), (0,0,0) )
clearText = font_smaller.render('CLEAR', True, (255,255,255), (0,0,0) )
worldListInit = []
tile_size = 50

def drawGrid():
	for line in range(0,20):
		pygame.draw.line(screen,white, (0,line * tile_size), (1000, line * tile_size))
		pygame.draw.line(screen,white, (line * tile_size,0), (line * tile_size,1000))
def clickHandlerInit(Location, Boxes, Master, DragAndHold, PlaceCoin):
	running = True
	rows = 0
	xpos = Location[0]
	ypos = Location[1]
	while(rows < 20 and running):
		cols=0
		while (cols < 20 and running):
			rect = Boxes[rows][cols]
			if (xpos > rect.x and xpos < rect.x + 50 and ypos > rect.y and ypos < rect.y +50):
				if PlaceCoin:
					return(11)
					running = False
				elif (Master[rows][cols] == 0):
					return(1)
					running = False
				elif (Master[rows][cols] == 1):
					return(2)
					running = False
				elif (Master[rows][cols] == 2):
					return(0)
					running = False
				elif (Master[rows][cols] == 7):
					return(7)
					running = False
			cols+=1
		rows+=1
def clickHandler(Location, Boxes, Master, key, PlaceCoin):
	running = True
	rows = 0
	xpos = Location[0]
	ypos = Location[1]
	while(rows < 20 and running):
		cols=0
		while (cols < 20 and running):
			rect = Boxes[rows][cols]
			if (xpos > rect.x and xpos < rect.x + 50 and ypos > rect.y and ypos < rect.y +50):
				if PlaceCoin:
					Master[rows][cols] = 7
					running = False
				elif (Master[rows][cols] == 0) and key == 1:
					Master[rows][cols] = 1
					running = False
				elif (Master[rows][cols] == 1) and key == 2:
					Master[rows][cols] = 2
					running = False
				elif (Master[rows][cols] == 2) and key ==0:
					Master[rows][cols] = 0
					running = False
				elif(Master[rows][cols] == 7):
					Master[rows][cols] = 0
					running = False
			cols+=1
		rows+=1
def world(data):
	tile_list = []
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
				tile = (img, imgRect)
				tile_list.append(tile)
			if tile == 2:
				img = pygame.transform.scale(grassImg, (tile_size, tile_size))
				imgRect = img.get_rect()
				imgRect.x = col_count * tile_size
				imgRect.y = rowCount * tile_size
				tile = (img, imgRect)
				tile_list.append(tile)
			if tile == 7:
				subsurf = (0,0,16,16)
				subsurfCoin= coinImg.subsurface(subsurf)
				img = pygame.transform.scale(subsurfCoin,(36, 36))
				imgRect = pygame.Rect(0,0,32,36)
				imgRect.x = (col_count * tile_size) +9
				imgRect.y = rowCount * tile_size + 14
				tile = (img, imgRect,7)
				tile_list.append(tile)
			col_count +=1
		rowCount +=1
		for tile in tile_list:
			screen.blit(tile[0],tile[1])
def reset():
	emptyList = []
	rows = 0
	while(rows < 20):
		cols=0
		colList = []
		while (cols<20):
			colList.append(0)
			cols+=1
		emptyList.append(colList)
		rows+=1
	return(emptyList)
def main():
	worldListBoxInit = []
	worldListInit = []
	rows = 0
	clock = pygame.time.Clock()
	while(rows < 20):
		cols=0
		colList = []
		colListBoxes= []
		while (cols<20):
			rect = pygame.Rect(cols * tile_size, rows * tile_size, tile_size,tile_size)
			colList.append(0)
			cols+=1
			colListBoxes.append(rect)
		worldListBoxInit.append(colListBoxes)
		worldListInit.append(colList)
		rows+=1
	mouseDown = False
	key = None
	run = True
	if not os.stat("editorOutput.txt").st_size == 0:
		f = open("editorOutput.txt")
		worldListInit1 = f.read().split(',')	
		worldListInit1 = map(lambda s: s.strip(), worldListInit1)
		worldListInit1= list(worldListInit1)
		
		workingList =[]
		for elem in worldListInit1:
			elem = elem.replace('[','')
			elem = elem.replace(']','')
			workingList.append(elem)
		i = 0
		for elem in workingList:
			if len(elem) == 3:
				stuff = list(elem)
				workingList.remove(elem)
				workingList.insert(i,stuff[0])
				workingList.insert(i+1, stuff[2])
			i+=1
		
		#print(workingList)	

		index= 0
		rows = 0
		newList = []
		while(rows < 20):
			cols=0
			colList = []
			while (cols<20):
				colList.append(int(workingList[index]))
				cols+=1
				index+=1
			newList.append(colList)
			rows+=1
		worldListInit = newList
		f.close()

	
	
	Drect = dumpText.get_rect()
	Drect.x = 1010
	Drect.y = 150

	saveRect = savebtn.get_rect()
	saveRect.x = 1060
	saveRect.y = 100

	coinRect= coinText.get_rect()
	coinRect.x = 1045
	coinRect.y = 200
	placeCoin = False

	clearRect= clearText.get_rect()
	clearRect.x = 1060
	clearRect.y = 300
	while run:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN or mouseDown:
				
				pos = pygame.mouse.get_pos()
				x = pos[0]
				y = pos[1]
				if clearRect.collidepoint(x,y):
					worldListInit = reset()
				if not mouseDown:
					if coinRect.collidepoint(x,y):
						if placeCoin:
							placeCoin = False
						else:
							placeCoin = True
					key = clickHandlerInit(pos, worldListBoxInit, worldListInit, mouseDown, placeCoin)
					mouseDown=True
				clickHandler(pos, worldListBoxInit, worldListInit, key, placeCoin)
				
				if Drect.collidepoint(x,y):
					print(worldListInit) 
				if saveRect.collidepoint(x,y):
					file = open('editorOutput.txt', 'w')
					for line in worldListInit:
						file.write("{}\n".format(line))
			if event.type == pygame.MOUSEBUTTONUP:
				mouseDown = False
			if event.type == pygame.QUIT:
				run = False
			


			screen.blit(skyImg, (0,0))
			screen.blit(sunImg, (250,50))
			#drawGrid()
			world(worldListInit)
			screen.blit(savebtn, (1060,100))
			if placeCoin:
				screen.blit(coinText, (1025,200))
			else:
				screen.blit(coinTextOff, (1025,200))
			screen.blit(clearText, (1060, 300))		
			screen.blit(dumpText, (1010,150))
			screen.blit(text, (1015, 50))
			pygame.display.update()

	
	pygame.quit()
if __name__ == "__main__":
	main()