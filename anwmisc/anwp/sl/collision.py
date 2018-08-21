# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# collision.py
# Contains classes dealing with simple collision detection
# ---------------------------------------------------------------------------
from utils import toRadians
import math

bigNumber = 99999999

EAST = 1
NORTH = 2
WEST = 3
SOUTH = 4

from aabb import AABB

class GridSquare:
    def __init__(self, posX, posY, width, height):
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.sims = []

    def addSim(self, sim):
        self.sims.append(sim)

    def removeSim(self, sim):
        self.sims.remove(sim)
        
class CollisionGrid:
    """grid that manages collision of simulation objects.
    """
    def __init__(self, width, height, ratio):
        self.width = width
        self.height = height
        self.squareWidth = width / ratio
        self.squareHeight = height / ratio
        self.numSquaresX = width / self.squareWidth
        self.numSquaresY = height / self.squareHeight
        self.squares = {} # dictionary of grid squares by location

        # initialize grid squares
        for y in range(0,self.numSquaresY+1):
            for x in range(0,self.numSquaresX+1):
                self.squares[ (x,y) ] = GridSquare(
                        x*self.squareWidth, y*self.squareHeight,
                        self.squareWidth, self.squareHeight)

    def addSim(self, sim):
        location = ( (int)(sim.posX/self.squareWidth), (int)(sim.posY/self.squareHeight) )
        sq = self.squares.get( location )
        sim.location = location
        sim.aabb.transform(sim.posX, sim.posY, sim.facing)
        sq.addSim(sim)

    def removeSim(self, sim):
        sq = self.squares.get(sim.location)
        sq.removeSim(sim)

    def moveSim(self, sim, newX, newY, newFacing):
        """This does not update the aabb as that should have been done in checkCollide
        before this was called.
        """
        newLocation = ( (int)(newX/self.squareWidth), (int)(newY/self.squareHeight) )        
        if newLocation != sim.location:
            oldSq = self.squares.get(sim.location)
            oldSq.removeSim(sim)
            newSq = self.squares.get(newLocation)
            newSq.addSim(sim)
            sim.location = newLocation

    def checkPoint(self, x, y):
        """Check if a point collides with any sims
        """
        location = ( (int)(x/self.squareWidth), (int)(y/self.squareHeight) )
        square = self.squares.get( location )
        if square:
            for sim in square.sims:
                if sim.aabb.checkPoint(x, y):
                    return sim
            
        
    def checkCollide(self, sim, newX, newY, newFacing):
        """Check if the sim can move to the new position and facing.
        If it would collide with another sim, then return that sim.
        On success return None.
        """
        #print "checking from %s,%s to %s,%s" %(sim.posX, sim.posY, newX, newY)
        sim.aabb.transform(newX, newY, newFacing)

        result = self.checkSkip(sim, newX, newY, newFacing)
        if result:
            return result
        return self.checkCollideAABB(sim.aabb, sim, newX, newY, newFacing)

    def checkCollideAABB(self, aabb, sim, newX, newY, newFacing):
        """check the collision for a AABB in world space.
        """
        # check for edges of world
        edge = sim.aabb.checkWorld(0,self.width, 0,self.height)
        if edge:
            sim.hit(edge, newX, newY, newFacing)
            return edge
        
        gridX = (int)(newX/self.squareWidth)
        gridY = (int)(newY/self.squareHeight)
        
        # iterate through local and adjacent squares
        for y in range( gridY-1, gridY+2):
            for x in range( gridX-1, gridX+2):
                if x < 0 or y < 0 or x >= self.numSquaresX or y >= self.numSquaresY:
                    continue
                sq = self.squares.get( (x,y) )
                for other in sq.sims:
                    if other.__module__ == sim.__module__:
                        continue
                    # check for collision
                    if aabb.checkCollide(other.aabb):
                        hitResult = sim.hit(other, newX, newY, newFacing)
                        if hitResult:
                            other.hit(sim, other.posX, other.posY, other.facing)
                            sim.aabb.transform(sim.posX, sim.posY, sim.facing)
                            return other

    
    def checkSkip(self, sim, newX, newY, newFacing):
        """check if this displacement skips any space
        """
        if  abs(sim.posX - newX) - sim.width > 0 or abs(sim.posY - newY) - sim.height > 0:
            #print "skipping %s from: (%.2f, %.2f) to: (%.2f, %.2f)" %( sim, sim.posX, sim.posY, newX, newY)
            # create a bounding box to fit in the skipped area
            skipBox = AABB()
            skipBox.computeFor(sim)

            # calculate skip box values
            dx = newX - sim.posX
            dy = newY - sim.posY

            if dx > 0:
                xMultiplier = 1
            else:
                xMultiplier = -1
            if dy > 0:
                yMultiplier = 1
            else:
                yMultiplier = -1
                
            if dy == 0:
                skipWidth = sim.width * xMultiplier
                skipHeight = 0
            elif dx == 0:
                skipWidth = 0
                skipHeight = sim.height * yMultiplier
            else:
                ratio = float(abs(dx)) / float(abs(dy))
                if ratio > (float(sim.width)/sim.height):
                    skipWidth = sim.width * xMultiplier
                    skipHeight = (sim.width / ratio) * yMultiplier
                else:
                    skipWidth = (sim.height * ratio) * xMultiplier
                    skipHeight = sim.height * yMultiplier

            #print "dx %.2f dy %.2f skipWidth %.2f skipHeight %.2f " % (dx, dy, skipWidth, skipHeight)
            # move the skipBox to the first position
            skipPosX = sim.posX + skipWidth
            skipPosY = sim.posY + skipHeight

            # move the skipbox along the path
            while 1:
                skipBox.transform(skipPosX, skipPosY, newFacing)
                result = self.checkCollideAABB(skipBox, sim, skipPosX, skipPosY, newFacing)
                if result:
                    return result
                if abs(newX -skipPosX) <= sim.width and abs(newY - skipPosY) <= sim.height:
                    break
                skipPosX += skipWidth
                skipPosY += skipHeight
                    
        return 0
                            
    
