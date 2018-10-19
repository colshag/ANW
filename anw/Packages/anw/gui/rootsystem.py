# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# rootsystem.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui common system gui information
# ---------------------------------------------------------------------------
from rootbutton import RootButton

class RootSystem(RootButton):
    """The Root System Industry Gui"""
    def __init__(self, path, x, y, mySystemDict, myEmpireDict, industrydata, name='', mode=0):
        self.setMyMode(mode)
        self.industrydata = industrydata
        self.mySystemDict = mySystemDict
        self.myEmpireDict = myEmpireDict
        RootButton.__init__(self, path, x=x, y=y, name=name)
        self.scale = 0.29
        self.xOffset = 0.65
        self.xInit = -0.28
        
    def getIndustryFactoryOutput(self, id, name):
        """Return Industry Output for given industry id using game information and systemDict"""
        value = self.mySystemDict[name][id]*self.industrydata[id].output
        return value