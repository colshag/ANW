# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# miupgrademarines.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This gui allows user to upgrade marine regiments
# ---------------------------------------------------------------------------
from anw.gui import mirepairmarines, submitbutton
from anw.gui import buttonlist, rootbutton, valuebar, selectallbutton
from anw.func import globals, funcs

class MIUpgradeMarines(mirepairmarines.MIRepairMarines):
    """The Military Installation Upgrade Marine Regiments Gui"""
    
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
        self.createInRepairQueList('Choose Marines to Cancel:')
        self.createDamagedList('Choose Marines:')
        self.createToRepairList('Marines Selected to Upgrade:')
        self.createCancelRepairList('Marines Selected to Cancel Upgrade:')
    
    def createSelectAlltoRepairButton(self):
        if self.damagedList.myScrolledList.getNumItems() > 0:
            if self.selectAllToRepairButton == None:
                self.selectAllToRepairButton = selectallbutton.SelectAllRegimentsToUpgradeButton(self.path, x=-0.31, y=0.78)
                self.selectAllToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllToRepairButton)
        else:
            self.removeMyWidget(self.selectAllToRepairButton)
            self.selectAllToRepairButton = None
        
    def createSelectAllinQueButton(self):
        if self.inRepairQueList.myScrolledList.getNumItems() > 0:
            if self.selectAllInQueButton == None:
                self.selectAllInQueButton = selectallbutton.SelectAllRegimentsInQueForUpgradeButton(self.path, x=-0.31, y=-0.22)
                self.selectAllInQueButton.setMyMode(self.mode)
                self.myWidgets.append(self.selectAllInQueButton)
        else:
            self.removeMyWidget(self.selectAllInQueButton)
            self.selectAllInQueButton = None
    
    def createSubmitToRepairButton(self):
        if self.toRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToRepairButton == None:
                self.submitToRepairButton = submitbutton.SubmitToUpgradeRegimentsButton(self.path, x=-0.31, y=0.24)
                self.submitToRepairButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToRepairButton)
        else:
            self.removeMyWidget(self.submitToRepairButton)
            self.submitToRepairButton = None
    
    def createSubmitToCancelButton(self):
        if self.cancelRepairList.myScrolledList.getNumItems() > 0:
            if self.submitToCancelButton == None:
                self.submitToCancelButton = submitbutton.SubmitToCancelRegimentsUpgradeButton(self.path, x=-0.31, y=-0.76)
                self.submitToCancelButton.setMyMode(self.mode)
                self.myWidgets.append(self.submitToCancelButton)
        else:
            self.removeMyWidget(self.submitToCancelButton)
            self.submitToCancelButton = None

    def populateDamagedFrom(self):
        self.damagedFrom = []
        for regID in funcs.sortStringList(self.mode.game.myRegiments.keys()):
            myRegiment = self.mode.game.myRegiments[regID]
            myRegimentData = self.mode.game.regimentdata[myRegiment['typeID']]
            regType = myRegimentData.abr[1]
            if (myRegiment['fromSystem'] == myRegiment['toSystem'] and
                myRegiment['fromSystem'] == self.mySystemDict['id'] and
                myRegiment['strength'] == 100 and 
                regType != 'P' and 
                self.isNotBeingRepaired(regID)):
                if self.techAvailableForUpgrade(myRegiment):
                    self.damagedFrom.append(myRegiment)
    
    def techAvailableForUpgrade(self, myRegiment):
        """Regiments should only be displayed if the tech is available for their upgrade"""
        newDataID = int(myRegiment['typeID'])+10
        newRegimentData = self.mode.game.regimentdata[str(newDataID)]
        if self.mode.game.myTech[newRegimentData.techReq].complete == 1:
            return 1
        return 0
                
    def populateRepairFrom(self):
        self.repairFrom = []
        for industryID in funcs.sortStringList(self.mode.game.myEmpire['industryOrders'].keys()):
            myOrder = self.mode.game.myEmpire['industryOrders'][industryID]
            if myOrder['type'] == 'Upgrade Regiment' and myOrder['round'] == self.mode.game.currentRound and myOrder['system'] == self.mySystemDict['id']:
                self.repairFrom.append(myOrder)
        
    def populateInRepairQueList(self):
        """Fill the list with Regiment Upgrade Orders"""
        self.totalRepairCosts = [0,0,0,0]
        id = self.inRepairQueList.getSelectedButtonID()
        self.inRepairQueList.myScrolledList.clear()
        for myOrder in self.repairFrom:
            myRegiment = self.mode.game.myRegiments[myOrder['value']]
            myRegimentData = self.mode.game.regimentdata[myRegiment['typeID']]
            info = self.mode.game.getRegInfo(myRegiment['id'])
            self.inRepairQueList.myScrolledList.addItem(text=info, extraArgs=myOrder)
            self.addToTotalRepairCosts([myRegimentData.costCR, myRegimentData.costAL,
                                        myRegimentData.costEC, myRegimentData.costIA])
        self.createCurrentResourceBars()
        self.inRepairQueList.focusOnNextButton(id)
        self.createSelectAllinQueButton()
    
    def submitUpgradeRegimentOrder(self):
        """Setup to send an upgrade regiment order to server"""
        myList = self.getIDList(self.damagedTo)
        self.mode.upgradeRegimentOrder(myList, self.mySystemDict['id'])
    
    def submitCancelUpgradeRegimentOrder(self):
        """Setup to send a cancel upgrade regiment order to server"""
        myList = self.getIDList(self.repairTo)
        self.mode.cancelUpgradeRegimentOrder(myList, self.mySystemDict['id'])

