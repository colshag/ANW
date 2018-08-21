# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modifyindustry.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to remove or add
# industry to a system.
# ---------------------------------------------------------------------------
from anw.func import globals, funcs
from anw.gui import rootsystem, valuebar, industryvalue

class ModifyIndustry(rootsystem.RootSystem):
    """The Modify Industry Gui"""
    def __init__(self, path, mySystemDict, myEmpireDict, myTechDict, industrydata, mode):
        rootsystem.RootSystem.__init__(self, path, -1, -0.2, mySystemDict,
                                       myEmpireDict, industrydata, name='industry')
        self.myTechDict = myTechDict
        self.myIndustry = mySystemDict['myIndustry']
        self.myOldIndustry = mySystemDict['myOldIndustry']
        self.cities = mySystemDict['cities']
        self.citiesUsed = mySystemDict['citiesUsed']
        self.keyList = funcs.sortStringList(self.industrydata.keys())
        self.createTitleCard('modifyindustryTitle1','Select Industry to Modify:',
                         40,self.posInitX-0.24,self.posInitY+0.04)
        self.createIndustryBars(mode)
        self.disableButtonTime = -1
        self.modifyIndustryValue = None
    
    def setID(self, id):
        self.id = id
    
    def createButtons(self):
        """Create all Buttons"""
        y = 0
        for key in ['af','cm','ss','sc','dc','rs','js','mf','fa','ma','sy','mi','wg','rc']:
            buttonPosition = (self.posInitX,0,(self.posInitY+y*.10))
            self.createButton(key, buttonPosition, geomX=0.5, geomY=0.045)
            y -= 0.5
        
    def createIndustryBars(self, mode):
        """Create all the industry bars using myIndustry, myOldIndustry"""
        num = 0
        y = 0
        for industryKey in self.keyList:
            num += 1
            id = str(num)
            myIndustryData = self.industrydata[id]
            text = myIndustryData.name
            setattr(self, 'industryBar%s' % id, valuebar.ValueBar(self.path, scale=self.scale, extraText=text))
            myBar = getattr(self, 'industryBar%s' % id)
            (x,y,color) = self.getIndustryPos(myIndustryData)
            myBar.setMyValues(self.myIndustry[id], self.myOldIndustry[id])
            myBar.setMyPosition(x,0,y)
            myBar.setColor(color)
            
            if (mode.game.myTech[myIndustryData.techReq].complete == 0 and
                myBar.currentValue == 0):
                myBar.destroy()
            else:
                self.myWidgets.append(myBar)
    
    def getIndustryPos(self, myIndustryData):
        """Setup Industry in 3 columns, Basic, Advanced, Intelligent Industry"""
        abr = myIndustryData.abr
        x = self.posInitX + 0.55
        y = int(myIndustryData.id)-1
        y = self.posInitY-((y/3)*0.05)
        color = globals.colors['guiwhite']
        if abr[0] == 'B':
            x = x
        elif abr[0] == 'A':
            color = globals.colors['guiwhite']
            x = x + 0.68
        else:
            x = x + 1.36
        return (x,y,color)
    
    def pressButton(self, key):
        """Called when industry button is pressed"""
        if key not in self.disabledButtons:
            self.createModifyIndustryValue(key)
            self.enableLastButton(key)
            self.disableButton(key)
            if self.mode != None:
                self.mode.playSound('beep01')
    
    def createModifyIndustryValue(self, key):
        """Create modifyIndustryValue button, remove old one if needed"""
        if self.modifyIndustryValue != None:
            self.myWidgets.remove(self.modifyIndustryValue)
            self.modifyIndustryValue.destroy()
        self.modifyIndustryValue = industryvalue.ModifyIndustryValue(self.path, key, myParent=self)
        self.myWidgets.append(self.modifyIndustryValue)
    
if __name__ == "__main__":
    from anw.func import storedata
    data = storedata.loadFromFile('../../../Client/client.data')
    
    myIndustry = {}
    for i in range(1,43):
        myIndustry[str(i)] = 1
    
    myTech = {}
    for i in range(277):
        myTech[str(i)] = {'complete':0}
    myTech['4']['complete'] = 1
        
    empireDict = {'CR':20000}
    systemDict = {'AL':1200, 'EC':110, 'IA':330,'cityIndustry':[10,0,0,0], 'oldCityIndustry':[10,0,0,0],
              'myIndustry':myIndustry, 'myOldIndustry':myIndustry, 'cities':10, 'citiesUsed':2}
    myModifyIndustry = ModifyIndustry('media', systemDict, empireDict, myTech, data['industrydata'])
    run()