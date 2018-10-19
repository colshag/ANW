# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipyardupgradeships.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui allows user to upgrade ships
# ---------------------------------------------------------------------------
from anw.gui import shipyardrepairships, systemresources, submitbutton
from anw.gui import buttonlist, rootbutton, valuebar, selectallbutton
from anw.func import globals, funcs
import string

class ShipyardUpgradeShips(shipyardrepairships.ShipyardRepairShips):
    """The System Shipyard Upgrade Ships Gui"""
    def __init__(self, path, mySystemDict, myEmpireDict, industrydata, mode):
        self.newShipDesign = None
        self.newShipDesignList = None
        shipyardrepairships.ShipyardRepairShips.__init__(self, path, mySystemDict, myEmpireDict, industrydata, mode)
    
    def createCurrentResourceBars(self):
        """These bars will show the resources used for repairs"""
        self.removeMyWidget(self.currentResourceBars)
        x = (self.posInitX+1.6)
        y = self.posInitY-0.6
        self.currentResourceBars = valuebar.CostBars(self.path, 
                                                     self.totalRepairCosts,
                                                     self.totalRepairCosts,
                                                     x=x,
                                                     y=y,scale=self.scale,extraText='COST OF UPGRADES',
                                                     title='Current Total Cost of Upgrades:')
        self.myWidgets.append(self.currentResourceBars)
        
    def createListBoxes(self):
        """First Ask user to choose a Ship Design"""
        self.createNewShipDesignList('First Choose an Upgrade Ship Design:')
        self.createInRepairQueList('Upgrade Que: Choose Ships to Cancel:')
        self.createCancelRepairList('Ships Selected to Cancel Upgrade:')
    
    def createNewShipDesignList(self, text):
        """List all Ship Designs that are available to be upgraded to"""
        self.newShipDesignList = buttonlist.ButtonList(self.path, text, width=1.0, height=0.55)
        self.newShipDesignList.setMyPosition(-0.56,0.50)
        self.newShipDesignList.setMyMode(self)
        self.newShipDesignList.setOnClickMethod('shipDesignSelected')
        self.myWidgets.append(self.newShipDesignList)
        self.populateNewShipDesignList()
    
    def populateNewShipDesignList(self):
        """Fill the list with Ship designs"""
        for shipDesignID in funcs.sortStringList(self.mode.game.shipDesigns.keys()):
            myShipDesign = self.mode.game.shipDesignObjects[shipDesignID]
            if myShipDesign.hasAllTech == 1:
                color = 'guiwhite'
            else:
                color = 'guigrey'
            self.newShipDesignList.myScrolledList.addItem(text=myShipDesign.name, extraArgs=shipDesignID, 
                                                          textColorName=color)

    def shipDesignSelected(self, shipDesignID, index, button):
        """Fill in Ship Design stats"""
        self.mode.playSound('beep01')
        self.newShipDesign = self.mode.game.shipDesignObjects[shipDesignID]
        self.removeMyWidget(self.newShipDesignList)
        self.createOtherListBoxes()
                
    def createOtherListBoxes(self):
        self.createToRepairList('Ships Selected to Upgrade:')
        self.createDamagedList('Choose Ships to upgrade to: %s:' % self.newShipDesign.name)
        
    def createSelectAlltoRepairButton(self):
        if self.damagedList.myScrolledList.getNumItems() > 0:
            if self.selectAllToRepairButton == None:
                self.selectAllToRepairButton = selectallbutton.SelectAllShipsToUpgradeButton(self.path, x=-0.31, y=0.78)
                self.selectAllToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllToRepairButton)
        else:
            self.removeMyWidget(self.selectAllToRepairButton)
            self.selectAllToRepairButton = None
    
    def createSelectAllinQueButton(self):
        if self.inRepairQueList.myScrolledList.getNumItems() > 0:
            if self.selectAllInQueButton == None:
                self.selectAllInQueButton = selectallbutton.SelectAllShipsInQueForUpgradeButton(self.path, x=-0.31, y=-0.22)
                self.selectAllInQueButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllInQueButton)
        else:
            self.removeMyWidget(self.selectAllInQueButton)
            self.selectAllInQueButton = None
    
    def createSubmitToRepairButton(self):
        if self.toRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToRepairButton == None:
                self.submitToRepairButton = submitbutton.SubmitToUpgradeShipsButton(self.path, x=-0.31, y=0.24)
                self.submitToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToRepairButton)
        else:
            self.removeMyWidget(self.submitToRepairButton)
            self.submitToRepairButton = None
    
    def createSubmitToCancelButton(self):
        if self.cancelRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToCancelButton == None:
                self.submitToCancelButton = submitbutton.SubmitToCancelShipsUpgradeButton(self.path, x=-0.31, y=-0.76)
                self.submitToCancelButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToCancelButton)
        else:
            self.removeMyWidget(self.submitToCancelButton)
            self.submitToCancelButton = None
        
    def populateDamagedFrom(self):
        self.damagedFrom = []
        for shipID in funcs.sortStringList(self.mode.game.myShips.keys()):
            myShip = self.mode.game.myShips[shipID]
            myShipDesign = self.mode.game.shipDesignObjects[myShip['designID']]
            if (myShip['fromSystem'] == myShip['toSystem'] and
                myShip['fromSystem'] == self.mySystemDict['id'] and
                (myShip['strength'] == 100 or (myShip['strength'] < 100 and myShipDesign.hasAllTech == 0)) and 
                self.isNotBeingRepaired(shipID) and
                self.shipCanBeUpgradedToDesign(myShip)):
                self.damagedFrom.append(myShip)
    
    def isNotBeingRepaired(self, shipID):
        """Return 1 if it is not being repaired already"""
        for myOrder in self.repairFrom:
            (id, newdesignID) = string.split(myOrder['value'], '-')
            if shipID == id:
                return 0
        return 1
                
    def shipCanBeUpgradedToDesign(self, myShip):
        """Only Ships of same hull type and not the same design can be upgraded"""
        myShipDesign = self.mode.game.shipDesignObjects[myShip['designID']]
        if myShipDesign.id == self.newShipDesign.id:
            return 0
        if myShipDesign.shipHullID != self.newShipDesign.shipHullID:
            return 0
        return 1
            
    def populateRepairFrom(self):
        self.repairFrom = []
        for industryID in funcs.sortStringList(self.mode.game.myEmpire['industryOrders'].keys()):
            myOrder = self.mode.game.myEmpire['industryOrders'][industryID]
            if myOrder['type'] == 'Upgrade Starship' and myOrder['round'] == self.mode.game.currentRound and myOrder['system'] == self.mySystemDict['id']:
                self.repairFrom.append(myOrder)
        
    def populateInRepairQueList(self):
        """Fill the list with Ship Upgrade Orders"""
        self.totalRepairCosts = [0,0,0,0]
        id = self.inRepairQueList.getSelectedButtonID()
        self.inRepairQueList.myScrolledList.clear()
        for myOrder in self.repairFrom:
            (shipID, designID) = string.split(myOrder['value'], '-')
            myShip = self.mode.game.myShips[shipID]
            upgradeDesign = self.mode.game.shipDesignObjects[designID]
            info = self.mode.game.getShipInfo(myShip['id'])
            self.inRepairQueList.myScrolledList.addItem(text='%s -> %s' % (info, upgradeDesign.name), extraArgs=myOrder)
            self.addToTotalRepairCosts(self.getShipUpgradeCost(myShip, upgradeDesign))
        self.createCurrentResourceBars()
        self.inRepairQueList.focusOnNextButton(id)
        self.createSelectAllinQueButton()
    
    def populateCancelRepairList(self):
        id = self.cancelRepairList.getSelectedButtonID()
        self.cancelRepairList.myScrolledList.clear()
        for myOrder in self.repairTo:
            (shipID, designID) = string.split(myOrder['value'], '-')
            myShip = self.mode.game.myShips[shipID]
            upgradeDesign = self.mode.game.shipDesignObjects[designID]
            info = self.mode.game.getShipInfo(myShip['id'])
            self.cancelRepairList.myScrolledList.addItem(text='%s -> %s' % (info, upgradeDesign.name), extraArgs=myOrder)
        self.cancelRepairList.focusOnNextButton(id)
        self.createSubmitToCancelButton()
        
    def getShipUpgradeCost(self, myShip, upgradeDesign):
        """Return the [CR,AL,EC,IA] cost of doing ship upgrade"""
        myShipDesign = self.mode.game.shipDesignObjects[myShip['designID']]
        costs = myShipDesign.getUpgradeCost(upgradeDesign)
        return [costs[0],costs[1],costs[2],costs[3]]
        
    def submitUpgradeStarshipOrder(self):
        """Setup to send a upgrade starship order to server"""
        submitList = []
        myList = self.getIDList(self.damagedTo)
        for item in myList:
            submitList.append('%s-%s' % (item, self.newShipDesign.id))
        self.mode.upgradeStarshipOrder(submitList, self.mySystemDict['id'])
    
    def submitCancelUpgradeStarshipOrder(self):
        """Setup to send a cancel upgrade starship order to server"""
        myList = self.getIDList(self.repairTo)
        self.mode.cancelUpgradeStarshipOrder(myList, self.mySystemDict['id'])
        
    