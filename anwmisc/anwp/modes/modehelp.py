# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modehelp.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the help mode
# ---------------------------------------------------------------------------
import pygame
import types
import string

import pyui
import anwp.sl.world
import anwp.sl.engine
import mode
import anwp.gui.footer
import anwp.gui.helpmenu
import anwp.func.globals

class ModeHelp(mode.Mode):
    """This represents the Help Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'HELP'
        
        # create gui panels
        self.helpMenu = anwp.gui.helpmenu.HelpMenu(self, self.game.app)
        self.mainFooter = anwp.gui.footer.Footer(self, self.game.app)
        self.helpList = [] # contains a list of help lists of strings(text), or a string (image)
        self.helpCount = 0 # displays the current help list being viewed
        
        # create the world
        self.worldWidth = 1024
        self.worldHeight = 1024
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight, 25))
        self.renderer.setBackMethod(self.draw)
        self.viewY += self.helpMenu.height
        self.scrollSpeed = 10 # speed of keyboard scrolling
    
    def draw(self):
        """Draw standard World information each frame"""
        self.bufferX = (self.appWidth/2) - self.viewX
        self.bufferY = (self.appHeight/2) - self.viewY
        anwp.sl.engine.clear()
        
        # draw the appropriate help comment
        if len(self.helpList) > 0:
            self.drawHelp(self.helpList[self.helpCount])
        
        # render engine
        anwp.sl.engine.render()

    def drawHelp(self, image):
        """Display Help, help is a list of images to display"""
        # display image
        x = self.bufferX
        y = self.bufferY
        anwp.sl.engine.drawImage(x,y, 1024, 1024, '%s%s' % (self.game.app.genImagePath, image))

    def onMouseDown(self, event):
        """Iterate through the helpList"""
        if self.helpCount < len(self.helpList)-1:
            self.helpCount += 1

    def onKey(self):
        """process keys within world"""
        key = pygame.key.get_pressed()
        vx = 0
        vy = 0
        if key[pygame.K_LEFT]:
            vx -= self.scrollSpeed
        if key[pygame.K_RIGHT]:
            vx += self.scrollSpeed
        if key[pygame.K_UP]:
            vy += self.scrollSpeed
        if key[pygame.K_DOWN]:
            vy -= self.scrollSpeed
        
        # constrain camera view to stay within world borders
        if ((self.viewX + vx) <= (self.worldWidth)):
            self.viewX += vx
        if ((self.viewY + vy) <= (self.worldHeight)):
            self.viewY += vy
        anwp.sl.engine.setView(self.viewX, self.viewY)

    def setHelp(self, helpType):
        """Setup the mode for help display"""
        self.helpList = []
        self.helpCount = 0
        
        # build image list
        for i in range(1,21):
            filename = 'help_%s%d.png' % (string.lower(helpType[:-1]), i)
            if filename in self.game.imageGenFileList:
                self.helpList.append(filename)
            