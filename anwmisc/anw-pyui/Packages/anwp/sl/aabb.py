# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# aabb.py
# the AABB Class is a bounding box, it is used for collision detection.
# ---------------------------------------------------------------------------
from utils import toRadians
import math

EAST = 1
NORTH = 2
WEST = 3
SOUTH = 4

bigNumber = 99999999
        
class AABB:
    """Axially Aligned Bounding Box.
    """
    def __init__(self, world=0):
        self.reset()
        if world:
            self.worldAABB = None
        else:
            self.worldAABB = AABB(1)
        
    def reset(self):
        self.minX = bigNumber
        self.minY = bigNumber
        self.maxX = -bigNumber
        self.maxY = -bigNumber

    def add(self, x, y):
        self.minX = min(self.minX, x)
        self.minY = min(self.minY, y)
        self.maxX = max(self.maxX, x)
        self.maxY = max(self.maxY, y)
        
    def computeFor(self, obj):
        """Compute the axially aligned bounding box for the simObject.
        Computes it in object space.
        """
        self.reset()
        self.add( -obj.width/2, -obj.height/2)
        self.add( obj.width/2, -obj.height/2)
        self.add( obj.width/2, obj.height/2)
        self.add( -obj.width/2, obj.height/2)

    def transform(self, x, y, facing):
        """transform the AABB into world space.
        """
        self.worldAABB.reset()
        radians = toRadians(facing)
        
        # transform upper left
        newX = x+( self.minX * math.cos(radians)+self.minY * math.sin(radians))
        newY = y+(-self.minX * math.sin(radians)+self.minY * math.cos(radians))
        self.worldAABB.add(newX, newY)

        # transform upper right
        newX = x+( self.maxX * math.cos(radians)+self.minY * math.sin(radians))
        newY = y+(-self.maxX * math.sin(radians)+self.minY * math.cos(radians))
        self.worldAABB.add(newX, newY)

        # transform lower left
        newX = x+( self.maxX * math.cos(radians)+self.maxY * math.sin(radians))
        newY = y+(-self.maxX * math.sin(radians)+self.maxY * math.cos(radians))
        self.worldAABB.add(newX, newY)

        # transform lower right
        newX = x+( self.minX * math.cos(radians)+self.maxY * math.sin(radians))
        newY = y+(-self.minX * math.sin(radians)+self.maxY * math.cos(radians))
        self.worldAABB.add(newX, newY)

    def checkCollide(self, aabb):
        """check if another aabb collides with this one.
        """
        #if not aabb.worldAABB:
        #    aabb.transform(aabb
        if self.worldAABB.minX > aabb.worldAABB.maxX:
            return 0
        if self.worldAABB.maxX < aabb.worldAABB.minX:
            return 0
        if self.worldAABB.minY > aabb.worldAABB.maxY:
            return 0
        if self.worldAABB.maxY < aabb.worldAABB.minY:
            return 0
        return 1

    def checkWorld(self, left, right, bottom, top):
        """check if the aabb collides with the edges of world.
        """
        if self.worldAABB.minX < left:
            return WEST
        elif self.worldAABB.maxX > right:
            return EAST
        elif self.worldAABB.minY < bottom:
            return SOUTH
        elif self.worldAABB.maxY > top:
            return NORTH
        return 0

    def checkPoint(self, x, y):
        """check if a point collides with me. in world space.
        """
        if x > self.worldAABB.minX and x < self.worldAABB.maxX:
            if y > self.worldAABB.minY and y < self.worldAABB.maxY:
                return 1
            
class BoundingSphere:
    """Bounding Sphere for a sim object.
    """
    def __init__(self, world=0):
        self.reset()
        if not world:
            self.worldSphere = BoundingSphere(1)

    def reset(self):
        self.posX = 0
        self.posY = 0
        self.radiusSq = 0
        self.radius = 0

    def add(self, x, y):
        r = x**2 + y**2
        self.radiusSq = max(r, self.radiusSq)

    def computeFor(self, obj):
        """Compute the bounding sphere for the object in object space.
        """
        self.reset()
        self.add( -obj.width/2, -obj.height/2)
        self.add( obj.width/2, -obj.height/2)
        self.add( obj.width/2, obj.height/2)
        self.add( -obj.width/2, obj.height/2)
        self.radius = math.sqrt(self.radiusSq)
        print self.radius, self.radiusSq        

    def transform(self, x, y, facing):
        self.worldSphere.reset()        
        self.worldSphere.posX = x
        self.worldSphere.posY = y
        self.worldSphere.radius = self.radius
        self.worldSphere.radiusSq = self.radiusSq        

    def checkCollide(self, sphere):
        dx = self.worldSphere.posX - sphere.worldSphere.posX
        dy = self.worldSphere.posY - sphere.worldSphere.posY
        distance = dx**2 + dy**2
        if distance < self.radiusSq + sphere.radiusSq:
            return 1
        else:
            return 0

    def checkWorld(self, left, right, bottom, top):
        """check if the sphere collides with the edges of world.
        """
        if self.worldSphere.posX - self.radius < left:
            return WEST
        elif self.worldSphere.posX + self.radius > right:
            return EAST
        elif self.worldSphere.posY - self.radius < bottom:
            return SOUTH
        elif self.worldSphere.posY + self.radius > top:
            return NORTH
        return 0

    def checkPoint(self, x, y):
        """check if a point collides with me. in world space.
        """
        dx = x - self.worldSphere.posX
        dy = y - self.worldSphere.posY
        distance = dx**2 + dy**2
        if distance < self.radiusSq:
            return 1
        else:
            return 0
        
