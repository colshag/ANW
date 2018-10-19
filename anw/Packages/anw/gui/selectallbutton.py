# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# selectallbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to warp ships
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class SelectAllShipButton(RootButton):
    """The Select All Button"""
    def __init__(self, path, x=-0.1, y=-0.35):
        RootButton.__init__(self, path, x=x, y=y, name='mapmove')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['selectall']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def pressselectall(self):
        """Select All Ships"""
        self.mode.selectAllShips()

class SelectAllRegButton(SelectAllShipButton):
    def pressselectall(self):
        """Select All Regiments"""
        self.mode.selectAllRegiments()

class SelectAllShipsToRepairButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Ships to Repair"""
        self.mode.systemmenu.shipyardrepairshipsgui.selectAllToRepair()

class SelectAllShipsToUpgradeButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Ships to Upgrade"""
        self.mode.systemmenu.shipyardupgradeshipsgui.selectAllToRepair()

class SelectAllRegimentsToRepairButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Regiments to Repair"""
        self.mode.systemmenu.mirepairmarinesgui.selectAllToRepair()

class SelectAllRegimentsToUpgradeButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Regiments to Repair"""
        self.mode.systemmenu.miupgrademarinesgui.selectAllToRepair()
        
class SelectAllShipsInQueButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Ships In Que to Cancel"""
        self.mode.systemmenu.shipyardrepairshipsgui.selectAllInQue()

class SelectAllShipsInQueForUpgradeButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Ships In Que to Cancel"""
        self.mode.systemmenu.shipyardupgradeshipsgui.selectAllInQue()
        
class SelectAllRegimentsInQueButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Regiments In Que to Cancel"""
        self.mode.systemmenu.mirepairmarinesgui.selectAllInQue()

class SelectAllRegimentsInQueForUpgradeButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=0, y=0):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
    
    def pressselectall(self):
        """Select All Regiments In Que to Cancel"""
        self.mode.systemmenu.miupgrademarinesgui.selectAllInQue()
        
class SelectAllDamagedShipsButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=-0.1, y=-0.30):
        RootButton.__init__(self, path, x=x, y=y, name='mapmove')
        self.scale = 0.25
    
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['selectdamaged']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
    
    def pressselectdamaged(self):
        """Select All Damaged Ships"""
        self.mode.selectAllDamagedShips()
        
class SelectAllDamagedRegimentsButton(SelectAllShipButton):
    """The Select All Button"""
    def __init__(self, path, x=-0.1, y=-0.3):
        RootButton.__init__(self, path, x=x, y=y, name='mapmove')
        self.scale = 0.25
    
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['selectdamaged']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
    
    def pressselectdamaged(self):
        """Select All Damaged Regiments"""
        self.mode.selectAllDamagedRegiments()
        
if __name__ == "__main__":
    myMenu = SelectAllButton('media')
    run()