# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# marketstat.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a Galactic Trade Market Statistic for a round of play
# ---------------------------------------------------------------------------
from anw.func import root, globals

class MarketStat(root.Root):
    """A MarketStat represents the Market Statistics for a round of play, id=round"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID = round
        self.avgSoldAL = float()
        self.avgSoldEC = float()
        self.avgSoldIA = float()
        self.sumSoldAL = float()
        self.sumSoldEC = float()
        self.sumSoldIA = float()
        self.volSoldAL = float()
        self.volSoldEC = float()
        self.volSoldIA = float()
        self.defaultAttributes = ('id','avgSoldAL','sumSoldAL','volSoldAL',
                                  'avgSoldEC','sumSoldEC','volSoldEC',
                                  'avgSoldIA','sumSoldIA','volSoldIA')
        self.setAttributes(args)
        # set the initial avg costs in case the market is stagnant.
        self.setInitialStat()
    
    def setInitialStat(self):
        """Set the initial market stats based on the global difference in production of the basic resources"""
        self.avgSoldAL = globals.cityCRGen/globals.cityALGen
        self.avgSoldEC = globals.cityCRGen/globals.cityECGen
        self.avgSoldIA = globals.cityCRGen/globals.cityIAGen
        