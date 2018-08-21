# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipbattle.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a ship battle that has teken place
# ---------------------------------------------------------------------------
import random

import anwp.func.root

class ShipBattle(anwp.func.root.Root):
    """A ship battle represents a moment in time when star ships from
    various ships engaged in battle within a Solar System"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.systemID = int() # id of system
        self.systemName = str() # name of system
        self.round = int() # round when battle took place
        self.count = int() # number of iterations though battle
        self.seed = float() # random seed
        self.defaultAttributes = ('id', 'systemID', 'systemName', 'round', 'seed')
        self.setAttributes(args)
        
        # TODO: these are potentially temporary to save space, remove when appropriate
        self.componentdata = {} # Dict key = componentdata id, value = obj
        self.shiphulldata = {} # Dict key = shiphulldata id, value = obj
        self.dronehulldata = {} # Dict key = dronehulldata id, value = obj
        self.weapondata = {} # Dict key = weapondata id, value = obj
        
        self.empiresDict = {} # key = empire id, value = empire Dict breakdown
        self.shipsDict = {} # key = ship id, value = ship Dict breakdown
        self.captainsDict = {} # key = captain id, value = captain Dict breakdown
    
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
    
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_shipbattle.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        