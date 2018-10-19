# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# mirepairmarines.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui allows user to repair marine regiments
# ---------------------------------------------------------------------------
from anw.gui import shipyardrepairships, systemresources, submitbutton
from anw.gui import buttonlist, rootbutton, valuebar, selectallbutton
from anw.func import globals, funcs

class MIRepairMarines(shipyardrepairships.ShipyardRepairShips):
    """The Military Installation Repair Marine Regiments Gui"""
    
    def createListBoxes(self):
        self.createInRepairQueList('Choose Marines to Cancel:')
        self.createDamagedList('Choose Damaged Marines:')
        self.createToRepairList('Marines Selected to Repair:')
        self.createCancelRepairList('Marines Selected to Cancel Repair:')
    
    def createSelectAlltoRepairButton(self):
        if self.damagedList.myScrolledList.getNumItems() > 0:
            if self.selectAllToRepairButton == None:
                self.selectAllToRepairButton = selectallbutton.SelectAllRegimentsToRepairButton(self.path, x=-0.31, y=0.78)
                self.selectAllToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllToRepairButton)
        else:
            self.removeMyWidget(self.selectAllToRepairButton)
            self.selectAllToRepairButton = None
        
    def createSelectAllinQueButton(self):
        if self.inRepairQueList.myScrolledList.getNumItems() > 0:
            if self.selectAllInQueButton == None:
                self.selectAllInQueButton = selectallbutton.SelectAllRegimentsInQueButton(self.path, x=-0.31, y=-0.22)
                self.selectAllInQueButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllInQueButton)
        else:
            self.removeMyWidget(self.selectAllInQueButton)
            self.selectAllInQueButton = None
    
    def createSubmitToRepairButton(self):
        if self.toRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToRepairButton == None:
                self.submitToRepairButton = submitbutton.SubmitToRepairRegimentsButton(self.path, x=-0.31, y=0.24)
                self.submitToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToRepairButton)
        else:
            self.removeMyWidget(self.submitToRepairButton)
            self.submitToRepairButton = None
    
    def createSubmitToCancelButton(self):
        if self.cancelRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToCancelButton == None:
                self.submitToCancelButton = submitbutton.SubmitToCancelRegimentsButton(self.path, x=-0.31, y=-0.76)
                self.submitToCancelButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToCancelButton)
        else:
            self.removeMyWidget(self.submitToCancelButton)
            self.submitToCancelButton = None
    
    def populateDamagedFrom(self):
        self.damagedFrom = []
        for regID in funcs.sortStringList(self.mode.game.myRegiments.keys()):
            myRegiment = self.mode.game.myRegiments[regID]
            if (myRegiment['fromSystem'] == myRegiment['toSystem'] and
                myRegiment['fromSystem'] == self.mySystemDict['id'] and
                myRegiment['strength'] < 100 and 
                self.isNotBeingRepaired(regID)):
                self.damagedFrom.append(myRegiment)
    
    def populateDamagedList(self):
        """Fill the list with Damaged Regiments currently in system"""
        id = self.damagedList.getSelectedButtonID()
        self.damagedList.myScrolledList.clear()
        for myRegiment in self.damagedFrom:
            info = self.mode.game.getRegInfo(myRegiment['id'])
            self.damagedList.myScrolledList.addItem(text=info, extraArgs=myRegiment)
        self.damagedList.focusOnNextButton(id)
        self.createSelectAlltoRepairButton()
        
    def populateToRepairList(self):
        id = self.toRepairList.getSelectedButtonID()
        self.toRepairList.myScrolledList.clear()
        for myRegiment in self.damagedTo:
            info = self.mode.game.getRegInfo(myRegiment['id'])
            self.toRepairList.myScrolledList.addItem(text=info, extraArgs=myRegiment)
        self.toRepairList.focusOnNextButton(id)
        self.createSubmitToRepairButton()

    def populateCancelRepairList(self):
        id = self.cancelRepairList.getSelectedButtonID()
        self.cancelRepairList.myScrolledList.clear()
        for myOrder in self.repairTo:
            myRegiment = self.mode.game.myRegiments[myOrder['value']]
            info = self.mode.game.getRegInfo(myRegiment['id'])
            self.cancelRepairList.myScrolledList.addItem(text=info, extraArgs=myOrder)
        self.cancelRepairList.focusOnNextButton(id)
        self.createSubmitToCancelButton()
    
    def populateRepairFrom(self):
        self.repairFrom = []
        for industryID in funcs.sortStringList(self.mode.game.myEmpire['industryOrders'].keys()):
            myOrder = self.mode.game.myEmpire['industryOrders'][industryID]
            if myOrder['type'] == 'Restore Regiment' and myOrder['round'] == self.mode.game.currentRound and myOrder['system'] == self.mySystemDict['id']:
                self.repairFrom.append(myOrder)
        
    def populateInRepairQueList(self):
        """Fill the list with Regiment Repair Orders"""
        self.totalRepairCosts = [0,0,0,0]
        id = self.inRepairQueList.getSelectedButtonID()
        self.inRepairQueList.myScrolledList.clear()
        for myOrder in self.repairFrom:
            myRegiment = self.mode.game.myRegiments[myOrder['value']]
            info = self.mode.game.getRegInfo(myRegiment['id'])
            self.inRepairQueList.myScrolledList.addItem(text=info, extraArgs=myOrder)
            self.addToTotalRepairCosts(myRegiment['restoreCost'])
        self.createCurrentResourceBars()
        self.inRepairQueList.focusOnNextButton(id)
        self.createSelectAllinQueButton()
    
    def submitRepairRegimentOrder(self):
        """Setup to send a restore regiment order to server"""
        myList = self.getIDList(self.damagedTo)
        self.mode.restoreRegimentOrder(myList, self.mySystemDict['id'])
    
    def submitCancelRepairRegimentOrder(self):
        """Setup to send a cancel restore regiment order to server"""
        myList = self.getIDList(self.repairTo)
        self.mode.cancelRestoreRegimentOrder(myList, self.mySystemDict['id'])

