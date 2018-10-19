# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# empirestat.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents empire statistics
# ---------------------------------------------------------------------------
from anw.func import root, globals

class EmpireStat(root.Root):
    """An EmpireStat represents the Empire Statistics for a round of play, id=round"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID = round
        self.CRcostOfDole = float()
        self.CRcostOfShips = float()
        self.CRcostOfMarines = float()
        self.CRfromMarketSales = float()
        self.previousCR = float()
        self.ALProduced = float()
        self.ECProduced = float()
        self.IAProduced = float()
        self.defaultAttributes = ('id','CRcostOfDole',
                                  'CRcostOfShips','CRcostOfMarines','previousCR',
                                  'CRFromMarketSales','ALProduced','ECProduced','IAProduced')
        self.setAttributes(args)
        
        