# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modemarket.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the galactic market mode
# ---------------------------------------------------------------------------
import pygame

import pyui
import anwp.sl.world
import anwp.sl.engine
import mode
import anwp.gui.footer
import anwp.gui.mainmenu
import anwp.gui.marketinfo

class ModeMarket(mode.Mode):
    """This represents the Galacic Market Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'MARKET'
        
        # create gui panels
        self.mainMenu = anwp.gui.mainmenu.MainMenu(self, self.game.app)
        self.mainMenu.panel.btnMarket.disable()
        self.mainFooter = anwp.gui.footer.Footer(self, self.game.app)
        self.marketInfo = anwp.gui.marketinfo.MarketInfoFrame(self, self.game.app)
        
        # create the world
        self.worldWidth = 700
        self.worldHeight = 700
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight, 25))
        self.renderer.setBackMethod(self.draw)
    
    def draw(self):
        """Draw standard World information each frame"""
        anwp.sl.engine.clear()
        
        # render engine
        anwp.sl.engine.render()
