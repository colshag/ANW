# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# line.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is a line that joins two points
# ---------------------------------------------------------------------------
from direct.task import Task
from anw.func import funcs
from anw.gui import rootsim, textonscreen

class Line(rootsim.RootSim):
    """A Line between two points in x,z plane"""
    def __init__(self, path, (x1,z1), (x2,z2), texture='square', width=0.05, glow=1, hit=1):
        rootsim.RootSim.__init__(self, path, texture)
        self.hit = hit
        self.fadeCount = 100.0
        self.fadeAmount = 5.0
        self.widthAmount = 0.0
        self.x1 = x1
        self.x2 = x2
        self.z1 = z1
        self.z2 = z2
        self.x = 0
        self.y = 20.5
        self.z = 0
        self.width = width
        self.glow = glow
        self.setMyDimensions()
        self.createMySim()
    
    def setMyDimensions(self):
        """Set the Line Dimensions based on coords given"""
        self.x = (self.x1+self.x2)/2
        self.z = (self.z1+self.z2)/2
        self.angle = self.getAngle()
        self.height = funcs.getTargetRange(self.x1, self.z1, self.x2, self.z2)
 
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.reSize()
        self.setPos()
        self.rotate()
    
    def updateMyPosition(self, x1, z1, x2, z2):
        """Update the Line position"""
        self.x1 = x1
        self.z1 = z1
        if self.hit == 1:
            self.x2 = x2
            self.z2 = z2
        self.setMyDimensions()
        self.setPos()
        self.reSize()
        self.rotate()
    
    def setColor(self, color):
        self.sim.setColor(color)
    
    def startFade(self, amount, myWeapon, myTarget):
        self.myWeapon = myWeapon
        self.myTarget = myTarget
        self.widthAmount = self.width * amount/100.0
        taskMgr.add(self.fadeWidth, 'fadeWidthTask')
    
    def fadeWidth(self, task):
        """Fade out the width and destroy line"""
        if self.fadeCount <= 0:
            self.destroy()
            return Task.done
        else:
            self.fadeCount -= self.fadeAmount
            self.width -= self.widthAmount
            (x,y) = self.myWeapon.getMyXY()
            self.updateMyPosition(x, y, self.myTarget.posX, self.myTarget.posY)
            return Task.cont
        
