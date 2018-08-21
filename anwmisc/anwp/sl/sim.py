# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# sim.py
# Generic Simulation objects for 2D space
# ---------------------------------------------------------------------------
import math
import copy

from utils import toRadians
from aabb import AABB
import engine
import collision


class SimObject:
    """ A Simulation object in a two-dimensional space. 
    """
    def __init__(self, category, drawCallback = None):
        self.category = category
        self.mobile = category.mobile       # is object mobile        
        self.life = category.life           # lifetime (seconds)
        self.collide = category.collide     # collision flag
        self.threshold = category.threshold # variable update frequency

        # create my graphics object
        self.graphicsObject = engine.GraphicsObject(
            category.source, self.mobile, category.image, drawCallback)

        # find out the size of my graphics object
        result = self.graphicsObject.getSimData()
        (self.centerX, self.centerY, self.width, self.height) = result
        
        self.posX = 0         # current X position
        self.posY = 0         # current Y position
        self.velocityX = 0    # current X velocity
        self.velocityY = 0    # current Y velocity
        self.facing = 0       # current facing (degrees)
        self.turnRate = 0     # degrees / second
        self.accel = 0        # speed / second
        self.alive = 1        # flag for staying alive
        self.uDelay = 0       # update delay
        self.uTimer = 0       # update timer        
        self.aabb = AABB()
        self.aabb.computeFor(self)
        self.removeCallback = None # callback when removed from the world 
        self.handle = 0

    def __del__(self):
        self.graphicsObject.destroy()
        
    def setState(self, posX, posY, facing, speed = 0):
        """Set the simulation state of the object.
        """
        self.posX = posX
        self.posY = posY
        self.facing = facing
        self.calculateVelocity(speed, facing)
        self.graphicsObject.setState(posX, posY, facing)

    def calculateVelocity(self, speed, facing):
        radians = toRadians(self.facing)
        self.velocityX = math.cos(radians) * speed
        self.velocityY = math.sin(radians) * speed # negative for anti-clockwise
        
    def update(self, interval, world):
        """update an object's physical state for an interval.
        """
        if self.threshold and self.uDelay:
            self.uTimer += interval
            if self.uTimer < self.uDelay:
                return
            else:
                interval = self.uTimer
                self.uTimer -= self.uDelay

        radians = toRadians(self.facing)
        if self.accel:
            dx = math.cos(radians) * self.accel * interval
            dy = math.sin(radians) * self.accel * interval
            ##print "dx:", dx
            self.velocityX += dx
            self.velocityY += dy

        newPosX = self.posX + (self.velocityX * interval)
        newPosY = self.posY + (self.velocityY * interval)

        if self.turnRate:
            newFacing = self.facing + self.turnRate*interval
            newFacing = newFacing % 360
        else:
            newFacing = self.facing

        if world.canMove(self, newPosX, newPosY, newFacing):
            self.posX = newPosX
            self.posY = newPosY
            self.facing = newFacing
            world.move(self, newPosX, newPosY, newFacing)
            self.graphicsObject.setState(newPosX, newPosY, newFacing)

        if self.life:
            self.life -= interval
            if self.life <= 0:
                self.alive = 0

        # calculate the variable delay
        if self.threshold:
            value = max( abs(self.velocityX), abs(self.velocityY), abs(self.turnRate) )
            if value < self.threshold:
                self.uDelay = 1.0 - (value / self.threshold)
            else:
                self.uDelay = 0

        return self.alive

    def hit(self, other, newPosX, newPosY, newFacing):
        """Called when I hit another object.
        """
        self.velocityX = -(self.velocityX*0.9)
        self.velocityY = -(self.velocityY*0.9)
        self.accel = 0
        self.turnRate = -(self.turnRate*0.9)
        return 1

    def setImage(self, image):
        """Change the image of this object"""
        engine.removeObject(self.graphicsObject)
        self.graphicsObject.image = image
        engine.addObject(self.graphicsObject, self.posX, self.posY, self.facing)

    def setRemoveCallback(self, callback):
        self.removeCallback = callback

    def findOffset(self, direction, distance):
        """find a position in a direction a distance from the center of the sim.
        """
        radians = toRadians(direction)        
        dx = math.cos(radians) * distance
        dy = math.sin(radians) * distance
        return (self.posX + dx, self.posY + dy)

    def findHitDirections(self, other, newPosX, newPosY, newFacing):
        """Determine what direction(s) an object should bounce.
        This should only be called from within the "hit" method of
        this class.
        """
        hitX = 0
        hitY = 0
        
        # test for world extents first
        if not isinstance(other, SimObject):
            if other == collision.WEST or other == collision.EAST:
                hitX = 1
            if other == collision.NORTH or other == collision.SOUTH:
                hitY = 1
            return (hitX, hitY)
        
        aabb = copy.copy(self.aabb)

        # test if collide if just X is changed
        aabb.transform(newPosX, self.posY, newFacing)
        hitX = aabb.checkCollide(other.aabb)

        # test if collide if just Y is changed
        aabb.transform(self.posX, newPosY, newFacing)
        hitY = aabb.checkCollide(other.aabb)

        # set both if neither hits alone
        if not hitY and not hitX:
            hitY = 1
            hitX = 1
        return (hitX, hitY)

    def __del__(self):
        pass
        #print "Deleting :", self
        
class Animated(SimObject):
    def __init__(self, category, frameSpeed, drawCallback = None):
        SimObject.__init__(self,category, drawCallback)
        self.frameSpeed = frameSpeed
        self.frameCounter = 0

    def update(self, interval, world):
        # update animation
        self.frameCounter += interval
        if self.frameCounter >= self.frameSpeed:
            self.frameCounter = 0
            self.graphicsObject.nextFrame()
            
        return SimObject.update(self, interval, world)
