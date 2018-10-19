# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipbattle.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a ship battle that has teken place
# ---------------------------------------------------------------------------
import random

from anw.func import root

class ShipBattle(root.Root):
    """A ship battle represents a moment in time when star ships from
    various ships engaged in battle within a Solar System"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.systemID = str() # id of system
        self.empireID = str() # empireID of system at time of battle
        self.systemName = str() # name of system
        self.cities = int() # cities in system
        self.x = float()
        self.y = float()
        self.round = int() # round when battle took place
        self.count = int() # number of iterations though battle
        self.seed = float() # random seed
        self.defaultAttributes = ('id', 'systemID', 'empireID', 'systemName', 'cities', 'x', 'y', 'round', 'seed')
        self.setAttributes(args)
        
        self.componentdata = {} # Dict key = componentdata id, value = obj
        self.shiphulldata = {} # Dict key = shiphulldata id, value = obj
        self.dronehulldata = {} # Dict key = dronehulldata id, value = obj
        self.weapondata = {} # Dict key = weapondata id, value = obj
        
        self.empiresDict = {} # key = empire id, value = empire Dict breakdown
        self.shipsDict = {} # key = ship id, value = ship Dict breakdown
        self.captainsDict = {} # key = captain id, value = captain Dict breakdown
        self.regimentsExposed = {} # key = empire id, value = regiment number exposed in transit
    
    def setRegimentsExposed(self, regimentsExposed):
        """Set the Regiments exposed"""
        self.regimentsExposed = regimentsExposed
        
    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this Ship Battle"""
        galaxyObject.shipBattles[self.id] = '%d-%s' % (self.round, self.systemName)
    
    def setCaptainsDict(self, captainsDict):
        """Set the Captains Dict"""
        self.captainsDict = captainsDict
    
    def setEmpiresDict(self, empiresDict):
        """Set the Empires Dict"""
        self.empiresDict = empiresDict
    
    def setShipsDict(self, shipsDict):
        """Set the Ships Dict"""
        self.shipsDict = shipsDict
    
    def setData(self, componentdata, shiphulldata, dronehulldata, weapondata):
        """Set the general Ship Simulator Data"""
        self.componentdata = componentdata
        self.shiphulldata = shiphulldata
        self.dronehulldata = dronehulldata
        self.weapondata = weapondata
    
    def setSeed(self):
        """Set the random seed"""
        self.seed = random.Random().random()
        