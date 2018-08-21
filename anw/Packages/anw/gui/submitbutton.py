# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# submitbutton.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# Allows user to Submit to Server
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class SubmitToMultiSimButton(RootButton):
    """Submit To do a Multi Simulation"""
    def __init__(self, path, x=-0.1, y=-0.85):
        RootButton.__init__(self, path, x=x, y=y, name='design')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['simulatedesign']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def presssimulatedesign(self):
        """Submit to Server to Repair Ships"""
        self.mode.multiSimulate()

class SubmitToRepairShipsButton(RootButton):
    """Submit To Repair Ships"""
    def __init__(self, path, x=-0.1, y=-0.85):
        RootButton.__init__(self, path, x=x, y=y, name='order')
        self.scale = 0.25
        
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['submit']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1

    def presssubmit(self):
        """Submit to Server to Repair Ships"""
        self.mode.systemmenu.shipyardrepairshipsgui.submitRepairStarshipOrder()

class SubmitToRepairRegimentsButton(SubmitToRepairShipsButton):
    """Submit To Repair Regiments"""
    
    def presssubmit(self):
        """Submit to Server to Repair Regiments"""
        self.mode.systemmenu.mirepairmarinesgui.submitRepairRegimentOrder()

class SubmitToUpgradeRegimentsButton(SubmitToRepairShipsButton):
    """Submit To Upgrade Regiments"""
    
    def presssubmit(self):
        """Submit to Server to Upgrade Regiments"""
        self.mode.systemmenu.miupgrademarinesgui.submitUpgradeRegimentOrder()

class SubmitToUpgradeShipsButton(SubmitToRepairShipsButton):
    """Submit To Upgrade Ships"""
    
    def presssubmit(self):
        """Submit to Server to Upgrade Ships"""
        self.mode.systemmenu.shipyardupgradeshipsgui.submitUpgradeStarshipOrder()
        
class SubmitToCancelShipsButton(SubmitToRepairShipsButton):
    
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['cancel']:
            buttonPosition = (self.posInitX+y,0,self.posInitY)
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.0525)
            y += 1
            
    def presscancel(self):
        """Submit to Server to Cancel Repair Ships Orders"""
        self.mode.systemmenu.shipyardrepairshipsgui.submitCancelRepairStarshipOrder()

class SubmitToCancelRegimentsButton(SubmitToCancelShipsButton):
    
    def presscancel(self):
        """Submit to Server to Cancel Repair Regiment Orders"""
        self.mode.systemmenu.mirepairmarinesgui.submitCancelRepairRegimentOrder()

class SubmitToCancelRegimentsUpgradeButton(SubmitToCancelShipsButton):
    
    def presscancel(self):
        """Submit to Server to Cancel Upgrade Regiment Orders"""
        self.mode.systemmenu.miupgrademarinesgui.submitCancelUpgradeRegimentOrder()
        
class SubmitToCancelShipsUpgradeButton(SubmitToCancelShipsButton):
    
    def presscancel(self):
        """Submit to Server to Cancel Upgrade Ships Orders"""
        self.mode.systemmenu.shipyardupgradeshipsgui.submitCancelUpgradeStarshipOrder()
        
class SubmitToCancelMarketOrderButton(SubmitToCancelShipsButton):

    def __init__(self, path, x, y, orderID):
        self.orderID = orderID
        SubmitToCancelShipsButton.__init__(self, path, x=x, y=y)
        self.scale = 0.25    
    
    def presscancel(self):
        """Submit to Server to Cancel a Market Order"""
        self.mode.systemmenu.cancelMarketOrder(self.orderID)
        
class SubmitToCancelSendCreditsButton(SubmitToCancelMarketOrderButton):
    
    def presscancel(self):
        self.mode.submitCancelSendCredits(self.orderID)

        