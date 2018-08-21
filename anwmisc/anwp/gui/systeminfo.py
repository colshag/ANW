# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# systeminfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all Relevant System Information, or a System Report on
# the man galactic map
# ---------------------------------------------------------------------------
import string

import pyui
import guibase
import anwp.func.globals

class SystemInfoFrame(guibase.BaseInfoFrame):
    """Displays System Information"""  
    def __init__(self, mode, app, title='Solar System Information'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(TabbedInfoPanel(self))
    
    def signal(self, subject):
        """New subject calling frame"""
        self.systemEntity = subject
        if self.systemEntity.systemID <> self.currentID:
            # different system populate panel
            self.currentID = self.systemEntity.systemID
            
            # Check if System owned by player
            if self.systemEntity.myEmpireDict['id'] == self.mode.game.myEmpireID:
                self.setPanel(TabbedInfoPanel(self))
            else:
                self.setPanel(OtherSystemInfoPanel(self))                
            
            # populate panel
            self.panel.populate(self.systemEntity.myEmpireDict, self.systemEntity.mySystemDict)

class TabbedInfoPanel(pyui.widgets.TabbedPanel):
    """This Panel Contains any SubPanels associated with the System"""
    def __init__(self, frame):
        pyui.widgets.TabbedPanel.__init__(self)
        self.addPanel('SYSTEM', SystemInfoPanel(frame))
        self.addPanel('TRADE', TradeInfoPanel(frame))
        self.addPanel('MARKET', MarketInfoPanel(frame))
        self.addPanel('RADAR', OtherSystemInfoPanel(frame))
    
    def populate(self, myEmpireDict, mySystemDict):
        """When asked to populate the Panel will populate its sub panels"""
        self.myEmpireDict = myEmpireDict
        self.mySystemDict = mySystemDict
        self.getPanel(1).populate(myEmpireDict, mySystemDict)
        self.getPanel(2).populate(myEmpireDict, mySystemDict)
        self.getPanel(3).populate(myEmpireDict, mySystemDict)
        self.getPanel(0).populate(myEmpireDict, mySystemDict)
    
class SystemInfoPanel(guibase.BasePanel):
    """Panel for information about Systems that player owns:
    This would include detailed information about system"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 2
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # system Info
        self.pctSystem = pyui.widgets.Picture('')
        self.addChild(self.pctSystem, (0, 0, 1, 3))
        self.pctEmpire = pyui.widgets.Picture('')
        self.addChild(self.pctEmpire, (1, 0, 1, 3))
        self.lblOwnedBy = pyui.widgets.Label(text='SYSTEM OWNER:', type=2)
        self.addChild(self.lblOwnedBy, (2, 1, 2, 1))
        self.lblEmpireName = pyui.widgets.Label(text='')
        self.addChild(self.lblEmpireName, (2, 2, 2, 1))
        
        # system Resources
        n = 4
        self.lblResLegend = pyui.widgets.Label(text='SYSTEM RESOURCES:', type=1)
        self.addChild(self.lblResLegend, (0, n, 4, 1))
        self.pctCR = pyui.widgets.Picture(self.symbolCR)
        self.pctAL = pyui.widgets.Picture(self.symbolAL)
        self.pctEC = pyui.widgets.Picture(self.symbolEC)
        self.pctIA = pyui.widgets.Picture(self.symbolIA)
        self.addChild(self.pctCR, (0, n+1, 1, 1))
        self.addChild(self.pctAL, (1, n+1, 1, 1))
        self.addChild(self.pctEC, (2, n+1, 1, 1))
        self.addChild(self.pctIA, (3, n+1, 1, 1))
        self.lblTotalAL = pyui.widgets.Label('0', type=1)
        self.lblTotalAL.setColor(anwp.func.globals.colors['blue'])
        self.lblTotalEC = pyui.widgets.Label('0', type=1)
        self.lblTotalEC.setColor(anwp.func.globals.colors['yellow'])
        self.lblTotalIA = pyui.widgets.Label('0', type=1)
        self.lblTotalIA.setColor(anwp.func.globals.colors['red'])
        self.addChild(self.lblTotalAL, (1, n+2, 1, 1))
        self.addChild(self.lblTotalEC, (2, n+2, 1, 1))
        self.addChild(self.lblTotalIA, (3, n+2, 1, 1))
        self.lblProdCR = pyui.widgets.Label('0', type=2)
        self.lblProdCR.setColor(anwp.func.globals.colors['dkgreen'])
        self.lblProdAL = pyui.widgets.Label('0', type=2)
        self.lblProdAL.setColor(anwp.func.globals.colors['dkblue'])
        self.lblProdEC = pyui.widgets.Label('0', type=2)
        self.lblProdEC.setColor(anwp.func.globals.colors['dkyellow'])
        self.lblProdIA = pyui.widgets.Label('0', type=2)
        self.lblProdIA.setColor(anwp.func.globals.colors['blood'])
        self.addChild(self.lblProdCR, (0, n+3, 1, 1))
        self.addChild(self.lblProdAL, (1, n+3, 1, 1))
        self.addChild(self.lblProdEC, (2, n+3, 1, 1))
        self.addChild(self.lblProdIA, (3, n+3, 1, 1))
        
        # system Cities
        n = n+5
        self.lblCitiesLegend = pyui.widgets.Label(text='SYSTEM CITIES:', type=1)
        self.addChild(self.lblCitiesLegend, (0, n, 2, 1))
        self.btnAllCities = pyui.widgets.Button('Select All', self.onAllCities)
        self.addChild(self.btnAllCities, (2, n, 2, 1))
        self.lblCityLegend2 = pyui.widgets.Label(text='(Name - Focus - Status)', type=2)
        self.addChild(self.lblCityLegend2, (0, n+1, 4, 1))
        self.lstCities = pyui.widgets.ListBox(self.onCitySelected, None, 100, 100, 1)
        self.addChild(self.lstCities, (0, n+2, 4, 3))
        self.btnAddCity = pyui.widgets.Button('Add City', self.onAddCity)
        self.addChild(self.btnAddCity, (0, n+5, 2, 1))
        self.btnChangeCity = pyui.widgets.Button('Change Focus', self.onChangeCity)
        self.addChild(self.btnChangeCity, (2, n+5, 2, 1))
        
        # system Industry
        n = n+7
        self.lblIndustryLegend = pyui.widgets.Label(text='SYSTEM INDUSTRY:', type=1)
        self.addChild(self.lblIndustryLegend, (0, n, 4, 1))
        self.lblIndustryLegend2 = pyui.widgets.Label(text='(Industry Type - Cities Req)', type=2)
        self.addChild(self.lblIndustryLegend2, (0, n + 1, 4, 1))
        self.lstIndustry = pyui.widgets.ListBox(self.onIndustrySelected, None, 100, 100, 1)
        self.addChild(self.lstIndustry, (0, n+2, 4, 3+x))
        self.btnAddIndustry = pyui.widgets.Button('Add', self.onAddIndustry)
        self.addChild(self.btnAddIndustry, (0, n+5+x, 1, 1))
        self.btnRemoveIndustry = pyui.widgets.Button('Remove', self.onRemoveIndustry)
        self.addChild(self.btnRemoveIndustry, (1, n+5+x, 1, 1))
        self.btnUpgradeIndustry = pyui.widgets.Button('Upgrade', self.onUpgradeIndustry)
        self.addChild(self.btnUpgradeIndustry, (2, n+5+x, 1, 1))
        
        # system Orders
        n = n+7+x
        self.buildOrders(n,x,'CURRENT SYSTEM ORDERS:',3)
        
        # pack widgets
        self.pack

    def populate(self, myEmpireDict, mySystemDict):
        """Populate frame with new data"""
        self.myEmpireDict = myEmpireDict
        self.mySystemDict = mySystemDict
        # disable buttons
        self.btnChangeCity.disable()
        self.btnRemoveIndustry.disable()
        self.btnUpgradeIndustry.disable()
        self.btnCancelOrder.disable()
        
        # load resources
        try:
            myEmpirePict = '%s%s.png' % (self.frame.app.simImagePath, myEmpireDict['imageFile'])
            mySystemPict = '%s%s.png' % (self.frame.app.simImagePath, mySystemDict['imageFile'])
            myProdCR = mySystemDict['prodCR']
            myProdAL = mySystemDict['prodAL']
            myProdEC = mySystemDict['prodEC']
            myProdIA = mySystemDict['prodIA']
            myAvailAL = mySystemDict['AL']
            myAvailEC = mySystemDict['EC']
            myAvailIA = mySystemDict['IA']
            myCities = self.buildCityData(mySystemDict['myCities'])
            myIndustry = self.buildIndustryData(mySystemDict['myIndustry'])
            myOrders = self.buildIndustryOrderData(myEmpireDict['industryOrders'])
        except:
            # this allows for testing panel outside game
            myEmpirePict = self.testImagePath + 'empire1.png'
            mySystemPict = self.testImagePath + 'star8.png'
            myProdCR = self.testAmount
            myProdAL = self.testAmount
            myProdEC = self.testAmount
            myProdIA = self.testAmount
            myAvailAL = self.testAmount
            myAvailEC = self.testAmount
            myAvailIA = self.testAmount
            myCities = self.testDict
            myIndustry = self.testDict
            myOrders = self.testDict
        
        mySystemTotalCities = mySystemDict['cities']
        mySystemUsedCities = mySystemDict['citiesUsed']
        
        # system Info
        self.frame.title = '%s: (%d/%d) Cities Employed' % (mySystemDict['name'], mySystemUsedCities, mySystemTotalCities)
        self.pctSystem.setFilename(mySystemPict)
        self.pctEmpire.setFilename(myEmpirePict)
        self.lblEmpireName.setText('  %s' % myEmpireDict['name'])
        self.lblEmpireName.setColor(anwp.func.globals.colors[myEmpireDict['color1']])
        
        # system Resources
        self.lblTotalAL.setText(str(int(myAvailAL)))
        self.lblTotalEC.setText(str(int(myAvailEC)))
        self.lblTotalIA.setText(str(int(myAvailIA)))
        self.lblProdCR.setText(str(int(myProdCR)))
        self.lblProdAL.setText(str(int(myProdAL)))
        self.lblProdEC.setText(str(int(myProdEC)))
        self.lblProdIA.setText(str(int(myProdIA)))
        
        # system Cities
        self.populateListbox(self.lstCities, myCities)
        
        # system Industry
        self.populateListbox(self.lstIndustry, myIndustry)
                
        # system Orders
        self.populateListbox(self.lstOrders, myOrders)
    
    def buildIndustryData(self, dIndustryData):
        """Take Industry data from Server and Transform into Form Friendly Data"""
        d = {}
        for id, dictIndustry in dIndustryData.iteritems():
            industryType = dictIndustry['industrytype']
            name = self.frame.mode.game.industrydata[industryType]['name']
            cities = self.frame.mode.game.industrydata[industryType]['cities']
            d[id] = '%s - %s' % (name, cities)
        return d
    
    def buildCityData(self, dCityData):
        """Take City Data from Server and Transform into Form Friendly Data"""
        d = {}
        for id, dictCity in dCityData.iteritems():
            if dictCity['state'] == 1:
                state = 'running'
            else:
                state = 'upgrading'
            d[id] = '%s - %s - %s' % (dictCity['name'], dictCity['resourceFocus'], state)
        return d
    
    def buildIndustryOrderData(self, dIndOrderData):
        """Take Industry Order Data from Server and Transform into Form Friendly Data"""
        d = {}
        for id, dIndOrder in dIndOrderData.iteritems():
            name = ''
            if dIndOrder['system'] == self.mySystemDict['id']:
                mySystemDict = self.frame.mode.game.allSystems[dIndOrder['system']]
                if dIndOrder['type'] == 'Add City':
                    name = 'ADD City (%s)' % (dIndOrder['value'])
                elif dIndOrder['type'] == 'Change City':
                    (cityID, resource) = string.split(dIndOrder['value'], '-')
                    name = 'Change City %s - (%s)' % (cityID, resource)
                elif dIndOrder['type'] == 'Add Industry':
                    (amount, type) = string.split(dIndOrder['value'], '-')
                    industryName = self.frame.mode.game.industrydata[type]['name']
                    name = 'ADD %s %s' % (amount, industryName)
                elif dIndOrder['type'] == 'Remove Industry':
                    type = mySystemDict['myIndustry'][dIndOrder['value']]['industrytype']
                    industryName = self.frame.mode.game.industrydata[type]['name']
                    name = 'REM %s%s' % (industryName, dIndOrder['value'])
                elif dIndOrder['type'] == 'Upgrade Industry':
                    type = mySystemDict['myIndustry'][dIndOrder['value']]['industrytype']
                    industryName = self.frame.mode.game.industrydata[type]['name']
                    name = 'UPG %s%s' % (industryName, dIndOrder['value'])
                if name <> '':
                    d[id] = name
        return d
    
    def onIndustrySelected(self, item):
        """Select item from List"""
        if self.lstIndustry.getMultiSelectedItems() == []:
            self.btnRemoveIndustry.disable()
            self.btnUpgradeIndustry.disable()
        else:
            self.enableButtons(self.lstIndustry, [self.btnRemoveIndustry, self.btnUpgradeIndustry])

    def onCitySelected(self, item):
        """Select item from List"""
        if self.lstCities.getMultiSelectedItems() == []:
            self.btnChangeCity.disable()
        else:
            self.enableButtons(self.lstCities, [self.btnChangeCity])
    
    def onAllCities(self, item):
        """Select All Cities from City List"""
        for key in self.lstCities.dSelected.keys():
            self.lstCities.dSelected[key] = 1
        self.lstCities.setDirty()
        self.enableButtons(self.lstCities, [self.btnChangeCity])
    
    def onAddCity(self, item):
        """Add a City"""
        self.frame.mode.createAddCityFrame(self.mySystemDict['id'], self.mySystemDict['name'])
    
    def onChangeCity(self, item):
        """Change City Resource Focus"""
        list = self.lstCities.getMultiSelectedItems()
        self.frame.mode.createChangeCityFrame(list, self.mySystemDict['id'], self.mySystemDict['name'])
    
    def onRemoveIndustry(self, item):
        """Set a Remove Industry Command on selected Industry"""
        self.frame.mode.removeIndustry(self.lstIndustry.getMultiSelectedItems(), self.mySystemDict['id'])
    
    def onUpgradeIndustry(self, item):
        """Set an Upgrade Industry Command on selected Industry"""
        self.frame.mode.upgradeIndustry(self.lstIndustry.getMultiSelectedItems(), self.mySystemDict['id'])
    
    def onAddIndustry(self, item):
        """Bring up the Add Industry Panel for system"""
        self.frame.mode.createAddIndustryFrame(self.mySystemDict['id'], self.mySystemDict['name'])
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if self.lstOrders.getMultiSelectedItems() == []:
            self.btnCancelOrder.disable()
        else:
            self.enableButtons(self.lstOrders, [self.btnCancelOrder])
    
    def onCancelOrder(self, item):
        """Set a Cancel Order Command on selected Order"""
        self.frame.mode.cancelIndustryOrder(self.lstOrders.getMultiSelectedItems(), self.mySystemDict['id'])

class TradeInfoPanel(guibase.BasePanel):
    """Panel for information about Inter-System Trade"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        x = (self.frame.app.height - 768) / (22 * 2)
        cells = 28 + (2 * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # add new trade route
        n = 1
        self.lblAddTrade = pyui.widgets.Label(text='ADD TRADE ROUTE FROM: *Hannah*', type=1)
        self.addChild(self.lblAddTrade, (0, n, 4, 1))
        self.lblChooseTrade = pyui.widgets.Label(text='Choose System to Trade With:', type=2)
        self.addChild(self.lblChooseTrade, (0, n+1, 4, 1))
        self.lstToSystem = pyui.widgets.ListBox(self.onToSystemSelected, None)
        self.addChild(self.lstToSystem, (0, n+2, 4, 6+x))
        self.lblResources = pyui.widgets.Label(text='Select Resources to Trade:', type=2)
        self.addChild(self.lblResources, (0, n+9+x, 4, 1))

        n = n + 10 + x
        self.lblAL = pyui.widgets.Label(text='Alloys(AL):', type=1)
        self.addChild(self.lblAL, (0, n, 2, 1))
        self.txtAL = pyui.widgets.NumberEdit('', 8, None, 0)
        self.addChild(self.txtAL, (2, n, 2, 1))
        
        self.lblEC = pyui.widgets.Label(text='Energy(EC):', type=1)
        self.addChild(self.lblEC, (0, n+1, 2, 1))
        self.txtEC = pyui.widgets.NumberEdit('', 8, None, 0)
        self.addChild(self.txtEC, (2, n+1, 2, 1))

        self.lblIA = pyui.widgets.Label(text='Arrays(IA):', type=1)
        self.addChild(self.lblIA, (0, n+2, 2, 1))
        self.txtIA = pyui.widgets.NumberEdit('', 8, None, 0)
        self.addChild(self.txtIA, (2, n+2, 2, 1))

        self.btnAddTradeRoute = pyui.widgets.Button('Always Trade', self.onAddTradeRoute)
        self.addChild(self.btnAddTradeRoute, (0, n+4, 2, 1))
        self.btnAddOneTimeTrade = pyui.widgets.Button('One Time Trade', self.onAddOneTimeTrade)
        self.addChild(self.btnAddOneTimeTrade, (2, n+4, 2, 1))
        self.btnTradeAllRoute = pyui.widgets.Button('Add Trade GEN Route', self.onTradeGenRoute)
        self.addChild(self.btnTradeAllRoute, (0, n+5, 4, 1))
        
        # system Orders
        n = n + 7
        self.lblTrade = pyui.widgets.Label(text='TRADE LIST FOR SYSTEM:', type=1)
        self.addChild(self.lblTrade, (0, n, 4, 1))
        self.lstTrade = pyui.widgets.ListBox(self.onTradeSelected, None, 100, 100, 1)
        self.addChild(self.lstTrade, (0, n+1, 4, 6+x))
        self.btnCancelTrade = pyui.widgets.Button('Cancel Trade Route', self.onCancelTrade)
        self.addChild(self.btnCancelTrade, (0, n+7+x, 3, 1))
        
        # pack widgets
        self.pack
    def populate(self, myEmpireDict, mySystemDict):
        """Populate frame with new data"""
        self.myEmpireDict = myEmpireDict
        self.mySystemDict = mySystemDict
        
        # disable buttons
        self.btnAddTradeRoute.disable()
        self.btnCancelTrade.disable()
        self.btnTradeAllRoute.disable()
        self.btnAddOneTimeTrade.disable()
        
        # load resources
        try:
            (myTotalAL, myTotalEC, myTotalIA, myAvailAL, myAvailEC, myAvailIA) = self.getTotalTrade()
            systemTrade = self.buildSystemTradeData()
            myTradeRoutes = self.buildTradeRouteData()
        except:
            # this allows for testing panel outside game
            (myTotalAL, myTotalEC, myTotalIA) = (1000, 1000, 100)
            systemTrade = self.testDict
            myAvailAL = 1000
            myAvailEC = 1000
            myAvailIA = 0
            myTradeRoutes = self.testDict
        
        # titles
        ##self.lblTitle.setText('TOTAL TRADE ON:')
        self.lblAddTrade.setText('ADD TRADE ROUTE:')
        
        # system Resources
        ##self.lblTotalAL.setText(str(int(myTotalAL)))
        ##self.lblTotalEC.setText(str(int(myTotalEC)))
        ##self.lblTotalIA.setText(str(int(myTotalIA)))
        
        # setup ranges
        ##if myAvailAL == 0:
            ##self.txtAL.readOnly = 1
        ##else:
            ##self.txtIA.readOnly = 0
            
        ##if myAvailEC == 0:
            ##self.txtEC.readOnly = 1
        ##else:
            ##self.txtIA.readOnly = 0
            
        ##if myAvailIA == 0:
            ##self.txtIA.readOnly = 1
        ##else:
            ##self.txtIA.readOnly = 0
            
        self.txtAL.setText('%d' % (int(myAvailAL)))
        self.txtEC.setText('%d' % (int(myAvailEC)))
        self.txtIA.setText('%d' % (int(myAvailIA)))
        
        # systems list
        self.populateListbox(self.lstToSystem, systemTrade)
        
        # trade route list
        self.populateListbox(self.lstTrade, myTradeRoutes)

    def getTotalTrade(self):
        """Return a tuple total and available resources for this system
        total resources = total resources coming in and out for system
        avail resources = total resource storage - resources going out of system"""
        totalAL = 0
        totalEC = 0
        totalIA = 0
        availAL = self.mySystemDict['AL']
        availEC = self.mySystemDict['EC']
        availIA = self.mySystemDict['IA']
        
        # go through all traderoutes given (traderoutes of this empire)
        ##for id, myTradeRoute in self.frame.mode.game.tradeRoutes.iteritems():
            ##if myTradeRoute['fromSystem'] == self.mySystemDict['id']:
                ##totalAL -= myTradeRoute['AL']
                ##totalEC -= myTradeRoute['EC']
                ##totalIA -= myTradeRoute['IA']
                ##availAL -= myTradeRoute['AL']
                ##availEC -= myTradeRoute['EC']
                ##availIA -= myTradeRoute['IA']
            ##elif myTradeRoute['toSystem'] == self.mySystemDict['id']:
                ##totalAL += myTradeRoute['AL']
                ##totalEC += myTradeRoute['EC']
                ##totalIA += myTradeRoute['IA']
        
        # don't allow negative values
        if availAL < 0:
            availAL = 0
        if availEC < 0:
            availEC = 0
        if availIA < 0:
            availIA = 0
        
        return (totalAL, totalEC, totalIA, availAL, availEC, availIA)
    
    def buildSystemTradeData(self):
        """Return a dictionary of Systems that can trade with this System"""
        d = {}
        for systemID in (self.mySystemDict['connectedSystems'] + self.mySystemDict['warpGateSystems']):
            systemDict = self.frame.mode.game.allSystems[systemID]
            if systemDict['myEmpireID'] == self.myEmpireDict['id'] or anwp.func.globals.diplomacy[self.frame.mode.game.myEmpire['diplomacy'][systemDict['myEmpireID']]['diplomacyID']]['trade'] == 1:
                d[systemID] = systemDict['name']
        return d
    
    def buildTradeRouteData(self):
        """Return a dictionary of Trade Routes that this system is involved in"""
        d = {}
        for tradeID, myTradeRouteDict in self.frame.mode.game.tradeRoutes.iteritems():
            if (myTradeRouteDict['fromSystem'] == self.mySystemDict['id'] or
                myTradeRouteDict['toSystem'] == self.mySystemDict['id']):
                # system involved in trade, build message
                s = ''
                if myTradeRouteDict['id'][-3:] == 'GEN':
                    s = s + 'GEN'
                if myTradeRouteDict['AL'] > 0:
                    s = s + ' AL:%d' % myTradeRouteDict['AL']
                if myTradeRouteDict['EC'] > 0:
                    s = s + ' EC:%d' % myTradeRouteDict['EC']
                if myTradeRouteDict['IA'] > 0:
                    s = s + ' IA:%d' % myTradeRouteDict['IA']
                if myTradeRouteDict['fromSystem'] == self.mySystemDict['id']:
                    s = s + ' -> %s' % self.frame.mode.game.allSystems[myTradeRouteDict['toSystem']]['name']
                elif myTradeRouteDict['toSystem'] == self.mySystemDict['id']:
                    s = s + ' <- %s' % self.frame.mode.game.allSystems[myTradeRouteDict['fromSystem']]['name']
                if myTradeRouteDict['oneTime'] == 1:
                    s = s + ' (ONCE)'
                if myTradeRouteDict['warpReq'] > 0:
                    s = s + '(WARP %d)' % myTradeRouteDict['warpReq']
                    
                d[tradeID] = s
            
        return d

    def onToSystemSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnAddTradeRoute.disable()
            self.btnTradeAllRoute.disable()
            self.btnAddOneTimeTrade.disable()
        else:
            self.btnAddTradeRoute.enable()
            self.btnTradeAllRoute.enable()
            self.btnAddOneTimeTrade.enable()

    def onAddTradeRoute(self, item):
        """Add Trade Route"""
        self.frame.mode.addTradeRoute(float(self.txtAL.getValue()), float(self.txtEC.getValue()),
                                      float(self.txtIA.getValue()), self.mySystemDict['id'],
                                      self.lstToSystem.getSelectedItem().data, 'REG')
    
    def onAddOneTimeTrade(self, item):
        """Add Trade Route only once"""
        self.frame.mode.addTradeRoute(float(self.txtAL.getValue()), float(self.txtEC.getValue()),
                                      float(self.txtIA.getValue()), self.mySystemDict['id'],
                                      self.lstToSystem.getSelectedItem().data, 'REG',1)
    
    def onTradeGenRoute(self, item):
        """Add Trade GEN Route"""
        self.frame.mode.addTradeRoute(0, 0, 0, self.mySystemDict['id'],
                                      self.lstToSystem.getSelectedItem().data, 'GEN')
    
    def onTradeSelected(self, item):
        """Select item from List"""
        if self.lstTrade.getMultiSelectedItems() == []:
            self.btnCancelTrade.disable()
        else:
            self.btnCancelTrade.enable()
    
    def onCancelTrade(self, item):
        """Cancel Trade Route associated with this system"""
        self.frame.mode.cancelTradeRoute(self.lstTrade.getMultiSelectedItems(), self.mySystemDict['id'])

class MarketInfoPanel(guibase.BasePanel):
    """Panel for information about System Commodity Trade of Resources"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        self.type = str()
        self.value = str()
        x = (self.frame.app.height - 768) / (22 * 2)
        cells = 28 + (2 * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # system Info
        self.pctMarket = pyui.widgets.Picture('%smarket.png' % (self.imagePath))
        self.addChild(self.pctMarket, (0, 0, 1, 3))
        self.lblTitle = pyui.widgets.Label(text=' GALACTIC MARKET', type=2)
        self.addChild(self.lblTitle, (1, 1, 3, 1))
        
        # average market prices
        n = 4
        self.buildResources(n, 'AVERAGE MARKET PRICES:', 1, '', ['AL','EC','IA'])
        
        # add new trade route
        n = n+4
        self.lblAdd = pyui.widgets.Label(text='PLACE A MARKET ORDER:', type=1)
        self.addChild(self.lblAdd, (0, n, 4, 1))
        self.lblType = pyui.widgets.Label(text='Bid Type:', type=2)
        self.addChild(self.lblType, (0, n+1, 2, 1))
        self.lblType2 = pyui.widgets.Label(text='Resource:', type=2)
        self.addChild(self.lblType2, (2, n+1, 2, 1))
        self.lstType = pyui.widgets.ListBox(self.onSelected, None)
        self.addChild(self.lstType, (0, n+2, 2, 3))
        self.lstRes = pyui.widgets.ListBox(self.onSelected, None)
        self.addChild(self.lstRes, (2, n+2, 2, 3))
        d = {'buy-all':'BUY(All or None)', 'buy-any':'BUY(Any)', 'sell':'SELL'}
        self.populateListbox(self.lstType, d)
        d = {'AL':' Alloys (AL)','EC':' Energy (EC)','IA':' Arrays (IA)'}
        self.populateListbox(self.lstRes, d)

        n = n+6
        self.lblMin = pyui.widgets.Label(text='MIN SELL AT:', type=1)
        self.addChild(self.lblMin, (0, n, 2, 1))
        self.txtMin = pyui.widgets.NumberEdit('', 8, None, 0)
        self.addChild(self.txtMin, (2, n, 2, 1))
        
        self.lblMax = pyui.widgets.Label(text='MAX BUY AT:', type=1)
        self.addChild(self.lblMax, (0, n+1, 2, 1))
        self.txtMax = pyui.widgets.NumberEdit('', 8, None, 0)
        self.addChild(self.txtMax, (2, n+1, 2, 1))

        self.lblAmount = pyui.widgets.Label(text='MAX AMOUNT:', type=1)
        self.addChild(self.lblAmount, (0, n+2, 2, 1))
        self.txtAmount = pyui.widgets.NumberEdit('', 8, None, 0)
        self.addChild(self.txtAmount, (2, n+2, 2, 1))

        self.btnAddMarketOrder = pyui.widgets.Button('Place Galactic Market Order', self.onAddMarketOrder)
        self.addChild(self.btnAddMarketOrder, (0, n+4, 4, 1))
        
        # system Orders
        n = n+6
        self.lblOrders = pyui.widgets.Label(text='MARKET ORDERS FOR SYSTEM:', type=1)
        self.addChild(self.lblOrders, (0, n, 4, 1))
        self.lstOrders = pyui.widgets.ListBox(self.onOrderSelected, None, 100, 100, 1)
        self.addChild(self.lstOrders, (0, n+1, 4, 6+(2*x)))
        self.btnCancelOrder = pyui.widgets.Button('Cancel Market Order', self.onCancelOrder)
        self.addChild(self.btnCancelOrder, (0, n+7+(2*x), 3, 1))
        
        # pack widgets
        self.pack
    def populate(self, myEmpireDict, mySystemDict):
        """Populate frame with new data"""
        self.myEmpireDict = myEmpireDict
        self.mySystemDict = mySystemDict
        
        # disable buttons
        self.btnAddMarketOrder.disable()
        self.btnCancelOrder.disable()
        self.clearBidData()
        
        # load resources
        try:
            (myAvgAL, myAvgEC, myAvgIA) = self.getAvgMarketCosts()
            myMarketOrders = self.buildMarketOrdersData()
        except:
            # this allows for testing panel outside game
            (myAvgAL, myAvgEC, myAvgIA) = (10.10100, 20.10100, 30.123120)
            myMarketOrders = self.testDict
        
        # system Resources
        self.lblTotalAL.setText('%.1f' % myAvgAL)
        self.lblTotalEC.setText('%.1f' % myAvgEC)
        self.lblTotalIA.setText('%.1f' % myAvgIA)
            
        # trade route list
        self.populateListbox(self.lstOrders, myMarketOrders)

    def getAvgMarketCosts(self):
        """Return a tuple of the Average Market Costs for the three resources"""
        try:
            avgAL = self.frame.mode.game.marketStats[str(self.frame.mode.game.currentRound-1)]['avgSoldAL']
            avgEC = self.frame.mode.game.marketStats[str(self.frame.mode.game.currentRound-1)]['avgSoldEC']
            avgIA = self.frame.mode.game.marketStats[str(self.frame.mode.game.currentRound-1)]['avgSoldIA']
        except:
            avgAL = 0.0
            avgEC = 0.0
            avgIA = 0.0
        
        return (avgAL, avgEC, avgIA)
    
    def buildMarketOrdersData(self):
        """Return a dictionary of Trade Routes that this system is involved in"""
        d = {}
        for orderID, myMarketOrderDict in self.frame.mode.game.marketOrders.iteritems():
            if myMarketOrderDict['system'] == self.mySystemDict['id']:
                amount = myMarketOrderDict['amount']
                min = myMarketOrderDict['min']
                max = myMarketOrderDict['max']
                value = myMarketOrderDict['value']
                if myMarketOrderDict['type'] == 'sell':
                    s = 'SELL (%d %s) for MIN=%d' % (amount, value, min)
                elif myMarketOrderDict['type'] == 'buy-all':
                    s = 'BUY ALL (%d %s) for MAX=%d' % (amount, value, max)
                elif myMarketOrderDict['type'] == 'buy-any':
                    s = 'BUY ANY (%d %s) for MAX=%d' % (amount, value, max)
                d[orderID] = s
        return d

    def onSelected(self, item):
        """Set type of order"""
        if not item:
            self.clearBidData()
        else:
            self.enableAddOrder()
    
    def enableAddOrder(self):
        """If certain checks are in place enable add Order button"""
        if self.lstType.selected == -1 or self.lstRes.selected == -1:
            self.btnAddMarketOrder.disable()
        else:
            self.btnAddMarketOrder.enable()
            if self.lstType.getSelectedItem().data == 'sell':
                self.txtMin.readOnly = 0
            else:
                self.txtMax.readOnly = 0
    
    def clearBidData(self):
        """Clear and disable bid data"""
        self.txtAmount.setText('')
        self.txtMin.setText('')
        self.txtMax.setText('')
        self.txtMin.readOnly = 1
        self.txtMax.readOnly = 1
        self.lstType.clearSelection()
        self.lstRes.clearSelection()
        self.btnAddMarketOrder.disable()
        self.btnCancelOrder.disable()
    
    def onAddMarketOrder(self, item):
        """Add Market Order"""
        self.frame.mode.addMarketOrder(self.lstType.getSelectedItem().data, self.lstRes.getSelectedItem().data,
                                    float(self.txtMin.getValue()),float(self.txtMax.getValue()),
                                    float(self.txtAmount.getValue()),self.mySystemDict['id'])
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if self.lstOrders.getMultiSelectedItems() == []:
            self.clearBidData()
        else:
            self.btnCancelOrder.enable()
    
    def onCancelOrder(self, item):
        """Cancel Market Order associated with this system"""
        self.frame.mode.cancelMarketOrder(self.lstOrders.getMultiSelectedItems(), self.mySystemDict['id'])
        

class OtherSystemInfoPanel(guibase.BasePanel):
    """Panel that contains information about other Systems
    This would contain information that is limited and depends on recent intel"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        x = (self.frame.app.height - 768) / (22 * 3)
        cells = 28 + (3 * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # system Info
        self.pctSystem = pyui.widgets.Picture('')
        self.addChild(self.pctSystem, (0, 0, 1, 3))
        self.pctEmpire = pyui.widgets.Picture('')
        self.addChild(self.pctEmpire, (1, 0, 1, 3))
        self.lblOwnedBy = pyui.widgets.Label(text='  System Owner:', type=2)
        self.addChild(self.lblOwnedBy, (2, 1, 2, 1))
        self.lblEmpireName = pyui.widgets.Label(text='')
        self.addChild(self.lblEmpireName, (2, 2, 2, 1))
                
        # system Industry
        n = 5
        self.lbl = pyui.widgets.Label(text='REPORT LAST UPDATED:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lblLastRound = pyui.widgets.Label(text='ROUND 999', type=2)
        self.addChild(self.lblLastRound, (0, n+1, 4, 1))
        self.lblIndustryLegend = pyui.widgets.Label(text='SYSTEM INDUSTRY:', type=1)
        self.addChild(self.lblIndustryLegend, (0, n+3, 4, 1))
        self.lstIndustry = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstIndustry, (0, n+4, 4, 5 + x))
        
        # system Ships
        n = n + 10 + x
        self.lblShipsLegend = pyui.widgets.Label(text='SYSTEM STARSHIPS:', type=1)
        self.addChild(self.lblShipsLegend, (0, n, 4, 1))
        self.lstShips = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstShips, (0, n + 1, 4, 5 + x))
        
        # system Marines
        n = n + 7 + x
        self.lblMarinesLegend = pyui.widgets.Label(text='SYSTEM MARINES:', type=1)
        self.addChild(self.lblMarinesLegend, (0, n, 4, 1))
        self.lstMarines = pyui.widgets.ListBox(None, None)
        self.addChild(self.lstMarines, (0, n + 1, 4, 5 + x))
        
        # pack widgets
        self.pack

    def populate(self, myEmpireDict, mySystemDict):
        """Populate frame with new data"""
        # load resources
        try:
            myEmpirePict = '%s%s.png' % (self.frame.app.simImagePath, myEmpireDict['imageFile'])
            mySystemPict = '%s%s.png' % (self.frame.app.simImagePath, mySystemDict['imageFile'])
        except:
            # this allows for testing panel outside game
            myEmpirePict = '%s.png' % myEmpireDict['imageFile']
            mySystemPict = '%s.png' % mySystemDict['imageFile']
        
        myIntelReport = mySystemDict['intelReport']
        myIndustry = myIntelReport['industryReport']
        myShips = myIntelReport['shipReport']
        myMarines = myIntelReport['marineReport']
        self.lblEmpireName.setText('  %s' % myEmpireDict['name'])
        self.lblEmpireName.setColor(anwp.func.globals.colors[myEmpireDict['color1']])
        self.lblLastRound.setText('ROUND %d' % myIntelReport['round'])
        
        # system Info
        self.frame.title = '%s - Intelligence Report:' % mySystemDict['name']
        self.pctSystem.setFilename(mySystemPict)
        self.pctEmpire.setFilename(myEmpirePict)
        
        # system Industry
        self.populateListbox(self.lstIndustry, myIndustry)
                
        # system Ships
        self.populateListbox(self.lstShips, myShips)
        
        # system Marines
        self.populateListbox(self.lstMarines, myMarines)

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    myEmpire = {'imageFile':'testempire', 'name': 'Kurita', 'ip': '', 'AL': 0, 'EC': 0, 'color1': 'red', 'simulationsLeft': 0, 'color1': 'black', 'emailAddress': '', 'key': '', 'designsLeft': 0, 'IA': 0, 'CR': 0, 'cities': 10}
    dIndustry = {'1':'Factory-1', '3':'Research Center-1', '2':'Marine Academy-2'}
    dShips = {'1':'5 Scouts', '2':'10 Destroyers', '3':'3 Super Dreadnoughts'}
    dMarines = {'1':'10 Flamers', '2':'10 Strikers', '3':'5 Gunners'}
    myIntelReport = {'round':99, 'industryReport':dIndustry, 'shipReport':dShips, 'marineReport':dMarines}
    mySystem = {'intelReport':myIntelReport, 'AL':12032, 'EC':455, 'IA':54, 'name': 'Hannah', 'imageFile': 'sys_8_yellow_black', 'id': '1001', 'connectedSystems': [], 'y': 300, 'x': 200, 'cities': 10, 'citiesUsed':4, 'myEmpireID': '2'}
    systemID = '1000'
    pyui.init(width, height, 'p3d', 0, 'Testing System Info Panel')
    app = run.TestApplication(width, height)
    frame = SystemInfoFrame(None, app)
    frame.panel.populate(myEmpire, mySystem)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
