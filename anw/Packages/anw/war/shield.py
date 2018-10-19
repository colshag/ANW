# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shield.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a shield
# ---------------------------------------------------------------------------
from anw.func import funcs, globals

class Shield(object):
    """A Shield enters the world briefy, it dynamically modifies its width"""
    def __init__(self, category, quad):
        self.myQuad = quad
        self.myShip = self.myQuad.myParent
        self.height = self.myShip.graphicsObject.sourceObject.h
        self.setMyPosition()
        self.setMyFacing()
        self.setMySize()
    
    def setMyPosition(self):
        """Set shield position"""
        (self.posX, self.posY) = self.myShip.findOffset(self.myShip.facing + globals.quadAngles[self.myQuad.position], self.myShip.graphicsObject.sourceObject.w)
    
    def setMyFacing(self):
        """Set shield facing"""
        self.facing = self.myShip.facing + globals.quadAngles[self.myQuad.position]
    
    def setMySize(self):
        """Set shield size"""
        ratio = self.life / self.category.life
        self.width = self.myShip.graphicsObject.sourceObject.w * ratio
        self.graphicsObject.setSize(self.height, self.width)
    
    def update(self, interval, world):
        """modify width during lifecycle"""

        # maintain correct position and facing
        self.setMyPosition()
        self.setMyFacing()
        self.setMySize()
        
        world.move(self, self.posX, self.posY, self.facing)
        self.graphicsObject.setState(self.posX, self.posY, self.facing)
        
        if self.life:
            self.life -= interval
            if self.life <= 0:
                self.alive = 0

        return self.alive
    