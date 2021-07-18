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

def InputListen(menu, event):
	if menu.focusedWidget:
		menu.focusedWidget.string += event.unicode
		if event.key == pygame.K_RETURN:
			menu.focusedWidget = None

class Menu:
	# menus = []
	border = 1
	textColor = BLACK
	TextColorInnactive = (170,170,170)
	backColor = BLACK
	width = 100
	
	BUTTON = 0
	INPUT = 1
	def __init__(self, name, winPos):
		# Menu.menus.append(self)
		self.name = name
		self.winPos = vectorCopy(winPos)
		self.elements = []
		self.currentHeight = 1
		self.dims = [0,0]
		self.scroll = Vector()
		self.focusedWidget = None
		self.valueDict = {}
		# print(self.winPos)
	def switchFocused(self, switched):
		if self.focusedWidget:
			self.valueDict[self.focusedWidget.key] = self.focusedWidget.string
		self.focusedWidget = switched
		
	def updateWinPos(self, pos):
		self.winPos[0] = pos[0]
		self.winPos[1] = pos[1]
		
	def addWidget(self, widget, params):
		w = widget(self.winPos, Vector(Menu.border, self.currentHeight), *params)
		w.menu = self
		self.elements.append(w)
		self.currentHeight += self.elements[-1].height + Menu.border
		self.dims[0] = max(self.dims[0], self.elements[-1].width + 2 * Menu.border)
		self.dims[1] = self.currentHeight
		for e in self.elements:
			e.width = self.dims[0] - 2 * Menu.border
		if w.widgetId == Menu.INPUT:
			self.valueDict[params[0]] = None
	def step(self):
		for element in self.elements:
			element.step()
	def draw(self):
		pygame.draw.rect(menuManager.window, Menu.backColor, (self.winPos + self.scroll, self.dims))
		for e in self.elements:
			e.draw()
	def destroy(self):
		pass
	def pressButton(self):
		done = True
		for element in self.elements:
			if element.selected:
				isDone = element.activate()
				if isDone == False:
					done = False
		if done:
			self.switchFocused(None)
		# print(self.valueDict)
		return done
		
class Input:
	idle = 0
	listen = 1
	def __init__(self, winPos, offset, text, width, bColor):
		self.widgetId = Menu.INPUT
		self.key = text
		self.menu = None
		self.surf = menuManager.font.render(text, True, Menu.textColor)
		self.winPos = winPos
		self.bColor = bColor
		self.width = max(Menu.width + Menu.border * 2, width)
		self.height = self.surf.get_height() + Menu.border * 2
		self.offset = offset
		self.selected = False
		self.mode = Input.idle
		self.string = ""
		self.stringSurf = None
	def activate(self):
		self.menu.switchFocused(self)
		return False
	def step(self):
		mousePos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
		
		if mousePos[0] > self.winPos[0] + self.offset[0] and mousePos[0] < self.winPos[0] + self.offset[0] + self.width and mousePos[1] > self.winPos[1] + self.offset[1] and mousePos[1] < self.winPos[1] + self.offset[1] + self.height:
			self.selected = True
		else:
			self.selected = False
		
	def draw(self):
		pygame.draw.rect(menuManager.window, self.bColor, (self.winPos + self.offset, (self.width, self.height)))
		boxOffsetX = self.surf.get_width() + 5
		pygame.draw.rect(menuManager.window, (255,0,0) if self.selected else (200,200,200) , (self.winPos + self.offset + Vector(boxOffsetX, 0), (self.width - boxOffsetX, self.height)))
		menuManager.window.blit(self.surf, self.winPos + self.offset + Vector(Menu.border,Menu.border))
		if self is self.menu.focusedWidget:
			self.stringSurf = menuManager.font.render(self.string, True, Menu.textColor)
			linep1 = self.winPos + self.offset + Vector(boxOffsetX + Menu.border + self.stringSurf.get_width(), 0)
			linep2 = self.winPos + self.offset + Vector(boxOffsetX + Menu.border + self.stringSurf.get_width(), self.stringSurf.get_height())
			pygame.draw.line(menuManager.window, Menu.textColor, linep1, linep2)
		
		if self.stringSurf:
			menuManager.window.blit(self.stringSurf, self.winPos + self.offset + Vector(boxOffsetX + Menu.border , 0))
			
class Button:
	def __init__(self, winPos, offset, text, bColor, active, action):
		self.widgetId = Menu.BUTTON
		self.key = text
		self.menu = None
		self.selected = False
		self.surf = menuManager.font.render(text, True, Menu.textColor if active else Menu.TextColorInnactive)
		self.width = Menu.width + Menu.border * 2
		self.height = self.surf.get_height() + Menu.border * 2
		self.winPos = winPos
		self.offset = offset
		self.bColor = bColor
		self.active = active
		self.action = action
		self.focused = False
	def activate(self):
		self.action()
		return True
	def step(self):
		mousePos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
		
		if mousePos[0] > self.winPos[0] + self.offset[0] and mousePos[0] < self.winPos[0] + self.offset[0] + self.width and mousePos[1] > self.winPos[1] + self.offset[1] and mousePos[1] < self.winPos[1] + self.offset[1] + self.height:
			self.selected = True
		else:
			self.selected = False
	def draw(self):
		pygame.draw.rect(menuManager.window, (255,0,0) if self.selected else self.bColor, (self.winPos + self.offset, (self.width, self.height)))
		menuManager.window.blit(self.surf, self.winPos + self.offset + Vector(Menu.border,Menu.border))
		