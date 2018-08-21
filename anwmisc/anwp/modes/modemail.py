# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modemail.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the galactic mail mode
# ---------------------------------------------------------------------------
import pygame

import pyui
import anwp.sl.world
import anwp.sl.engine
import mode
import anwp.gui.footer
import anwp.gui.mainmenu
import anwp.gui.mailinfo
import anwp.gui.sendmailinfo

class ModeMail(mode.Mode):
    """This represents the Mail System Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'MAIL'
        
        # create gui panels
        self.mainMenu = anwp.gui.mainmenu.MainMenu(self, self.game.app)
        self.mainMenu.panel.btnMail.disable()
        self.mailInfo = None
        self.mailBodyFrame = None
        
        # create the world
        self.worldWidth = 700
        self.worldHeight = 700
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight, 25))
        self.renderer.setBackMethod(self.draw)
        
        self.getMailUpdate()
        self.setCheckMail()
    
    def createMailBodyFrame(self, mailID):
        """Build a Mail Body Frame by passing the mailID"""
        self.mailBodyFrame = anwp.gui.mailinfo.MailBodyFrame(self, self.game.app, mailID)
        self.tempFrames.append(self.mailBodyFrame)
    
    def draw(self):
        """Draw standard World information each frame"""
        anwp.sl.engine.clear()
        
        # render engine
        anwp.sl.engine.render()
    
    def setCheckMail(self):
        """Setup the Check Mail GUI"""
        self.mailInfo = anwp.gui.mailinfo.MailInfoFrame(self, self.game.app)

