# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# rootsim.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a parent object for all gui objects that make a sim as their main function
# ---------------------------------------------------------------------------
from anw.func import funcs, globals
from anw.gui import textonscreen
from direct.particles.ParticleEffect import ParticleEffect
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Filename
from pandac.PandaModules import Vec4, Point3, NodePath

class RootSim(DirectObject):
    """This is a parent object for all gui objects that make a sim as their main function"""
    def __init__(self, path, texture='', type='plane', transparent=1, scale=1):
        self.path = path
        self.scale = scale
        self.transparent = transparent
        self.type = type
        self.textAL = None
        self.textEC = None
        self.textIA = None
        self.resourceSize = 0.15
        self.resourceCount = 0
        self.x1 = 0
        self.x2 = 0
        self.z1 = 0
        self.z2 = 0
        self.x = 0
        self.y = 20
        self.z = 0
        self.angle = 0
        self.width = 1
        self.height = 1
        self.glow = 1
        self.sim = None
        self.mode = None
        self.game = None
        self.myWidgets = []
        self.texture = '%s/%s.png' % (self.path, texture)
 
    def setMyGame(self, game):
        """Set the game object"""
        self.game = game

    def setMyMode(self, mode):
        """Set the mode object"""
        self.mode = mode
 
    def clearText(self, textSim):
        """If sim exists remove from panda"""
        if textSim != None:
            textSim.destroy()
            textSim = None
 
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        
    def registerMySim(self):
        """Setup the sim object with panda3d"""
        self.sim = loader.loadModelCopy('%s/%s' % (self.path, self.type))
        self.sim.setScale(self.scale)
        self.sim.reparentTo(render)
        self.sim.setTransparency(self.transparent)
    
    def loadMyTexture(self):
        """Load the texture to the sim"""
        tex = loader.loadTexture(self.texture)
        self.sim.setTexture(tex, 1)
 
    def setColor(self):
        """Set the color of the sim"""
        self.sim.setColor(globals.colors['mod' + self.empireID])
 
    def setGlow(self):
        """Does the object glow"""
        self.sim.setShaderInput('glow',Vec4(self.glow,0,0,0),self.glow)
    
    def setPos(self):
        """Set the position"""
        self.sim.setPos(Point3(self.x, self.y, self.z))
      
    def destroy(self):
        """Remove the Line from game"""
        self.sim.removeNode()
        self.removeMyWidgets()
    
    def removeMyWidgets(self):
        """Remove all sub widgets"""
        for myWidget in self.myWidgets:
            try:
                myWidget.removeNode()
            except:
                myWidget.destroy()
        self.ignoreAll()
    
    def removeWidget(self, widget):
        """Remove widget"""
        if widget != None:
            if widget in self.myWidgets:
                self.myWidgets.remove(widget)
            widget.destroy()
    
    def rotate(self):
        self.sim.setHpr(0, 0, self.angle)
    
    def getAngle(self):
        angle = funcs.getRelativeAngle(self.x1, self.z1, self.x2, self.z2)
        return angle
    
    def reSize(self):
        self.sim.setSx(self.width)
        self.sim.setSz(self.height)
    
    def writeCR(self, x, y, z, value):
        resource = 'CR'
        text = '%s = %d' % (resource, value)
        color = globals.resourceColors[resource]
        self.textCR = textonscreen.TextOnScreen(self.path, text, self.resourceSize, font=5)
        self.textCR.writeTextToScreen(x, y, z, wordwrap=20)
        self.textCR.setColor(globals.colors[color])
        self.myWidgets.append(self.textCR)
    
    def writeAL(self, x, y, z, value):
        resource = 'AL'
        text = '%s = %d' % (resource, value)
        color = globals.resourceColors[resource]
        self.textAL = textonscreen.TextOnScreen(self.path, text, self.resourceSize, font=5)
        self.textAL.writeTextToScreen(x, y, z, wordwrap=20)
        self.textAL.setColor(globals.colors[color])
        self.myWidgets.append(self.textAL)
    
    def writeEC(self, x, y, z, value):
        resource = 'EC'
        text = '%s = %d' % (resource, value)
        color = globals.resourceColors[resource]
        self.textEC = textonscreen.TextOnScreen(self.path, text, self.resourceSize, font=5)
        self.textEC.writeTextToScreen(x, y, z, wordwrap=20)
        self.textEC.setColor(globals.colors[color])
        self.myWidgets.append(self.textEC)
    
    def writeIA(self, x, y, z, value):
        resource = 'IA'
        text = '%s = %d' % (resource, value)
        color = globals.resourceColors[resource]
        self.textIA = textonscreen.TextOnScreen(self.path, text, self.resourceSize, font=5)
        self.textIA.writeTextToScreen(x, y, z, wordwrap=20)
        self.textIA.setColor(globals.colors[color])
        self.myWidgets.append(self.textIA)
    

        