# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# designmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to setup tech choices and hull type for ship and drone design
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class DesignMenu(RootButton):
    """The Design Menu Gui"""
    def __init__(self, path, x=-0.53, y=0.85):
        RootButton.__init__(self, path, x=x, y=y, name='design')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['mytech','alltech','setupsim']:
            buttonPosition = (self.posInitX+y*0.525,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def pressmytech(self):
        """Setup Hull types for my tech"""
        self.mode.resetMode()
        self.setupMyTech()
        
    def setupMyTech(self):
        self.mode.allTech = 0
        shipHullDicts = {}
        droneHullDicts = {}
        for id, myDict in self.mode.game.shiphulldata.iteritems():
            if self.mode.game.myTech[myDict.techReq].complete == 1:
                shipHullDicts[id] = myDict
        self.mode.createShipHulls(shipHullDicts)
        for id, myDict in self.mode.game.dronehulldata.iteritems():
            if self.mode.game.myTech[myDict.techReq].complete == 1:
                droneHullDicts[id] = myDict
        self.mode.createDroneHulls(droneHullDicts)
        self.mode.createShipDesignList()
        self.mode.createDroneDesignList()

    def pressalltech(self):
        """Setup Hull types for all tech"""
        self.mode.resetMode()
        self.setupAllTech()
    
    def setupAllTech(self):
        self.mode.allTech = 1
        self.mode.createShipHulls(self.mode.game.shiphulldata)
        self.mode.createDroneHulls(self.mode.game.dronehulldata)
        self.mode.createShipDesignList()
        self.mode.createDroneDesignList()
    
    def presssetupsim(self):
        """Setup a complicated simulation"""
        self.mode.resetMode()
        self.mode.refreshMultiSim()
        
    def ignoreShortcuts(self):
        if self.mode.selectedShipHull != None:
            self.mode.selectedShipHull.ignoreShortcuts()
    
    def setShortcuts(self):
        if self.mode.selectedShipHull != None:
            self.mode.selectedShipHull.setShortcuts()
    
if __name__ == "__main__":
    myMenu = DesignMenu('media')
    run()