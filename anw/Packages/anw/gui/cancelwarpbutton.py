# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# cancelwarpbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to warp ships
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class CancelWarpButton(RootButton):
    """The Cancel Button"""
    def __init__(self, path, x=-0.1, y=-0.85):
        RootButton.__init__(self, path, x=x, y=y, name='mapmove')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['cancel']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def presscancel(self):
        """Cancel Action"""
        self.mode.cancelWarpShips()

class CancelWarpRegButton(CancelWarpButton):
    
    def presscancel(self):
        """Cancel Action"""
        self.mode.cancelWarpReg()
        
if __name__ == "__main__":
    myMenu = CancelWarpButton('media')
    run()