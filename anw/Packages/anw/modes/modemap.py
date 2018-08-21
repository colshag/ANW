# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modemap.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Galactic Map in ANW
# ---------------------------------------------------------------------------
import types
import copy
import string

import mode
from anw.gui import line, system, systemmenu, traderoute, tradevalue, regimentinfo
from anw.gui import armada, army, buttonlist, cancelwarpbutton, textentry, sendmailbutton
from anw.gui import swapcaptainbutton, selectallbutton, shipwarpbutton, regwarpbutton
from anw.gui import decreasediplomacybutton, increasediplomacybutton, textonscreen, groupmoveunits
from anw.gui import sendcreditsvalue, submitbutton
from anw.func import globals, funcs

if globals.serverMode == 0:
    from anw.war import ship, captain
    from anw.gui import shipinfo

class ModeMap(mode.Mode):
    """This is the Map Mode, This Mode allows player to interact with the majority
    of commands dealing with the strategy of the game including systems, fleets, armies"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.resetCamera()
        self.canSelectFlags['creatingTradeRoute'] = 0
        self.canSelectFlags['movingShips'] = 0
        self.canSelectFlags['cancelMovingShips'] = 0
        self.canSelectFlags['movingRegiments'] = 0
        self.canSelectFlags['cancelMovingRegiments'] = 0
        self.canSelectFlags['systemSelected'] = 0
        self.createSelector('select2',5)
        self.createSelector2('select2',5)
        self.zoomCameraDepth = 11.0
        self.name = 'MAP'
        self.diplomacyEmpireID = ''
        self.sendMailText = None
        self.sendMailButton = None
        self.messageText = ''
        self.diplomacyTitle = None
        self.diplomacyDescription1 = None
        self.diplomacyDescription2 = None
        self.diplomacyDescription3 = None
        self.increaseDiplomacyButton = None
        self.decreaseDiplomacyButton = None
        self.systemmenu = None
        self.tradevaluegui = None
        self.movearmygui = None
        self.movearmadagui = None
        self.sendcreditsgui = None
        self.sendcreditsList = None
        self.cancelSendCreditsButton = None
        self.intelList = None
        self.shipList = None
        self.swapList = None
        self.selectedShipID = ''
        self.regList = None
        self.systemList = None
        self.shipFromList = None
        self.shipToList = None
        self.shipWarpButton = None
        self.regFromList = None
        self.regToList = None
        self.regWarpButton = None
        self.cancelWarpShipButton = None
        self.cancelWarpRegButton = None
        self.selectAllShipButton = None
        self.selectAllRegButton = None
        self.selectAllDamagedShipButton = None
        self.selectAllDamagedRegButton = None
        self.swapCaptainButton = None
        self.createMainMenu('R')
        self.systems = {}
        self.myArmadas = {}
        self.otherArmadas = {}
        self.warpedArmadas = {}
        self.myArmies = {}
        self.otherArmies = {}
        self.warpedArmies = {}
        self.radars = {}
        self.warpgates = {}
        self.traderoutes = {}
        self.resources = {}
        self.selectTypes = ['systems', 'traderoutes', 'myArmadas', 'otherArmadas', 'warpedArmadas', 'myArmies', 'warpedArmies', 'otherArmies']
        self.createWarpLines()
        self.createSystems()
        self.createTradeRoutes()
        self.createMyArmadas()
        self.createOtherArmadas()
        self.createWarpedArmadas()
        self.createMyArmies()
        self.createOtherArmies()
        self.createWarpedArmies()
        self.centerCameraOnSim(self.getMyCapitalSystemSim())
        self.selectedArmada = None
        self.selectedArmy = None
        self.shipsFrom = []
        self.shipsTo = []
        self.regFrom = []
        self.regTo = []
        self.selectedSystem = None
        self.shipInfo = None
        self.regInfo = None       
        
    def getMyCapitalSystemSim(self):
        """Return the sim of the biggest system player owns"""
        capitalSystem = '1'
        cityNum = 0
        for systemID, mySystemDict in self.game.allSystems.iteritems():
            if (mySystemDict['myEmpireID'] == self.game.myEmpireID and
                mySystemDict['cities'] > cityNum):
                cityNum = mySystemDict['cities']
                capitalSystem = mySystemDict['id']
        return self.systems[capitalSystem].sim
    
    def createWarpLines(self):
        """Draw the System Warp Lines"""
        for item in self.game.warpLines:
            myWarpLine = line.Line(self.guiMediaPath, (item[0], item[1]), (item[2], item[3]))
            self.gui.append(myWarpLine)
    
    def createSystems(self):
        """Populate all Systems"""
        for systemID, systemDict in self.game.allSystems.iteritems():
            empireDict = self.game.allEmpires[systemDict['myEmpireID']]
            mySystem = system.System(self.guiMediaPath, self, systemDict)
            mySystem.setMyMode(self)
            mySystem.setMyGame(self.game)
            self.systems[mySystem.id] = mySystem
            self.setSpherePickable(mySystem, 'systems')
            self.gui.append(mySystem)
     
    def clearMouseSelection(self):
        """Clear mouse selection before selecting something new"""
        self.stopCameraTasks()
        self.clearAllCanSelectFlags()
        self.hideMySelector()
        self.clearAnyGui()
        self.enableScrollWheelZoom = 1
    
    def clearAnyGui(self):
        if self.canSelectFlags['creatingTradeRoute'] == 0:
            self.removeMyGui('systemmenu')
            self.removeMyGui('tradevaluegui')
        if (self.canSelectFlags['movingShips'] == 0 and
            self.canSelectFlags['cancelMovingShips'] == 0):            
            self.removeMyGui('shipFromList')
            self.removeMyGui('shipToList')
            self.removeMyGui('shipWarpButton')
            self.removeMyGui('cancelWarpShipButton')
            self.removeMyGui('selectAllShipButton')
            self.removeMyGui('selectAllDamagedShipButton')
            self.removeMyGui('swapCaptainButton')
            self.removeMyGui('shipList')
            self.removeMyGui('swapList')
            self.removeMyGui('shipInfo')
            self.removeMyGui('movearmadagui')
            self.shipsFrom = []
            self.shipsTo = []
            self.selectedArmada = None
            self.selectedShipID = ''
        if (self.canSelectFlags['movingRegiments'] == 0 and 
            self.canSelectFlags['cancelMovingRegiments'] == 0):
            self.removeMyGui('regFromList')
            self.removeMyGui('regToList')
            self.removeMyGui('regList')
            self.removeMyGui('regInfo')
            self.removeMyGui('regWarpButton')
            self.removeMyGui('cancelWarpRegButton')
            self.removeMyGui('selectAllRegButton')
            self.removeMyGui('selectAllDamagedRegButton')
            self.removeMyGui('movearmygui')
            self.regFrom = []
            self.regTo = []
            self.selectedArmy = None
        if (self.canSelectFlags['movingShips'] == 0 and
            self.canSelectFlags['movingRegiments'] == 0):
            self.removeMyGui('systemList')
            self.selectedSystem = None
        self.removeMyGui('intelList')
        self.removeMyGui('sendcreditsList')
        self.removeMyGui('cancelSendCreditsButton')
        self.removeMyGui('sendMailText')
        self.removeMyGui('sendMailButton')
        self.removeMyGui('diplomacyTitle')
        self.removeMyGui('diplomacyDescription1')
        self.removeMyGui('diplomacyDescription2')
        self.removeMyGui('diplomacyDescription3')
        self.removeMyGui('increaseDiplomacyButton')
        self.removeMyGui('decreaseDiplomacyButton')
        self.removeMyGui('sendcreditsgui')
        self.messageText = ''
        self.diplomacyEmpireID = ''
 
    def onMouse1Down(self):
        """Allow dynamic picking of an object within mode"""
        #Check to see if we can access the mouse. We need it to do anything else
        if base.mouseWatcherNode.hasMouse():
            #get the mouse position
            mpos = base.mouseWatcherNode.getMouse()
         
            #Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            
            #Do the actual collision pass (Do it only on the selectable for
            #efficiency purposes)
            self.picker.traverse(self.selectable)
            if self.pq.getNumEntries() > 0:
                #if we have hit something, sort the hits so that the closest
                #is first, and highlight that node
                self.pq.sortEntries()
                for selectable in self.selectTypes:
                    name = self.pq.getEntry(0).getIntoNode().getTag(selectable)
                    if name != '':
                        mySelectedDict = getattr(self, selectable)
                        mySelected = mySelectedDict[name]
                        myMethod = getattr(self, '%sSelected' % selectable)
                        if self.validateSelection():
                            myMethod(mySelected)
                        break
    
    def onSpaceBarClear(self):
        """Space bar should reset the view in the mode"""
        self.clearMouseSelection()
        self.zoomOutCamera()
                    
    def systemsSelected(self, mySystem):
        """System Selected"""
        self.playSound('beep01')
        if self.canSelectFlags['creatingTradeRoute'] == 1:
            self.selectTradeListItem(mySystem.id)
        elif self.canSelectFlags['movingShips'] == 1 or self.canSelectFlags['movingRegiments'] == 1:
            self.selectWarpToSystemListItem(mySystem.id)
        elif self.isAnyFlagSelected() == 1:
            return
        else:
            self.selector2.setPos(-1,-1,-1)
            if self.setMySelector(mySystem.sim.getX(), mySystem.sim.getY(), mySystem.sim.getZ(), scale=2.2):
                self.setCanSelectFlag('systemSelected')
                self.createSystemMenu(mySystem.id)
                self.centerCameraOnSim(mySystem.sim)
                self.zoomInCamera()
                
    def selectTradeListItem(self, systemID):
        """Using systemID select the trade list"""
        tradeListButton = self.getListButton(systemID, self.systemmenu.newtradelist.myScrolledList)
        if tradeListButton != None:
            self.systemmenu.newtradelist.myScrolledList.selectButton(tradeListButton, systemID)
    
    def selectWarpToSystemListItem(self, systemID):
        """Using systemID select the system to warp to"""
        warpSystemListButton = self.getListButton(systemID, self.systemList.myScrolledList)
        if warpSystemListButton != None:
            self.systemList.myScrolledList.selectButton(warpSystemListButton, systemID)
    
    def traderoutesSelected(self, myTradeRoute, disableGenRoute=0):
        """Trade Route Selected"""
        if self.isAnyFlagSelected() == 1:
            return
        self.playSound('beep01')
        self.clearMouseSelection()
        if self.setMySelector(myTradeRoute.sim.getX(), myTradeRoute.sim.getY(), myTradeRoute.sim.getZ(), scale=1.0):
            self.tradevaluegui = tradevalue.TradeValue(self.guiMediaPath, myTradeRoute.fromSystemDict,
                                                       myTradeRoute.toSystemDict, myTradeRoute.tradeRouteDict,
                                                       x=-0, y=-0.4)
            self.tradevaluegui.setMyMode(self)
            self.tradevaluegui.enableButton('cancel')
            if disableGenRoute == 1:
                self.tradevaluegui.disableButton('tradegen')
            self.gui.append(self.tradevaluegui)
            self.centerCameraOnSim(myTradeRoute.sim)
            
    def myArmadasSelected(self, myArmada):
        """myArmada Selected"""
        if self.isAnyFlagSelected() == 1:
            return
        self.clearAllCanSelectFlags()
        self.clearAnyGui()
        self.selectedArmada = myArmada
        self.setCanSelectFlag('movingShips')
        self.playSound('beep01')
        if self.setMySelector(myArmada.sim.getX(), myArmada.sim.getY(), myArmada.sim.getZ(), scale=0.5):
            self.createArmadaToSystemList(myArmada.availSystems, 'systemSelectedForShipWarp')
            self.createShipList(myArmada.myShipList)
            self.centerCameraOnSim(myArmada.sim)
    
    def createArmadaToSystemList(self, availSystems, onClickMethod):
        """Create List of Systems to select"""
        if self.systemList != None:
            self.removeMyGui('systemList')
        self.systemList = buttonlist.ButtonList(self.guiMediaPath, 'Choose Destination System:', width=0.5, height=0.5)
        self.systemList.setMyPosition(-0.5,0)
        self.systemList.setMyMode(self)
        self.systemList.setOnClickMethod(onClickMethod)
        self.gui.append(self.systemList)
        self.populateSystemList(availSystems)
    
    def populateSystemList(self, availSystems):
        """Fill the systemList with systems"""
        self.systemList.myScrolledList.clear()
        for systemID in availSystems:
            mySystem = self.game.allSystems[systemID]
            name = funcs.getSystemName(mySystem)
            color = self.game.allEmpires[mySystem['myEmpireID']]['color1']
            self.systemList.myScrolledList.addItem(text=name, 
                                                   extraArgs=systemID, textColorName=color)
    
    def createIntelList(self, myIntel, title):
        """Display Intel gathered"""
        if self.intelList != None:
            self.removeMyGui('intelList')
        self.intelList = buttonlist.ButtonList(self.guiMediaPath, title, width=1.0, height=0.5)
        self.intelList.setMyPosition(-0.45,0.5)
        self.intelList.setMyMode(self)
        self.intelList.myTitle.setMyPosition(-0.99, 0, 0.79)
        self.gui.append(self.intelList)
        self.populateIntelList(myIntel)
        
    def populateIntelList(self, myIntel):
        """Fill the intelList with myIntel"""
        self.intelList.myScrolledList.clear()
        for id, desc in myIntel.iteritems():
            self.intelList.myScrolledList.addItem(text=desc)
    
    def createSendCreditsList(self, title):
        """Display Intel gathered"""
        if self.sendcreditsList != None:
            self.removeMyGui('sendcreditsList')
        self.sendcreditsList = buttonlist.ButtonList(self.guiMediaPath, title, width=1.0, height=0.5)
        self.sendcreditsList.setMyPosition(-0.45,-0.45)
        self.sendcreditsList.setMyMode(self)
        self.sendcreditsList.setOnClickMethod('createCancelSendCreditsButton')
        self.gui.append(self.sendcreditsList)
        self.populateSendCreditsList()
        
    def populateSendCreditsList(self):
        """Fill the Send Credits List with all Send Credit Orders"""
        self.sendcreditsList.myScrolledList.clear()
        for otherEmpireID, amount in self.game.myEmpire['creditsInLieu'].iteritems():
            desc = '%d CREDITS send to: %s' % (amount, self.game.allEmpires[otherEmpireID]['name'])
            self.sendcreditsList.myScrolledList.addItem(text=desc,
                                                        extraArgs=otherEmpireID)
    
    def createSendMailText(self):
        self.sendMailText = textentry.TextEntry(self.guiMediaPath, self, command='onSendMailTextEntered',
                                                   initialText='',
                                                   title='Click Box Below to start, Enter key will enable sending:', lines=16, width=33, 
                                                   x=0.1, z=-0.1, titleWidth=80)
        self.gui.append(self.sendMailText)
        
    def onSendMailTextEntered(self, name):
        self.messageText = name
        self.sendMailButton.enableButton('sendmail')
            
    def createShipList(self, shipList):
        """Create List of Ships to select for details"""
        if self.shipList != None:
            self.removeMyGui('shipList')
        title = self.getShipSummary(shipList)
        self.shipList = buttonlist.ButtonList(self.guiMediaPath, title, width=0.9, height=0.5,titlewidth=50)
        self.shipList.setMyPosition(-0.3,0.6)
        self.shipList.setMyMode(self)
        self.shipList.setOnClickMethod('createShipInfo')
        self.gui.append(self.shipList)
        self.populateShipList(shipList)
    
    def getShipSummary(self, shipList):
        """Return a string summarizing ships in list"""
        platform = 0
        assault = 0
        carrier = 0
        warship = 0
        total = 0
        for shipID in shipList:
            designID = self.game.myShips[shipID]['designID']
            shipDesign = self.game.shipDesignObjects[designID]
            function = shipDesign.myShipHull.function
            if function == 'platform':
                platform += 1
            elif function == 'assault':
                assault += 1
            elif function == 'carrier':
                carrier += 1
            else:
                warship += 1
        total = platform+assault+carrier+warship
        s = '%d Ships:  ' % total
        if platform > 0:
            s = s + '(%d Platform) ' % platform
        if assault > 0:
            s = s + '(%d Assault) ' % assault
        if carrier > 0:
            s = s + '(%d Carrier) ' % carrier
        if warship > 0:
            s = s + '(%d Warship) ' % warship
        return s
                
        
    def populateShipList(self, shipList):
        """Fill the shipList with ships"""
        self.shipList.myScrolledList.clear()
        sortedShipList = self.getSortedShipListByExp(shipList)
        for shipID in sortedShipList:
            info = self.game.getShipInfo(shipID)
            self.shipList.myScrolledList.addItem(text=info, extraArgs=shipID)
    
    def getSortedShipListByExp(self, shipList):
        d = {}
        for shipID in shipList:
            myShipDict = self.game.myShips[shipID]
            myCaptainDict = self.game.myCaptains[myShipDict['captainID']]
            d[shipID] = myCaptainDict['experience']
        sortedShipList = funcs.sortDictByValue(d, True)
        return sortedShipList
    
    def getSortedRegListByGlory(self, regList):
        d = {}
        for regID in regList:
            myRegDict = self.game.myRegiments[regID]
            d[regID] = myRegDict['glory']
        sortedRegList = funcs.sortDictByValue(d, True)
        return sortedRegList
    
    def createSwapList(self, shipList):
        """Create List of Ships to select for captain swap"""
        if self.swapList != None:
            self.removeMyGui('swapList')
        self.removeMyGui('systemList')
        self.removeMyGui('shipFromList')
        self.removeMyGui('shipToList')
        self.removeMyGui('selectAllShipButton')
        self.swapList = buttonlist.ButtonList(self.guiMediaPath, 'Choose Ship to Swap Captain With:', width=0.9, height=0.5)
        self.swapList.setMyPosition(-0.3,0)
        self.swapList.setMyMode(self)
        self.swapList.setOnClickMethod('swapShipCaptains')
        self.gui.append(self.swapList)
        self.populateSwapList(shipList)

    def populateSwapList(self, shipList):
        """Fill the swapList with ships"""
        self.swapList.myScrolledList.clear()
        sortedList = self.getSortedShipListByExp(shipList)
        for shipID in sortedList:
            info = self.game.getShipInfo(shipID)
            self.swapList.myScrolledList.addItem(text=info, extraArgs=shipID)
    
    def swapShipCaptains(self, shipTwoID, index, button):
        """Ship Selected for Captain Swap"""
        shipOneID = self.selectedShipID
        if (shipOneID not in self.game.myShips.keys() or
            shipTwoID not in self.game.myShips.keys()):
            self.modeMsgBox('Invalid Ships Chosen for captain swap')
            return
        try:
            serverResult = self.game.server.swapCaptains(self.game.authKey, shipOneID, shipTwoID)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            elif serverResult == 1:
                myShipOneDict = self.game.myShips[shipOneID]
                myShipTwoDict = self.game.myShips[shipTwoID]
                shipTwoCaptain = myShipTwoDict['captainID']
                myShipTwoDict['captainID'] = myShipOneDict['captainID']
                myShipOneDict['captainID'] = shipTwoCaptain
                self.modeMsgBox('Ship %s and Ship %s Have swapped Captains' % (shipOneID, shipTwoID))
                self.clearMouseSelection()
        except:
            self.modeMsgBox('swapShipCaptains->Connection to Server Lost')
            
    def sortAllCaptains(self, shipList):
        """Ship Selected for Captain Swap"""
        try:
            systemID = self.game.myShips[shipList[0]]['fromSystem']
            serverResult = self.game.server.sortAllCaptains(self.game.authKey, systemID, shipList)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.refreshShipCaptains(serverResult)
                self.clearMouseSelection()
        except:
            self.modeMsgBox('sortAllCaptains->Connection to Server Lost')
    
    def refreshShipCaptains(self, serverResults):
        """The Server has re-sorted Ship Captains, transfer this to the client"""
        for shipID, captainID in serverResults.iteritems():
            myShipDict = self.game.myShips[shipID]
            myShipDict['captainID'] = captainID
            self.modeMsgBox('%s captain is <%s>%s' % (myShipDict['name'], self.game.myCaptains[captainID]['rank'], self.game.myCaptains[captainID]['name']))
            
    def createRegList(self, regList):
        """Create List of Regiments to select for details"""
        if self.regList != None:
            self.removeMyGui('regList')
        title = self.getRegimentSummary(regList)
        self.regList = buttonlist.ButtonList(self.guiMediaPath, title, width=0.9, height=0.5,titlewidth=50)
        self.regList.setMyPosition(-0.4,0.6)
        self.regList.setMyMode(self)
        self.regList.setOnClickMethod('createRegInfo')
        self.gui.append(self.regList)
        self.populateRegList(regList)
    
    def getRegimentSummary(self, regList):
        """Return a string summarizing regiments in list"""
        inf = 0
        mec = 0
        art = 0
        for regID in regList:
            myRegiment = self.game.myRegiments[regID]
            if self.game.regimentdata[myRegiment['typeID']].abr[2] == 'I':
                inf += 1
            elif self.game.regimentdata[myRegiment['typeID']].abr[2] == 'M':
                mec += 1
            else:
                art += 1
        tot = inf+mec+art
        s = '%d Regiments:  ' % tot
        if inf > 0:
            s = s + '(%d Infantry) ' % inf
        if mec > 0:
            s = s + '(%d Mechanized) ' % mec
        if art > 0:
            s = s + '(%d Artillery) ' % art
        return s
        
    def populateRegList(self, regList):
        """Fill the regList with regiments"""
        self.regList.myScrolledList.clear()
        sortedList = self.getSortedRegListByGlory(regList)
        for regID in sortedList:
            info = self.game.getRegInfo(regID)
            self.regList.myScrolledList.addItem(text=info, extraArgs=regID)            
            
    def myArmiesSelected(self, myArmy):
        """myArmy Selected"""
        if self.isAnyFlagSelected() == 1:
            return
        self.clearAllCanSelectFlags()
        self.clearAnyGui()
        self.selectedArmy = myArmy
        self.setCanSelectFlag('movingRegiments')
        self.playSound('beep01')
        if self.setMySelector(myArmy.sim.getX(), myArmy.sim.getY(), myArmy.sim.getZ(), scale=0.5):
            self.createArmyToSystemList(myArmy.availSystems, 'systemSelectedForRegWarp')
            self.createRegList(myArmy.myRegList)
            self.centerCameraOnSim(myArmy.sim)
      
    def createArmyToSystemList(self, availSystems, onClickMethod):
        """Create List of Systems to select"""
        if self.systemList != None:
            self.removeMyGui('systemList')
        self.systemList = buttonlist.ButtonList(self.guiMediaPath, 'Choose Destination System:', width=0.5, height=0.5)
        self.systemList.setMyPosition(-0.6,0)
        self.systemList.setMyMode(self)
        self.systemList.setOnClickMethod(onClickMethod)
        self.gui.append(self.systemList)
        self.populateSystemList(availSystems)
    
    def createShipInfo(self, shipID, index, button):
        """Display information about selected ship"""
        self.selectedShipID = shipID
        shipList = self.getSwapCaptainShipList()
        if shipList != []:
            self.selectedShipID = shipID
            myShipDict = self.game.myShips[shipID]
            if myShipDict['fromSystem'] == myShipDict['toSystem']:
                self.createSwapCaptainButton(shipList)
        myShipDict = self.game.myShips[shipID]
        myCaptainDict = self.game.myCaptains[myShipDict['captainID']]
        myCaptain = captain.Captain(myCaptainDict)
        myShipDesign = self.game.shipDesignObjects[myShipDict['designID']]
        myShip = ship.Ship(myShipDict)
        myShip.setMyGalaxy(self.game)
        myShip.setMyCaptain(myCaptain)
        myShip.setMyDesign(myShipDesign)
        myShip.setFromDict(myShipDesign, myShipDict)
        self.removeShipInfo()
        self.shipInfo = shipinfo.ShipInfo(self.guiMediaPath, myShip, 0.3, 0.84)
        self.shipInfo.setMyMode(self)
        self.gui.append(self.shipInfo)        
    
    def getSwapCaptainShipList(self):
        """Which Ships can swap captains with selectedShipID"""
        myShip = self.game.myShips[self.selectedShipID]
        list = []
        for id, myShipDict in self.game.myShips.iteritems():
            if (myShipDict['fromSystem'] == myShip['fromSystem'] and
                myShipDict['toSystem'] == myShip['toSystem'] and
                id != self.selectedShipID):
                list.append(id)
        return list
        
    def createSwapCaptainButton(self, shipList):
        if self.swapCaptainButton == None:
            self.swapCaptainButton = swapcaptainbutton.SwapCaptainButton(self.guiMediaPath, -0.1, 0.35, shipList)
            self.swapCaptainButton.setMyMode(self)
            self.gui.append(self.swapCaptainButton)
        
    def removeShipInfo(self):
        if self.shipInfo != None:
            self.removeMyGui('shipInfo')
    
    def createRegInfo(self, regimentID, index, button):
        """Display the Selected Regiment Info"""
        self.removeRegInfo()
        myRegiment = self.game.myRegiments[regimentID]
        myRegimentData = self.game.regimentdata[myRegiment['typeID']]
        self.regInfo = regimentinfo.RegimentInfo(self.guiMediaPath, self.game.myEmpireID,
                                                 myRegiment, myRegimentData, 0.10, 0.65)
        self.regInfo.setMyMode(self)
        self.regInfo.writeAttributes()
        self.gui.append(self.regInfo)
    
    def removeRegInfo(self):
        if self.regInfo != None:
            self.removeMyGui('regInfo')
            
    def systemSelectedForShipWarp(self, systemID, index, button):
        """System selected for ship warp"""
        self.removeMyGui('shipFromList')
        self.removeMyGui('shipToList')
        self.removeMyGui('selectAllShipButton')
        self.removeMyGui('movearmadagui')
        self.selectedSystem = self.systems[systemID]
        self.playSound('beep01')
        if self.setMySelector2(self.selectedSystem.sim.getX(), self.selectedSystem.sim.getY(), self.selectedSystem.sim.getZ(), scale=2.2):
            self.shipsFrom = copy.copy(self.selectedArmada.myShipList)
            self.shipsTo = []
            self.createShipFromList('addShipsToRemoveShipsFrom', 'Choose Ships to Warp:')
            self.populateShipFromListToWarp()
            self.createShipToList('addShipsFromRemoveShipsTo', 'Ships to Warp to:%s' % self.selectedSystem.textName.text)
            self.createSelectAllShipButton()
            self.createSelectAllDamagedShipButton()
            self.createMoveArmadaGui()
            
    def createShipFromList(self, onClickMethod, title):
        """Create List of Ships to select"""
        self.shipFromList = buttonlist.ButtonList(self.guiMediaPath, title, width=0.9, height=0.5)
        self.shipFromList.setMyPosition(-0.3,-0.6)
        self.shipFromList.setMyMode(self)
        self.shipFromList.setOnClickMethod(onClickMethod)
        self.gui.append(self.shipFromList)
    
    def populateShipFromListToWarp(self):
        """Fill the List with ships"""
        id = self.shipFromList.getSelectedButtonID()
        self.shipFromList.myScrolledList.clear()
        sortedList = self.getSortedShipListByExp(self.shipsFrom)
        for shipID in sortedList:
            myShipDict = self.game.myShips[shipID]
            info = self.game.getShipInfo(shipID)
            systemDict = self.game.allSystems[myShipDict['fromSystem']]
            self.shipFromList.myScrolledList.addItem(text='%s <- %s' % (info, systemDict['name']), 
                                                     extraArgs=shipID)
        self.shipFromList.focusOnNextButton(id)
            
    def populateShipFromListToCancelWarp(self):
        """Fill the List with ships"""
        id = self.shipFromList.getSelectedButtonID()
        self.shipFromList.myScrolledList.clear()
        sortedList = self.getSortedShipListByExp(self.shipsFrom)
        for shipID in sortedList:
            myShipDict = self.game.myShips[shipID]
            info = self.game.getShipInfo(shipID)
            systemDict = self.game.allSystems[myShipDict['fromSystem']]
            self.shipFromList.myScrolledList.addItem(text='%s <- %s' % (info, systemDict['name']), 
                                                     extraArgs=shipID)
        self.shipFromList.focusOnNextButton(id)
            
    def createShipToList(self, onClickMethod, title):
        """Create List of Ships"""
        self.shipToList = buttonlist.ButtonList(self.guiMediaPath, title, width=0.9, height=0.5)
        self.shipToList.setMyPosition(0.7,-0.6)
        self.shipToList.setMyMode(self)
        self.shipToList.setOnClickMethod(onClickMethod)
        self.gui.append(self.shipToList)
            
    def populateShipToList(self):
        """Fill the List with ships"""
        id = self.shipToList.getSelectedButtonID()
        self.shipToList.myScrolledList.clear()
        sortedList = self.getSortedShipListByExp(self.shipsTo)
        for shipID in sortedList:
            myShipDict = self.game.myShips[shipID]
            info = self.game.getShipInfo(shipID)
            systemDict = self.game.allSystems[myShipDict['fromSystem']]
            self.shipToList.myScrolledList.addItem(text='%s <- %s' % (info, systemDict['name']), 
                                                     extraArgs=shipID)
        self.shipToList.focusOnNextButton(id)

    def addShipsToRemoveShipsFrom(self, shipID, index, button):
        """Ship selected for ship warp"""
        self.shipsFrom.remove(shipID)
        self.shipsTo.append(shipID)
        self.refreshShipLists()
        self.removeMyGui('movearmadagui')

    def addShipsFromRemoveShipsTo(self, shipID, index, button):
        """Ship selected to be cancelled for warp"""
        self.shipsFrom.append(shipID)
        self.shipsTo.remove(shipID)
        self.refreshShipLists()
        self.removeMyGui('movearmadagui')
    
    def refreshShipLists(self):
        """Refresh Ship Lists and Warp Button"""
        self.playSound('beep01')
        self.populateShipFromListToWarp()
        self.populateShipToList()
        self.createSelectAllShipButton()
        self.createSelectAllDamagedShipButton()
        if self.systemList != None:
            self.createShipWarpButton()
        else:
            self.createCancelWarpShipButton()
    
    def refreshRegLists(self):
        """Refresh Regiment Lists and Warp Button"""
        self.playSound('beep01')
        self.populateRegFromListToWarp()
        self.populateRegToList()
        self.createSelectAllRegButton()
        self.createSelectAllDamagedRegButton()
        if self.systemList != None:
            self.createRegWarpButton()
        else:
            self.createCancelWarpRegButton()
    
    def createShipWarpButton(self):
        if self.shipToList.myScrolledList.getNumItems() > 0:
            if self.shipWarpButton == None:
                self.shipWarpButton = shipwarpbutton.ShipWarpButton(self.guiMediaPath)
                self.shipWarpButton.setMyMode(self)
                self.gui.append(self.shipWarpButton)
        else:
            self.removeMyGui('shipWarpButton')
    
    def createCancelWarpShipButton(self):
        if self.shipToList.myScrolledList.getNumItems() > 0:
            if self.cancelWarpShipButton == None:
                self.cancelWarpShipButton = cancelwarpbutton.CancelWarpButton(self.guiMediaPath)
                self.cancelWarpShipButton.setMyMode(self)
                self.gui.append(self.cancelWarpShipButton)
        else:
            self.removeMyGui('cancelWarpShipButton')

    def createSendMailButton(self):
        if self.sendMailButton == None:
            self.sendMailButton = sendmailbutton.SendMailButton(self.guiMediaPath)
            self.sendMailButton.setMyMode(self)
            self.sendMailButton.disableButton('sendmail')
            self.gui.append(self.sendMailButton)
        else:
            self.removeMyGui('sendMailButton')            
    
    def createSelectAllShipButton(self):
        if self.shipFromList.myScrolledList.getNumItems() > 0:
            if self.selectAllShipButton == None:
                self.selectAllShipButton = selectallbutton.SelectAllShipButton(self.guiMediaPath)
                self.selectAllShipButton.setMyMode(self)
                self.gui.append(self.selectAllShipButton)
        else:
            self.removeMyGui('selectAllShipButton')
            
    def createSelectAllDamagedShipButton(self):
        for shipID in self.shipsFrom:
            myShip = self.game.myShips[shipID]
            if myShip['strength'] < 100:
                if self.selectAllDamagedShipButton == None:
                    self.selectAllDamagedShipButton = selectallbutton.SelectAllDamagedShipsButton(self.guiMediaPath)
                    self.selectAllDamagedShipButton.setMyMode(self)
                    self.gui.append(self.selectAllDamagedShipButton)
                    return
        else:
            self.removeMyGui('selectAllDamagedShipButton')
    
    def createSelectAllRegButton(self):
        if self.regFromList.myScrolledList.getNumItems() > 0:
            if self.selectAllRegButton == None:
                self.selectAllRegButton = selectallbutton.SelectAllRegButton(self.guiMediaPath)
                self.selectAllRegButton.setMyMode(self)
                self.gui.append(self.selectAllRegButton)
        else:
            self.removeMyGui('selectAllRegButton')
            
    def createSelectAllDamagedRegButton(self):
        for regID in self.regFrom:
            myReg = self.game.myRegiments[regID]
            if myReg['strength'] < 100:
                if self.selectAllDamagedRegButton == None:
                    self.selectAllDamagedRegButton = selectallbutton.SelectAllDamagedRegimentsButton(self.guiMediaPath)
                    self.selectAllDamagedRegButton.setMyMode(self)
                    self.gui.append(self.selectAllDamagedRegButton)
                    return
        else:
            self.removeMyGui('selectAllDamagedRegButton')
            
    def warpedArmadasSelected(self, warpedArmada):
        """warpedArmada Selected"""
        if self.isAnyFlagSelected() == 1:
            return
        self.clearAllCanSelectFlags()
        self.clearAnyGui()
        self.selectedArmada = warpedArmada
        self.setCanSelectFlag('cancelMovingShips')
        self.playSound('beep01')
        if self.setMySelector(warpedArmada.sim.getX(), warpedArmada.sim.getY(), warpedArmada.sim.getZ(), scale=0.5):
            self.shipsFrom = copy.copy(self.selectedArmada.myShipList)
            self.shipsTo = []
            self.createShipFromList('addShipsToRemoveShipsFrom', 'Ships to Cancel:')
            self.populateShipFromListToCancelWarp()
            self.createShipToList('addShipsFromRemoveShipsTo', 'Ships to be Cancelled for Warp:')
            self.createShipList(warpedArmada.myShipList)
            self.createSelectAllShipButton()
            self.createSelectAllDamagedShipButton()
            self.centerCameraOnSim(warpedArmada.sim)
            
    def otherArmadasSelected(self, otherArmada):
        """otherArmada Selected"""
        if self.isAnyFlagSelected() == 1:
            return
        self.playSound('beep01')
        self.clearAllCanSelectFlags()
        self.clearAnyGui()
        self.clearMouseSelection()
        if self.setMySelector(otherArmada.sim.getX(), otherArmada.sim.getY(), otherArmada.sim.getZ(), scale=0.5):
            self.centerCameraOnSim(otherArmada.sim)
            self.displayOtherArmadaIntel(otherArmada)
    
    def displayOtherArmadaIntel(self, otherArmada):
        """Display whatever intel is available for this otherArmada selected"""
        otherEmpire = self.game.allEmpires[otherArmada.myEmpireID]
        otherSystem = self.game.allSystems[otherArmada.myGuiSystem.id]
        roundNum = otherSystem['intelReport']['round']
        shipReport = otherSystem['intelReport']['shipReport']
        title = '(%s) Best Armada Intel Available (Based on Scans from Round %d):' % (otherEmpire['name'], roundNum)
        self.createIntelList(shipReport, title)
        self.createDiplomacyGui(otherArmada.myEmpireID)
    
    def createDiplomacyGui(self, empireID):
        """Create Diplomacy and Send Message Gui and send credits Gui"""
        if empireID != '0':
            self.diplomacyEmpireID = empireID
            self.createSendMailText()
            self.createSendMailButton()
            self.createDiplomacyTitle()
            self.createDiplomacyDescription1()
            self.createDiplomacyDescription2()
            self.createDiplomacyDescription3()
            self.createIncreaseDiplomacyButton()
            self.createDecreaseDiplomacyButton()
            self.createSendCredits()
            self.createSendCreditsList('Credits you will be sending this turn:')
    
    def createSendCredits(self):
        name = self.game.allEmpires[self.diplomacyEmpireID]['name']
        self.sendcreditsgui = sendcreditsvalue.SendCreditsValue(self.guiMediaPath, self.game.myEmpire, self.diplomacyEmpireID, name)
        self.sendcreditsgui.setMyMode(self)
        self.gui.append(self.sendcreditsgui)
    
    def createDiplomacyTitle(self):
        title = 'Your Current Diplomacy Status:'
        self.diplomacyTitle = textonscreen.TextOnScreen(self.guiMediaPath, title,
                                                          scale=0.04, font=5, parent=aspect2d)
        self.diplomacyTitle.writeTextToScreen(0.1, 0, 0.53, 35)
        self.diplomacyTitle.setCardColor(globals.colors['guiblue3'], 0.1, 0.1, 0.1, 0.1)
        self.gui.append(self.diplomacyTitle)
    
    def createDiplomacyDescription1(self):
        d = self.game.myEmpire['diplomacy'][self.diplomacyEmpireID]
        d2 = globals.diplomacy[d['diplomacyID']]
        s = '<<%s>>  :  %s  ' % (d2['name'], d2['description'])
        self.diplomacyDescription1 = textonscreen.TextOnScreen(self.guiMediaPath, s,
                                                          scale=0.03, font=5, parent=aspect2d)
        self.diplomacyDescription1.writeTextToScreen(0.1, 0, 0.23, 35)
        self.diplomacyDescription1.setCardColor(globals.colors['guiblue3'], 0.1, 0.1, 0.5, 0.5)
        self.diplomacyDescription1.setColor(globals.colors['guiwhite'])
        self.gui.append(self.diplomacyDescription1)
    
    def createDiplomacyDescription2(self):
        d = self.game.myEmpire['diplomacy'][self.diplomacyEmpireID]
        if d['myIntent'] == 'none':
            s = 'You have not submitted for any change in diplomatic Relations with this empire for next turn yet'
            color = 'guiyellow'
        elif d['myIntent'] == 'increase':
            s = 'You have submitted to increase relations for next turn, they will be notified of your good intentions'
            color = 'guigreen'
        else:
            s = 'You have submitted to decrease relations for next turn, they will not be notified of this'
            color = 'guired'
        
        self.diplomacyDescription2 = textonscreen.TextOnScreen(self.guiMediaPath, s,
                                                          scale=0.03, font=5, parent=aspect2d)
        self.diplomacyDescription2.writeTextToScreen(0.1, 0, 0.4, 35)
        self.diplomacyDescription2.setCardColor(globals.colors['guiblue3'], 0.1, 0.1, 0.1, 0.1)
        self.diplomacyDescription2.setColor(globals.colors[color])
        self.gui.append(self.diplomacyDescription2)

    def createDiplomacyDescription3(self):
        d = self.game.myEmpire['diplomacy'][self.diplomacyEmpireID]
        if d['empireIntent'] == 'increase':
            s = 'This Empire has submitted to increase relations with you for next turn'
            color = 'guigreen'
        else:
            s = 'You do not detect any change in relations from this Empire for next turn so far.'
            color = 'guiyellow'
        
        self.diplomacyDescription3 = textonscreen.TextOnScreen(self.guiMediaPath, s,
                                                          scale=0.03, font=5, parent=aspect2d)
        self.diplomacyDescription3.writeTextToScreen(0.1, 0, 0.305, 35)
        self.diplomacyDescription3.setCardColor(globals.colors['guiblue3'], 0.1, 0.1, 0.1, 0.1)
        self.diplomacyDescription3.setColor(globals.colors[color])
        self.gui.append(self.diplomacyDescription3)
        
    def createIncreaseDiplomacyButton(self):
        if self.increaseDiplomacyButton == None:
            self.increaseDiplomacyButton = increasediplomacybutton.IncreaseDiplomacyButton(self.guiMediaPath)
            self.increaseDiplomacyButton.setMyMode(self)
            self.gui.append(self.increaseDiplomacyButton)
        else:
            self.removeMyGui('increaseDiplomacyButton')
            
    def createDecreaseDiplomacyButton(self):
        if self.decreaseDiplomacyButton == None:
            self.decreaseDiplomacyButton = decreasediplomacybutton.DecreaseDiplomacyButton(self.guiMediaPath)
            self.decreaseDiplomacyButton.setMyMode(self)
            self.gui.append(self.decreaseDiplomacyButton)
        else:
            self.removeMyGui('decreaseDiplomacyButton')
        
    def warpShips(self):
        """Send Warp Ships command to Server"""
        try:
            serverResult = self.game.server.moveShips(self.game.authKey, self.shipsTo, self.selectedSystem.id)
            if serverResult == 1:
                self.modeMsgBox('Ships Warped to %s' % self.selectedSystem.textName.text)
                self.playSound('warp')
                self.updateWarpedShips()
            elif type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('moveShips->Connection to Server Lost')
    
    def updateWarpedShips(self):
        """Update the Ships that have gone through warp to Server"""
        fromShips = copy.copy(self.shipsFrom)
        toShips = copy.copy(self.shipsTo)
        fromSystem = copy.copy(self.selectedArmada.id)
        toSystem = self.selectedSystem.id
        
        if fromShips == []:
            del self.game.myArmadas[fromSystem]
            del self.myArmadas[fromSystem]
            self.selectedArmada.destroy()
            self.selectedArmada = None
        else:
            self.game.myArmadas[fromSystem] = fromShips
            self.selectedArmada.refreshMyShipList()
        for shipID in self.shipsTo:
            myShip = self.game.myShips[shipID]
            myShip['toSystem'] = toSystem
            myShip['oldAvailSystems'] = copy.copy(myShip['availSystems'])
            myShip['availSystems'] = fromSystem
            
        self.addToWarpedArmada(toSystem, toShips)
        self.updateSystemUnits([fromSystem, toSystem])
        self.updateSystemWarpInfo([fromSystem, toSystem])
        self.clearMouseSelection()
    
    def updateSystemWarpInfo(self, systemList):
        for systemID in systemList:
            mySystemGui = self.systems[systemID]
            systemDict = mySystemGui.systemDict
            d = self.game.myEmpire['diplomacy'][systemDict['myEmpireID']]
            d2 = globals.diplomacy[d['diplomacyID']]
            if systemDict['myEmpireID'] == self.game.myEmpireID or d2['alliance'] == 1:
                self.getSystemUpdate(['usedWGC', 'availWGC'], systemID)
            mySystemGui.writeName()
                
    def addToWarpedArmada(self, systemID, shipList):
        """Add ships to warpedarmada"""
        if systemID not in self.game.warpedArmadas.keys():
            self.game.warpedArmadas[systemID] = shipList
            self.createWarpedArmada(systemID)
        else:
            self.game.warpedArmadas[systemID] = self.game.warpedArmadas[systemID] + shipList
            self.warpedArmadas[systemID].refreshMyShipList()
            
    def cancelWarpShips(self):
        """Send Cancel Warp Ships command to Server"""
        try:
            serverResult = self.game.server.cancelMoveShips(self.game.authKey, self.shipsTo)
            if serverResult == 1:
                self.modeMsgBox('Cancel Ship Warp')
                self.playSound('cancelwarp')
                self.updateCancelWarpedShips()
            elif type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('cancelMoveShips->Connection to Server Lost')
            
    def updateCancelWarpedShips(self):
        """Update the Ships that have cancelled warp to Server"""
        fromShips = copy.copy(self.shipsFrom)
        toShips = copy.copy(self.shipsTo)
        toSystem = copy.copy(self.selectedArmada.id)
        systemList = [toSystem]
        
        if fromShips == []:
            del self.game.warpedArmadas[toSystem]
            del self.warpedArmadas[toSystem]
            self.selectedArmada.destroy()
            self.selectedArmada = None
        else:
            self.game.warpedArmadas[toSystem] = fromShips
            self.selectedArmada.refreshMyShipList()
        for shipID in self.shipsTo:
            myShip = self.game.myShips[shipID]
            fromSystem = copy.copy(myShip['fromSystem'])
            if fromSystem not in systemList:
                systemList.append(fromSystem)
            myShip['toSystem'] = fromSystem
            myShip['availSystems'] = copy.copy(myShip['oldAvailSystems'])
            self.addToMyArmada(fromSystem, shipID)
                
        self.updateSystemUnits(systemList)
        self.updateSystemWarpInfo(systemList)
        self.clearMouseSelection()
        
    def addToMyArmada(self, systemID, shipID):
        """Add ships back to myArmada"""
        if systemID not in self.game.myArmadas.keys():
            self.game.myArmadas[systemID] = [shipID]
            self.createMyArmada(systemID)
        else:
            self.game.myArmadas[systemID].append(shipID)
            self.myArmadas[systemID].refreshMyShipList()

    def systemSelectedForRegWarp(self, systemID, index, button):
        """System selected for Regiment warp"""
        self.removeMyGui('regFromList')
        self.removeMyGui('regToList')
        self.removeMyGui('selectAllRegButton')
        self.removeMyGui('movearmygui')
        self.selectedSystem = self.systems[systemID]
        self.playSound('beep01')
        if self.setMySelector2(self.selectedSystem.sim.getX(), self.selectedSystem.sim.getY(), self.selectedSystem.sim.getZ(), scale=2.2):
            self.regFrom = copy.copy(self.selectedArmy.myRegList)
            self.regTo = []
            self.createRegFromList('addRegToRemoveRegFrom', 'Choose Marine to Warp:')
            self.populateRegFromListToWarp()
            self.createRegToList('addRegFromRemoveRegTo', 'Marine to Warp to:%s' % self.selectedSystem.textName.text)
            self.createSelectAllRegButton()
            self.createSelectAllDamagedRegButton()
            self.createMoveArmiesGui()
    
    def createMoveArmiesGui(self):
        """Create the Move Armies Gui to allow mass movement of army types"""
        availList = self.getAvailMarineList()
        self.movearmygui = groupmoveunits.MoveArmies(self.guiMediaPath, -0.2, -0.1, 'movearmies', availList)
        self.movearmygui.setMyMode(self)
        self.gui.append(self.movearmygui)
    
    def createMoveArmadaGui(self):
        """Create the Move Armada Gui to allow mass movement of ships"""
        availList = self.getAvailShipList()
        self.movearmadagui = groupmoveunits.MoveShips(self.guiMediaPath, -0.2, -0.1, 'movearmada', availList)
        self.movearmadagui.setMyMode(self)
        self.gui.append(self.movearmadagui)
    
    def populateArmyMove(self, currentByType):
        """Move Army Group in Bulk given a army list [M, A, I]"""
        while currentByType[0] > 0:
            self.moveRegByType('M')
            currentByType[0] -= 1
        while currentByType[1] > 0:
            self.moveRegByType('A')
            currentByType[1] -= 1
        while currentByType[2] > 0:
            self.moveRegByType('I')
            currentByType[2] -= 1
        self.refreshRegLists()
        self.removeMyGui('movearmygui')
    
    def populateArmadaMove(self, currentByType):
        """Move Armada Group in Bulk given a ship list [Platform, Assault, Warship]"""
        while currentByType[0] > 0:
            self.moveShipByType(['platform'])
            currentByType[0] -= 1
        while currentByType[1] > 0:
            self.moveShipByType(['assault'])
            currentByType[1] -= 1
        while currentByType[2] > 0:
            self.moveShipByType(['carrier', 'warship'])
            currentByType[2] -= 1
        self.refreshShipLists()
        self.removeMyGui('movearmadagui')
    
    def moveShipByType(self, hulltype):
        """Move the Ship based on its hulltype"""
        for shipID in self.shipsFrom:
            designID = self.game.myShips[shipID]['designID']
            shipDesign = self.game.shipDesignObjects[designID]
            function = shipDesign.myShipHull.function
            if function in hulltype:
                self.shipsFrom.remove(shipID)
                self.shipsTo.append(shipID)
                return
    
    def moveDamagedShips(self):
        """Move only Damaged Ships"""
        for shipID in self.shipsFrom:
            myShip = self.game.myShips[shipID]
            if myShip['strength'] < 100.0:
                self.shipsFrom.remove(shipID)
                self.shipsTo.append(shipID)

    def moveDamagedRegiments(self):
        """Move only Damaged Regiments"""
        for regID in self.regFrom:
            myReg = self.game.myReg[regID]
            if myReg['strength'] < 100.0:
                self.regFrom.remove(regID)
                self.regTo.append(regID)
    
    def moveRegByType(self, regLetter):
        """Move the Regiment based on its type"""
        for regID in self.regFrom:
            myType = self.game.myRegiments[regID]['typeID']
            data = self.game.regimentdata[myType]
            regType = data.abr[2]
            if regType == regLetter:
                self.regFrom.remove(regID)
                self.regTo.append(regID)
                return
        
    def getAvailMarineList(self):
        """Get the available marines for transport as list [Mech, Art, Inf]"""
        availList = [0,0,0]
        for regID in self.regFrom:
            myType = self.game.myRegiments[regID]['typeID']
            data = self.game.regimentdata[myType]
            regType = data.abr[2]
            if regType == 'M':
                availList[0] += 1
            elif regType == 'A':
                availList[1] += 1
            elif regType == 'I':
                availList[2] += 1
                
        return availList
    
    def getAvailShipList(self):
        """Get the available ships that can move as list [Platform, Assault, Warship]"""
        availList = [0,0,0]
        for shipID in self.shipsFrom:
            designID = self.game.myShips[shipID]['designID']
            shipDesign = self.game.shipDesignObjects[designID]
            function = shipDesign.myShipHull.function
            if function == 'platform':
                availList[0] += 1
            elif function == 'assault':
                availList[1] += 1
            elif function in ['carrier', 'warship']:
                availList[2] += 1
                
        return availList
    
    def createRegFromList(self, onClickMethod, title):
        """Create List of Regiments to select"""
        self.regFromList = buttonlist.ButtonList(self.guiMediaPath, title, width=0.9, height=0.5)
        self.regFromList.setMyPosition(-0.3,-0.6)
        self.regFromList.setMyMode(self)
        self.regFromList.setOnClickMethod(onClickMethod)
        self.gui.append(self.regFromList)
    
    def populateRegFromListToWarp(self):
        """Fill the List with regiments"""
        id = self.regFromList.getSelectedButtonID()
        self.regFromList.myScrolledList.clear()
        sortedList = self.getSortedRegListByGlory(self.regFrom)
        for regID in sortedList:
            info = self.game.getRegInfo(regID)
            myRegDict = self.game.myRegiments[regID]
            self.regFromList.myScrolledList.addItem(text=info, 
                                                    extraArgs=regID)
        self.regFromList.focusOnNextButton(id)
            
    def populateRegFromListToCancelWarp(self):
        """Fill the List with regiments"""
        id = self.regFromList.getSelectedButtonID()
        self.regFromList.myScrolledList.clear()
        sortedList = self.getSortedRegListByGlory(self.regFrom)
        for regID in sortedList:
            info = self.game.getRegInfo(regID)
            myRegDict = self.game.myRegiments[regID]
            systemDict = self.game.allSystems[myRegDict['fromSystem']]
            self.regFromList.myScrolledList.addItem(text='%s <- %s' % (info, systemDict['name']), 
                                                    extraArgs=regID)
        self.regFromList.focusOnNextButton(id)
       
    def createRegToList(self, onClickMethod, title):
        """Create List of Regiments"""
        self.regToList = buttonlist.ButtonList(self.guiMediaPath, title, width=0.9, height=0.5)
        self.regToList.setMyPosition(0.7,-0.6)
        self.regToList.setMyMode(self)
        self.regToList.setOnClickMethod(onClickMethod)
        self.gui.append(self.regToList)
            
    def populateRegToList(self):
        """Fill the List with regiments"""
        id = self.regToList.getSelectedButtonID()
        self.regToList.myScrolledList.clear()
        sortedList = self.getSortedRegListByGlory(self.regTo)
        for regID in sortedList:
            myRegDict = self.game.myRegiments[regID]
            info = self.game.getRegInfo(regID)
            systemDict = self.game.allSystems[myRegDict['fromSystem']]
            self.regToList.myScrolledList.addItem(text='%s <- %s' % (info, systemDict['name']), 
                                                     extraArgs=regID)
        self.regToList.focusOnNextButton(id)

    def addRegToRemoveRegFrom(self, regID, index, button):
        """Regiment selected for regiment warp"""
        self.regFrom.remove(regID)
        self.regTo.append(regID)
        self.refreshRegLists()
        self.removeMyGui('movearmygui')
    
    def selectAllShips(self):
        """move all ships from fromlist to tolist"""
        self.shipsTo = self.shipsTo + self.shipsFrom
        self.shipsFrom = []
        self.refreshShipLists()
        
    def selectAllDamagedShips(self):
        """move all damaged ships from fromlist to tolist"""
        self.shipsTo = []
        for shipID in self.shipsFrom:
            myShip = self.game.myShips[shipID]
            if myShip['strength'] < 100:
                self.shipsTo.append(shipID)
        self.shipsFrom = [x for x in self.shipsFrom if x not in self.shipsTo]  
        self.refreshShipLists()    
    
    def selectAllRegiments(self):
        """move all regiments from fromlist to tolist"""
        self.regTo = self.regTo + self.regFrom
        self.regFrom = []
        self.refreshRegLists()
        
    def selectAllDamagedRegiments(self):
        """move all damaged regiments from fromlist to tolist"""
        self.regTo = []
        for regID in self.regFrom:
            myReg = self.game.myRegiments[regID]
            if myReg['strength'] < 100:
                self.regTo.append(regID)
        self.regFrom = [x for x in self.regFrom if x not in self.regTo]        
        self.refreshRegLists()
            
    def addRegFromRemoveRegTo(self, regID, index, button):
        """Regiment selected to be cancelled for warp"""
        self.regFrom.append(regID)
        self.regTo.remove(regID)
        self.refreshRegLists()
        self.removeMyGui('movearmygui')
    
    def createRegWarpButton(self):
        if self.regToList.myScrolledList.getNumItems() > 0:
            if self.regWarpButton == None:
                self.regWarpButton = regwarpbutton.RegWarpButton(self.guiMediaPath)
                self.regWarpButton.setMyMode(self)
                self.gui.append(self.regWarpButton)
        else:
            self.removeMyGui('regWarpButton')
    
    def createCancelWarpRegButton(self):
        if self.regToList.myScrolledList.getNumItems() > 0:
            if self.cancelWarpRegButton == None:
                self.cancelWarpRegButton = cancelwarpbutton.CancelWarpRegButton(self.guiMediaPath)
                self.cancelWarpRegButton.setMyMode(self)
                self.gui.append(self.cancelWarpRegButton)
        else:
            self.removeMyGui('cancelWarpRegButton')
    
    def createCancelSendCreditsButton(self, orderID, index, button):
        if self.sendcreditsList.myScrolledList.getNumItems() > 0:
            if self.cancelSendCreditsButton == None:
                self.cancelSendCreditsButton = submitbutton.SubmitToCancelSendCreditsButton(self.guiMediaPath, x=-0.2, y=-0.7, orderID=orderID)
                self.cancelSendCreditsButton.setMyMode(self)
                self.gui.append(self.cancelSendCreditsButton)
        else:
            self.removeMyGui('cancelSendCreditsButton')
            self.cancelSendCreditsButton = None
            
    def warpedArmiesSelected(self, warpedArmy):
        """warpedArmy Selected"""
        if self.isAnyFlagSelected() == 1:
            return
        self.clearAllCanSelectFlags()
        self.clearAnyGui()
        self.selectedArmy = warpedArmy
        self.setCanSelectFlag('cancelMovingRegiments')
        self.playSound('beep01')
        if self.setMySelector(warpedArmy.sim.getX(), warpedArmy.sim.getY(), warpedArmy.sim.getZ(), scale=0.5):
            self.regFrom = copy.copy(self.selectedArmy.myRegList)
            self.regTo = []
            self.createRegFromList('addRegToRemoveRegFrom', 'Regiments to Cancel:')
            self.populateRegFromListToCancelWarp()
            self.createRegToList('addRegFromRemoveRegTo', 'Regiments to be Cancelled for Warp:')
            self.createRegList(warpedArmy.myRegList)
            self.createSelectAllRegButton()
            self.createSelectAllDamagedRegButton()
            self.centerCameraOnSim(warpedArmy.sim)
            
    def otherArmiesSelected(self, otherArmy):
        """otherArmy Selected"""
        if self.isAnyFlagSelected() == 1:
            return
        self.playSound('beep01')
        self.clearAllCanSelectFlags()
        self.clearAnyGui()
        self.clearMouseSelection()
        if self.setMySelector(otherArmy.sim.getX(), otherArmy.sim.getY(), otherArmy.sim.getZ(), scale=0.5):
            self.centerCameraOnSim(otherArmy.sim)
            self.displayOtherArmyIntel(otherArmy)
    
    def displayOtherArmyIntel(self, otherArmy):
        """Display whatever intel is available for this otherArmy selected"""
        otherEmpire = self.game.allEmpires[otherArmy.myEmpireID]
        otherSystem = self.game.allSystems[otherArmy.myGuiSystem.id]
        roundNum = otherSystem['intelReport']['round']
        marineReport = otherSystem['intelReport']['marineReport']
        title = '(%s) Best Army Intel Available (Based on Scans from Round %d):' % (otherEmpire['name'], roundNum)
        self.createIntelList(marineReport, title)
        self.createDiplomacyGui(otherArmy.myEmpireID)
            
    def warpReg(self):
        """Send Warp Regiments command to Server"""
        try:
            serverResult = self.game.server.moveReg(self.game.authKey, self.regTo, self.selectedSystem.id)
            if serverResult == 1:
                self.modeMsgBox('Regiments Warped to %s' % self.selectedSystem.textName.text)
                self.playSound('warp')
                self.updateWarpedReg()
            elif type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('moveReg->Connection to Server Lost')
    
    def updateWarpedReg(self):
        """Update the Regiments that have gone through warp to Server"""
        fromReg = copy.copy(self.regFrom)
        toReg = copy.copy(self.regTo)
        fromSystem = copy.copy(self.selectedArmy.id)
        toSystem = self.selectedSystem.id
        if fromReg == []:
            del self.game.myArmies[fromSystem]
            del self.myArmies[fromSystem]
            self.selectedArmy.destroy()
            self.selectedArmy = None
        else:
            self.game.myArmies[fromSystem] = fromReg
            self.selectedArmy.refreshMyRegList()
        for regID in self.regTo:
            myReg = self.game.myRegiments[regID]
            myReg['toSystem'] = toSystem
            myReg['oldAvailSystems'] = copy.copy(myReg['availSystems'])
            myReg['availSystems'] = fromSystem
            
        self.addToWarpedArmy(toSystem, toReg)
        self.updateSystemUnits([fromSystem, toSystem])
        self.updateSystemWarpInfo([fromSystem, toSystem])
        self.clearMouseSelection()
        
    def addToWarpedArmy(self, systemID, regList):
        """Add regiments to warpedarmy"""
        if systemID not in self.game.warpedArmies.keys():
            self.game.warpedArmies[systemID] = regList
            self.createWarpedArmy(systemID)
        else:
            self.game.warpedArmies[systemID] = self.game.warpedArmies[systemID] + regList
            self.warpedArmies[systemID].refreshMyRegList()
            
    def cancelWarpReg(self):
        """Send Cancel Warp Regiments command to Server"""
        try:
            serverResult = self.game.server.cancelMoveReg(self.game.authKey, self.regTo)
            if serverResult == 1:
                self.modeMsgBox('Cancel Regiment Warp')
                self.playSound('cancelwarp')
                self.updateCancelWarpedReg()
            elif type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('cancelMoveReg->Connection to Server Lost')
            
    def updateCancelWarpedReg(self):
        """Update the Regiments that have cancelled warp to Server"""
        fromReg = copy.copy(self.regFrom)
        toReg = copy.copy(self.regTo)
        toSystem = copy.copy(self.selectedArmy.id)
        systemList = [toSystem]
        
        if fromReg == []:
            del self.game.warpedArmies[toSystem]
            del self.warpedArmies[toSystem]
            self.selectedArmy.destroy()
            self.selectedArmy = None
        else:
            self.game.warpedArmies[toSystem] = fromReg
            self.selectedArmy.refreshMyRegList()
        for regID in self.regTo:
            myReg = self.game.myRegiments[regID]
            fromSystem = copy.copy(myReg['fromSystem'])
            if fromSystem not in systemList:
                systemList.append(fromSystem)
            myReg['toSystem'] = fromSystem
            myReg['availSystems'] = copy.copy(myReg['oldAvailSystems'])
            self.addToMyArmy(fromSystem, regID)
        
        self.updateSystemUnits(systemList)
        self.updateSystemWarpInfo(systemList)
        self.clearMouseSelection()
    
    def updateSystemUnits(self, systemList):
        """For systems given update the army and armada positions"""
        for systemID in systemList:
            mySystemGui = self.systems[systemID]
            mySystemGui.setMyPositions()
            for id in self.myArmadas.keys():
                if id == systemID:
                    self.myArmadas[id].setMyPosition()
                    self.myArmadas[id].setPos()
            for id in self.myArmies.keys():
                if id == systemID:
                    self.myArmies[id].setMyPosition()
                    self.myArmies[id].setPos()
            for id in self.warpedArmadas.keys():
                if id == systemID:
                    self.warpedArmadas[id].setMyPosition()
                    self.warpedArmadas[id].setPos()
            for id in self.warpedArmies.keys():
                if id == systemID:
                    self.warpedArmies[id].setMyPosition()
                    self.warpedArmies[id].setPos()
            for key in self.otherArmadas.keys():
                (id, empireID) = string.split(key, '-')
                if id == systemID:
                    self.otherArmadas[key].setMyPosition()
                    self.otherArmadas[key].setPos()
            for key in self.otherArmies.keys():
                (id, empireID) = string.split(key, '-')
                if id == systemID:
                    self.otherArmies[key].setMyPosition()
                    self.otherArmies[key].setPos()
        
    def addToMyArmy(self, systemID, regID):
        """Add regiments back to myArmy"""
        if systemID not in self.game.myArmies.keys():
            self.game.myArmies[systemID] = [regID]
            self.createMyArmy(systemID)
        else:
            self.game.myArmies[systemID].append(regID)
            self.myArmies[systemID].refreshMyRegList()
            
    def createSystemMenu(self, systemID):
        """Create the System Menu which calls other System Guis as needed"""
        mySystemDict = self.game.allSystems[systemID]
        if mySystemDict['myEmpireID'] == self.game.myEmpireID:
            self.systemmenu = systemmenu.SystemMenu(self.guiMediaPath, mySystemDict)
            self.systemmenu.setMyMode(self)
            self.gui.append(self.systemmenu)
        else:
            self.displayOtherSystemIntel(mySystemDict)
            
    def displayOtherSystemIntel(self, otherSystem):
        """Display whatever intel is available for this system selected"""
        otherEmpire = self.game.allEmpires[otherSystem['myEmpireID']]
        roundNum = otherSystem['intelReport']['round']
        industryReport = otherSystem['intelReport']['industryReport']
        title = '(%s) Best Industry Intel Available (Based on Scans from Round %d):' % (otherEmpire['name'], roundNum)
        self.createIntelList(industryReport, title)
        self.createDiplomacyGui(otherSystem['myEmpireID'])
    
    def changeCityIndustry(self, systemID, cityIndustryList):
        """Send a changeCityIndustry Request to the Server"""
        try:
            serverResult = self.game.server.changeCityIndustry(self.game.authKey, systemID, cityIndustryList)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('City Industry Updated to Server')
                self.refreshChangeCityIndustry(systemID)
        except:
            self.modeMsgBox('changeCityIndustry->Connection to Server Lost, Login Again')
    
    def refreshChangeCityIndustry(self, systemID):
        """Modify City Industry Command Sent, refresh results"""
        self.game.allSystems[systemID]['cityIndustry'] = copy.copy(self.systemmenu.cityindustrygui.cityIndustryList)
        self.refreshSystem(systemID)
        self.systems[systemID].refreshGenTradeRoute()
        self.systemmenu.press1()
    
    def modifyIndustry(self, systemID, amount, industryID):
        """Send an Add or Remove Industry Request to the Server"""
        try:
            if amount > 0:
                    serverResult = self.game.server.addIndustry(self.game.authKey, systemID, amount, industryID)
            else:
                serverResult = self.game.server.removeIndustry(self.game.authKey, systemID, abs(amount), industryID)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Industry Request sent to Server Successfully')
                self.refreshModifyIndustry(systemID, amount, industryID)
        except:
            self.modeMsgBox('modifyIndustry->Connection to Server Lost, Login Again')
            
    def refreshModifyIndustry(self, systemID, amount, industryID):
        """Command sent to server, refresh industry gui"""
        self.getEmpireUpdate(['CR','AL','EC','IA'])
        self.getSystemUpdate(['AL','EC','IA','cities','citiesUsed'], systemID)
        self.game.allSystems[systemID]['myIndustry'][industryID] += amount
        self.refreshSystem(systemID)
        self.systems[systemID].refreshGenTradeRoute()
        self.refreshCredit()
        self.systemmenu.press2()
        
    def refreshSystemAfterTradeRoute(self, tradeRouteID, refreshToSystem):
        """Refresh Systems after trade route changes"""
        (fromSystemID, toSystemID, type) = string.split(tradeRouteID, '-')
        self.getSystemUpdate(['AL','EC','IA','usedWGC'], fromSystemID)
        self.refreshSystem(fromSystemID)
        if refreshToSystem:
            self.getSystemUpdate(['AL','EC','IA','usedWGC'], toSystemID)
            self.refreshSystem(toSystemID)            
        
    def refreshSystemMarketOrder(self, systemID):
        """Command sent to server, refresh system gui"""
        self.getEmpireUpdate(['CR','AL','EC','IA'])
        self.getSystemUpdate(['AL','EC','IA'], systemID)
        self.refreshSystem(systemID)
        self.refreshCredit()
        self.systemmenu.press4()
        
    def refreshSystem(self, systemID):
        mySystem = self.systems[systemID]
        mySystem.refreshResources()
        mySystem.refreshIndustrySims()
        mySystem.writeCitiesUsed()
        mySystem.writeName()
    
    def addTradeRoute(self, tradeRouteDict):
        """Add Trade Route"""
        try:
            serverResult = self.game.server.addTradeRoute(self.game.authKey, tradeRouteDict)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Trade Route Request Sent Successfully')
                self.getTradeRoute(tradeRouteDict['id'])
                self.refreshTradeRoutes()
        except:
            self.modeMsgBox('addTradeRoute->Connection to Server Lost, Login Again')
    
    def cancelTradeRoute(self, tradeRouteID):
        """Cancel Trade Route"""
        try:
            serverResult = self.game.server.cancelTradeRoute(self.game.authKey, tradeRouteID)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Cancel Trade Route Request Sent Successfully')
                del self.game.tradeRoutes[tradeRouteID]
                self.refreshTradeRoutes()
                self.refreshSystemAfterTradeRoute(tradeRouteID, 1)
        except:
            self.modeMsgBox('cancelTradeRoute->Connection to Server Lost, Login Again')
    
    def refreshTradeRoutes(self):
        """Perform refresh to trade routes"""
        try:
            if self.game.myEmpire['viewTradeRoutes'] == 0:
                self.toggleTradeRoutes()
            else:
                self.createTradeRoutes()
            self.onSpaceBarClear()
        except:
            self.modeMsgBox('refreshTradeRoute error')
    
    def getTradeRoute(self, tradeRouteID):
        """Ask the Server for an updated Trade Route"""
        try:
            serverResult = self.game.server.getTradeRoutes(self.game.authKey, tradeRouteID)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.game.tradeRoutes[tradeRouteID] = serverResult[tradeRouteID]
        except:
            self.modeMsgBox('getTradeRoute->Connection to Server Lost')
    
    def toggleTradeRoutes(self):
        """Toggle the viewing of trade route sims"""
        if self.game.myEmpire['viewTradeRoutes'] == 0:
            self.game.myEmpire['viewTradeRoutes'] = 1
            self.createTradeRoutes()
        else:
            self.game.myEmpire['viewTradeRoutes'] = 0
            self.removeTradeRoutes()
    
    def createTradeRoutes(self):
        """Create the Trade Route Sims"""
        self.removeTradeRoutes()
        for tradeRouteID, tradeRouteDict in self.game.tradeRoutes.iteritems():
            fromSystemDict = self.game.allSystems[tradeRouteDict['fromSystem']]
            toSystemDict = self.game.allSystems[tradeRouteDict['toSystem']]
            
            myTradeRoute = traderoute.TradeRoute(self.guiMediaPath, tradeRouteDict,
                                                 fromSystemDict, toSystemDict, 
                                                 self.checkForTradeRoute(tradeRouteDict['fromSystem'],
                                                                         tradeRouteDict['toSystem']))
            myTradeRoute.setMyMode(self)
            myTradeRoute.setMyGame(self)
            myTradeRoute.setOffsetPosition()
            if tradeRouteDict['warpReq'] > 0:
                self.refreshSystemAfterTradeRoute(tradeRouteID, 1)
            else:
                self.refreshSystemAfterTradeRoute(tradeRouteID, 0)
            self.traderoutes[tradeRouteID] = myTradeRoute
            self.setPlanePickable(myTradeRoute, 'traderoutes')
            self.gui.append(myTradeRoute)
    
    def createMyArmadas(self):
        """Create my Armada Sims"""
        for systemID in self.game.myArmadas.keys():
            self.createMyArmada(systemID)

    def createMyArmada(self, systemID):
        myArmada = armada.MyArmada(self.guiMediaPath, self, systemID)
        myArmada.setMyMode(self)
        self.myArmadas[myArmada.id] = myArmada
        self.setPlanePickable(myArmada, 'myArmadas')
        self.gui.append(myArmada)
            
    def createOtherArmadas(self):
        """Create other Armada Sims"""
        for systemID, empireList in self.game.otherArmadas.iteritems():
            for empireID in empireList:
                otherArmada = armada.OtherArmada(self.guiMediaPath, self, systemID, empireID)
                self.otherArmadas[otherArmada.id] = otherArmada
                self.setPlanePickable(otherArmada, 'otherArmadas')
                self.gui.append(otherArmada)
    
    def createWarpedArmadas(self):
        """Create warped Armada Sims"""
        for systemID in self.game.warpedArmadas.keys():
            self.createWarpedArmada(systemID)
    
    def createWarpedArmada(self, systemID):
        warpedArmada = armada.WarpedArmada(self.guiMediaPath, self, systemID)
        warpedArmada.setMyMode(self)
        self.warpedArmadas[warpedArmada.id] = warpedArmada
        self.setPlanePickable(warpedArmada, 'warpedArmadas')
        self.gui.append(warpedArmada)
        
    def createMyArmies(self):
        """Create my Army Sims"""
        for systemID in self.game.myArmies.keys():
            self.createMyArmy(systemID)

    def createMyArmy(self, systemID):
        myArmy = army.MyArmy(self.guiMediaPath, self, systemID)
        myArmy.setMyMode(self)
        self.myArmies[myArmy.id] = myArmy
        self.setPlanePickable(myArmy, 'myArmies')
        self.gui.append(myArmy)
            
    def createOtherArmies(self):
        """Create other Army Sims"""
        for systemID, empireList in self.game.otherArmies.iteritems():
            for empireID in empireList:
                otherArmy = army.OtherArmy(self.guiMediaPath, self, systemID, empireID)
                self.otherArmies[otherArmy.id] = otherArmy
                self.setPlanePickable(otherArmy, 'otherArmies')
                self.gui.append(otherArmy)
    
    def createWarpedArmies(self):
        """Create warped Army Sims"""
        for systemID in self.game.warpedArmies.keys():
            self.createWarpedArmy(systemID)
    
    def createWarpedArmy(self, systemID):
        warpedArmy = army.WarpedArmy(self.guiMediaPath, self, systemID)
        warpedArmy.setMyMode(self)
        self.warpedArmies[warpedArmy.id] = warpedArmy
        self.setPlanePickable(warpedArmy, 'warpedArmies')
        self.gui.append(warpedArmy)
        
    def checkForTradeRoute(self, fromSystemID, toSystemID):
        """Check if there is an existing trade route between systems"""
        key = '%s-%s-' % (fromSystemID, toSystemID)
        for traderouteID in self.traderoutes.keys():
            if traderouteID[:-3] == key:
                return 2
        return 1
            
    def removeTradeRoutes(self):
        """Remove the Trade Route Sims"""
        for id, tradeRouteSim in self.traderoutes.iteritems():
            tradeRouteSim.destroy()
        self.traderoutes = {}
        
    def refreshShipOrder(self, systemID):
        self.getEmpireUpdate(['CR','AL','EC','IA'])
        self.getSystemUpdate(['AL','EC','IA','fleetCadets','usedSYC'], systemID)
        self.getEmpireOrders('industryOrders')
        self.refreshSystem(systemID)
        self.refreshCredit()
        self.systemmenu.press5()
        self.systemmenu.createBuildShipsGui()
    
    def refreshRegimentOrder(self, systemID):
        self.getEmpireUpdate(['CR','AL','EC','IA'])
        self.getSystemUpdate(['AL','EC','IA','armyCadets','usedMIC'], systemID)
        self.getEmpireOrders('industryOrders')
        self.refreshSystem(systemID)
        self.refreshCredit()
        self.systemmenu.press6()
        self.systemmenu.createBuildMarinesGui()
    
    def refreshRepairShipsOrder(self, systemID):
        self.refreshShipsOrder(systemID)
        self.systemmenu.createRepairShipsGui()
    
    def refreshUpgradeShipsOrder(self, systemID):
        self.refreshShipsOrder(systemID)
        self.systemmenu.createUpgradeShipsGui()
    
    def refreshShipsOrder(self, systemID):
        self.getEmpireUpdate(['CR','AL','EC','IA'])
        self.getSystemUpdate(['AL','EC','IA','usedSYC'], systemID)
        self.getEmpireOrders('industryOrders')
        self.refreshSystem(systemID)
        self.refreshCredit()
        self.systemmenu.press5()
        
    def refreshRestoreRegimentsOrder(self, systemID):
        self.refreshRegimentsOrder(systemID)
        self.systemmenu.createRepairMarinesGui()
    
    def refreshUpgradeRegimentsOrder(self, systemID):
        self.refreshRegimentsOrder(systemID)
        self.systemmenu.createUpgradeMarinesGui()
    
    def refreshRegimentsOrder(self, systemID):
        self.getEmpireUpdate(['CR','AL','EC','IA'])
        self.getSystemUpdate(['AL','EC','IA','usedMIC'], systemID)
        self.getEmpireOrders('industryOrders')
        self.refreshSystem(systemID)
        self.refreshCredit()
        self.systemmenu.press6()
        
    def addShipOrder(self, amount, shipDesignID, systemID):
        """Send an Add Ship Request to the Server"""
        try:
            dOrder = {'type':'Add Ship', 'value':'%s-%s' % (str(amount), shipDesignID),
                      'system':systemID, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Ship Order Request Sent Successfully')
                self.refreshShipOrder(systemID)
        except:
            self.modeMsgBox('addShipOrder->Connection to Server Lost, Login Again')

    def modifyShipOrder(self, amount, orderID):
        """Modify an Add Ship Request to the Server"""
        try:
            serverResult = self.game.server.modifyShipOrder(self.game.authKey, orderID, amount)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Modify Ship Order Request Sent Successfully')
                myOrder = self.game.myEmpire['industryOrders'][orderID]
                self.refreshShipOrder(myOrder['system'])
        except:
            self.modeMsgBox('modifyShipOrder->Connection to Server Lost, Login Again')
            
    def getEmpireOrders(self, orderType):
        """Ask the Server for an updated Industry Orders list"""
        try:
            serverResult = self.game.server.getEmpireOrders(self.game.authKey, orderType)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.game.myEmpire[orderType] = serverResult
        except:
            self.modeMsgBox('getEmpireOrders->Connection to Server Lost')
            
    def addRegimentOrder(self, amount, typeID, systemID):
        """Send an Add Regiment Request to the Server"""
        try:
            dOrder = {'type':'Add Regiment', 'value':'%s-%s' % (str(amount), typeID),
                      'system':systemID, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.refreshRegimentOrder(systemID)
        except:
            self.modeMsgBox('addRegimentOrder->Connection to Server Lost, Login Again')
    
    def modifyRegimentOrder(self, amount, orderID):
        """Modify an Add Regiment Request to the Server"""
        try:
            serverResult = self.game.server.modifyRegimentOrder(self.game.authKey, orderID, amount)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Modify Regiment Order Request Sent Successfully')
                myOrder = self.game.myEmpire['industryOrders'][orderID]
                self.refreshRegimentOrder(myOrder['system'])
        except:
            self.modeMsgBox('modifyRegimentOrder->Connection to Server Lost, Login Again')
            
    def restoreRegimentOrder(self, regimentList, systemID):
        """Send a Restore Regiment Request to the Server"""
        try:
            for value in regimentList:
                dOrder = {'type':'Restore Regiment', 'value':value,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshRestoreRegimentsOrder(systemID)
                    return
            self.modeMsgBox('Repair Marine Regiment Order Request Sent Successfully')
            self.refreshRestoreRegimentsOrder(systemID)
        except:
            self.modeMsgBox('restoreRegimentOrder->Connection to Server Lost, Login Again')
    
    def upgradeRegimentOrder(self, regimentList, systemID):
        """Send an Upgrade Regiment Request to the Server"""
        try:
            for value in regimentList:
                dOrder = {'type':'Upgrade Regiment', 'value':value,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshUpgradeRegimentsOrder(systemID)
                    return
            self.modeMsgBox('Upgrade Marine Regiment Order Request Sent Successfully')
            self.refreshUpgradeRegimentsOrder(systemID)
        except:
            self.modeMsgBox('upgradeRegimentOrder->Connection to Server Lost, Login Again')
    
    def repairStarshipOrder(self, shipList, systemID):
        """Send a Repair Starship Request to the Server"""
        try:
            for value in shipList:
                dOrder = {'type':'Repair Starship', 'value':value,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshRepairShipsOrder(systemID)
                    return
            self.modeMsgBox('Repair Starship Order Request Sent Successfully')
            self.refreshRepairShipsOrder(systemID)
        except:
            self.modeMsgBox('repairStarshipOrder->Connection to Server Lost, Login Again')
    
    def upgradeStarshipOrder(self, shipList, systemID):
        """Send an Upgrade Starship Request to the Server"""
        try:
            for value in shipList:
                dOrder = {'type':'Upgrade Starship', 'value':value,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshUpgradeShipsOrder(systemID)
                    return
            self.modeMsgBox('Upgrade Starship Order Request Sent Successfully')
            self.refreshUpgradeShipsOrder(systemID)
        except:
            self.modeMsgBox('upgradeStarshipOrder->Connection to Server Lost, Login Again')
    
    def cancelRepairStarshipOrder(self, orderList, systemID):
        """Send a Cancel Repair Starship Order Request to the Server"""
        try:
            for orderID in orderList:
                serverResult = self.game.server.cancelIndustryOrder(self.game.authKey, orderID)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshRepairShipsOrder(systemID)
                    return
            self.modeMsgBox('Cancel Repair Starship Order Request Sent Successfully')
            self.refreshRepairShipsOrder(systemID)
        except:
            self.modeMsgBox('cancelRepairStarshipOrder->Connection to Server Lost, Login Again')
            
    def cancelUpgradeStarshipOrder(self, orderList, systemID):
        """Send a Cancel Upgrade Starship Order Request to the Server"""
        try:
            for orderID in orderList:
                serverResult = self.game.server.cancelIndustryOrder(self.game.authKey, orderID)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshUpgradeShipsOrder(systemID)
                    return
            self.modeMsgBox('Cancel Upgrade Starship Order Request Sent Successfully')
            self.refreshUpgradeShipsOrder(systemID)
        except:
            self.modeMsgBox('cancelRepairStarshipOrder->Connection to Server Lost, Login Again')
            
    def cancelRestoreRegimentOrder(self, orderList, systemID):
        """Send a Cancel Restore Regiment Order Request to the Server"""
        try:
            for orderID in orderList:
                serverResult = self.game.server.cancelIndustryOrder(self.game.authKey, orderID)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshRestoreRegimentsOrder(systemID)
                    return
            self.modeMsgBox('Cancel Repair Marine Regiment Order Request Sent Successfully')
            self.refreshRestoreRegimentsOrder(systemID)
        except:
            self.modeMsgBox('cancelRestoreRegimentOrder->Connection to Server Lost, Login Again')

    def cancelUpgradeRegimentOrder(self, orderList, systemID):
        """Send a Cancel Upgrade Regiment Order Request to the Server"""
        try:
            for orderID in orderList:
                serverResult = self.game.server.cancelIndustryOrder(self.game.authKey, orderID)
                if serverResult != 1:
                    self.modeMsgBox(serverResult)
                    self.refreshUpgradeRegimentsOrder(systemID)
                    return
            self.modeMsgBox('Cancel Upgrade Marine Regiment Order Request Sent Successfully')
            self.refreshUpgradeRegimentsOrder(systemID)
        except:
            self.modeMsgBox('cancelUpgradeRegimentOrder->Connection to Server Lost, Login Again')
    
    def sendMail(self):
        """Send another Empire a message"""
        try:
            serverResult = self.game.server.sendMail(self.game.authKey, self.diplomacyEmpireID, self.messageText)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
                return
            self.modeMsgBox('Message Sent Successfully')
            self.onSpaceBarClear()
        except:
            self.modeMsgBox('sendMail->Connection to Server Lost, Login Again')
    
    def increaseDiplomacy(self):
        """Send an Increase Diplomacy Request to the Server"""
        try:
            serverResult = self.game.server.increaseDiplomacy(self.game.authKey, self.diplomacyEmpireID)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
                return
            self.modeMsgBox('Increase Diplomacy Request Sent Successfully')
            self.getEmpireUpdate(['diplomacy'])
            self.onSpaceBarClear()
        except:
            self.modeMsgBox('increaseDiplomacy->Connection to Server Lost, Login Again')
    
    def decreaseDiplomacy(self):
        """Send an Decrease Diplomacy Request to the Server"""
        try:
            serverResult = self.game.server.decreaseDiplomacy(self.game.authKey, self.diplomacyEmpireID)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
                return
            self.modeMsgBox('Decrease Diplomacy Request Sent Successfully')
            self.getEmpireUpdate(['diplomacy'])
            self.onSpaceBarClear()
        except:
            self.modeMsgBox('decreaseDiplomacy->Connection to Server Lost, Login Again')

    def submitMarketOrder(self, orderDict):
        """Submit a Market Order to Server"""
        try:
            serverResult = self.game.server.addMarketOrder(self.game.authKey, orderDict)
            if type(serverResult) != types.DictionaryType:
                self.modeMsgBox(serverResult)
                return
            self.modeMsgBox('Submit Market Order Request Sent Successfully')
            self.game.marketOrders[serverResult['id']] = serverResult
            self.refreshSystemMarketOrder(orderDict['system'])
        except:
            self.modeMsgBox('submitMarketOrder->Connection to Server Lost, Login Again')            
            
    def submitCancelMarketOrder(self, orderID):
        """Send a cancel Market Order to Server"""
        try:
            serverResult = self.game.server.cancelMarketOrder(self.game.authKey, orderID)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
                return
            self.modeMsgBox('Cancel Market Order Request Sent Successfully')
            self.refreshSystemMarketOrder(self.game.marketOrders[orderID]['system'])
            del self.game.marketOrders[orderID]
        except:
            self.modeMsgBox('submitCancelMarketOrder->Connection to Server Lost, Login Again')

    def submitSendCredits(self, amount):
        """Submit a send credit order to send credits to other empire for next round"""
        try:
            serverResult = self.game.server.sendCredits(self.game.authKey, self.diplomacyEmpireID, amount)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
                return
            self.modeMsgBox('Submit Credits Order Sent Successfully')
            self.refreshCreditsOrder()
        except:
            self.modeMsgBox('submitMarketOrder->Connection to Server Lost, Login Again')            
    
    def submitCancelSendCredits(self, orderID):
        """Send a cancel Send Credits to Server"""
        try:
            serverResult = self.game.server.cancelSendCredits(self.game.authKey, orderID)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
                return
            self.modeMsgBox('Cancel Send Credits to %s Sent Successfully' % self.game.allEmpires[orderID]['name'])
            self.refreshCreditsOrder()
        except:
            self.modeMsgBox('submitCancelSendCredits->Connection to Server Lost, Login Again')
            
    def refreshCreditsOrder(self):
        self.getEmpireUpdate(['CR', 'creditsInLieu'])
        self.refreshCredit()
        self.onSpaceBarClear()
            
    