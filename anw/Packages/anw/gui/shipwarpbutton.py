# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipwarpbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to warp ships
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class ShipWarpButton(RootButton):
    """The Ship Warp Button"""
    def __init__(self, path, x=-0.1, y=-0.85):
        RootButton.__init__(self, path, x=x, y=y, name='mapmove')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['warpships']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def presswarpships(self):
        """Warp Ships to new System"""
        self.mode.warpShips()
    
if __name__ == "__main__":
    myMenu = ShipWarpButton('media')
    run()