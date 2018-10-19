# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# industryvalue.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This uses scroll mouse up/down or plus and minus buttons to 
# Add/Remove Industry from System
# ---------------------------------------------------------------------------
import string

from anw.func import globals, funcs
from anw.gui import textonscreen, scrollvalue

class ModifyIndustryValue(scrollvalue.ScrollValue):
    """Add or remove industry"""
    def __init__(self, path, key, myParent):
        self.key = key
        self.myIndustryData = None
        self.myParent = myParent
        self.industrySim = None
        self.textIndustryName = None
        self.textIndustryDescription = None
        self.textCR = None
        self.textAL = None
        self.textEC = None
        self.textIA = None
        scrollvalue.ScrollValue.__init__(self, path, x=0.67, y=-0.1, name='age')
        self.allKeys = ['A','S','D','Z','X','C']
        self.scrollFactor = 1
        self.pressButton('Z')
        self.myTitle.setText('Choose Amount of Industry to Add or Subtract:')
    
    def pressZ(self):
        """Display Basic Industry Info"""
        self.enableLastButton('Z')
        self.disableButton('Z')
        self.setMyIndustryData('b')
        self.createIndustryInfo()
    
    def pressX(self):
        """Display Advanced Industry Info"""
        self.enableLastButton('X')
        self.disableButton('X')
        self.setMyIndustryData('a')
        self.createIndustryInfo()
    
    def pressC(self):
        """Display Intelligent Industry Info"""
        self.enableLastButton('C')
        self.disableButton('C')
        self.setMyIndustryData('i')
        self.createIndustryInfo()
    
    def setMyIndustryData(self, prefix):
        """Based on prefix and key determine industry being modified"""
        abr = string.upper(prefix + self.key)
        for id, myIndustryData in self.myParent.industrydata.iteritems():
            if myIndustryData.abr == abr:
                self.myIndustryData = myIndustryData
                return
    
    def createIndustryInfo(self):
        """Create Industry Info based on id given"""
        self.setCurrentValue(0)
        self.setMinMax()
        self.writeIndustryName()
        self.createIndustrySim()
        self.writeIndustryDescription()
        self.writeIndustryCost()
    
    def setMinMax(self):
        """Set the min and max values that should be allowed"""
        currentIndustryNum = self.myParent.myIndustry[self.myIndustryData.id]
        oldIndustryNum = self.myParent.myOldIndustry[self.myIndustryData.id]
        self.setMinValue(-currentIndustryNum)
        if oldIndustryNum > currentIndustryNum:
            self.setMaxValue(oldIndustryNum-currentIndustryNum)
        elif self.isIndustryResearched() == 0:
            self.setMaxValue(0)
        else:
            max = self.getMaxFromFundsAvail()
            cityNum = (self.myParent.cities-self.myParent.citiesUsed)/self.myIndustryData.cities
            if max < cityNum:
                self.setMaxValue(max)
            else:
                self.setMaxValue(cityNum)
    
    def isIndustryResearched(self):
        return self.myParent.myTechDict[self.myIndustryData.techReq].complete
    
    def getMaxFromFundsAvail(self):
        systemFunds = self.getCurrentSystemFunds()
        industryCost = [self.myIndustryData.costCR, self.myIndustryData.costAL,
                        self.myIndustryData.costEC, self.myIndustryData.costIA]
        max = funcs.getPurchaseNumFromFunds(funds=systemFunds,
                                            cost=industryCost)
        return max
    
    def getCurrentSystemFunds(self):
        """Return [CR, AL, EC, IA] of current system funds"""
        e = self.myParent.myEmpireDict
        d = self.myParent.mySystemDict
        return [e['CR'], d['AL'],d['EC'],d['IA']]
    
    def writeIndustryName(self):
        """Create Industry Name"""
        if self.textIndustryName == None:
            self.textIndustryName = textonscreen.TextOnScreen(self.path, self.myIndustryData.name,
                                                          scale=0.04, font=5, parent=aspect2d)
            self.textIndustryName.writeTextToScreen(self.posInitX+0.29, 0, self.posInitY+0.31, 10)
            self.textIndustryName.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 7, 0.2)
            self.myWidgets.append(self.textIndustryName)
        else:
            self.textIndustryName.myText.setText(self.myIndustryData.name)
    
    def createIndustrySim(self):
        """Create Industry Picture"""
        if self.industrySim == None:
            self.industrySim = loader.loadModelCopy('%s/plane' % self.path)
            self.industrySim.setScale(0.08)
            self.industrySim.reparentTo(aspect2d)
            self.industrySim.setTransparency(1)
            tex = loader.loadTexture('%s/%s.png' % (self.path, self.key))
            self.industrySim.setTexture(tex, 0)
            self.industrySim.setPos(self.posInitX+0.35, 0, self.posInitY+0.17)
            self.myWidgets.append(self.industrySim)
        else:
            tex = loader.loadTexture('%s/%s.png' % (self.path, self.key))
            self.industrySim.setTexture(tex, 0)
    
    def writeIndustryDescription(self):
        """Create Industry Description"""
        if self.textIndustryDescription == None:
            self.textIndustryDescription = textonscreen.TextOnScreen(self.path, self.myIndustryData.description,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textIndustryDescription.writeTextToScreen(self.posInitX+0.29, 0, self.posInitY+0.09, 10)
            self.textIndustryDescription.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 0.2, 0.2)
            self.myWidgets.append(self.textIndustryDescription)
        else:
            self.textIndustryDescription.myText.setText(self.myIndustryData.description)
    
    def writeIndustryCost(self):
        """Create Industry Cost"""
        self.writeCRCost()
        self.writeALCost()
        self.writeECCost()
        self.writeIACost()
    
    def writeCRCost(self):
        value = '%d' % (self.myIndustryData.costCR)
        if self.textCR == None:
            self.textCR = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textCR.writeTextToScreen(self.posInitX+0.40, 0, self.posInitY+0.2, 10)
            self.textCR.setColor(globals.colors['guigreen'])
            self.myWidgets.append(self.textCR)
        else:
            self.textCR.myText.setText(value)
    
    def writeALCost(self):
        value = '%d' % (self.myIndustryData.costAL)
        if self.textAL == None:
            self.textAL = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textAL.writeTextToScreen(self.posInitX+0.40, 0, self.posInitY+0.2-0.02, 10)
            self.textAL.setColor(globals.colors['guiblue1'])
            self.myWidgets.append(self.textAL)
        else:
            self.textAL.myText.setText(value)
    
    def writeECCost(self):
        value = '%d' % (self.myIndustryData.costEC)
        if self.textEC == None:
            self.textEC = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textEC.writeTextToScreen(self.posInitX+0.40, 0, self.posInitY+0.2-0.04, 10)
            self.textEC.setColor(globals.colors['guiyellow'])
            self.myWidgets.append(self.textEC)
        else:
            self.textEC.myText.setText(value)
    
    def writeIACost(self):
        value = '%d' % (self.myIndustryData.costIA)
        if self.textIA == None:
            self.textIA = textonscreen.TextOnScreen(self.path, value,
                                                          scale=0.03, font=5, parent=aspect2d)
            self.textIA.writeTextToScreen(self.posInitX+0.40, 0, self.posInitY+0.2-0.06, 10)
            self.textIA.setColor(globals.colors['guired'])
            self.myWidgets.append(self.textIA)
        else:
            self.textIA.myText.setText(value)
    
    def pressS(self):
        """Submit value to server"""
        self.myParent.mode.modifyIndustry(self.myParent.mySystemDict['id'], self.currentValue, self.myIndustryData.id)
        self.disableButton('S')