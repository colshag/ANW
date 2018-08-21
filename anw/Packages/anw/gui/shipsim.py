# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipsim.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The shipsim represents one Ship Sim object in shipsimulator mode
# ---------------------------------------------------------------------------
from anw.func import globals
from anw.gui import textonscreen, warsim, line
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import Filename
from pandac.PandaModules import Vec3, Point3
import direct.directbase.DirectStart
import logging
import math
import os
import random
import string

        
class ShipSim(warsim.WarSim):
    """The shipsim represents one Ship Sim object in shipsimulator mode"""
    def __init__(self, path, mode, myShip):
        texture=string.lower(myShip.myShipHull.abr)
        warsim.WarSim.__init__(self, path, mode, myShip, texture)
        self.textAssault = None
        self.deathCount = 250
    
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.setColor()
        self.setPos()
        self.writeName()
        self.writeMode()
        
    def updateTargetLine(self):
        if self.myShip.currentTarget == None:
            self.removeTargetLine()
        else:
            if self.myTargetLine == None:
                self.myTargetLine = line.Line(self.path, (self.x, self.z), 
                                             (self.myShip.currentTarget.shipsim.x, self.myShip.currentTarget.shipsim.z),
                                              texture='square_grey', width=0.05, glow=0)
                self.myTargetLine.setColor(globals.colors[self.color1])
            else:
                self.myTargetLine.updateMyPosition(self.x, self.z, self.myShip.currentTarget.shipsim.x, self.myShip.currentTarget.shipsim.z)
        
    def destroy(self):
        """Remove the ship sim from game"""
        self.destroyParticles()
        self.myShip.myGalaxy.removeMiniMapTarget(self.myShip)
        if self.myShip.myGalaxy.shipSelected == self.myShip:
            self.myShip.myGalaxy.clearMouseSelection()
        if self.sim in self.myShip.myGalaxy.sims:
            self.myShip.myGalaxy.sims.remove(self.sim)
        self.myShip = None
        self.removeMyGui()
        self.sim.removeNode()
    
    def removeAssaultText(self):
        self.clearText(self.textAssault)
        self.textAssault = None
        
    def removeMyGui(self):
        """Remove all gui associated with ship"""
        self.removeMyWidgets()
        self.removeTargetLine()
        self.clearText(self.textName)
        self.clearText(self.textMode)
        self.clearText(self.textAssault)
        self.textName = None
        self.textMode = None
        self.textAssault = None
        
    def removeTargetLine(self):
        if self.myTargetLine != None:
            self.myTargetLine.destroy()
            self.myTargetLine = None
    
    def writeName(self):
        """Write the name"""
        self.textName = textonscreen.TextOnScreen(self.path, self.myShip.name, 0.20)
        self.textName.writeTextToScreen(self.x-0.9, self.y, self.z+0.8, wordwrap=14)
        self.textName.setColor(globals.colors[self.color1])
        self.myWidgets.append(self.textName)
    
    def writeMode(self):
        """Write the mode"""
        self.textMode = textonscreen.TextOnScreen(self.path, self.myShip.mode, 0.20)
        self.textMode.writeTextToScreen(self.x-0.9, self.y, self.z-0.8, wordwrap=14)
        self.textMode.setColor(globals.colors[self.color1])
        self.myWidgets.append(self.textMode)
    
    def writeAssault(self, message, color):
        """Write the assault status of assault battle"""
        if self.textAssault == None:
            self.textAssault = textonscreen.TextOnScreen(self.path, message, 0.20)
            self.textAssault.writeTextToScreen(self.x-0.9, self.y, self.z-1.0, wordwrap=100)
            self.myWidgets.append(self.textAssault)
        else:
            self.textAssault.myText.setText(message)
        self.textAssault.setColor(globals.colors[color])
        
    def setMyPosition(self, x, y, facing):
        """Update the Sim position"""
        self.x = x
        self.z = y
        newPos = self.sim.getPos()
        newPos.setX(x)
        newPos.setZ(y)
        self.sim.setPos(newPos)
        self.sim.setR(facing)
        self.textName.setMyPosition(x-0.9, self.y, y+0.8)
        self.textMode.setMyPosition(x-0.9, self.y, y-0.8)
        self.updateMySelector()
        if self.myShip.myGalaxy.debug == 1:
            self.updateTargetLine()
    
        self.updateParticleEffects(facing)
    
    
    def updateShipMode(self):
        """Update the mode description of ship"""
        self.textMode.myText.setText('%s' % self.myShip.mode)
    