# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mimenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to choose a military installation sub selection of choices
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class MIMenu(RootButton):
    """The Military Installation Menu Gui"""
    def __init__(self, path, x=0, y=-0.1):
        RootButton.__init__(self, path, x=x, y=y, name='mi')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['upgrademarines','refitmarines','buildmarines']:
            buttonPosition = (self.posInitX,0,self.posInitY+y*0.0525)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
            
    def pressbuildmarines(self):
        """Setup to build marines"""
        self.mode.systemmenu.press6()
        self.mode.systemmenu.createBuildMarinesGui()
        
    def pressrefitmarines(self):
        """Setup to restore marines"""
        self.mode.systemmenu.press6()
        self.mode.systemmenu.createRepairMarinesGui()
    
    def pressupgrademarines(self):
        """Setup to upgrade marines"""
        self.mode.systemmenu.press6()
        self.mode.systemmenu.createUpgradeMarinesGui()
    
if __name__ == "__main__":
    myMenu = MIMenu('media')
    run()