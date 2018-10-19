# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# armada.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# An Armada Represents the client side grouping of ships at a system
# ---------------------------------------------------------------------------
import string
from anw.gui import rootsim
from anw.func import funcs
        
class MyArmada(rootsim.RootSim):
    """An Armada Represents the client side grouping of ships at a system"""
    def __init__(self, path, mode, systemID):
        self.path = path
        self.mode = mode
        self.myGuiSystem = self.mode.systems[systemID]
        self.myImage = ''
        self.myShipList = []
        self.availSystems = []
        self.id = systemID
        self.refreshMyShipList()
        rootsim.RootSim.__init__(self, path, texture=self.myImage, 
                           type='plane', transparent=1, scale=1)
        self.mode = mode
        self.glow = 1
        self.y = 20.2
        self.setMyPosition()
        self.width = 0.3
        self.height = 0.3
        self.createMySim()
    
    def refreshMyShipList(self):
        """Refresh the list of ships in armada"""
        shipHullID = 0
        self.setMyShipList()
        self.setAvailSystems()
        for myShipID in self.myShipList:
            designID = self.mode.game.myShips[myShipID]['designID']
            myShipHull = int(self.mode.game.shipDesignObjects[designID].shipHullID)
            if myShipHull > shipHullID:
                shipHullID = myShipHull
        if shipHullID == 0:
            self.destroy()
        else:
            abr = self.mode.game.shiphulldata[str(shipHullID)].abr
            self.myImage = '%s_%s' % (string.lower(abr), self.mode.game.myEmpireID)
            try:
                self.texture = '%s/%s.png' % (self.path, self.myImage)
                self.loadMyTexture()
            except:
                pass
    
    def setMyShipList(self):
        self.myShipList = self.mode.game.myArmadas[self.id]
            
    def setAvailSystems(self):
        firstShip = self.mode.game.myShips[self.myShipList[0]]
        self.availSystems = firstShip['availSystems']
        
    def setMyPosition(self):
        """Set the Armada Position based on the system position"""
        (self.x, self.z) = self.myGuiSystem.getMyArmadaPosition(self.mode.game.myEmpireID)
        
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
        

class OtherArmada(MyArmada):
    """An Armada Represents the client side grouping of ships at a system"""
    def __init__(self, path, mode, systemID, empireID):
        self.myEmpireID = empireID
        self.path = path
        self.mode = mode
        self.myGuiSystem = self.mode.systems[systemID]
        self.myImage = ''
        self.myShipList = []
        self.availSystems = []
        self.id = '%s-%s' % (systemID, empireID)
        self.refreshMyShipList()
        rootsim.RootSim.__init__(self, path, texture=self.myImage, 
                           type='plane', transparent=1, scale=1)
        self.mode = mode
        self.glow = 1
        self.y = 20.2
        self.setMyPosition()
        self.width = 0.3
        self.height = 0.3
        self.createMySim()
        
        
    def refreshMyShipList(self):
        """Refresh the list of ships in armada"""
        self.myImage = 'armada_%s' % self.myEmpireID
    
    def setMyPosition(self):
        """Set the Armada Position based on the system position"""
        (self.x, self.z) = self.myGuiSystem.getMyArmadaPosition(self.myEmpireID)


class WarpedArmada(MyArmada):
    """An Armada Represents the client side grouping of ships at a system"""
    
    def setAvailSystems(self):
        self.availSystems = []
    
    def setMyShipList(self):
        self.myShipList = self.mode.game.warpedArmadas[self.id]
        
    def setMyPosition(self):
        """Set the Armada Position based on the system position"""
        (self.x, self.z) = self.myGuiSystem.getMyWarpedArmadaPosition(self.mode.game.myEmpireID)