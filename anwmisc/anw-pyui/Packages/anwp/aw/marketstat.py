# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# marketstat.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a Galactic Trade Market Statistic for a round of play
# ---------------------------------------------------------------------------
import anwp.func.root
import anwp.func.globals

class MarketStat(anwp.func.root.Root):
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
        self.avgSoldAL = anwp.func.globals.cityCRGen/anwp.func.globals.cityALGen
        self.avgSoldEC = anwp.func.globals.cityCRGen/anwp.func.globals.cityECGen
        self.avgSoldIA = anwp.func.globals.cityCRGen/anwp.func.globals.cityIAGen

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_marketstat.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        