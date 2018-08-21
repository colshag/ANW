# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# weaparc.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a weapon arc
# ---------------------------------------------------------------------------
from anw.func import funcs

class WeaponArc(object):
    """A Weapon Arc displays the ships weapon arcs"""
    def __init__(self, category, weapon):
        self.myWeapon = weapon
        if weapon.myWeaponData.AMS == 1:
            # distance is the sims size
            self.distance = 200
        else:
            self.distance = 400
        (self.posX, self.posY) = weapon.getMyXY()
    
    def update(self, interval, world):
        """maintain arc"""
        # maintain correct position and facing
        (wX, wY) = self.myWeapon.getMyXY()
        self.facing = self.myWeapon.getMyFacing()
        (tX, tY) = funcs.getXYfromAngle(wX, wY, self.distance, self.facing)
        centerX = (wX+tX)/2
        centerY = (wY+tY)/2
        world.move(self, centerX, centerY, self.facing)
        self.graphicsObject.setState(centerX, centerY, self.facing)
        return self.alive
        
