# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# systemmenu.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This sub menu allows player to decide what sub actions to command of a system
# in map mode
# ---------------------------------------------------------------------------
import string
from rootbutton import RootButton
from anw.gui import systemindustry, modifyindustry, cityindustry
from anw.gui import futureindustry, tradevalue, systemresources, mibuildmarines
from anw.gui import buttonlist, shipyardmenu, shipyardbuildships, mimenu
from anw.gui import shipyardrepairships, shipyardupgradeships, mirepairmarines, miupgrademarines
from anw.gui import marketsystemsellvalue, systemmarketmenu, submitbutton
from anw.func import globals, funcs

class SystemMenu(RootButton):
    """A System Menu Allows player to decide sub actions on a system in map mode"""
    def __init__(self, path, mySystemDict):
        RootButton.__init__(self, path, x=-0.26, y=0.08, name='system')
        self.allKeys = ['1','2','3','5','6']
        self.mySystemDict = mySystemDict
        self.myText = None
        self.disableButtonTime = -1
        self.disableButtonIgnore = []
        self.id = ''
        self.font = loader.loadFont('%s/star5' % self.path)
        self.newtradelist = None
        self.cityindustrygui = None
        self.systemindustrygui = None
        self.modifyindustrygui = None
        self.systemresourcesgui = None
        self.shipyardbuildshipsgui = None
        self.shipyardrepairshipsgui = None
        self.shipyardupgradeshipsgui = None
        self.mibuildmarinesgui = None
        self.mirepairmarinesgui = None
        self.miupgrademarinesgui = None
        self.tradevaluegui = None
        self.shipyardmenu = None
        self.systemmarketmenu = None
        self.mimenu = None
        self.marketsystemsellgui = None
        self.marketsystembuygui = None
        self.marketorderslist = None
        self.cancelMarketOrderButton = None
        self.createTitle()
    
    def createMIMenu(self):
        """Create the Military Installation Menu which calls other Guis as needed"""
        self.mimenu = mimenu.MIMenu(self.path)
        self.mimenu.setMyMode(self.mode)
        self.myWidgets.append(self.mimenu)
        
    def createShipyardMenu(self):
        """Create the Shipyard Menu which calls other Guis as needed"""
        self.shipyardmenu = shipyardmenu.ShipyardMenu(self.path)
        self.shipyardmenu.setMyMode(self.mode)
        self.myWidgets.append(self.shipyardmenu)
    
    def createSystemMarketMenu(self):
        """Create the various market choices sub menu under market gui"""
        self.systemmarketmenu = systemmarketmenu.SystemMarketMenu(self.path, self.mySystemDict)
        self.systemmarketmenu.setMyMode(self.mode)
        self.systemmarketmenu.createGalaxyPrices()
        self.systemmarketmenu.disableMarketButtons()
        self.myWidgets.append(self.systemmarketmenu)
        
    def createTitle(self):
        self.createTitleCard('systemTitle','Choose Management Section:',
                         30,self.posInitX-0.04,self.posInitY+0.07)
        
    def createButtons(self):
        """Create all Buttons"""
        x = 0
        for key in ['1','2','3','4','5','6']:
            buttonPosition = ((self.posInitX+x*.10),0,(self.posInitY))
            self.createButton(key, buttonPosition)
            x += 1
            
    def press1(self):
        """Enable City Management"""
        self.clearSubWidgets()
        self.resetSystem()
        self.enableLastButton('1')
        self.disableButton('1')
        self.createSystemIndustryGui()
        self.createCityIndustryGui()
        self.mode.zoomInCamera()
        self.mode.game.app.disableMouseCamControl()
        self.mode.enableMouseCamControl=0
        
    def press2(self):
        """Enable Industry Management"""
        self.clearSubWidgets()
        self.resetSystem()
        self.enableLastButton('2')
        self.disableButton('2')
        self.createSystemIndustryGui()
        self.createFutureIndustryBars()
        self.createModifyIndustryGui()
        self.mode.zoomInCamera()
        self.mode.game.app.disableMouseCamControl()
        self.mode.enableMouseCamControl=0
    
    def press3(self):
        """Enable Trade Management"""
        self.mode.game.app.enableMouseCamControl()
        self.mode.enableMouseCamControl=1
        self.clearSubWidgets()
        self.resetSystem()
        self.createNewTradeList()
        self.mode.setCanSelectFlag('creatingTradeRoute')
        self.enableLastButton('3')
        self.disableButton('3')
        self.mode.zoomOutCamera()

    def press4(self):
        """Enable Ship Management"""
        self.clearSubWidgets()
        self.resetSystem()
        self.enableLastButton('4')
        self.disableButton('4')
        self.createMarketOrdersList()
        self.createSystemMarketMenu()
        if self.cancelMarketOrderButton != None:
            self.removeMyWidget(self.cancelMarketOrderButton)
            self.cancelMarketOrderButton = None
        self.mode.zoomInCamera()
        self.mode.game.app.disableMouseCamControl()
        self.mode.enableMouseCamControl=0
        
    def press5(self):
        """Enable Ship Management"""
        self.clearSubWidgets()
        self.resetSystem()
        self.enableLastButton('5')
        self.disableButton('5')
        self.createShipyardMenu()
        self.mode.zoomInCamera()
        self.mode.game.app.disableMouseCamControl()
        self.mode.enableMouseCamControl=0
    
    def press6(self):
        """Enable Marine Management"""
        self.clearSubWidgets()
        self.resetSystem()
        self.enableLastButton('6')
        self.disableButton('6')
        self.createMIMenu()
        self.mode.zoomInCamera()
        self.mode.game.app.disableMouseCamControl()
        self.mode.enableMouseCamControl=0
    
    def createNewTradeList(self):
        """Show list of systems that can be traded with"""
        x = self.posInitX-0.7
        y = self.posInitY+0.4
        self.newtradelist = buttonlist.ButtonList(self.path, 'Choose System to Trade With:', width=0.5, height=0.5)
        self.newtradelist.setMyPosition(x+0.27,y-0.3)
        self.newtradelist.setMyMode(self)
        self.newtradelist.setOnClickMethod('createTradeValueGui')
        self.myWidgets.append(self.newtradelist)
        self.populateNewTradeList()
    
    def populateNewTradeList(self):
        """Fill the newtradelist with systems that can be traded with"""
        mySystemTradeDict = self.getSystemTradeData()
        self.newtradelist.myScrolledList.clear()
        for systemID, systemName in mySystemTradeDict.iteritems():
            mySystem = self.mode.game.allSystems[systemID]
            name = funcs.getSystemName(mySystem)
            color = self.mode.game.allEmpires[mySystem['myEmpireID']]['color1']
            self.newtradelist.myScrolledList.addItem(text=name, 
                                                     extraArgs=systemID, textColorName=color)
    
    def createMarketOrdersList(self):
        """Show list market orders for this system this round"""
        x = self.posInitX+0.3
        y = self.posInitY-0.65
        self.marketorderslist = buttonlist.ButtonList(self.path, 'Current Market Orders This Turn:', width=1.1, height=0.6)
        self.marketorderslist.setMyPosition(x,y)
        self.marketorderslist.setMyMode(self)
        self.marketorderslist.setOnClickMethod('createCancelMarketOrderButton')
        self.myWidgets.append(self.marketorderslist)
        self.populateMarketOrderList()
        
    def createCancelMarketOrderButton(self, orderID, index, button):
        if self.marketorderslist.myScrolledList.getNumItems() > 0:
            if self.cancelMarketOrderButton == None:
                self.cancelMarketOrderButton = submitbutton.SubmitToCancelMarketOrderButton(self.path, x=self.posInitX+0.62, y=self.posInitY-0.97,orderID=orderID)
                self.cancelMarketOrderButton.setMyMode(self.mode)
                self.myWidgets.append(self.cancelMarketOrderButton)
        else:
            self.removeMyWidget(self.cancelMarketOrderButton)
            self.cancelMarketOrderButton = None        
        
    def cancelMarketOrder(self, orderID):
        """Cancel Market Order Selected"""
        self.mode.submitCancelMarketOrder(orderID)
        self.press4()
        
    def createTradeValueGui(self, systemID, index, button):
        """Show System that is to be traded with, create Trade Gui"""
        tradeKey = '%s-%s-REG' % (self.mySystemDict['id'], systemID)
        if tradeKey in self.mode.game.tradeRoutes.keys():
            myTradeRoute = self.mode.traderoutes[tradeKey]
            self.mode.clearAllCanSelectFlags()
            self.mode.traderoutesSelected(myTradeRoute, 1)
            return
            
        if self.tradevaluegui != None:
            self.tradevaluegui.destroy()
        mySystem = self.mode.systems[systemID]
        self.mode.playSound('beep01')
        if self.mode.setMySelector2(mySystem.sim.getX(), mySystem.sim.getY(), mySystem.sim.getZ(), scale=2.2):
            toSystemDict = self.mode.game.allSystems[systemID]
            self.tradevaluegui = tradevalue.TradeValue(self.path, self.mySystemDict, toSystemDict, None)
            self.tradevaluegui.setMyMode(self.mode)
            self.myWidgets.append(self.tradevaluegui)        
        
    def populateMarketOrderList(self):
        """Fill the market order list with current market orders"""
        mySystemTradeDict = self.getSystemTradeData()
        self.marketorderslist.myScrolledList.clear()
        for id, marketDict in self.mode.game.marketOrders.iteritems():
            if marketDict['type'] == 'sell':
                price = marketDict['min']
            else:
                price = marketDict['max']
            name = '%s to %s %d %s AT %d CREDITS' % (self.mode.game.allSystems[marketDict['system']]['name'],
                                                                string.upper(marketDict['type']),
                                                                marketDict['amount'],
                                                                marketDict['value'],
                                                                price)
            self.marketorderslist.myScrolledList.addItem(text=name, extraArgs=id)
            
    def getSystemTradeData(self):
        """Return a dictionary of Systems that can trade with this System"""
        myEmpireDict = self.mode.game.myEmpire
        d = {}
        for systemID in (self.mySystemDict['connectedSystems'] + self.mySystemDict['warpGateSystems']):
            systemDict = self.mode.game.allSystems[systemID]
            if systemDict['myEmpireID'] == myEmpireDict['id'] or globals.diplomacy[myEmpireDict['diplomacy'][systemDict['myEmpireID']]['diplomacyID']]['trade'] == 1:
                d[systemID] = systemDict['name']
        return d
    
    def clearSubWidgets(self):
        """Remove all widgets except the systemmenu buttons"""
        self.destroy()
        self.createButtons()
        self.createTitle()
    
    def resetSystem(self):
        self.mode.selector2.setPos(-1,-1,-1)
        self.mode.centerCameraOnSim(self.mode.systems[self.mySystemDict['id']].sim)
        camera.setY(self.mode.zoomCameraDepth)
        self.mode.removeAllTasks()
        self.mode.cameraMoving = 0
    
    def createCityIndustryGui(self):
        """Create the city Industry Gui to allow for city industry focus modification"""
        self.cityindustrygui = cityindustry.CityIndustry(self.path, -1.25, 0.25, 'city', self.mySystemDict['id'],
                                                         self.mySystemDict['cityIndustry'])
        self.cityindustrygui.setMyMode(self.mode)
        self.myWidgets.append(self.cityindustrygui)
    
    def createSystemIndustryGui(self):
        """Create the System Industry Gui to display system industry info"""
        self.systemindustrygui = systemindustry.SystemIndustry(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata)
        self.systemindustrygui.setMyMode(self.mode)
        self.myWidgets.append(self.systemindustrygui)
        
    def createModifyIndustryGui(self):
        """Create the Modify Industry Gui"""
        self.modifyindustrygui = modifyindustry.ModifyIndustry(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.myTech, self.mode.game.industrydata, self.mode)
        self.modifyindustrygui.setMyMode(self.mode)
        self.myWidgets.append(self.modifyindustrygui)
    
    def createFutureIndustryBars(self):
        self.futureIndustryBars = futureindustry.futureIndustry(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata)
        self.futureIndustryBars.setMyMode(self.mode)
        self.myWidgets.append(self.futureIndustryBars)
    
    def createSystemMarketSellGui(self, resource):
        """Create the System Market Sell Gui"""
        self.marketsystemsellgui = marketsystemsellvalue.MarketSystemSellValue(self.path, self.mySystemDict, resource, self.mode.game.prices[resource])
        self.marketsystemsellgui.setMyMode(self.mode)
        self.myWidgets.append(self.marketsystemsellgui)
        
    def createSystemMarketBuyGui(self, resource):
        """Create the System Market Buy Gui"""
        self.marketsystembuygui = marketsystemsellvalue.MarketSystemBuyValue(self.path, self.mySystemDict, resource, self.mode.game.prices[resource])
        self.marketsystembuygui.setMyMode(self.mode)
        self.myWidgets.append(self.marketsystembuygui)
        
    def createBuildShipsGui(self):
        """Create the Build Ships Gui"""
        self.shipyardbuildshipsgui = shipyardbuildships.ShipyardBuildShips(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata, mode=self.mode)
        self.myWidgets.append(self.shipyardbuildshipsgui)
    
    def createRepairShipsGui(self):
        """Create the Repair Ships Gui"""
        self.shipyardrepairshipsgui = shipyardrepairships.ShipyardRepairShips(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata, mode=self.mode)
        self.myWidgets.append(self.shipyardrepairshipsgui)
    
    def createUpgradeShipsGui(self):
        """Create the Upgrade Ships Gui"""
        self.shipyardupgradeshipsgui = shipyardupgradeships.ShipyardUpgradeShips(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata, mode=self.mode)
        self.myWidgets.append(self.shipyardupgradeshipsgui)
        
    def createBuildMarinesGui(self):
        """Create the Build Marines Gui"""
        self.mibuildmarinesgui = mibuildmarines.MIBuildMarines(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata, mode=self.mode)
        self.myWidgets.append(self.mibuildmarinesgui)
    
    def createRepairMarinesGui(self):
        """Create the Repair Marines Gui"""
        self.mirepairmarinesgui = mirepairmarines.MIRepairMarines(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata, mode=self.mode)
        self.myWidgets.append(self.mirepairmarinesgui)
    
    def createUpgradeMarinesGui(self):
        """Create the Upgrade Marines Gui"""
        self.miupgrademarinesgui = miupgrademarines.MIUpgradeMarines(self.path, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata, mode=self.mode)
        self.myWidgets.append(self.miupgrademarinesgui)
    
    def createSystemResourcesGui(self):
        self.systemresourcesgui = systemresources.SystemResources(self.path, -0.9, 0.9, self.mySystemDict, self.mode.game.myEmpire,
                                                               self.mode.game.industrydata)
        self.myWidgets.append(self.systemresourcesgui)
    
if __name__ == "__main__":
    mySystemMenu = SystemMenu('media', {})
    run()