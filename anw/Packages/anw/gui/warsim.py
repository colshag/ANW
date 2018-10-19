# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# warsim.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# The warsim contains common methods for sims in the simulator, 
# ships, missiles, and drones
# ---------------------------------------------------------------------------
import direct.directbase.DirectStart #camera
from pandac.PandaModules import Point3
import direct.directbase.DirectStart
from pandac.PandaModules import Filename,Vec4,Vec3,Point3
from anw.gui import textonscreen, rootsim, explosion, smoketrail
from anw.func import globals
import math
from direct.particles.ParticleEffect import ParticleEffect
        
class WarSim(rootsim.RootSim):
    """The sim represents one Sim object in shipsimulator mode"""
    def __init__(self, path, mode, myShip, texture):
        self.id = myShip.id
        self.empireID = myShip.empireID
        self.color1 = globals.empires[int(self.empireID)]['color1']
        self.color2 = globals.empires[int(self.empireID)]['color2']
        self.texture = '%s_%s' % (texture, self.empireID)
        self.myShip = myShip
        rootsim.RootSim.__init__(self, path, self.texture)
        self.mode = mode
        self.textName = None
        self.textMode = None
        self.myTargetLine = None
        self.mySelector = None
        self.x = myShip.posX
        self.z = myShip.posY
        self.y = 20
        self.createMySim()
        self.deathCount = 50
    
            # FIXME - how to load this right?
        self.initializeParticleEffect()

    
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.setColor()
        self.setPos()
        
    def updateTargetLine(self):
        if self.myShip.currentTarget == None:
            if self.myTargetLine != None:
                self.myTargetLine.destroy()
                self.myTargetLine = None
        else:
            if self.myTargetLine == None:
                self.myTargetLine = line.Line(self.path, (self.x, self.z), 
                                             (self.myShip.currentTarget.sim.x, self.myShip.currentTarget.sim.z),
                                              texture='square_grey')
                self.myTargetLine.setColor(globals.colors[self.color1])
            else:
                self.myTargetLine.updateMyPosition(self.x, self.z, self.myShip.currentTarget.sim.x, self.myShip.currentTarget.sim.z)
        
    def destroy(self):
        """Remove the sim from game"""
        self.destroyParticles()
        self.myShip = None
        self.removeMyWidgets()
        self.sim.removeNode()
        
    def destroyParticles(self):
        self.smoketrail.cleanup()
        
    def setMyPosition(self, x, y, facing):
        """Update the Sim position"""
        self.x = x
        self.z = y
        newPos = self.sim.getPos()
        newPos.setX(x)
        newPos.setZ(y)
        self.sim.setPos(newPos)
        self.sim.setR(facing)

    def initializeParticleEffect(self):
        self.smoketrail = smoketrail.SmokeTrail(self
                                                )
    def updateParticleEffects(self, facing):
        self.smoketrail.update(facing)

        
    def displayDamage(self, amount, color, position):
        """Display damage taken by a shot"""
        textDamage = textonscreen.TextOnScreen(self.path, '%s %d' % (position, amount), 0.30)
        textDamage.writeTextToScreen(self.x, self.y+0.1, self.z, wordwrap=14)
        textDamage.setColor(globals.colors[color])
        textDamage.startFade()
    
    def updateMySelector(self):
        """Update position of selector"""
        if self.mySelector != None:
            self.mySelector.setPos(Point3(self.x, self.y, self.z))
    
    def setMySelector(self, selector):
        """Set the Selector for shipsim"""
        self.mySelector = selector
    
    def removeMySelector(self):
        """Remove Selector"""
        if self.mySelector != None:
            self.mySelector = None
    
    def explode(self):
        """Sim has exploded"""
        self.sim.removeNode()
        if globals.serverMode == 0:
            x = self.myShip.posX
            z = self.myShip.posY
            myExplosion = explosion.Explosion(self.path, self.myShip.myShipHull.size , x, z, self.empireID)
            self.myShip.myGalaxy.addExplosion(myExplosion)
   