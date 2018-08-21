# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# swapcaptainbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to swap ship captains
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class SwapCaptainButton(RootButton):
    """The Swap Captain Button, shipList is list of ships that could swap"""
    def __init__(self, path, x, y, shipList):
        self.shipList = shipList
        RootButton.__init__(self, path, x=x, y=y, name='map')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['swap', 'sort']:
            buttonPosition = (self.posInitX,0,(self.posInitY+y*.09))
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.045)
            y -= 0.5

    def pressswap(self):
        """Swap Action"""
        self.mode.createSwapList(self.shipList)
    
    def presssort(self):
        """Sort all Captains and swap out the best captains into the best ships"""
        self.mode.sortAllCaptains(self.shipList)
        
if __name__ == "__main__":
    myMenu = SwapCaptainButton('media')
    run()