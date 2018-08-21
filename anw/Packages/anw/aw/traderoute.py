# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# traderoute.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a trade route
# ---------------------------------------------------------------------------
import string

from anw.func import root, globals

class TradeRoute(root.Root):
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
        self.type = str()
        self.defaultAttributes = ('id', 'fromSystem', 'toSystem', 'AL', 'EC', 'IA',
                                  'imageFile', 'oneTime', 'warpReq', 'type')
        self.setAttributes(args)
        self.myGalaxy = None # Acutal Galaxy Object that owns trade route
        self.getImageFileName()
    
    def getImageFileName(self):
        """Generate the image filename depends on number of resources being used"""
        # check for trade type
        try:
            (systemFrom, systemTo, self.type) = string.split(self.id, '-')
            if self.type == 'REG':
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
            elif self.type == 'GEN':
                self.imageFile = 'traderoute_orange'
            return 1
        except:
            return 'TradeRoute->cannot determine traderoute filename'

    def getWarpRequired(self, myGalaxy=None):
        """Return the amount of Warp Capactiy required to send this trade route through warp gates"""
        self.warpReq = 0
        # check if trade route requires warp gates
        if myGalaxy == None:
            myGalaxy = self.myGalaxy
        systemFrom = myGalaxy.systems[self.fromSystem]
        systemTo = myGalaxy.systems[self.toSystem]
        if systemTo.id not in systemFrom.warpGateSystems:
            return 0
        AL = 0
        EC = 0
        IA = 0
        if self.type == 'GEN':
            AL = systemFrom.prodAL
            EC = systemFrom.prodEC
            IA = systemFrom.prodIA
        else:
            AL = self.AL
            EC = self.EC
            IA = self.IA
            
        # calculate warpReq
        self.warpReq += int(AL/(globals.cityALGen*20))
        self.warpReq += int(EC/(globals.cityECGen*20))
        self.warpReq += int(IA/(globals.cityIAGen*20))
        if (AL > 0 or EC > 0 or IA > 0) and self.warpReq == 0:
            self.warpReq = 1
            
        return self.warpReq

    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this trade route"""
        self.myGalaxy = galaxyObject
        galaxyObject.tradeRoutes[self.id] = self
        