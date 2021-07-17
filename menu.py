from vector import *
import pygame
BLACK = (0,0,0)

class MenuManager:
	def __init__(self):
		self.font = None
		self.window = None

menuManager = MenuManager()

def menuSetFont(font):
	menuManager.font = font

def menuInitialize(window):
	menuManager.window = window

class Dialog:
	widthSpace = 20
	heightSpace = 10
	buttonSpace = 5
	def __init__(self, text, buttons, values):
		textSurf = menuManager.font.render(text, True, (255,255,255))
		self.valueSurf = [menuManager.font.render(i, True, (255,255,255)) for i in values]
		self.buttonSurfs = [menuManager.font.render(i[0], True, (255,255,255)) for i in buttons]
		
		self.valuesHeight = self.heightSpace * 2 + textSurf.get_height()
		self.buttonHeight = self.heightSpace * 3 + textSurf.get_height() + self.valuesHeight
		
		self.buttonWidth = self.widthSpace + sum(i.get_width() for i in self.buttonSurfs)
		self.dims = Vector(max(textSurf.get_width() + 2 * self.widthSpace, self.buttonWidth), self.buttonHeight + self.buttonSurfs[0].get_height() + self.heightSpace)
		self.surf = pygame.Surface(self.dims)
		self.surf.fill(BLACK)
		self.surf.blit(textSurf, (self.widthSpace, self.heightSpace))
		self.winPos = Vector(menuManager.window.get_width()//2, menuManager.window.get_height()//2) - tup2vec(self.surf.get_size())//2
		
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
		menuManager.window.blit(self.surf, self.winPos)
		
		for i, rect in enumerate(self.rects):
			color = (100,100,100)
			if self.selected[i]:
				color = (255,0,0)
			pygame.draw.rect(menuManager.window, color, rect)
		xPos = self.dims[0]/2 - self.buttonWidth/2
		for surf in self.buttonSurfs:
			menuManager.window.blit(surf, self.winPos + Vector(xPos, self.buttonHeight))
			xPos += surf.get_width() + self.widthSpace
	
	def pressButton(self):
		for i, v in enumerate(self.selected):
			if self.selected[i]:
				self.actions[i]()

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
		pygame.draw.rect(menuManager.window, Menu.backColor, (self.winPos + self.scroll, self.dims))
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
		self.surf = menuManager.font.render(string, False, BLACK)
		self.width = self.surf.get_width()
		self.height = self.surf.get_height()
	def draw(self):
		menuManager.window.blit(self.surf, self.winPos)
	
class Button:
	def __init__(self, text, bColor, winPos, offset, active, action, scroll):
		self.text = text
		self.selected = False
		self.surf = menuManager.font.render(text, True, Menu.textColor if active else Menu.TextColorInnactive)
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
		pygame.draw.rect(menuManager.window, (255,0,0) if self.selected else self.bColor, (self.winPos + self.scroll + self.offset, (self.width, self.height)))
		menuManager.window.blit(self.surf, self.winPos + self.scroll + self.offset + Vector(Menu.border,Menu.border))
		