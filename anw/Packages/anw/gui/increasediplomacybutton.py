# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# increasediplomacybutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to increase diplomacy with another user
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class IncreaseDiplomacyButton(RootButton):
    """The Increase Diplomacy Button"""
    def __init__(self, path, x=0.35, y=0.48):
        RootButton.__init__(self, path, x=x, y=y, name='diplomacy')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['increase']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def pressincrease(self):
        """Send Mail to other Empire"""
        self.mode.increaseDiplomacy()
    
if __name__ == "__main__":
    myMenu = IncreaseDiplomacyButton('media')
    run()