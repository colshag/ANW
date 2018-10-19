# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# futureindustry.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui displays the future system industry infrastructure
# ---------------------------------------------------------------------------
from anw.gui import rootsystem, valuebar
from anw.func import globals

class futureIndustry(rootsystem.RootSystem):
    """Future system industry infrastructure"""
    def __init__(self, path, mySystemDict, myEmpireDict, industrydata):
        rootsystem.RootSystem.__init__(self, path, -0.9, 0.38, mySystemDict,
                                       myEmpireDict, industrydata)
        self.infrastructureBars = None
        self.infrastructureOutput = self.getInfrastructureOutputList()
        self.infrastructureOutput.append([0, 'CITIES BEING USED', 
                                          self.mySystemDict['citiesUsed'],
                                          self.mySystemDict['cities']])
        self.createInfrastructureBars()
        
    def getInfrastructureOutputList(self):
        """Return List of Infrastructure Output data"""
        output = [[40, 'TECHNOLOGY POINTS'],
                  [22, 'SYSTEM MILITIA'],
                  [31, 'SHIPYARD POINTS'],
                  [34, 'MARINE POINTS'],
                  [37, 'WARP GATE POINTS'],
                  [25, 'FLEET CADETS PER TURN'],
                  [28, 'MARINE CADETS PER TURN'],
                  [16, 'RADAR STRENGTH'],
                  [19, 'JAMMING STRENGTH'],
                  [10, 'SIMULATIONS PER TURN'],
                  [13, 'DESIGNS PER TURN']]
        for myList in output:
            currentOutput = self.getInfrastructureOutput(myList[0], 'myIndustry')
            oldOutput = self.getInfrastructureOutput(myList[0], 'myOldIndustry')
            myList.append(currentOutput)
            myList.append(oldOutput)
        return output
    
    def getInfrastructureOutput(self, myId, name):
        """Return infrastructure output based on 
        name= myIndustry or myOldIndustry, id=industry id
        return a number that is the cumulation of all 3 ages of industry on system"""
        output = 0
        for i in range(myId,myId+3):
            id = str(i)
            output += self.getIndustryFactoryOutput(id, name)
        return output

    def createInfrastructureBars(self):
        """These bars will show the infrastructure output of system"""
        wordWrap = 30
        x = (self.posInitX+0.55)-(1*self.xOffset)
        y = self.posInitY+0.15
        self.createTitleCard('infrastructureBars','Future System Infrastructure:',
                         wordWrap,x+self.xInit,y+0.04)
        i = 0
        for myList in self.infrastructureOutput:
            id = myList[0]
            text = myList[1]
            setattr(self, 'infrastructureBar%s' % id, valuebar.ValueBar(self.path, scale=self.scale, extraText=text))
            myBar = getattr(self, 'infrastructureBar%s' % id)
            barHeight = myBar.myBar.getHeight()*self.scale
            myBar.setMyValues(myList[2],myList[3])
            myBar.setMyPosition(x,0,y-barHeight*i)
            myBar.setColor(globals.colors['guiwhite'])
            self.myWidgets.append(myBar)
            i += 1
    
    
if __name__ == "__main__":
    from anw.func import storedata
    data = storedata.loadFromFile('../../../Client/client.data')
    
    myIndustry = {}
    for i in range(1,46):
        myIndustry[str(i)] = 1
    systemDict = {'AL':1200, 'EC':110, 'IA':330,'cityIndustry':[10,0,0,0], 'oldCityIndustry':[10,0,0,0],
              'myIndustry':myIndustry, 'myOldIndustry':myIndustry, 'cities':20, 'citiesUsed':15}
    empireDict = {'CR':12301}
    myFutureIndustry = futureIndustry('media',systemDict, empireDict, data['industrydata'])
    run()