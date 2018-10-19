# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# systemresources.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui displays the current system resources available
# ---------------------------------------------------------------------------
from anw.gui import rootsystem, valuebar

class SystemResources(rootsystem.RootSystem):
    """The System Resources Gui"""
    def __init__(self, path, x, y, mySystemDict, myEmpireDict, industrydata):
        rootsystem.RootSystem.__init__(self, path, x, y, mySystemDict,
                                       myEmpireDict, industrydata)
        self.resources = [self.mySystemDict['AL'], 
                          self.mySystemDict['EC'], self.mySystemDict['IA']]
        self.systemResourceBars = None
        self.createSystemResourceBars()
        
    def createSystemResourceBars(self):
        """These bars will show the proposed City Industry breakdown"""
        wordWrap = 30
        x = (self.posInitX+0.55)-(1*self.xOffset)
        y = self.posInitY
        self.systemResourceBars = valuebar.IndustryBars(self.path, 
                                                        self.resources,
                                                        self.resources,
                                                        x=x,
                                                        y=y,scale=self.scale,
                                                        extraText='RESOURCE AVAILABLE',
                                                        title='Current System Resources:')
        self.myWidgets.append(self.systemResourceBars)
    
class GalaxyResourcePrices(SystemResources):
    def createSystemResourceBars(self):
        pass
    
    def createGalaxyResourcePrices(self):
        """These bars will show prices of each resource currently this turn"""
        self.resources = [self.mode.game.prices['AL'], 
                          self.mode.game.prices['EC'], self.mode.game.prices['IA']]
        wordWrap = 30
        x = (self.posInitX+0.55)-(1*self.xOffset)
        y = self.posInitY
        self.systemResourceBars = valuebar.IndustryBars(self.path, 
                                                        self.resources,
                                                        self.resources,
                                                        x=x,
                                                        y=y,scale=self.scale,
                                                        extraText='CURRENT PRICE',
                                                        title='Current Round Global Prices:')
        self.myWidgets.append(self.systemResourceBars)
        
if __name__ == "__main__":
    systemDict = {'AL':1200, 'EC':110, 'IA':330}
    empireDict = {'CR':12301}
    mySystemResources = SystemResources('media', -0.9, -0.2, systemDict, empireDict, {})
    run()