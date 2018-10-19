# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# decreasediplomacybutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to decrease diplomacy with another user
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class DecreaseDiplomacyButton(RootButton):
    """The Decrease Diplomacy Button"""
    def __init__(self, path, x=0.85, y=0.48):
        RootButton.__init__(self, path, x=x, y=y, name='diplomacy')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['decrease']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def pressdecrease(self):
        """Send Mail to other Empire"""
        self.mode.decreaseDiplomacy()
    
if __name__ == "__main__":
    myMenu = DecreaseDiplomacyButton('media')
    run()