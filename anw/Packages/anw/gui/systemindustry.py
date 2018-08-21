# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# systemindustry.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui displays the current and future system industry stats
# ---------------------------------------------------------------------------
from anw.gui import rootsystem, valuebar, systemresources
from anw.func import globals

class SystemIndustry(rootsystem.RootSystem):
    """The System Industry Gui"""
    def __init__(self, path, mySystemDict, myEmpireDict, industrydata, writeGui=1):
        rootsystem.RootSystem.__init__(self, path, -0.9, 0.4, mySystemDict,
                                       myEmpireDict, industrydata)
        self.cityIndustry = self.mySystemDict['cityIndustry']
        self.oldCityIndustry = self.mySystemDict['oldCityIndustry']
        self.cityIndustryBars = None
        self.industryFactoryBars = None
        self.prodPerCityBars = None
        self.currentProductionBars = None
        self.currentResourceBars = None
        
        self.prodPerCityFactor = [globals.cityALGen, globals.cityECGen, globals.cityIAGen]
        self.currentIndustryFactor = self.getIndustryFactoryOutputList('myIndustry')
        self.oldIndustryFactor = self.getIndustryFactoryOutputList('myOldIndustry')
        self.currentProduction = self.getCurrentProduction()
        self.oldProduction = self.getOldProduction()
        
        if writeGui:
            self.createIndustryFactoryBars()
            self.createCityIndustryBars()
            self.createProdPerCityBars()
            self.createCurrentProductionBars()
            self.createMySystemResources()
    
    def createMySystemResources(self):
        self.mySystemResources = systemresources.SystemResources(self.path, self.posInitX+1.9, self.posInitY+0.13, 
                                                                 self.mySystemDict, self.myEmpireDict, self.industrydata)
        self.myWidgets.append(self.mySystemResources)

    def getCurrentProduction(self):
        """Current production = cityIndustry * currentIndustryFactor * productionPerCity"""
        output = [0,0,0]
        for i in range(3):
            output[i] = self.cityIndustry[i] * (1+self.currentIndustryFactor[i]/100) * self.prodPerCityFactor[i]
        return output
    
    def getOldProduction(self):
        """Old production = oldCityIndustry * oldIndustryFactor * productionPerCity"""
        output = [0,0,0]
        for i in range(3):
            output[i] = self.oldCityIndustry[i] * (1+self.oldIndustryFactor[i]/100) * self.prodPerCityFactor[i]
        return output

    def getIndustryFactoryOutputList(self, name):
        """Return industry output based on myIndustry or
        myOldIndustry as a list [AL,EC,IA]"""
        output = [0,0,0]
        for i in range(9):
            id = str(i+1)
            resource = i/3
            output[resource] += self.getIndustryFactoryOutput(id, name)*100
        return output
    
    def createCityIndustryBars(self):
        """These bars will show the proposed City Industry breakdown"""
        x = (self.posInitX+0.55)-(1*self.xOffset)
        y = self.posInitY+0.4
        self.cityIndustryBars = valuebar.IndustryBars(self.path, 
                                                     self.cityIndustry,
                                                     self.oldCityIndustry,
                                                     x=x,
                                                     y=y,scale=self.scale,extraText='INDUSTRY FOCUS',
                                                     title='Future City Industry Focus:')
        
        self.myWidgets.append(self.cityIndustryBars)
    
    def createProdPerCityBars(self):
        """These bars will show the resource production per city"""
        x = (self.posInitX+0.55)
        y = self.posInitY+0.4
        self.prodPerCityBars = valuebar.IndustryBars(self.path, 
                                                     self.prodPerCityFactor,
                                                     self.prodPerCityFactor,
                                                     x=x,
                                                     y=y,scale=self.scale,extraText='PRODUCTION PER CITY',
                                                     title='Resource Production Per City:')
        self.myWidgets.append(self.prodPerCityBars)

    def createIndustryFactoryBars(self):
        """These bars will show the Industry Production Bonus percentage based on
        Factories built at system"""
        x = (self.posInitX+0.5)+(1*self.xOffset)
        y = self.posInitY+0.4
        self.industryFactoryBars = valuebar.IndustryBars(self.path, 
                                                     self.currentIndustryFactor,
                                                     self.oldIndustryFactor,
                                                     x=x,
                                                     y=y,scale=self.scale,extraText='FACTORY BONUS %',
                                                     title='Future Industry Factory Bonus:')
        self.myWidgets.append(self.industryFactoryBars)
    
    def createCurrentProductionBars(self):
        """These bars will show the current production vs old production at system"""
        x = (self.posInitX+0.5)+(2*self.xOffset)
        y = self.posInitY+0.4
        self.currentProductionBars = valuebar.IndustryBars(self.path, 
                                                     self.currentProduction,
                                                     self.oldProduction,
                                                     x=x,
                                                     y=y,scale=self.scale,extraText='PRODUCTION PER TURN',
                                                     title='Future Resource Production:')
        self.myWidgets.append(self.currentProductionBars)
        
if __name__ == "__main__":
    from anw.func import storedata
    data = storedata.loadFromFile('../../../Client/client.data')
    
    myIndustry = {}
    for i in range(1,46):
        myIndustry[str(i)] = 1
    systemDict = {'AL':1200, 'EC':110, 'IA':330,'cityIndustry':[10,0,0,0], 'oldCityIndustry':[10,0,0,0],
              'myIndustry':myIndustry, 'myOldIndustry':myIndustry}
    empireDict = {'CR':12301}
    mySystemIndustry = SystemIndustry('media',systemDict, empireDict, data['industrydata'])
    run()