# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# empire.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents an Empire in the war package
# ---------------------------------------------------------------------------
import string

import anwp.func.root
import anwp.func.funcs
import anwp.func.globals

class Empire(anwp.func.root.Root):
    """A Empire object represents a Player or AI Controlled Empire."""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Name of Empire
        self.color1 = str() # First Color Representing Empire
        self.color2 = str() # Second Color Representing Empire
        self.imageFile = str() # image file of empire
        self.defaultAttributes = ('id', 'name', 'color1', 'color2', 'imageFile')
        self.setAttributes(args)
        
        self.myGalaxy = None # Actual Galaxy Object that contains this Empire
        self.shipDesigns = {} # all starship designs created key=id, value=obj
        self.droneDesigns = {} # all drone designs created key=id, value=obj
        
        # this is for in-simulation stats
        self.maxBV = 0.0
        self.maxCR = 0.0
        self.maxAL = 0.0
        self.maxEC = 0.0
        self.maxIA = 0.0
    
    def setMyValue(self):
        """Set the in-simulation battle values"""
        # check if this is first time
        if self.maxBV == 0.0:
            for shipID, myShip in self.myGalaxy.ships.iteritems():
                if myShip.empireID == self.id:
                    (BV,CR,AL,EC,IA) = myShip.getMyValue()
                    self.maxBV += BV
                    self.maxCR += CR
                    self.maxAL += AL
                    self.maxEC += EC
                    self.maxIA += IA
    
    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this Empire"""
        self.myGalaxy = galaxyObject
        galaxyObject.empires[self.id] = self
  
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_empire.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()