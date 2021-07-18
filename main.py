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
from menu import *

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

menuInitialize(win)
menuSetFont(myfont)

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
focusedHandle = None

l = Linear()
handles += l.handles

def step():
	for h in handles:
		if squareCollision(h.pos - Vector(5,5)/globalvars.scaleFactor, parami(pygame.mouse.get_pos()), 5/globalvars.scaleFactor , 1/globalvars.scaleFactor):
			h.selected = True
		else:
			h.selected = False
	if currentMenu: currentMenu.step()
	
def draw():
	for h in handles:
		h.draw()
	for func in Func._reg:
		func.draw()
	if currentMenu: currentMenu.draw()

def eventHandler(events):
	global mouseMode, movedObj, currentMenu, focusedHandle
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
			menuDone = True
			if currentMenu:
				menuDone = currentMenu.pressButton()
				if menuDone:
					if currentMenu.name == "menuEditHandle":
						if currentMenu.valueDict["x: "]:
							focusedHandle.pos.x = float(currentMenu.valueDict["x: "])
						if currentMenu.valueDict["y: "]:
							focusedHandle.pos.y = float(currentMenu.valueDict["y: "])
						focusedHandle = None
					currentMenu = None
				
			
		# mouse right click
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
			clickEvent = MENU_CALL
			# edit handles:
			for h in handles:
				if h.active and squareCollision(h.pos - Vector(5,5)/globalvars.scaleFactor, parami(pygame.mouse.get_pos()), 5/globalvars.scaleFactor , 1/globalvars.scaleFactor):
					# mouseMode = DIALOG
					clickEvent = EDIT_HANDLE
					focusedHandle = h
			# menus:
			if clickEvent == MENU_CALL:
				m = Menu("menuAdd", pygame.mouse.get_pos())
				m.addWidget(Button, ["Add Line", (255,255,255), True, addLine])
				currentMenu = m
			if clickEvent == EDIT_HANDLE:
				m = Menu("menuEditHandle", pygame.mouse.get_pos())
				m.addWidget(Input, ["x: ", 200, (255,255,255)])
				m.addWidget(Input, ["y: ", 200, (255,255,255)])
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
			# print(event.key)
			if currentMenu: InputListen(currentMenu, event)
				
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
