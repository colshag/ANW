# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modedesign.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Design Mode in ANW
# ---------------------------------------------------------------------------
import types
import string

import mode
from anw.func import globals, funcs
from anw.gui import designmenu, textonscreen, shiphull, buttonlist
from anw.gui import multisimassignships, designinfo, submitbutton

class ModeDesign(mode.Mode):
    """This is the StarShip Design Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.allTech = 0
        self.canSelectFlags['hullSelected'] = 0
        self.enableMouseCamControl = 0
        self.createSelector('select2',5)
        self.cameraPos = (0,-10, 0)
        self.zoomCameraDepth = 18.5
        self.zoomCameraOutDepth = 0.0
        self.resetCamera()
        self.name = 'DESIGN'
        self.createMainMenu('I')
        self.designmenu = None
        self.selectedShipHull = None
        self.shipdesignList = None
        self.dronedesignList = None
        self.multidesignList = None
        self.multisimassignships = None
        self.designInfo = None
        self.multisim = {1:{},2:{}} # {id=shipdesignID : shipnum, ...}
        self.titleCost = None
        self.titleAvail = None
        self.multisimCost = None
        self.multisimAvail = None
        self.multiTeam1List = None
        self.multiTeam2List = None
        self.selectTypes = ['shiphulls', 'dronehulls']
        self.shiphulls = {}
        self.dronehulls = {}
        self.designName = ''
        self.createDesignMenu()
        self.simulateButton = None
        if game.currentDesign != None:
            self.zoomToPreviousDesign()
    
    def createSimulateButton(self):
        if self.simulateButton == None:
            self.simulateButton = submitbutton.SubmitToMultiSimButton(self.guiMediaPath, x=0.1, y=0)
            self.simulateButton.setMyMode(self)
            self.gui.append(self.simulateButton)
            
    def createDesignInfo(self, myShipDesign):
        """Display Design Info"""
        self.removeMyGui('designInfo')
        self.designInfo = designinfo.DesignInfo(self.guiMediaPath, self.game.myEmpireID,
                                                myShipDesign, 0.45, 0.70)
        self.designInfo.setMyMode(self)
        self.designInfo.writeAttributes()
        self.gui.append(self.designInfo)
            
    def createMainMenu(self, key):
        mode.Mode.createMainMenu(self, key)
        self.mainmenu.ignoreShortcuts()
        
    def createDesignMenu(self):
        """Create the Design Menu which calls other Guis as needed"""
        self.designmenu = designmenu.DesignMenu(self.guiMediaPath)
        self.designmenu.setMyMode(self)
        self.gui.append(self.designmenu)
    
    def createShipHulls(self, shipHullDict):
        """Create all the ship hulls, group by function type"""
        self.createHullTypeTitles()
        positions = {'warship':[-6,2.75], 'carrier':[-6,0.75], 'assault':[-6,-1.25], 'platform':[-6,-3.25]}
        myList = funcs.sortStringList(shipHullDict.keys())
        for id in myList:
            myShipHullDict = shipHullDict[id]
            (x,z) = positions[myShipHullDict.function]
            myShipHull = shiphull.ShipHull(self.guiMediaPath, self, 
                                           self.game.myEmpireID, myShipHullDict, x, z)
            myShipHull.setMyMode(self)
            myShipHull.setMyGame(self.game)
            self.shiphulls[myShipHull.id] = myShipHull
            self.gui.append(myShipHull)
            positions[myShipHullDict.function] = [x+1.1,z]
            self.setPlanePickable(myShipHull, 'shiphulls')
    
    def createDroneHulls(self, droneHullDict):
        """Create all the drone hulls"""
        positions = {'drone':[-2.6, 0.75]}
        myList = funcs.sortStringList(droneHullDict.keys())
        for id in myList:
            myDroneHullDict = droneHullDict[id]
            (x,z) = positions[myDroneHullDict.function]
            myDroneHull = shiphull.DroneHull(self.guiMediaPath, self, 
                                             self.game.myEmpireID, myDroneHullDict, x, z)
            myDroneHull.setMyMode(self)
            myDroneHull.setMyGame(self.game)
            self.dronehulls[myDroneHull.id] = myDroneHull
            self.gui.append(myDroneHull)
            positions[myDroneHullDict.function] = [x+1.1,z]
            self.setPlanePickable(myDroneHull, 'dronehulls')
    
    def multiSimulate(self):
        """Setup a Multi Simulation"""
        self.setEmpireValues({'simulationsLeft':self.game.myEmpire['simulationsLeft']-self.getMultiSimCost()})
        self.game.createShipSimulation(self.multisim)
            
    def createShipDesignList(self):
        """Create a listbox to store all the existing ships designs"""
        self.removeMyGui('shipdesignList')
        self.shipdesignList = buttonlist.ButtonList(self.guiMediaPath, 'Or Select from existing Ship Designs:',
                                                    width=0.625, height=0.7)
        self.shipdesignList.setMyPosition(0,-0.5)
        self.shipdesignList.setMyMode(self)
        self.shipdesignList.setOnClickMethod('shipDesignSelected')
        self.gui.append(self.shipdesignList)
        self.populateShipDesignList()
    
    def refreshMultiSim(self):
        """Refresh the multi sim view and populate the teams and remaining sim points"""
        self.clearMouseSelection()
        self.createMultiDesignList()
        self.createMultiTeamLists()
        self.createMultiSimCost()
        self.createMultiSimAvail()
        multiSimCost = self.getMultiSimCost()
        if (self.game.myEmpire['simulationsLeft'] > 0 and multiSimCost > 0 and 
            multiSimCost <= self.game.myEmpire['simulationsLeft']):
            self.createSimulateButton()
        else:
            self.removeMyGui('simulateButton')
        
    def createMultiSimCost(self):
        """Calculate and display the Cost to simulate currently"""
        self.createTitleCost()
        self.createTextCardCost(self.getMultiSimCost())
    
    def getMultiSimCost(self):
        simCost = 0
        simCost1 = 0
        simCost2 = 0
        for designID, num in self.multisim[1].iteritems():
            simCost1 += 1
        for designID, num in self.multisim[2].iteritems():
            simCost2 += 1
        simCost = simCost1 * simCost2
        return simCost
        
    def createTextCardCost(self, simCost,):
        """Text Card For Simulation Cost"""
        if self.multisimCost == None:
            self.multisimCost = textonscreen.TextOnScreen(self.guiMediaPath, str(simCost),
                                                              scale=0.09, font=5, parent=aspect2d)
            self.multisimCost.writeTextToScreen(0.15, 0, 0.27, 10)
            self.multisimCost.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 0.2, 0.2)
            self.gui.append(self.multisimCost)
            
        funcs.setZeroToText(self.multisimCost.myText, simCost)
    
    def createMultiSimAvail(self):
        """Display the Available Simulation Points"""
        self.createTitleAvail()
        self.createTextCardAvail(self.game.myEmpire['simulationsLeft'])

    def createTextCardAvail(self, simAvail):
        """Text Card For Simulation Points Available"""
        if self.multisimAvail == None:
            self.multisimAvail = textonscreen.TextOnScreen(self.guiMediaPath, str(simAvail),
                                                              scale=0.09, font=5, parent=aspect2d)
            self.multisimAvail.writeTextToScreen(0.15, 0, 0.12, 10)
            self.multisimAvail.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 0.2, 0.2)
            self.gui.append(self.multisimAvail)
            
        funcs.setZeroToText(self.multisimAvail.myText, simAvail)
        
    def createTitleCost(self):
        if self.titleCost == None:
            self.titleCost = textonscreen.TextOnScreen(self.guiMediaPath, 'Cost of Current Simulation:',
                                                          scale=0.03, font=5, parent=aspect2d)
            self.titleCost.writeTextToScreen(-0.1, 0, 0.3, 10)
            self.titleCost.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 0.2, 0.2)
            self.gui.append(self.titleCost)
        
    def createTitleAvail(self):
        if self.titleAvail == None:
            self.titleAvail = textonscreen.TextOnScreen(self.guiMediaPath, 'Available Simulation Points:',
                                                          scale=0.03, font=5, parent=aspect2d)
            self.titleAvail.writeTextToScreen(-0.1, 0, 0.15, 10)
            self.titleAvail.setCardColor(globals.colors['guiblue3'], 0.2, 0.2, 0.2, 0.2)
            self.gui.append(self.titleAvail)    
        
    def createMultiTeamLists(self):
        self.createMultiTeamList(1)
        self.createMultiTeamList(2)
        self.populateMultiTeamLists()
    
    def createMultiTeamList(self, num):
        listname = 'multiTeam%dList' % num
        self.removeMyGui(listname)
        myList = getattr(self, listname)
        myList = buttonlist.ButtonList(self.guiMediaPath, 'Team %d Ships: (select to remove)' % num,
                                       width=0.9, height=0.5)
        myList.setMyPosition(-0.5 + (num-1)*1, -0.35)
        myList.setMyMode(self)
        myList.setOnClickMethod(listname + 'Selected')
        setattr(self, listname, myList)
        self.gui.append(myList)
        
    def createMultiDesignList(self):
        """Create a listbox to store all the existing ships designs"""
        self.removeMyGui('multidesignList')
        self.multidesignList = buttonlist.ButtonList(self.guiMediaPath, 'Select a Ship Design:',
                                                    width=0.8, height=0.7)
        self.multidesignList.setMyPosition(-0.55,0.35)
        self.multidesignList.setMyMode(self)
        self.multidesignList.setOnClickMethod('multiShipDesignSelected')
        self.gui.append(self.multidesignList)
        self.populateMultiShipDesignList()
        
    def createDroneDesignList(self):
        """Create a listbox to store all the existing drone designs"""
        self.removeMyGui('dronedesignList')
        self.dronedesignList = buttonlist.ButtonList(self.guiMediaPath, 'Or Select from existing Drone Designs:',
                                                    width=0.625, height=0.7)
        self.dronedesignList.setMyPosition(0.8,-0.5)
        self.dronedesignList.setMyMode(self)
        self.dronedesignList.setOnClickMethod('droneDesignSelected')
        self.gui.append(self.dronedesignList)
        self.populateDroneDesignList()
    
    def zoomToPreviousDesign(self):
        """If game has saved simulated design, zoom back to it"""
        if self.game.currentDesign != None:
            if self.game.currentDesign.hasAllTech == 1:
                self.designmenu.setupMyTech()
            else:
                self.designmenu.setupAllTech()
            (name, hullID, compDict, weapDict) = self.game.currentDesign.getMyDesign()
            myShipHull = self.shiphulls[hullID]
            self.shiphullsSelected(myShipHull, compDict, weapDict, name)
    
    def clearCurrentDesign(self):
        self.game.currentDesign = None
            
    def populateShipDesignList(self):
        """Fill the list with Ship designs"""
        for shipDesignID in funcs.sortStringList(self.game.shipDesigns.keys()):
            myShipDesign = self.game.shipDesignObjects[shipDesignID]
            if self.allTech == 1 or myShipDesign.hasAllTech == 1:
                self.shipdesignList.myScrolledList.addItem(text=myShipDesign.name, extraArgs=shipDesignID)
   
    def populateMultiShipDesignList(self):
        """Fill the list with Ship designs"""
        for shipDesignID in funcs.sortStringList(self.game.shipDesigns.keys()):
            myShipDesign = self.game.shipDesignObjects[shipDesignID]
            self.multidesignList.myScrolledList.addItem(text=myShipDesign.name, extraArgs=shipDesignID)
    
    def populateMultiTeamLists(self):
        self.populateMultiTeamList(1)
        self.populateMultiTeamList(2)
        
    def populateMultiTeamList(self, num):
        listname = 'multiTeam%dList' % num
        myList = getattr(self, listname)
        d = self.multisim[num]
        for shipDesignID, shipNum in d.iteritems():
            myShipDesign = self.game.shipDesignObjects[shipDesignID]
            myList.myScrolledList.addItem(text='%d - %s' % (shipNum, myShipDesign.name), extraArgs=shipDesignID)
            
    def populateDroneDesignList(self):
        """Fill the list with Drone designs"""
        for droneDesignID in funcs.sortStringList(self.game.droneDesigns.keys()):
            myDroneDesign = self.game.droneDesignObjects[droneDesignID]
            if self.allTech == 1 or myDroneDesign.hasAllTech == 1:
                self.dronedesignList.myScrolledList.addItem(text=myDroneDesign.name, extraArgs=droneDesignID)
    
    def shipDesignSelected(self, designID, index, button):
        """Fill in Ship Design stats to allow for new modifications"""
        self.playSound('beep01')
        myShipHull = self.shiphulls[self.game.shipDesigns[designID][1]]
        self.shiphullsSelected(myShipHull, self.game.shipDesigns[designID][2], 
                               self.game.shipDesigns[designID][3],
                               self.game.shipDesigns[designID][0])
        
    def multiShipDesignSelected(self, designID, index, button):
        """Ship Design selected, open gui to allow for number of ships to add to sim"""
        self.removeMyGui('multisimassignships')
        self.removeMyGui('designInfo')
        name = self.game.shipDesigns[designID][0]
        self.multisimassignships = multisimassignships.MultiSimAssignShips(self.guiMediaPath,
                                                                           name,
                                                                           50,
                                                                           designID, -0.05, 0.285)
        self.multisimassignships.setMyMode(self)
        self.gui.append(self.multisimassignships)
        myShipDesign = self.game.shipDesignObjects[designID]
        self.createDesignInfo(myShipDesign)
    
    def multiTeam1ListSelected(self, designID, index, button):
        """remove design from list"""
        del self.multisim[1][designID]
        self.refreshMultiSim()
    
    def multiTeam2ListSelected(self, designID, index, button):
        """remove design from list"""
        del self.multisim[2][designID]
        self.refreshMultiSim()
        
    def droneDesignSelected(self, designID, index, button):
        """Fill in Drone Design stats to allow for new modifications"""
        self.playSound('beep01')
        myDroneHull = self.dronehulls[self.game.droneDesigns[designID][1]]
        self.dronehullsSelected(myDroneHull, self.game.droneDesigns[designID][2], 
                               self.game.droneDesigns[designID][3],
                               self.game.droneDesigns[designID][0])
        
    def createHullTypeTitles(self):
        for (title, z) in (('Click for a Warship Design Here:', 3.5),
                           ('Click for a Carrier/Drone Design Here:', 1.5),
                           ('Click for a Assault Design Here:', -0.5),
                           ('Click for a Platform Design Here:', -2.5)):
            self.writeToScreen(title, x=-6, z=z, scale=0.2, 
                               color=globals.colors['guiwhite'], font=3, wordwrap=40)
    
    def shiphullsSelected(self, myShipHull, compDict={'fore':[], 'aft':[], 'port':[], 'star':[]}, weapDict={}, name=''):
        """ShipHull Selected"""
        if self.canSelectFlags['hullSelected'] == 1:
            return
        if self.setMySelector(myShipHull.sim.getX(), myShipHull.sim.getY(), myShipHull.sim.getZ(), scale=0.6):
            self.setCanSelectFlag('hullSelected')
            self.playSound('beep01')
            self.selectedShipHull = myShipHull
            myShipHull.setupShipDesign(compDict, weapDict, name)
            self.centerCameraOnSim(myShipHull.sim)
            self.zoomInCamera()
    
    def dronehullsSelected(self, myDroneHull, compDict={'fore':[]}, weapDict={}, name=''):
        """DroneHull Selected"""
        if self.canSelectFlags['hullSelected'] == 1:
            return
        if self.setMySelector(myDroneHull.sim.getX(), myDroneHull.sim.getY(), myDroneHull.sim.getZ(), scale=0.6):
            self.setCanSelectFlag('hullSelected')
            self.playSound('beep01')
            self.selectedShipHull = myDroneHull
            myDroneHull.setupShipDesign(compDict, weapDict, name)
            self.centerCameraOnSim(myDroneHull.sim)
            self.zoomInCamera()
    
    def clearMouseSelection(self):
        """Clear mouse selection before selecting something new"""
        self.hideMySelector()
        self.removeMyGui('shipdesignList')
        self.removeMyGui('dronedesignList')
        self.removeMyGui('multisimassignships')
        self.removeMyGui('designInfo')
        self.removeMyGui('multidesignList')
        self.removeMyGui('multiTeam1List')
        self.removeMyGui('multiTeam2List')
        self.removeMyGui('multisimCost')
        self.removeMyGui('multisimAvail')
        self.removeMyGui('titleCost')
        self.removeMyGui('titleAvail')
        self.clearAllCanSelectFlags()
        self.designName = ''
        self.clearCurrentDesign()
    
    def resetMode(self):
        """Reset the Mode"""
        self.multisim = {1:{},2:{}}
        self.clearMouseSelection()
        self.clearAllCanSelectFlags()
        self.resetCamera()
        self.hideMySelector()
        self.removeAllGui()
        self.createMainMenu('U')
        self.createDesignMenu()
    
    def zoomInCamera(self):
        if camera.getY() <= self.zoomCameraOutDepth:
            self.game.app.disableMouseCamControl()
            taskMgr.add(self.zoomInCameraTask, 'zoomInCameraTask', extraArgs=[self.zoomCameraDepth])
            self.runningTasks.append('zoomInCameraTask')
            self.removeMyGui('shipdesignList')
            self.removeMyGui('dronedesignList')
            self.removeMyGui('designInfo')
            
    def onDesignNameEntered(self, name):
        self.designName = name
        self.selectedShipHull.designSubmit.enableDesignSubmit()
    
    def submitDesign(self, myShipDesign):
        """Submit the design to server, either ship or drone"""
        (oldName, hullID, compDict, weaponDict) = myShipDesign.getMyDesign()
        dOrder = {'name':string.upper(self.designName), 'hullID':hullID, 'compDict':compDict, 'weaponDict':weaponDict}
        if 'aft' not in compDict.keys():
            self.submitDroneDesign(dOrder)
        else:
            self.submitShipDesign(dOrder)
        
    def submitShipDesign(self, dOrder):
        """Submit the ship design to server"""
        try:
            serverResult = self.game.server.addShipDesign(self.game.authKey, dOrder)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                (ID,name) = serverResult
                self.game.shipDesigns[ID] = (name, dOrder['hullID'], dOrder['compDict'], dOrder['weaponDict'])
                self.game.createShipDesigns()
                self.game.myEmpire['designsLeft'] -= 1
                self.modeMsgBox('Add Ship Design:%s Successfully' % self.designName)
                self.resetMode()
        except:
            self.modeMsgBox('submitShipDesign->Connection to Server Lost, Login Again')
    
    def submitDroneDesign(self, dOrder):
        """Submit the drone design to server"""
        try:
            serverResult = self.game.server.addDroneDesign(self.game.authKey, dOrder)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                (ID,name) = serverResult
                self.game.droneDesigns[ID] = (name, dOrder['hullID'], dOrder['compDict'], dOrder['weaponDict'])
                self.game.createDroneDesigns()
                self.game.myEmpire['designsLeft'] -= 1
                self.modeMsgBox('Add Drone Design:%s Successfully' % self.designName)
                self.resetMode()
        except:
            self.modeMsgBox('submitDroneDesign->Connection to Server Lost, Login Again')

    def submitRemoveShipDesign(self, designID):
        """Submit to remove the ship design to server"""
        try:
            serverResult = self.game.server.removeShipDesign(self.game.authKey, designID)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                del self.game.shipDesigns[designID]
                del self.game.shipDesignObjects[designID]
                self.clearCurrentDesign()
                self.modeMsgBox('Ship Design Removed Successfully')
                self.resetMode()
        except:
            self.modeMsgBox('submitRemoveShipDesign->Connection to Server Lost, Login Again')
            
    def submitRemoveDroneDesign(self, designID):
        """Submit to remove the drone design to server"""
        try:
            serverResult = self.game.server.removeDroneDesign(self.game.authKey, designID)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                del self.game.droneDesigns[designID]
                del self.game.droneDesignObjects[designID]
                self.clearCurrentDesign()
                self.modeMsgBox('Drone Design Removed Successfully')
                self.resetMode()
        except:
            self.modeMsgBox('submitRemoveDroneDesign->Connection to Server Lost, Login Again')
            
    def onSpaceBarClear(self):
        """Space bar should not clear anything in design mode!"""
        pass

    