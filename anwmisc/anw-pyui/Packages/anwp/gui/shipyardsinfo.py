# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipyardsinfo.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This panel Displays all controls for Shipyards display and control
# This is brought up from the galactic map on a shipyard click
# ---------------------------------------------------------------------------
import string
import types

import pyui
import guibase
import anwp.func.globals
import anwp.war.shipdesign

class ShipyardsInfoFrame(guibase.BaseInfoFrame):
    """Displays Shipyards Information"""  
    def __init__(self, mode, app, title='Shipyards Information'):
        guibase.BaseInfoFrame.__init__(self, mode, app, title)
        self.setPanel(TabbedInfoPanel(self))
    
    def signal(self, subject):
        """New subject calling frame"""
        self.shipyardEntity = subject
        if self.shipyardEntity.systemID <> self.currentID:
            # different shipyard populate panel
            self.currentID = self.shipyardEntity.systemID
            self.setPanel(TabbedInfoPanel(self))
            self.panel.populate(self.shipyardEntity.mySystemDict)

class TabbedInfoPanel(pyui.widgets.TabbedPanel):
    """This Panel Contains any SubPanels associated with the System"""
    def __init__(self, frame):
        pyui.widgets.TabbedPanel.__init__(self)
        self.addPanel('BUILD', BuildInfoPanel(frame))
        self.addPanel('REPAIR', RepairInfoPanel(frame))
        self.addPanel('UPGRADE', UpgradeInfoPanel(frame))
    
    def populate(self, mySystemDict):
        """When asked to populate the Panel will populate its sub panels"""
        self.mySystemDict = mySystemDict
        self.getPanel(0).populate(mySystemDict)
        self.getPanel(1).populate(mySystemDict)
        self.getPanel(2).populate(mySystemDict)
    
class BuildInfoPanel(guibase.BasePanel):
    """Panel for Building new Starships"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 2
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # Shipyards info
        self.pctShipyard = pyui.widgets.Picture('')
        self.addChild(self.pctShipyard, (0, 0, 1, 3))
        self.lblName = pyui.widgets.Label(text=' Test Shipyards', type=1)
        self.addChild(self.lblName, (1, 0, 3, 1))
        self.lblSPAvail = pyui.widgets.Label(text=' Capacity (Used/Avail): 0/0', type=2)
        self.addChild(self.lblSPAvail, (1, 1, 3, 1))
        self.lblCadetsAvail = pyui.widgets.Label(text=' Fleet Cadets Available: 0', type=2)
        self.addChild(self.lblCadetsAvail, (1, 2, 3, 1))
        
        # Choose design
        n = 4
        self.lbl = pyui.widgets.Label(text='SHIP DESIGN <CAPACITY REQUIRED>:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstDesign = pyui.widgets.ListBox(self.onDesignSelected, None, 100, 100, 0)
        self.addChild(self.lstDesign, (0, n+1, 4, 6+x))
        
        n = n+7+x
        self.buildResources(n, 'SELECTED DESIGN COST:', 1, 'Design')
        
        # available resources
        n = n+4
        self.buildResources(n, 'AVAILABLE RESOURCES:', 1, 'Avail')
        
        n = n+4
        self.lbl = pyui.widgets.Label(text='BUILD:', type=1)
        self.addChild(self.lbl, (0, n, 1, 1))
        self.slbAmount = pyui.widgets.SliderBar(None, 10)
        self.addChild(self.slbAmount, (1, n, 2, 1))
        self.btnBuild = pyui.widgets.Button('Build', self.onBuildShip)
        self.addChild(self.btnBuild, (3, n, 1, 1))
        
        n = n+2
        self.buildOrders(n,x,'CURRENT SHIPYARD ORDERS:',5)
        
        # pack widgets
        self.pack
    
    def buildDesignData(self):
        """Display all available Starship Designs"""
        d = {}
        shipDesigns = self.frame.mode.game.shipDesigns
        myDesignKeys = anwp.func.funcs.sortStringList(shipDesigns.keys())
        for id in myDesignKeys:
            shipDesignTuple = shipDesigns[id]
            SYCReq = returnCapacityRequired(self.frame, shipDesignTuple[1])
            d[id] = '%s <%d>' % (shipDesignTuple[0], SYCReq)
        return d
    
    def buildShipyardOrderData(self, dIndOrderData):
        """Display all Shipyard orders this round"""
        d = {}
        for id, dIndOrder in dIndOrderData.iteritems():
            if dIndOrder['system'] == self.mySystemDict['id'] and dIndOrder['type'] in ('Add Ship', 'Repair Ship', 'Upgrade Ship'):
                mySystemDict = self.frame.mode.game.allSystems[dIndOrder['system']]
                if dIndOrder['type'] == 'Add Ship':
                    (amount, shipType) = string.split(dIndOrder['value'], '-')
                    name = 'ADD %s: %s' % (amount, self.frame.mode.game.shipDesigns[shipType][0])
                d[id] = name
        return d
    
    def enableBuildShip(self):
        """Check if shipyards should allow ship to be built"""
        if self.frame.mode.myShipDesign <> None:
            myShipDesign = self.frame.mode.myShipDesign
            # check if ship could be built
            amount = int(self.slbAmount.position)
            if (self.myEmpireDict['CR'] >= myShipDesign.costCR * amount and
                self.mySystemDict['AL'] >= myShipDesign.costAL * amount and
                self.mySystemDict['EC'] >= myShipDesign.costEC * amount and
                self.mySystemDict['IA'] >= myShipDesign.costIA * amount and
                (self.mySystemDict['availSYC'] - self.mySystemDict['usedSYC']) >= (returnCapacityRequired(self.frame, myShipDesign.shipHullID)*amount)
                and amount > 0):
                self.btnBuild.enable()
            else:
                self.btnBuild.disable()
        else:
            self.btnBuild.disable()
    
    def onBuildShip(self, item):
        """Send a Build Starship commande to server"""
        self.frame.mode.addShipOrder(self.slbAmount.position, self.lstDesign.getSelectedItem().data, self.mySystemDict['id'])

    def onDesignSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnBuild.disable()
        else:
            # create temporary design for display
            (name, shipHullID, compDict, weapDict) = self.frame.mode.game.shipDesigns[item.data]
            self.frame.mode.myShipDesign = self.frame.mode.getShipDesign(shipHullID, compDict, weapDict)
            myShipDesign = self.frame.mode.myShipDesign
            self.lblTotalCRDesign.setText('%d' % myShipDesign.costCR)
            self.lblTotalALDesign.setText('%d' % myShipDesign.costAL)
            self.lblTotalECDesign.setText('%d' % myShipDesign.costEC)
            self.lblTotalIADesign.setText('%d' % myShipDesign.costIA)
            self.enableBuildShip()
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.enableButtons(self.lstOrders, [self.btnCancelOrder])
    
    def onCancelOrder(self, item):
        """Set a Cancel Order Command on selected Order"""
        self.frame.mode.cancelIndustryOrder(self.lstOrders.getMultiSelectedItems(), self.mySystemDict['id'])
    
    def populate(self, mySystemDict):
        """Populate frame with new data"""
        self.mySystemDict = mySystemDict
        # disable buttons
        self.btnBuild.disable()
        self.btnCancelOrder.disable()
        
        # load resources
        try:
            self.myEmpireDict = self.frame.mode.game.myEmpire
            name = 'shipyards_%s_%s' % (self.frame.mode.game.myEmpire['color1'], self.frame.mode.game.myEmpire['color2'])
            myShipyardPict = '%s%s.png' % (self.frame.app.simImagePath, name)
            myDesigns = self.buildDesignData()
            myOrders = self.buildShipyardOrderData(self.myEmpireDict['industryOrders'])
            self.lblName.setText(' %s Shipyards' % mySystemDict['name'])
            self.lblSPAvail.setText(' Capacity: %d/%d' % (mySystemDict['usedSYC'], mySystemDict['availSYC']))
            self.lblCadetsAvail.setText(' Fleet Cadets: %d' % self.mySystemDict['fleetCadets'])
            self.lblTotalCRAvail.setText('%d' % self.myEmpireDict['CR'])
            self.lblTotalALAvail.setText('%d' % self.mySystemDict['AL'])
            self.lblTotalECAvail.setText('%d' % self.mySystemDict['EC'])
            self.lblTotalIAAvail.setText('%d' % self.mySystemDict['IA'])
        except:
            # this allows for testing panel outside game
            myShipyardPict = self.testImagePath + 'empire1.png'
            myDesigns = myOrders = self.testDict
        
        # Shipyards info        
        self.pctShipyard.setFilename(myShipyardPict)
        self.populateListbox(self.lstDesign, myDesigns)
                
        # system Orders
        self.populateListbox(self.lstOrders, myOrders)

class RepairInfoPanel(guibase.BasePanel):
    """Panel for Repairing Starships"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 2
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        
        # SY info
        self.pctSY = pyui.widgets.Picture('')
        self.addChild(self.pctSY, (0, 0, 1, 3))
        self.lblName = pyui.widgets.Label(text=' Test Starships', type=1)
        self.addChild(self.lblName, (1, 0, 3, 1))
        self.lblSYAvail = pyui.widgets.Label(text=' Capacity (Used/Avail): 0/0', type=2)
        self.addChild(self.lblSYAvail, (1, 1, 3, 1))
        
        # Choose Starships to Repair
        n = 4
        self.lbl = pyui.widgets.Label(text='CHOOSE STARSHIPS TO REPAIR:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstStarship = pyui.widgets.ListBox(self.onStarshipSelected, None, 100, 100, 1)
        self.addChild(self.lstStarship, (0, n+1, 4, 6+x))
        
        n = n+7+x
        self.buildResources(n, 'TOTAL REPAIR COST:', 1, 'Starship')
        
        # available resources
        n = n+4
        self.buildResources(n, 'AVAILABLE RESOURCES:', 1, 'Avail')
        
        n = n+4
        self.btnRepair = pyui.widgets.Button('Repair Selected Starships', self.onRepairStarship)
        self.addChild(self.btnRepair, (0, n, 4, 1))
        
        n = n+2
        self.buildOrders(n,x,'CURRENT SHIPYARD ORDERS:',5)
        
        # pack widgets
        self.pack
    
    def buildStarshipData(self):
        """Display all Starships in need of repair"""
        d = {}
        for fleetID, myFleetDict in self.frame.mode.game.myFleets.iteritems():
            if myFleetDict['fromSystem'] == self.mySystemDict['id'] and myFleetDict['toSystem'] == self.mySystemDict['id']:
                for shipID, myShipDict in myFleetDict['ships'].iteritems():
                    if myShipDict['strength'] < 100 and myShipDict['id'] not in self.toRepairShips:
                        d['%s-%s' % (fleetID, shipID)] = '%s(%d%s)' % (myShipDict['name'], myShipDict['strength'], '%')
        return d
    
    def buildOrderData(self, dIndOrderData):
        """Display all SY orders this round"""
        d = {}
        self.toRepairShips = [] # list of ships being repaired
        for id, dIndOrder in dIndOrderData.iteritems():
            if dIndOrder['system'] == self.mySystemDict['id'] and dIndOrder['type'] =='Repair Starship':
                mySystemDict = self.frame.mode.game.allSystems[dIndOrder['system']]
                name = ''
                if dIndOrder['type'] == 'Repair Starship':
                    myShipDict = self.getMyShipDict(dIndOrder['value'])
                    name = 'RPR %s(%d%s)' % (myShipDict['name'], myShipDict['strength'], '%')
                    self.toRepairShips.append(myShipDict['id'])
                if name <> '':
                    d[id] = name
        return d
    
    def enableRepairStarship(self):
        """Check if SY should allow ship to be repaired"""
        myShipDict = self.getMyShipDict()
        # check if ship can be repaired
        [CR,AL,EC,IA,capacity] = self.getRepairCost()
        if (self.myEmpireDict['CR'] >= CR and
            self.mySystemDict['AL'] >= AL and
            self.mySystemDict['EC'] >= EC and
            self.mySystemDict['IA'] >= IA and
            (self.mySystemDict['availSYC'] - self.mySystemDict['usedSYC']) >= (capacity)):
            self.btnRepair.enable()
        else:
            self.btnRepair.disable()
    
    def getRepairCost(self):
        """Return the Repair Costs of selected Starships"""
        CR = 0
        AL = 0
        EC = 0
        IA = 0
        capacity = 0
        for item in self.lstStarship.getMultiSelectedItems():
            myShipDict = self.getMyShipDict(item)
            CR += myShipDict['repairCost'][0]
            AL += myShipDict['repairCost'][1]
            EC += myShipDict['repairCost'][2]
            IA += myShipDict['repairCost'][3]
            capacity += int((1-(myShipDict['strength']/100.0)) * (returnCapacityRequired(self.frame, self.frame.mode.game.shipDesigns[myShipDict['designID']][1])))
        return [CR,AL,EC,IA,capacity]
    
    def getMyShipDict(self, value=''):
        """Return the Ship Dict of selected Ship"""
        if value == '':
            value = self.lstStarship.getSelectedItem().data
        (fleetID, shipID) = string.split(value, '-')
        myFleetDict = self.frame.mode.game.myFleets[fleetID]
        myShipDict = myFleetDict['ships'][shipID]
        return myShipDict
    
    def onRepairStarship(self, item):
        """Send a Repair Starship Command to server"""
        self.frame.mode.repairStarshipOrder(self.lstStarship.getMultiSelectedItems(), self.mySystemDict['id'])

    def onStarshipSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnRepair.disable()
        else:
            (CR,AL,EC,IA,capacity) = self.getRepairCost()
            self.lblTotalCRStarship.setText('%d' % CR)
            self.lblTotalALStarship.setText('%d' % AL)
            self.lblTotalECStarship.setText('%d' % EC)
            self.lblTotalIAStarship.setText('%d' % IA)
            self.enableRepairStarship()
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.enableButtons(self.lstOrders, [self.btnCancelOrder])
    
    def onCancelOrder(self, item):
        """Set a Cancel Order Command on selected Order"""
        self.frame.mode.cancelIndustryOrder(self.lstOrders.getMultiSelectedItems(), self.mySystemDict['id'])
    
    def populate(self, mySystemDict):
        """Populate frame with new data"""
        self.mySystemDict = mySystemDict
        # disable buttons
        self.btnRepair.disable()
        self.btnCancelOrder.disable()
        
        # load resources
        try:
            self.myEmpireDict = self.frame.mode.game.myEmpire
            name = 'shipyards_%s_%s' % (self.frame.mode.game.myEmpire['color1'], self.frame.mode.game.myEmpire['color2'])
            myPict = '%s%s.png' % (self.frame.app.simImagePath, name)
            myOrders = self.buildOrderData(self.myEmpireDict['industryOrders'])
            myShips = self.buildStarshipData()
            self.lblName.setText(' %s Starships' % mySystemDict['name'])
            self.lblSYAvail.setText(' Capacity: %d/%d' % (mySystemDict['usedSYC'], mySystemDict['availSYC']))
            self.lblTotalCRAvail.setText('%d' % self.myEmpireDict['CR'])
            self.lblTotalALAvail.setText('%d' % self.mySystemDict['AL'])
            self.lblTotalECAvail.setText('%d' % self.mySystemDict['EC'])
            self.lblTotalIAAvail.setText('%d' % self.mySystemDict['IA'])
        except:
            # this allows for testing panel outside game
            myPict = self.testImagePath + 'empire1.png'
            myShips = myOrders = self.testDict
        
        # Shipyards info        
        self.pctSY.setFilename(myPict)
        self.populateListbox(self.lstStarship, myShips)
                
        # system Orders
        self.populateListbox(self.lstOrders, myOrders)
        
class UpgradeInfoPanel(guibase.BasePanel):
    """Panel for Upgrading Starships"""
    def __init__(self, frame):
        guibase.BasePanel.__init__(self, frame)
        numExtend = 3
        x = (self.frame.app.height - 768) / (22 * numExtend)
        cells = 28 + (numExtend * x)
        self.setLayout(pyui.layouts.TableLayoutManager(4, cells))
        self.shipDesigns = {} # dict of ship Designs key=design ID, value = design obj
        
        # SY info
        self.pctSY = pyui.widgets.Picture('')
        self.addChild(self.pctSY, (0, 0, 1, 3))
        self.lblName = pyui.widgets.Label(text=' Test Starships', type=1)
        self.addChild(self.lblName, (1, 0, 3, 1))
        self.lblSYAvail = pyui.widgets.Label(text=' Capacity (Used/Avail): 0/0', type=2)
        self.addChild(self.lblSYAvail, (1, 1, 3, 1))
        
        # Choose Starships to Upgrade
        n = 3
        self.lbl = pyui.widgets.Label(text='CHOOSE STARSHIP TO UPGRADE:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstStarship = pyui.widgets.ListBox(self.onSelected, None, 100, 100, 0)
        self.addChild(self.lstStarship, (0, n+1, 4, 3+x))
        
        n = n+5+x
        self.lbl = pyui.widgets.Label(text='CHOOSE STARSHIP DESIGN:', type=1)
        self.addChild(self.lbl, (0, n, 4, 1))
        self.lstDesign = pyui.widgets.ListBox(self.onSelected, None, 100, 100, 0)
        self.addChild(self.lstDesign, (0, n+1, 4, 3+x))
        
        n = n+5+x
        self.buildResources(n, 'UPGRADE COST:', 1, 'Starship')
        
        # available resources
        n = n+3
        self.buildResources(n, 'AVAILABLE RESOURCES:', 1, 'Avail')
        
        n = n+3
        self.btnUpgrade = pyui.widgets.Button('Upgrade Starship', self.onUpgradeStarship)
        self.addChild(self.btnUpgrade, (0, n, 4, 1))
        
        n = n+2
        self.buildOrders(n,x,'CURRENT SHIPYARD ORDERS:',5)
        
        # pack widgets
        self.pack
    
    def buildDesignData(self):
        """Display all available Starship Designs"""
        d = {}
        shipDesigns = self.frame.mode.game.shipDesigns
        myDesignKeys = anwp.func.funcs.sortStringList(shipDesigns.keys())
        for id in myDesignKeys:
            shipDesignTuple = shipDesigns[id]
            SYCReq = returnCapacityRequired(self.frame, shipDesignTuple[1])
            d[id] = '%s <%d>' % (shipDesignTuple[0], SYCReq)
        return d
    
    def buildStarshipData(self):
        """Display all Starships that could be upgraded"""
        d = {}
        for fleetID, myFleetDict in self.frame.mode.game.myFleets.iteritems():
            if myFleetDict['fromSystem'] == self.mySystemDict['id'] and myFleetDict['toSystem'] == self.mySystemDict['id']:
                for shipID, myShipDict in myFleetDict['ships'].iteritems():
                    if myShipDict['strength'] == 100 and myShipDict['id'] not in self.toUpgradeShips:
                        d['%s-%s' % (fleetID, shipID)] = '%s' % myShipDict['name']
        return d
    
    def buildOrderData(self, dIndOrderData):
        """Display all SY orders this round"""
        d = {}
        self.toUpgradeShips = [] # list of ships being upgraded
        for id, dIndOrder in dIndOrderData.iteritems():
            if dIndOrder['system'] == self.mySystemDict['id'] and dIndOrder['type'] =='Upgrade Starship':
                mySystemDict = self.frame.mode.game.allSystems[dIndOrder['system']]
                name = ''
                if dIndOrder['type'] == 'Upgrade Starship':
                    (fleetID, shipID, newDesignID) = string.split(dIndOrder['value'], '-')
                    myNewDesign = self.getMyDesign(newDesignID)
                    myShipDict = self.getMyShipDict('%s-%s' % (fleetID, shipID))
                    name = 'UPG %s->%s' % (myShipDict['name'], myNewDesign.name)
                    self.toUpgradeShips.append(myShipDict['id'])
                if name <> '':
                    d[id] = name
        return d
    
    def enableUpgradeStarship(self):
        """Check if SY should allow ship to be upgraded"""
        try:
            myShipDict = self.getMyShipDict()
            myOldDesign = self.getMyDesign(myShipDict['designID'])
            myNewDesign = self.getMyDesign(self.lstDesign.getSelectedItem().data)
            # check if ship can be upgraded
            result = myOldDesign.getUpgradeCost(myNewDesign)
            if result == types.StringType:
                self.frame.mode.modeMsgBox(result)
                self.btnUpgrade.disable()
                self.lblTotalCRStarship.setText('0')
                self.lblTotalALStarship.setText('0')
                self.lblTotalECStarship.setText('0')
                self.lblTotalIAStarship.setText('0')
            else:
                [CR,AL,EC,IA,capacity] = result
                self.lblTotalCRStarship.setText('%d' % CR)
                self.lblTotalALStarship.setText('%d' % AL)
                self.lblTotalECStarship.setText('%d' % EC)
                self.lblTotalIAStarship.setText('%d' % IA)
                if (self.myEmpireDict['CR'] >= CR and
                    self.mySystemDict['AL'] >= AL and
                    self.mySystemDict['EC'] >= EC and
                    self.mySystemDict['IA'] >= IA and
                    (self.mySystemDict['availSYC'] - self.mySystemDict['usedSYC']) >= (capacity)):
                    self.btnUpgrade.enable()
                else:
                    self.btnUpgrade.disable()
        except:
            self.btnUpgrade.disable()
            self.lblTotalCRStarship.setText('0')
            self.lblTotalALStarship.setText('0')
            self.lblTotalECStarship.setText('0')
            self.lblTotalIAStarship.setText('0')
            
    def getMyDesign(self, designID):
        """Return the new Design Object"""
        myNewDesign = self.frame.mode.game.shipDesignObjects[designID]
        return myNewDesign

    def getMyShipDict(self, value=''):
        """Return the Ship Upgrade Design Dict of selected Ship"""
        if value == '':
            value = self.lstStarship.getSelectedItem().data
        (fleetID, shipID) = string.split(value, '-')
        myFleetDict = self.frame.mode.game.myFleets[fleetID]
        myShipDict = myFleetDict['ships'][shipID]
        return myShipDict
    
    def onUpgradeStarship(self, item):
        """Send a Repair Starship Command to server"""
        self.frame.mode.upgradeStarshipOrder(self.lstStarship.getSelectedItem().data, self.lstDesign.getSelectedItem().data, self.mySystemDict['id'])

    def onSelected(self, item):
        """Select item from List"""
        if not item:
            self.btnUpgrade.disable()
        else:
            self.enableUpgradeStarship()
    
    def onOrderSelected(self, item):
        """Select item from List"""
        if not item:
            pass
        else:
            self.enableButtons(self.lstOrders, [self.btnCancelOrder])
    
    def onCancelOrder(self, item):
        """Set a Cancel Order Command on selected Order"""
        self.frame.mode.cancelIndustryOrder(self.lstOrders.getMultiSelectedItems(), self.mySystemDict['id'])
    
    def populate(self, mySystemDict):
        """Populate frame with new data"""
        self.mySystemDict = mySystemDict
        # disable buttons
        self.btnUpgrade.disable()
        self.btnCancelOrder.disable()
        
        # load resources
        try:
            self.myEmpireDict = self.frame.mode.game.myEmpire
            name = 'shipyards_%s_%s' % (self.frame.mode.game.myEmpire['color1'], self.frame.mode.game.myEmpire['color2'])
            myPict = '%s%s.png' % (self.frame.app.simImagePath, name)
            myOrders = self.buildOrderData(self.myEmpireDict['industryOrders'])
            myShips = self.buildStarshipData()
            myDesigns = self.buildDesignData()
            self.lblName.setText(' %s Starships' % mySystemDict['name'])
            self.lblSYAvail.setText(' Capacity: %d/%d' % (mySystemDict['usedSYC'], mySystemDict['availSYC']))
            self.lblTotalCRAvail.setText('%d' % self.myEmpireDict['CR'])
            self.lblTotalALAvail.setText('%d' % self.mySystemDict['AL'])
            self.lblTotalECAvail.setText('%d' % self.mySystemDict['EC'])
            self.lblTotalIAAvail.setText('%d' % self.mySystemDict['IA'])
        except:
            # this allows for testing panel outside game
            myPict = self.testImagePath + 'empire1.png'
            myShips = myOrders = myDesigns = self.testDict
        
        # Shipyards info        
        self.pctSY.setFilename(myPict)
        self.populateListbox(self.lstStarship, myShips)
        self.populateListbox(self.lstDesign, myDesigns)
                
        # system Orders
        self.populateListbox(self.lstOrders, myOrders)

def returnCapacityRequired(frame, hullID):
        """Return the Shipyard Capacity Required given hull id"""
        return frame.mode.game.shiphulldata[hullID].componentNum * 8

def main():
    """Run gui for testing"""
    import run
    width = 1024
    height = 768
    pyui.init(width, height, 'p3d', 0, 'Testing Shipyard Info Panel')
    app = run.TestApplication(width, height)
    frame = ShipyardsInfoFrame(None, app)
    frame.panel.populate(None)
    app.addGui(frame)
    app.run()
    pyui.quit()

if __name__ == '__main__':
    main()
    
