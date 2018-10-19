# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# regwarpbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to warp regiments
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class RegWarpButton(RootButton):
    """The Regiment Warp Button"""
    def __init__(self, path, x=-0.1, y=-0.85):
        RootButton.__init__(self, path, x=x, y=y, name='mapmove')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['warparmies']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def presswarparmies(self):
        """Warp Regiments to new System"""
        self.mode.warpReg()
    
if __name__ == "__main__":
    myMenu = RegWarpButton('media')
    run()