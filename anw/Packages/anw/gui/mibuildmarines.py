# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# mibuildmarines.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui allows user to build marines from existing marine choices
# ---------------------------------------------------------------------------
import string
from anw.gui import rootsystem, valuebar, systemresources
from anw.gui import regimentinfo, buttonlist, miscrollvalue
from anw.func import globals, funcs

class MIBuildMarines(rootsystem.RootSystem):
    """The System Military Installation Build Marines Gui"""
    def __init__(self, path, mySystemDict, myEmpireDict, industrydata, mode):
        rootsystem.RootSystem.__init__(self, path, -0.9, 0.66, mySystemDict,
                                       myEmpireDict, industrydata)
        self.setMyMode(mode)
        self.enableMouseCamControl = 1
        self.game = self.mode.game
        self.cadetsNeeded = 0
        self.cadetsAvailable = None
        self.availMIC = None
        self.currentResourceBars = None
        self.regimentList = None
        self.regimentBuildList = None
        self.regimentInfo = None
        self.scrollvaluegui = None
        
        self.createMySystemResources()
        self.createRegimentList()
        self.createRegimentBuildList()
    
    def createScrollValue(self, id, min, max):
        """Create the scrollValue gui to allow for ship build/cancel orders"""
        self.removeMyWidget(self.scrollvaluegui)
        if min < 0:
            addRegiments = 0
            y = -0.56
        else:
            addRegiments = 1
            y = 0.17
        self.scrollvaluegui = miscrollvalue.MIScrollValue(self.path, -0.6, y, 'scroll', addRegiments, myParent=self)
        self.scrollvaluegui.setMyMode(self.mode)
        self.scrollvaluegui.setMaxValue(max)
        self.scrollvaluegui.setMinValue(min)
        self.scrollvaluegui.setID(id)
        self.myWidgets.append(self.scrollvaluegui)
        
    def createRegimentInfo(self, regimentDataID):
        """Display Selected Regiment Info"""
        self.removeRegimentInfo()
        myRegimentData = self.mode.game.regimentdata[regimentDataID]
        self.regimentInfo = regimentinfo.RegimentInfo(self.path, self.mode.game.myEmpireID, None,
                                                      myRegimentData, -0.20, 0.84)
        self.regimentInfo.setMyMode(self.mode)
        self.regimentInfo.writeAttributes()
        self.myWidgets.append(self.regimentInfo)

    def removeRegimentInfo(self):
        if self.regimentInfo != None:
            self.removeMyWidget(self.regimentInfo)
        
    def createMySystemResources(self):
        self.mySystemResources = systemresources.SystemResources(self.path, self.posInitX, self.posInitY+0.14, 
                                                                 self.mySystemDict, self.myEmpireDict, self.industrydata)
        self.myWidgets.append(self.mySystemResources)

    def createCadetsAvailable(self):
        """Display Cadets currently ready to pilot new ships"""
        cadetsUsed = self.mySystemDict['armyCadets'] - self.cadetsNeeded
        if cadetsUsed < 0:
            cadetsUsed = 0
        x = self.posInitX+0.55-(1*self.xOffset)
        y = self.posInitY
        self.cadetsAvailable = valuebar.ValueBar(self.path, scale=self.scale,
                                                 extraText='CADETS AVAILABLE')
        self.cadetsAvailable.setMyPosition(x,0,y)
        self.cadetsAvailable.setColor(globals.colors['guiwhite'])
        self.cadetsAvailable.setMyValues(cadetsUsed,self.mySystemDict['armyCadets'])
        self.myWidgets.append(self.cadetsAvailable)
    
    def createAvailMIC(self):
        """Display Available MI Capacity"""
        remaining = self.mySystemDict['availMIC'] - self.mySystemDict['usedMIC']
        x = self.posInitX+0.55-(1*self.xOffset)
        y = self.posInitY-0.04
        self.availMIC = valuebar.ValueBar(self.path, scale=self.scale,
                                                 extraText='MILITARY INST CAPACITY')
        self.availMIC.setMyPosition(x,0,y)
        self.availMIC.setColor(globals.colors['guiwhite'])
        self.availMIC.setMyValues(remaining,self.mySystemDict['availMIC'])
        self.myWidgets.append(self.availMIC)
        
    def createRegimentList(self):
        """List all Available Regiments"""
        text = 'Choose a Marine Regiment Type to Recruit:'
        self.regimentList = buttonlist.ButtonList(self.path, text, width=0.6, height=0.55)
        self.regimentList.setMyPosition(-0.96,0.23)
        self.regimentList.setMyMode(self)
        self.regimentList.setOnClickMethod('regimentTypeSelected')
        self.myWidgets.append(self.regimentList)
        self.populateRegimentList()
        self.regimentList.myScrolledList.scrollToBottom()
    
    def populateRegimentList(self):
        """Fill the list with available regiments"""
        for regimentdataID in funcs.sortStringList(self.mode.game.regimentdata.keys()):
            myRegimentData = self.mode.game.regimentdata[regimentdataID]
            if (self.mode.game.myTech[myRegimentData.techReq].complete == 1 and 
                myRegimentData.abr[2] != 'L'):
                self.regimentList.myScrolledList.addItem(text=myRegimentData.name, extraArgs=regimentdataID)
        
    def createRegimentBuildList(self):
        """List all Regiments to be built"""
        text = 'Choose a Build Order to Reduce:'
        self.regimentBuildList = buttonlist.ButtonList(self.path, text, width=0.6, height=0.55)
        self.regimentBuildList.setMyPosition(-0.96,-0.5)
        self.regimentBuildList.setMyMode(self)
        self.regimentBuildList.setOnClickMethod('regimentOrderSelected')
        self.myWidgets.append(self.regimentBuildList)
        self.populateRegimentBuildList()
        self.createCadetsAvailable()
        self.createAvailMIC()    
    
    def populateRegimentBuildList(self):
        """Fill the list with Regiment Build Orders"""
        for industryID in funcs.sortStringList(self.mode.game.myEmpire['industryOrders'].keys()):
            myOrder = self.mode.game.myEmpire['industryOrders'][industryID]
            if myOrder['type'] == 'Add Regiment' and myOrder['round'] == self.mode.game.currentRound and myOrder['system'] == self.mySystemDict['id']:
                (amount,regimentDataID) = string.split(myOrder['value'],'-')
                self.cadetsNeeded += int(amount)
                myRegimentData = self.mode.game.regimentdata[regimentDataID]
                self.regimentBuildList.myScrolledList.addItem(text='Add %s %s' % (amount, myRegimentData.name), extraArgs=industryID)
    
    def regimentOrderSelected(self, orderID, index, button):
        """Regiment Order Selected for cancellation/modification"""
        self.mode.playSound('beep01')
        myOrder = self.mode.game.myEmpire['industryOrders'][orderID]
        (amount, regimentDataID) = string.split(myOrder['value'], '-')
        self.createRegimentInfo(regimentDataID)
        amount = int(amount)
        min = -amount
        self.createScrollValue(orderID, min, 0)
    
    def regimentTypeSelected(self, regimentDataID, index, button):
        """Fill in regiment stats"""
        self.mode.playSound('beep01')
        self.createRegimentInfo(regimentDataID)
        max = self.getMaxFromFundsAvail(regimentDataID)
        max2 = self.getMaxFromAvailMIC()
        if max2 < max:
            max = max2
        self.createScrollValue(regimentDataID, 0, max)
    
    def getMaxFromAvailMIC(self):
        """Set Avail Regiment purchased also based on MI Capacity"""
        remaining = self.mySystemDict['availMIC'] - self.mySystemDict['usedMIC']
        spaceRequired = 100.0
        max = remaining/spaceRequired
        return max
        
    def getMaxFromFundsAvail(self, regimentDataID):
        myRegimentData = self.mode.game.regimentdata[regimentDataID]
        systemFunds = self.getCurrentSystemFunds()
        myCost = [myRegimentData.costCR, myRegimentData.costAL,
                          myRegimentData.costEC, myRegimentData.costIA]
        max = funcs.getPurchaseNumFromFunds(funds=systemFunds,
                                            cost=myCost)
        return max
    
    def getCurrentSystemFunds(self):
        """Return [CR, AL, EC, IA] of current system funds"""
        e = self.myEmpireDict
        d = self.mySystemDict
        return [e['CR'], d['AL'],d['EC'],d['IA']]
    