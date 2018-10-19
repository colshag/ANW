# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# app.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the main application that runs ANW
# ---------------------------------------------------------------------------
import os
import sys

from game import ANWGame

class Application(object):
    """set the basic app parameters, startup a client game, main Panda3d World Class"""
    def __init__(self, server='', galaxy='', empire='', password='', shipBattle=None, glow=1):
        self.path = os.path.abspath(sys.path[0])
        self.server = str(server)
        self.password = password
        self.galaxy = str(galaxy)
        self.empire = str(empire)
        self.intervalValue = 0
        self.game = None
        self.shipBattle = shipBattle
            
    def setIntervalValue(self, value):
        """Set the intervale Value to 0 for regular, or a value from 0 to 1 for set interval"""
        self.intervalValue = value

    def loadGame(self):
        """Load the game"""
        self.game = ANWGame(self, self.shipBattle)
    
    def quit(self):
        return 0
    