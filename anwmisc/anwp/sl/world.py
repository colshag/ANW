# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# world.py
# Library Utility Modules
# ---------------------------------------------------------------------------
import math
from utils import toRadians
from collision import CollisionGrid

import engine

class World:
    """Simulation world.
    """
    def __init__(self, width, height, ratio=20):
        self.width = width
        self.height = height
        self.debug = 0
        self.mobiles = []    # the set of mobile simObjects
        self.immobiles = []	 # the set of immobile simObjects
        self.grid = CollisionGrid(width, height, ratio)

    def addToWorld(self, sim, x, y, facing, speed=0, force=0):
        # prevent skip collision tests
        sim.posX = x
        sim.posY = y
        if force==0 and self.canMove(sim,x, y, facing) == 0:
            return 0
        if sim.graphicsObject.image <> None:
            if sim.mobile:
                self.mobiles.append(sim)
            else:
                self.immobiles.append(sim)
        sim.setState(x, y, facing, speed)
        if sim.collide:
            self.grid.addSim(sim)
        engine.addObject(sim.graphicsObject, x, y, facing)
        return 1

    def removeFromWorld(self, sim):
        if sim.mobile:
            self.mobiles.remove(sim)
        else:
            self.immobiles.remove(sim)
        if sim.collide:
            self.grid.removeSim(sim)
        engine.removeObject(sim.graphicsObject)
        if sim.removeCallback:
            sim.removeCallback(self)
        return 1

    def update(self, interval, name=''):
        """update the simulation world for an interval
        """
        deleteList = []
        for sim in self.mobiles:
            if name == '':
                if sim.update(interval, self) == 0:
                    deleteList.append(sim)
            else:
                # this section means only a sim with the category name will be updated
                if sim.category.name == name:
                    if sim.update(interval, self) == 0:
                        deleteList.append(sim)
        for sim in deleteList:
            self.removeFromWorld(sim)

        return 1

    def move(self, sim, newPosX, newPosY, newFacing):
        if sim.collide:
            self.grid.moveSim(sim, newPosX, newPosY, newFacing)
            
    def canMove(self, sim, newPosX, newPosY, newFacing):
        if sim.collide:
            if self.grid.checkCollide(sim, newPosX, newPosY, newFacing):
                return 0
        return 1

    def removeAll(self):
        while len(self.mobiles):
            m = self.mobiles[0]
            self.removeFromWorld(m)
        while len(self.immobiles):
            m = self.immobiles[0]
            self.removeFromWorld(m)
            
    def checkPoint(self, x, y):
        return self.grid.checkPoint(x,y)
    
    def setDebug(self, value):
        """Set Debug value"""
        self.debug = value
