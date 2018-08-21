# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# direct.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a direct fire shot
# ---------------------------------------------------------------------------
import anwp.sl.sim
import anwp.func.funcs

class Direct(anwp.sl.sim.SimObject):
    """A Direct fire shot enters the world briefy, it dynamically modifies its length
    between ships"""
    def __init__(self, category, weapon, x, y, facing, target):
        anwp.sl.sim.SimObject.__init__(self, category, None)
        self.myWeapon = weapon
        self.myTarget = target
        self.posX = x
        self.posY = y
    
    def update(self, interval, world):
        """maintain direct fire angle, length, and width during lifecycle"""

        # maintain correct position and facing
        (wX, wY) = self.myWeapon.getMyXY()
        tX = self.myTarget.posX
        tY = self.myTarget.posY
        centerX = (wX+tX)/2
        centerY = (wY+tY)/2
        self.facing = anwp.func.funcs.getRelativeAngle(wX, wY, tX, tY)
        
        # set variable height of image
        height = anwp.func.funcs.getTargetRange(wX, wY, tX, tY)/2

        # set a reducing width based on life cycle
        width = self.graphicsObject.sourceObject.w * (self.life / self.category.life)
        
        self.graphicsObject.setSize(width, height)
        
        # update
        self.posX = centerX
        self.posY = centerY
        world.move(self, centerX, centerY, self.facing)
        self.graphicsObject.setState(centerX, centerY, self.facing)
        
        if self.life:
            self.life -= interval
            if self.life <= 0:
                self.alive = 0

        return self.alive
    
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_direct.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        
