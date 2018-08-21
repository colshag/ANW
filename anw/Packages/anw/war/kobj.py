# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# kobj.py
# Written by Kris Kundert
# ---------------------------------------------------------------------------
# This represents a parent object in ship simulator
# ---------------------------------------------------------------------------
from anw.func import root, funcs, globals

class KObj(object):
    """This is the parent object for ship simulator objects"""
    def __init__(self, name, x, y, radius, direction, speed):
        self.name = name
        self.posX = x
        self.posY = y
        self.radius = radius # aka ship hull radius
        self.externalRadius = radius # aka antimissile guns
        self.collidemask = 0

        self.direction = direction
        self.speed = speed

        self.hitSomething = 0
        
        if globals.serverMode == 0:
            self.shipsim = None
        self.world = None

        self.iteration = 0

    def setCollidemask(self):
        """Set the objects Collide Mask"""
        pass

    def hitRadius(self, myMissile):
        pass
    
    def hitExternalRadius(self, myMissile):
        pass

    def hitWeaponRetargetRadius(self, otherShip):
        pass
    
    def updatePos(self, x, y, facing):
        if globals.serverMode == 0:
            if self.shipsim == None:
                return
            self.shipsim.setMyPosition(x, y, facing)

    def setShipsim(self, model):
        if globals.serverMode == 0:
            self.sim = model.sim
            self.shipsim = model
            self.shipsim.width = self.radius
            self.shipsim.height = self.radius
            self.shipsim.reSize()
            self.updatePos(self.posX, self.posY, self.direction)

    def setWorld(self, world):
        self.world = world
