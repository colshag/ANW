# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# army.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# An Army Represents the client side grouping of regiments at a system
# ---------------------------------------------------------------------------
import string
from anw.gui import rootsim
from anw.func import funcs
        
class MyArmy(rootsim.RootSim):
    """An Army Represents the client side grouping of regiments at a system"""
    def __init__(self, path, mode, systemID):
        self.mode = mode
        self.myGuiSystem = self.mode.systems[systemID]
        self.myImage = ''
        self.myRegList = []
        self.availSystems = []
        self.id = systemID
        self.refreshMyRegList()
        rootsim.RootSim.__init__(self, path, texture=self.myImage, 
                           type='plane', transparent=1, scale=1)
        self.mode = mode
        self.glow = 1
        self.y = 20.2
        self.setMyPosition()
        self.width = 0.3
        self.height = 0.3
        self.createMySim()
    
    def addToAvailSystems(self, systemID):
        """Add System to availSystems for Army and all regiments in army"""
        if systemID in self.availSystems:
            return
        for regimentID in self.myRegList:
            myRegiment = self.mode.game.myRegiments[regimentID]
            myRegiment['availSystems'].append(systemID)
        self.setAvailSystems()
    
    def removeFromAvailSystems(self, systemID):
        """Remove System from availSystems for Army and all regiments in army"""
        if systemID not in self.availSystems:
            return
        for regimentID in self.myRegList:
            myRegiment = self.mode.game.myRegiments[regimentID]
            myRegiment['availSystems'].remove(systemID)
        self.setAvailSystems()
        
    def refreshMyRegList(self):
        """Refresh the list of regiments in army"""
        self.setMyRegList()
        self.setAvailSystems()
        if self.myRegList == []:
            self.destroy()
        else:
            self.myImage = 'army_%s' % self.mode.game.myEmpireID
    
    def setMyRegList(self):
        self.myRegList = self.mode.game.myArmies[self.id]
            
    def setAvailSystems(self):
        firstRegiment = self.mode.game.myRegiments[self.myRegList[0]]
        self.availSystems = firstRegiment['availSystems']
        
    def setMyPosition(self):
        """Set the Army Position based on the system position"""
        (self.x, self.z) = self.myGuiSystem.getMyArmyPosition(self.mode.game.myEmpireID)
        
    def createMySim(self):
        """Create The Sim"""
        self.registerMySim()
        self.loadMyTexture()
        self.setGlow()
        self.reSize()
        self.setPos()
        self.rotate()
    
    def destroy(self):
        """Remove the armada from game"""
        self.sim.removeNode()
        
class OtherArmy(MyArmy):
    """An Army Represents the client side grouping of regiments at a system"""
    def __init__(self, path, mode, systemID, empireID):
        self.myEmpireID = empireID
        self.mode = mode
        self.myGuiSystem = self.mode.systems[systemID]
        self.myImage = ''
        self.myRegList = []
        self.availSystems = []
        self.id = '%s-%s' % (systemID, empireID)
        self.refreshMyRegList()
        rootsim.RootSim.__init__(self, path, texture=self.myImage, 
                           type='plane', transparent=1, scale=1)
        self.mode = mode
        self.glow = 1
        self.y = 20.2
        self.setMyPosition()
        self.width = 0.3
        self.height = 0.3
        self.createMySim()
        
    def refreshMyRegList(self):
        """Refresh the list of regiments in army"""
        self.myImage = 'army_%s' % self.myEmpireID

    def setMyPosition(self):
        """Set the Army Position based on the system position"""
        (self.x, self.z) = self.myGuiSystem.getMyArmyPosition(self.myEmpireID)
        
class WarpedArmy(MyArmy):
    """An Army Represents the client side grouping of regiments at a system"""
    
    def setAvailSystems(self):
        self.availSystems = []
    
    def setMyRegList(self):
        self.myRegList = self.mode.game.warpedArmies[self.id]
        
    def setMyPosition(self):
        """Set the Army Position based on the system position"""
        (self.x, self.z) = self.myGuiSystem.getMyWarpedArmyPosition(self.mode.game.myEmpireID)