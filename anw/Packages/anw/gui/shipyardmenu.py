# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipyardmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to choose a shipyard sub selection of choices
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class ShipyardMenu(RootButton):
    """The shipyard Menu Gui"""
    def __init__(self, path, x=0, y=-0.1):
        RootButton.__init__(self, path, x=x, y=y, name='shipyard')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['upgradeships','repairships','buildships']:
            buttonPosition = (self.posInitX,0,self.posInitY+y*0.0525)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
            
    def pressbuildships(self):
        """Setup to build ships"""
        self.mode.systemmenu.press5()
        self.mode.systemmenu.createBuildShipsGui()
        
    def pressrepairships(self):
        """Setup to repair ships"""
        self.mode.systemmenu.press5()
        self.mode.systemmenu.createRepairShipsGui()
    
    def pressupgradeships(self):
        """Setup to upgrade ships"""
        self.mode.systemmenu.press5()
        self.mode.systemmenu.createUpgradeShipsGui()
    
if __name__ == "__main__":
    myMenu = ShipyardMenu('media')
    run()