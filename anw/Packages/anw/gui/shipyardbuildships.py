# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipyardbuildships.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui allows user to build ships from existing ship designs
# ---------------------------------------------------------------------------
import string
from anw.gui import rootsystem, valuebar, systemresources
from anw.gui import designinfo, buttonlist, shipinfo, shipyardscrollvalue
from anw.war import ship, captain
from anw.func import globals, funcs

class ShipyardBuildShips(rootsystem.RootSystem):
    """The System Shipyard Build Ships Gui"""
    def __init__(self, path, mySystemDict, myEmpireDict, industrydata, mode):
        rootsystem.RootSystem.__init__(self, path, -0.9, 0.66, mySystemDict,
                                       myEmpireDict, industrydata)
        self.setMyMode(mode)
        self.enableMouseCamControl = 1
        self.game = self.mode.game
        self.cadetsNeeded = 0
        self.cadetsAvailable = None
        self.availSYC = None
        self.currentResourceBars = None
        self.shipdesignList = None
        self.shipbuildList = None
        self.shipInfo = None
        self.designInfo = None
        self.myShipDesign = None
        self.scrollvaluegui = None
        
        self.createMySystemResources()
        self.createShipDesignList()
        self.createShipBuildList()
    
    def createScrollValue(self, id, min, max):
        """Create the scrollValue gui to allow for ship build/cancel orders"""
        self.removeMyWidget(self.scrollvaluegui)
        if min < 0:
            addShips = 0
            y = -0.56
        else:
            addShips = 1
            y = 0.17
        self.scrollvaluegui = shipyardscrollvalue.ShipyardScrollValue(self.path, -0.6, y, 'scroll', addShips, myParent=self)
        self.scrollvaluegui.setMyMode(self.mode)
        self.scrollvaluegui.setMaxValue(max)
        self.scrollvaluegui.setMinValue(min)
        self.scrollvaluegui.setID(id)
        self.myWidgets.append(self.scrollvaluegui)
        
    def createDesignInfo(self):
        """Display Design Info"""
        self.removeDesignInfo()
        self.designInfo = designinfo.DesignInfo(self.path, self.mode.game.myEmpireID,
                                                self.myShipDesign, -0.20, 0.84)
        self.designInfo.setMyMode(self.mode)
        self.designInfo.writeAttributes()
        self.myWidgets.append(self.designInfo)

    def removeDesignInfo(self):
        if self.designInfo != None:
            self.removeMyWidget(self.designInfo)
        
    def createMySystemResources(self):
        self.mySystemResources = systemresources.SystemResources(self.path, self.posInitX, self.posInitY+0.14, 
                                                                 self.mySystemDict, self.myEmpireDict, self.industrydata)
        self.myWidgets.append(self.mySystemResources)

    def createCadetsAvailable(self):
        """Display Cadets currently ready to pilot new ships"""
        cadetsUsed = self.mySystemDict['fleetCadets'] - self.cadetsNeeded
        if cadetsUsed < 0:
            cadetsUsed = 0
        x = self.posInitX+0.55-(1*self.xOffset)
        y = self.posInitY
        self.cadetsAvailable = valuebar.ValueBar(self.path, scale=self.scale,
                                                 extraText='CADETS AVAILABLE')
        self.cadetsAvailable.setMyPosition(x,0,y)
        self.cadetsAvailable.setColor(globals.colors['guiwhite'])
        self.cadetsAvailable.setMyValues(cadetsUsed,self.mySystemDict['fleetCadets'])
        self.myWidgets.append(self.cadetsAvailable)
    
    def createAvailSYC(self):
        """Display Available Shipyard Capacity"""
        remaining = self.mySystemDict['availSYC'] - self.mySystemDict['usedSYC']
        x = self.posInitX+0.55-(1*self.xOffset)
        y = self.posInitY-0.04
        self.availSYC = valuebar.ValueBar(self.path, scale=self.scale,
                                                 extraText='SHIPYARD CAPACITY')
        self.availSYC.setMyPosition(x,0,y)
        self.availSYC.setColor(globals.colors['guiwhite'])
        self.availSYC.setMyValues(remaining,self.mySystemDict['availSYC'])
        self.myWidgets.append(self.availSYC)
        
    def createShipDesignList(self):
        """List all Available Ship Designs"""
        text = 'Choose a Ship Design to Build From:'
        self.shipdesignList = buttonlist.ButtonList(self.path, text, width=0.6, height=0.55)
        self.shipdesignList.setMyPosition(-0.96,0.23)
        self.shipdesignList.setMyMode(self)
        self.shipdesignList.setOnClickMethod('shipDesignSelected')
        self.myWidgets.append(self.shipdesignList)
        self.populateShipDesignList()
    
    def createShipBuildList(self):
        """List all Ships to be built"""
        text = 'Choose a Build Order to Reduce:'
        self.shipbuildList = buttonlist.ButtonList(self.path, text, width=0.6, height=0.55)
        self.shipbuildList.setMyPosition(-0.96,-0.5)
        self.shipbuildList.setMyMode(self)
        self.shipbuildList.setOnClickMethod('shipOrderSelected')
        self.myWidgets.append(self.shipbuildList)
        self.populateShipBuildList()
        self.createCadetsAvailable()
        self.createAvailSYC()
    
    def populateShipDesignList(self):
        """Fill the list with Ship designs"""
        for shipDesignID in funcs.sortStringList(self.mode.game.shipDesigns.keys()):
            myShipDesign = self.mode.game.shipDesignObjects[shipDesignID]
            if myShipDesign.hasAllTech == 1:
                self.shipdesignList.myScrolledList.addItem(text=myShipDesign.name, extraArgs=shipDesignID)
    
    def populateShipBuildList(self):
        """Fill the list with Ship Build Orders"""
        for industryID in funcs.sortStringList(self.mode.game.myEmpire['industryOrders'].keys()):
            myOrder = self.mode.game.myEmpire['industryOrders'][industryID]
            if myOrder['type'] == 'Add Ship' and myOrder['round'] == self.mode.game.currentRound and myOrder['system'] == self.mySystemDict['id']:
                (amount,shipDesignID) = string.split(myOrder['value'],'-')
                self.cadetsNeeded += int(amount)
                myShipDesign = self.mode.game.shipDesignObjects[shipDesignID]
                self.shipbuildList.myScrolledList.addItem(text='Add %s %s' % (amount, myShipDesign.name), extraArgs=industryID)
    
    def shipOrderSelected(self, orderID, index, button):
        """Ship Order Selected for cancellation/modification"""
        self.mode.playSound('beep01')
        myOrder = self.mode.game.myEmpire['industryOrders'][orderID]
        (amount, designID) = string.split(myOrder['value'], '-')
        self.createShipDesignInfo(designID)
        amount = int(amount)
        min = -amount
        self.createScrollValue(orderID, min, 0)
    
    def shipDesignSelected(self, designID, index, button):
        """Fill in Ship Design stats"""
        self.mode.playSound('beep01')
        self.createShipDesignInfo(designID)
        max = self.getMaxFromFundsAvail()
        max2 = self.getMaxFromAvailSYC()
        if max2 < max:
            max = max2
        self.createScrollValue(designID, 0, max)
    
    def getMaxFromAvailSYC(self):
        """Set Avail Ship purchased also based on Shipyard Capacity"""
        remaining = self.mySystemDict['availSYC'] - self.mySystemDict['usedSYC']
        spaceRequired = self.myShipDesign.getSYCRequired()
        max = remaining/spaceRequired
        return max
        
    def createShipDesignInfo(self, designID):
        """Show the ship design selected from ship design list or order list"""
        if self.mySystemDict['fleetCadets'] > 0:
            name = 'Fleet Cadet'
        else:
            name = 'Rookie Cadet'
        myCaptain = captain.Captain({'id':'999', 'name':name})
        self.myShipDesign = self.mode.game.shipDesignObjects[designID]
        myShip = ship.Ship({'id':'999', 'fromSystem':'999', 'empireID':self.mode.game.myEmpireID})
        myShip.setMyGalaxy(self.mode.game)
        myShip.setMyCaptain(myCaptain)
        myShip.setMyDesign(self.myShipDesign)
        myShip.setMyStatus()
        self.createShipInfo(myShip)
        self.createDesignInfo()
        
    def getMaxFromFundsAvail(self):
        systemFunds = self.getCurrentSystemFunds()
        shipDesignCost = [self.myShipDesign.costCR, self.myShipDesign.costAL,
                          self.myShipDesign.costEC, self.myShipDesign.costIA]
        max = funcs.getPurchaseNumFromFunds(funds=systemFunds,
                                            cost=shipDesignCost)
        return max
    
    def getCurrentSystemFunds(self):
        """Return [CR, AL, EC, IA] of current system funds"""
        e = self.myEmpireDict
        d = self.mySystemDict
        return [e['CR'], d['AL'],d['EC'],d['IA']]
    
    def createShipInfo(self, myShip):
        """Create the Ship Description GUI to allow for ship information in detail"""
        self.removeShipInfo()
        self.shipInfo = shipinfo.ShipInfo(self.path, myShip, 0.45, 0.84)
        self.shipInfo.setMyMode(self.mode)
        self.myWidgets.append(self.shipInfo)
        
    def removeShipInfo(self):
        if self.shipInfo != None:
            self.removeMyWidget(self.shipInfo)
    