# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipyardrepairships.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui allows user to repair ships
# ---------------------------------------------------------------------------
import string
from anw.gui import rootsystem, systemresources, submitbutton
from anw.gui import buttonlist, rootbutton, valuebar, selectallbutton
from anw.func import globals, funcs

class ShipyardRepairShips(rootsystem.RootSystem):
    """The System Shipyard Repair Ships Gui"""
    def __init__(self, path, mySystemDict, myEmpireDict, industrydata, mode):
        rootsystem.RootSystem.__init__(self, path, -0.9, 0.66, mySystemDict,
                                       myEmpireDict, industrydata)
        self.setMyMode(mode)
        self.enableMouseCamControl = 1
        self.game = self.mode.game
        self.currentResourceBars = None
        self.damagedList = None
        self.toRepairList = None
        self.inRepairQueList = None
        self.cancelRepairList = None
        self.selectAllToRepairButton = None
        self.selectAllInQueButton = None
        self.submitToRepairButton = None
        self.submitToCancelButton = None
        self.totalRepairCosts = [0,0,0,0]
        self.damagedFrom = []
        self.damagedTo = []
        self.repairFrom = []
        self.repairTo = []
        self.createMySystemResources()
        self.createListBoxes()

    def createListBoxes(self):
        self.createInRepairQueList('Repair Que: Select Ship to Cancel:')
        self.createDamagedList('Choose Damaged Ships:')
        self.createToRepairList('Ships Selected to Repair:')
        self.createCancelRepairList('Ships Selected to Cancel Repair:')
        
    def createSelectAlltoRepairButton(self):
        if self.damagedList.myScrolledList.getNumItems() > 0:
            if self.selectAllToRepairButton == None:
                self.selectAllToRepairButton = selectallbutton.SelectAllShipsToRepairButton(self.path, x=-0.31, y=0.78)
                self.selectAllToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllToRepairButton)
        else:
            self.removeMyWidget(self.selectAllToRepairButton)
            self.selectAllToRepairButton = None
    
    def createSelectAllinQueButton(self):
        if self.inRepairQueList.myScrolledList.getNumItems() > 0:
            if self.selectAllInQueButton == None:
                self.selectAllInQueButton = selectallbutton.SelectAllShipsInQueButton(self.path, x=-0.31, y=-0.22)
                self.selectAllInQueButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllInQueButton)
        else:
            self.removeMyWidget(self.selectAllInQueButton)
            self.selectAllInQueButton = None
    
    def createSubmitToRepairButton(self):
        if self.toRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToRepairButton == None:
                self.submitToRepairButton = submitbutton.SubmitToRepairShipsButton(self.path, x=-0.31, y=0.24)
                self.submitToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToRepairButton)
        else:
            self.removeMyWidget(self.submitToRepairButton)
            self.submitToRepairButton = None
    
    def createSubmitToCancelButton(self):
        if self.cancelRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToCancelButton == None:
                self.submitToCancelButton = submitbutton.SubmitToCancelShipsButton(self.path, x=-0.31, y=-0.76)
                self.submitToCancelButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToCancelButton)
        else:
            self.removeMyWidget(self.submitToCancelButton)
            self.submitToCancelButton = None
        
    def createMySystemResources(self):
        self.mySystemResources = systemresources.SystemResources(self.path, self.posInitX+0.2, self.posInitY-0.6, 
                                                                 self.mySystemDict, self.myEmpireDict, self.industrydata)
        self.myWidgets.append(self.mySystemResources)

    def createCurrentResourceBars(self):
        """These bars will show the resources used for repairs"""
        self.removeMyWidget(self.currentResourceBars)
        x = (self.posInitX+1.6)
        y = self.posInitY-0.6
        self.currentResourceBars = valuebar.CostBars(self.path, 
                                                     self.totalRepairCosts,
                                                     self.totalRepairCosts,
                                                     x=x,
                                                     y=y,scale=self.scale,extraText='COST OF REPAIRS',
                                                     title='Current Total Cost of Repairs:')
        self.myWidgets.append(self.currentResourceBars)
        
    def selectAllToRepair(self):
        """Select all that can be repaired"""
        self.damagedTo = self.damagedTo + self.damagedFrom
        self.damagedFrom = []
        self.refreshDamaged()
    
    def selectAllInQue(self):
        """Select All that are in the Que"""
        self.repairTo = self.repairTo + self.repairFrom
        self.repairFrom = []
        self.refreshRepair()
        
    def refreshDamaged(self):
        self.mode.playSound('beep01')
        self.populateDamagedList()
        self.populateToRepairList()
        
    def refreshRepair(self):
        self.mode.playSound('beep01')
        self.populateInRepairQueList()
        self.populateCancelRepairList()
        
    def createDamagedList(self, text):
        """List all Ships that are Damaged that can be Repaired"""
        self.damagedList = buttonlist.ButtonList(self.path, text, width=1.0, height=0.55)
        self.damagedList.setMyPosition(-0.56,0.5)
        self.damagedList.setMyMode(self)
        self.damagedList.setOnClickMethod('damagedSelected')
        self.myWidgets.append(self.damagedList)
        self.populateDamagedFrom()
        self.populateDamagedList()
    
    def populateDamagedFrom(self):
        self.damagedFrom = []
        for shipID in funcs.sortStringList(self.mode.game.myShips.keys()):
            myShip = self.mode.game.myShips[shipID]
            if (myShip['fromSystem'] == myShip['toSystem'] and
                myShip['fromSystem'] == self.mySystemDict['id'] and
                myShip['strength'] < 100 and 
                self.isNotBeingRepaired(shipID)):
                self.damagedFrom.append(myShip)
    
    def isNotBeingRepaired(self, shipID):
        """Return 1 if it is not being repaired already"""
        for myOrder in self.repairFrom:
            if shipID == myOrder['value']:
                return 0
        return 1
    
    def populateDamagedList(self):
        """Fill the list with Damaged Ships currently in system"""
        id = self.damagedList.getSelectedButtonID()
        self.damagedList.myScrolledList.clear()
        for myShip in self.damagedFrom:
            info = self.mode.game.getShipInfo(myShip['id'])
            self.damagedList.myScrolledList.addItem(text=info, extraArgs=myShip)
        self.damagedList.focusOnNextButton(id)
        self.createSelectAlltoRepairButton()
    
    def damagedSelected(self, myShip, index, button):
        """Fill in Ship Design stats"""
        self.mode.playSound('beep01')
        if self.canRepair(myShip):
            self.damagedFrom.remove(myShip)
            self.damagedTo.append(myShip)
            self.refreshDamaged()
    
    def canRepair(self, myShip):
        return 1
            
    def createToRepairList(self, text):
        """Create the To Repair List"""
        self.toRepairList = buttonlist.ButtonList(self.path, text, width=1.0, height=0.55)
        self.toRepairList.setMyPosition(0.55,0.5)
        self.toRepairList.setMyMode(self)
        self.toRepairList.setOnClickMethod('toRepairSelected')
        self.myWidgets.append(self.toRepairList)
    
    def toRepairSelected(self, myShip, index, button):
        self.mode.playSound('beep01')
        self.damagedTo.remove(myShip)
        self.damagedFrom.append(myShip)
        self.refreshDamaged()
        
    def populateToRepairList(self):
        id = self.toRepairList.getSelectedButtonID()
        self.toRepairList.myScrolledList.clear()
        for myShip in self.damagedTo:
            info = self.mode.game.getShipInfo(myShip['id'])
            self.toRepairList.myScrolledList.addItem(text=info, extraArgs=myShip)
        self.toRepairList.focusOnNextButton(id)
        self.createSubmitToRepairButton()
        
    def createCancelRepairList(self, text):
        """Create the Cancel Repair List"""
        self.cancelRepairList = buttonlist.ButtonList(self.path, text, width=1.0, height=0.55)
        self.cancelRepairList.setMyPosition(0.55,-0.5)
        self.cancelRepairList.setMyMode(self)
        self.cancelRepairList.setOnClickMethod('cancelRepairSelected')
        self.myWidgets.append(self.cancelRepairList)

    def populateCancelRepairList(self):
        id = self.cancelRepairList.getSelectedButtonID()
        self.cancelRepairList.myScrolledList.clear()
        for myOrder in self.repairTo:
            myShip = self.mode.game.myShips[myOrder['value']]
            info = self.mode.game.getShipInfo(myShip['id'])
            self.cancelRepairList.myScrolledList.addItem(text=info, extraArgs=myOrder)
        self.cancelRepairList.focusOnNextButton(id)
        self.createSubmitToCancelButton()
        
    def createInRepairQueList(self, text):
        """List all Ships to be repaired"""
        self.inRepairQueList = buttonlist.ButtonList(self.path, text, width=1.0, height=0.55)
        self.inRepairQueList.setMyPosition(-0.56,-0.5)
        self.inRepairQueList.setMyMode(self)
        self.inRepairQueList.setOnClickMethod('inRepairQueSelected')
        self.myWidgets.append(self.inRepairQueList)
        self.populateRepairFrom()
        self.populateInRepairQueList()
    
    def populateRepairFrom(self):
        self.repairFrom = []
        for industryID in funcs.sortStringList(self.mode.game.myEmpire['industryOrders'].keys()):
            myOrder = self.mode.game.myEmpire['industryOrders'][industryID]
            if myOrder['type'] == 'Repair Starship' and myOrder['round'] == self.mode.game.currentRound and myOrder['system'] == self.mySystemDict['id']:
                self.repairFrom.append(myOrder)
        
    def populateInRepairQueList(self):
        """Fill the list with Ship Repair Orders"""
        self.totalRepairCosts = [0,0,0,0]
        id = self.inRepairQueList.getSelectedButtonID()
        self.inRepairQueList.myScrolledList.clear()
        for myOrder in self.repairFrom:
            myShip = self.mode.game.myShips[myOrder['value']]
            info = self.mode.game.getShipInfo(myShip['id'])
            self.inRepairQueList.myScrolledList.addItem(text=info, extraArgs=myOrder)
            self.addToTotalRepairCosts(myShip['repairCost'])
        self.createCurrentResourceBars()
        self.inRepairQueList.focusOnNextButton(id)
        self.createSelectAllinQueButton()
    
    def inRepairQueSelected(self, myOrder, index, button):
        """Ship Order Selected for cancellation/modification"""
        self.mode.playSound('beep01')
        self.repairFrom.remove(myOrder)
        self.repairTo.append(myOrder)
        self.refreshRepair()
    
    def cancelRepairSelected(self, myOrder, index, button):
        self.mode.playSound('beep01')
        self.repairTo.remove(myOrder)
        self.repairFrom.append(myOrder)
        self.refreshRepair()
    
    def submitRepairStarshipOrder(self):
        """Setup to send a repair starship order to server"""
        myList = self.getIDList(self.damagedTo)
        self.mode.repairStarshipOrder(myList, self.mySystemDict['id'])
    
    def submitCancelRepairStarshipOrder(self):
        """Setup to send a cancel repair starship order to server"""
        myList = self.getIDList(self.repairTo)
        self.mode.cancelRepairStarshipOrder(myList, self.mySystemDict['id'])
        
    def getIDList(self, dictList):
        """Return just the ID's assuming the items in list have an id key"""
        idList = []
        for myDict in dictList:
            idList.append(myDict['id'])
        return idList
    
    def addToTotalRepairCosts(self, repairCosts):
        """Go through current orders and return total repair costs"""
        for i in range(4):
            self.totalRepairCosts[i] += repairCosts[i]
                        
    
    