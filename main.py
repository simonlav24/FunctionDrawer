from math import fabs, sqrt, cos, sin, pi, floor, ceil, e
from random import uniform, randint, choice
import os, pygame
if os.path.exists("graph.py"):
	import graph
else:
	print("fetching graph")
	import urllib.request
	with urllib.request.urlopen('https://raw.githubusercontent.com/simonlav24/Graph-plotter/master/graph.py') as f:
		text = f.read().decode('utf-8')
		with open("graph.py", "w+") as graphpy:
			graphpy.write(text)
	import graph
from graph import *
#from pygame import gfxdraw
pygame.init()
fpsClock = pygame.time.Clock()
#pygame.font.init()
#myfont = pygame.font.SysFont('Arial', 12)

# winWidth = 800
# winHeight = 500
# win = pygame.display.set_mode((winWidth,winHeight))
# pygame.display.set_caption('Simon\'s desmos')

MENU_CALL = 0
EDIT_HANDLE = 1

def squareCollision(pos1, pos2, rad1, rad2):
	return True if pos1.x < pos2.x + rad2*2 and pos1.x + rad1*2 > pos2.x and pos1.y < pos2.y + rad2*2 and pos1.y + rad1*2 > pos2.y else False

################################################################################ Classes

class Func:
	_reg = []
	def __init__(self):
		Func._reg.append(self)
		self.p1 = Vector()
		self.p2 = Vector()
		self.b0 = -50
		self.b1 = 50
		self.active = True
		self.handles = [Handle((-10,0)), Handle((10,0))]
	def func(self, x):
		return x
	def draw(self):
		borders = [self.b0, self.b1]
		borders.sort()
		drawGraph(self.b0, self.b1, 0.5, self.func)

class Handle:
	def __init__(self, pos):
		self.pos = vectorCopy(pos)
		self.active = True
		self.selected = False
	def draw(self):
		color = (50,200,50)
		if self.selected:
			color = (200,50,50)
		pygame.draw.rect(win, color, (param(self.pos) - Vector(5,5), (10,10)))
		
class Linear(Func):
	def func(self, x):
		borders = sorted(self.handles, key=lambda x: x.pos[0])
		self.b0 = borders[0].pos.x
		self.b1 = borders[1].pos.x
		if self.handles[0].pos[0] == self.handles[1].pos[0]:
			m = 0
		else:
			m = (self.handles[1].pos[1] - self.handles[0].pos[1])/(self.handles[1].pos[0] - self.handles[0].pos[0])
		return m*(x - self.handles[0].pos[0]) + self.handles[0].pos[1]
	
	def __str__(self):
		### not right
		m = (self.p2[1] - self.p1[1])/(self.p2[0] - self.p1[0])
		n = -m*self.p1[0]+self.p1[1]
		string = "y=" + formet(m) + "\\cdot x+" + formet(n)
		
		borders = [self.b0, self.b1]
		borders.sort()
		string += "\\left\\{" + formet(borders[0]) + "<x<" + formet(borders[1]) + "\\right\\}"
		return string
		
	def draw(self):
		pygame.draw.line(win, (255,10,10), param(self.handles[0].pos), param(self.handles[1].pos))

class Parabole(Func):
	def func(self, x):
		if self.p1[0] - self.p2[0] == 0:
			return 0
		h = (self.p2[1] - self.p1[1])/((self.p1[0] - self.p2[0])**2)
		return h * (x - self.p2[0]) * (x + self.p2[0] - 2*self.p1[0]) + self.p2[1]
		
	def __str__(self):
		a = self.p1[0]; b = self.p1[1]; c = self.p2[0]; d = self.p2[1]
		h = (d-b)/(a-c)**2
		i = -2*h*a
		j = d-h*c**2-i*c
		
		borders = [self.b0, self.b1]
		borders.sort()
		
		string = "y=" + formet(h) + "\\cdot x^{2}+" + formet(i) + "\\cdot x+" + formet(j) + "\\left\\{" + formet(borders[0]) + "<x<" + formet(borders[1]) + "\\right\\}"
		
		return string

class SemiCircle(Func):
	def func(self, x):
		a = self.p1[0]; b = self.p1[1]; c = self.p2[0]; d = self.p2[1]
		if c-a == 0:
			return 0
		if 1-((x-c)/(c-a))**2 < 0:
			return 0
		return (d-b)*sqrt(1-((x-c)/(c-a))**2)+b
	def __str__(self):
		a = self.p1[0]; b = self.p1[1]; c = self.p2[0]; d = self.p2[1]
		
		string = formet((d-b)/(c-a)) + "\\sqrt{" + formet((c-a)**2) + "-\\left(x-" + formet(c) + "\\right)^{2}}+" + formet(b)
		borders = [self.b0, self.b1]
		borders.sort()
		string += "\\left\\{" + formet(borders[0]) + "<x<" + formet(borders[1]) + "\\right\\}"
		return string

def funcDiactivate():
	global handles
	for func in Func._reg:
		func.active = False
	handles = []

################################################################################ Menu

class Dialog:
	widthSpace = 20
	heightSpace = 10
	buttonSpace = 5
	def __init__(self, text, buttons, values):
		textSurf = myfont.render(text, True, (255,255,255))
		self.valueSurf = [myfont.render(i, True, (255,255,255)) for i in values]
		self.buttonSurfs = [myfont.render(i[0], True, (255,255,255)) for i in buttons]
		
		self.valuesHeight = self.heightSpace * 2 + textSurf.get_height()
		self.buttonHeight = self.heightSpace * 3 + textSurf.get_height() + self.valuesHeight
		
		self.buttonWidth = self.widthSpace + sum(i.get_width() for i in self.buttonSurfs)
		self.dims = Vector(max(textSurf.get_width() + 2 * self.widthSpace, self.buttonWidth), self.buttonHeight + self.buttonSurfs[0].get_height() + self.heightSpace)
		self.surf = pygame.Surface(self.dims)
		self.surf.fill(BLACK)
		self.surf.blit(textSurf, (self.widthSpace, self.heightSpace))
		self.winPos = Vector(globalvars.winWidth//2, globalvars.winHeight//2) - tup2vec(self.surf.get_size())//2
		
		self.rects = []
		self.selected = []
		self.actions = [i[1] for i in buttons]
		lastSurfWidth = 0
		for i, s in enumerate(self.buttonSurfs):
			if i != 0:
				lastSurfWidth += self.buttonSurfs[i-1].get_width()
			x = self.dims[0]//2 - self.buttonWidth//2 + i * self.widthSpace + lastSurfWidth - self.buttonSpace
			y = self.buttonHeight
			self.rects.append((self.winPos + Vector(x, y), (s.get_width() + self.buttonSpace * 2 , s.get_height())))
			self.selected.append(False)
		
	def step(self):
		mousePos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
		for i, rect in enumerate(self.rects):
			if mousePos[0] > rect[0][0] and mousePos[0] <= rect[0][0] + rect[1][0] and mousePos[1] > rect[0][1] and mousePos[1] <= rect[0][1] + rect[1][1]:
				self.selected[i] = True
			else:
				self.selected[i] = False
	
	def draw(self):
		win.blit(self.surf, self.winPos)
		
		for i, rect in enumerate(self.rects):
			color = (100,100,100)
			if self.selected[i]:
				color = (255,0,0)
			pygame.draw.rect(win, color, rect)
		xPos = self.dims[0]/2 - self.buttonWidth/2
		for surf in self.buttonSurfs:
			win.blit(surf, self.winPos + Vector(xPos, self.buttonHeight))
			xPos += surf.get_width() + self.widthSpace
	
	def pressButton(self):
		for i, v in enumerate(self.selected):
			if self.selected[i]:
				self.actions[i]()
		
BLACK = (0,0,0)

class Menu:
	menus = []
	border = 1
	textColor = BLACK
	TextColorInnactive = (170,170,170)
	backColor = BLACK
	width = 100
	def __init__(self, winPos):
		Menu.menus.append(self)
		self.winPos = vectorCopy(winPos)
		self.elements = []
		self.buttons = []
		self.currentHeight = 1
		self.dims = [0,0]
		self.scroll = Vector()
		# print(self.winPos)
	def updateWinPos(self, pos):
		self.winPos[0] = pos[0]
		self.winPos[1] = pos[1]
	def addButton(self, text, bColor, active, action):
		b = Button(text, bColor, self.winPos, Vector(Menu.border, self.currentHeight), active, action, self.scroll)
		self.elements.append(b)
		self.buttons.append(b)
		self.currentHeight += self.elements[-1].height + Menu.border
		self.dims[0] = max(self.dims[0], self.elements[-1].width + 2 * Menu.border)
		self.dims[1] = self.currentHeight
	def step(self):
		for element in self.elements:
			element.step()
	def draw(self):
		pygame.draw.rect(win, Menu.backColor, (self.winPos + self.scroll, self.dims))
		for e in self.elements:
			e.draw()
	def destroy(self):
		Menu.menus.remove(self)
	def pressButton(self):
		for button in self.buttons:
			if button.selected:
				button.activate()

class MenuString:
	def __init__(self, string, winPos):
		self.winPos = winPos
		self.surf = myfont.render(string, False, BLACK)
		self.width = self.surf.get_width()
		self.height = self.surf.get_height()
	def draw(self):
		win.blit(self.surf, self.winPos)
	
class Button:
	def __init__(self, text, bColor, winPos, offset, active, action, scroll):
		self.text = text
		self.selected = False
		self.surf = myfont.render(text, True, Menu.textColor if active else Menu.TextColorInnactive)
		self.width = Menu.width + Menu.border * 2
		self.height = self.surf.get_height() + Menu.border * 2
		self.winPos = winPos
		self.offset = offset
		self.scroll = scroll
		self.bColor = bColor
		self.active = active
		self.action = action
		# print(self.winPos, self.offset)
	def activate(self):
		self.action(self)
	def step(self):
		mousePos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
		
		if mousePos[0] > self.winPos[0] + self.scroll[0] + self.offset[0] and mousePos[0] < self.winPos[0] + self.scroll[0] + self.offset[0] + self.width and mousePos[1] > self.winPos[1] + self.scroll[1] + self.offset[1] and mousePos[1] < self.winPos[1] + self.scroll[1] + self.offset[1] + self.height:
			self.selected = True
		else:
			self.selected = False
	def draw(self):
		pygame.draw.rect(win, (255,0,0) if self.selected else self.bColor, (self.winPos + self.scroll + self.offset, (self.width, self.height)))
		win.blit(self.surf, self.winPos + self.scroll + self.offset + Vector(Menu.border,Menu.border))

def test_t():
	print("click")
	
def addLine(self):
	global handles
	funcDiactivate()
	l = Linear()
	l.active = True
	handles += l.handles

def cancel():
	global currentDialog, mouseMode
	currentDialog = None
	mouseMode = HAND

def changeHandleValues():
	pass

################################################################################ Setup
HAND = 0
MOVE = 1
DIALOG = 2

handles = []
movedObj = None
mouseMode = HAND
currentMenu = None
currentDialog = None

l = Linear()
handles += l.handles

# ha = Handle((10,12))
# ha.active = True
# ha2 = Handle((20,12))
# ha2.active = True

# d = Dialog("this is a doalog window that will be made soon", [("Cancel", test_t), ("Ok", test_t)])
# currentDialog = d

def step():
	for h in handles:
		if squareCollision(h.pos - Vector(5,5)/globalvars.scaleFactor, parami(pygame.mouse.get_pos()), 5/globalvars.scaleFactor , 1/globalvars.scaleFactor):
			h.selected = True
		else:
			h.selected = False
	if currentMenu: currentMenu.step()
	if currentDialog: currentDialog.step()
	
def draw():
	for h in handles:
		h.draw()
	for func in Func._reg:
		func.draw()
	if currentMenu: currentMenu.draw()
	if currentDialog: currentDialog.draw()

def eventHandler(events):
	global mouseMode, movedObj, currentMenu, currentDialog
	for event in events:
		if event.type == pygame.QUIT:
			globalvars.run = False
		# mouse left click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			globalvars.point = Vector(pygame.mouse.get_pos()[0] / globalvars.scaleFactor, pygame.mouse.get_pos()[1] / globalvars.scaleFactor) 
			globalvars.mousePressed = True
			if mouseMode == HAND:
				# search for handle to move
				for h in handles:
					if h.active and squareCollision(h.pos - Vector(5,5)/globalvars.scaleFactor, parami(pygame.mouse.get_pos()), 5/globalvars.scaleFactor , 1/globalvars.scaleFactor):
						mouseMode = MOVE
						movedObj = h
			globalvars.camPrev = Vector(globalvars.cam[0], globalvars.cam[1])
			# menus:
			if currentMenu:
				currentMenu.pressButton()
			currentMenu = None
			if currentDialog:
				currentDialog.pressButton()
				
			
		# mouse right click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
			clickEvent = MENU_CALL
			# edit handles:
			for h in handles:
				if h.active and squareCollision(h.pos - Vector(5,5)/globalvars.scaleFactor, parami(pygame.mouse.get_pos()), 5/globalvars.scaleFactor , 1/globalvars.scaleFactor):
					mouseMode = DIALOG
					d = Dialog("this is a doalog window that will be made soon", [("Cancel", cancel), ("Ok", test_t)], ["x", "y"])
					currentDialog = d
					clickEvent = EDIT_HANDLE
			# menus:
			if clickEvent == MENU_CALL:
				m = Menu(pygame.mouse.get_pos())
				m.addButton("Add Line", (255,255,255), True, addLine)
				currentMenu = m
			
		# mouse left release
		if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			globalvars.mousePressed = False
			if mouseMode == MOVE:
				mouseMode = HAND
				movedObj = None

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
			origin = param((0,0))
			mouse = pygame.mouse.get_pos()
			adjust = Vector(mouse[0] - origin[0], mouse[1] - origin[1])
			globalvars.cam = globalvars.cam + adjust * 0.2
			globalvars.scaleFactor += 0.2 * globalvars.scaleFactor
			
			globalvars.gridView = int((downRight()[0] - upLeft()[0])/10) + 1
			globalvars.gridView = max(5 * int(globalvars.gridView/5), 5)
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
			origin = param((0,0))
			mouse = pygame.mouse.get_pos()
			adjust = Vector(mouse[0] - origin[0], mouse[1] - origin[1])
			globalvars.cam = globalvars.cam - adjust * 0.2
			globalvars.scaleFactor -= 0.2 * globalvars.scaleFactor
			
			globalvars.gridView = int((downRight()[0] - upLeft()[0])/10) + 1
			globalvars.gridView = max(5 * int(globalvars.gridView/5), 5)
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_h:
				mouseMode = HAND
			if event.key == pygame.K_1:
				mouseMode = 1
				
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		globalvars.run = False
	
	# if mouse pressed:
	if globalvars.mousePressed:
		if mouseMode == HAND:
			current = Vector(pygame.mouse.get_pos()[0] / globalvars.scaleFactor, pygame.mouse.get_pos()[1] / globalvars.scaleFactor)
			globalvars.cam = globalvars.camPrev + (globalvars.point - current) * globalvars.scaleFactor
		elif mouseMode == MOVE:
			movedObj.pos = parami(pygame.mouse.get_pos())
	
mainLoop(step, draw, eventHandler)
