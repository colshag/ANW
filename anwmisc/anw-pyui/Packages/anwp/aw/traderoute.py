# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# traderoute.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a trade route
# ---------------------------------------------------------------------------
import string

import anwp.func.root

class TradeRoute(anwp.func.root.Root):
    """A Trade Route represents one Trade Route Object in ANW"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.fromSystem = str() # ID of System
        self.toSystem = str() # ID of System
        self.AL = float()
        self.EC = float()
        self.IA = float()
        self.imageFile = str()
        self.oneTime = int()
        self.warpReq = int()
        self.defaultAttributes = ('id', 'fromSystem', 'toSystem', 'AL', 'EC', 'IA',
                                  'imageFile', 'oneTime', 'warpReq')
        self.setAttributes(args)
        self.myGalaxy = None # Acutal Galaxy Object that owns trade route
        self.getImageFileName()
    
    def getImageFileName(self):
        """Generate the image filename depends on number of resources being used"""
        # check for trade type
        try:
            (systemFrom, systemTo, tradeType) = string.split(self.id, '-')
            if tradeType == 'REG':
                if self.AL > 0 and self.EC == 0 and self.IA == 0:
                    if self.oneTime == 0:
                        self.imageFile = 'traderoute_blue'
                    else:
                        self.imageFile = 'traderoute_blue_once'
                elif self.AL == 0 and self.EC > 0 and self.IA == 0:
                    if self.oneTime == 0:
                        self.imageFile = 'traderoute_yellow'
                    else:
                        self.imageFile = 'traderoute_yellow_once'
                elif self.AL == 0 and self.EC == 0 and self.IA > 0:
                    if self.oneTime == 0:
                        self.imageFile = 'traderoute_red'
                    else:
                        self.imageFile = 'traderoute_red_once'
                elif self.AL > 0 or self.EC > 0 or self.IA > 0:
                    if self.oneTime == 0:
                        self.imageFile = 'traderoute_white'
                    else:
                        self.imageFile = 'traderoute_white_once'
            elif tradeType == 'GEN':
                self.imageFile = 'traderoute_orange'
            return 1
        except:
            return 'TradeRoute->cannot determine traderoute filename'

    def getWarpRequired(self):
        """Return the amount of Warp Capactiy required to send this trade route through warp gates"""
        self.warpReq = 0
        # check if trade route requires warp gates
        if self.myGalaxy <> None:
            systemFrom = self.myGalaxy.systems[self.fromSystem]
            systemTo = self.myGalaxy.systems[self.toSystem]
            if systemTo.id not in systemFrom.warpGateSystems:
                return 0
        
        # otherwise calculate warpReq
        self.warpReq += int(self.AL/(anwp.func.globals.cityALGen*20))
        self.warpReq += int(self.EC/(anwp.func.globals.cityECGen*20))
        self.warpReq += int(self.IA/(anwp.func.globals.cityIAGen*20))
        if (self.AL > 0 or self.EC > 0 or self.IA > 0) and self.warpReq == 0:
            self.warpReq = 1
        return self.warpReq

    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this trade route"""
        self.myGalaxy = galaxyObject
        galaxyObject.tradeRoutes[self.id] = self

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_traderoute.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        