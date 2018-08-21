# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modeconfig.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the user config mode
# ---------------------------------------------------------------------------
import pygame

import pyui
import anwp.sl.world
import anwp.sl.engine
import mode
import anwp.gui.footer
import anwp.gui.mainmenu
import anwp.gui.configinfo

class ModeConfig(mode.Mode):
    """This represents the User Config Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'CONFIG'
        
        # create gui panels
        self.mainMenu = anwp.gui.mainmenu.MainMenu(self, self.game.app)
        self.mainMenu.panel.btnConfig.disable()
        self.mainFooter = anwp.gui.footer.Footer(self, self.game.app)
        self.configInfo = anwp.gui.configinfo.ConfigInfoFrame(self, self.game.app)
        
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
    
    def surrenderNo(self):
        """Do no surrender"""
        self.yesnoBox.destroy()
    
    def surrenderYes(self):
        """Surrender"""
        try:
            d = {}
            d['ai'] = 1
            serverResult = self.game.server.setEmpire(self.game.authKey, d)
            if serverResult == 1:
                self.modeMsgBox('You have Surrendered, thank you for playing, good luck next time.')
                self.yesnoBox.destroy()
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('onSurrender->Connection to Server Lost, Login Again')
