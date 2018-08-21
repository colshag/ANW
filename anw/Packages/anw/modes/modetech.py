# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modetech.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Technology Tree in ANW
# ---------------------------------------------------------------------------
import types

import mode
from anw.gui import techbeaker, scrollvalue, techline, valuebar
from anw.func import globals

class ModeTech(mode.Mode):
    """This is the Tech Mode, this mode allows player to manage a technology tree"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.zoomCameraDepth = 0.0
        self.resetCamera()
        self.createSelector('select')
        self.name = 'TECH'
        self.createMainMenu('T')
        self.scrollvaluegui = None
        self.techTotal = None
        self.beakers = {}
        self.selectTypes = ['beakers']
        self.createTechTotal()
        self.createTechLines()
        self.createTechBeakers()
        self.centerCameraOnRecentTech()
        
    def centerCameraOnRecentTech(self):
        """Find the most recent tech and center camera on it"""
        maxID = 0
        for techID, myTech in self.game.myTech.iteritems():
            if myTech.complete == 1 and int(techID) > maxID:
                maxID = int(techID)
        self.selectedBeaker = self.beakers[str(maxID)]
        self.centerCameraOnSim(self.selectedBeaker.sim)
    
    def createTechTotal(self):
        """Display tech total"""
        self.techTotal = valuebar.ValueBar(self.guiMediaPath, scale=0.45)
        self.techTotal.setMyPosition(0, 0, 0.85)
        self.techTotal.setColor(globals.colors['guiyellow'])
        self.updateTechTotal()
        self.gui.append(self.techTotal)
    
    def updateTechTotal(self):
        """Update Tech Total based on empire rpUsed/rpAvail"""
        avail = self.game.myEmpire['rpAvail']
        used = self.game.myEmpire['rpUsed']
        self.techTotal.setMyValues(avail, avail+used)
    
    def createTechBeakers(self):
        """Populate all tech beakers"""
        for techID, myTech in self.game.myTech.iteritems():
            myTechBeaker = techbeaker.TechBeaker(self.guiMediaPath, myTech, self.game)
            myTechBeaker.setMyMode(self)
            myTechBeaker.setMyGame(self.game)
            myTechBeaker.setCurrentTechOrder()
            self.beakers[myTechBeaker.id] = myTechBeaker
            if myTechBeaker.clickable == 1:
                self.setPlanePickable(myTechBeaker, 'beakers')
            self.gui.append(myTechBeaker)
    
    def createTechLines(self):
        """Draw the Tech Lines"""
        for item in self.game.techLines:
            myTechLine = techline.TechLine(self.guiMediaPath, (item[0], item[1]), (item[2], item[3]),item[4])
            self.gui.append(myTechLine)
    
    def clearMouseSelection(self):
        """Clear mouse selection before selecting something new"""
        if self.selectedBeaker:
            self.centerCameraOnSim(self.selectedBeaker.sim)
        self.hideMySelector()
        self.clearAnyGui()
        self.zoomOutCamera()
        self.enableScrollWheelZoom = 1
    
    def clearAnyGui(self):
        self.removeMyGui('scrollvaluegui')
    
    def beakersSelected(self, myTechBeaker):
        """Beaker Selected"""
        self.playSound('beep01')
        self.selectedBeaker = myTechBeaker
        if self.setMySelector(myTechBeaker.sim.getX(), myTechBeaker.sim.getY(), myTechBeaker.sim.getZ(), scale=2):
            self.createScrollValue(myTechBeaker)
            self.centerCameraOnSim(myTechBeaker.sim)
            self.zoomInCamera()
            # mode is wacky for this one, can't figure out how to get the mode into the button
            self.enableScrollWheelZoom = 0
    
    def createScrollValue(self, myTechBeaker):
        """Create the scrollValue gui to allow for tech orders"""
        self.scrollvaluegui = scrollvalue.ScrollValue(self.guiMediaPath, 0.1, 0.1, 'scroll')
        self.scrollvaluegui.setMyMode(self)
        self.scrollvaluegui.setMaxValue(myTechBeaker.getMaxValue(self.techTotal.currentValue))
        self.scrollvaluegui.setMinValue(myTechBeaker.getMinValue())
        self.scrollvaluegui.setID(myTechBeaker.id)
        self.gui.append(self.scrollvaluegui)
    
    def getTechOrders(self):
        """Ask the Server for an updated Tech Orders list"""
        try:
            serverResult = self.game.server.getEmpireOrders(self.game.authKey, 'techOrders')
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.game.myEmpire['techOrders'] = serverResult
        except:
            self.modeMsgBox('getTechOrders->Connection to Server Lost')
    
    def refreshTechOrder(self, techID):
        """Perform refresh to accomodate tech Order"""
        try:
            self.removeMyGui('scrollvaluegui')
            self.getTechOrders()
            self.getEmpireUpdate(['rpUsed', 'rpAvail'])
            self.updateTechTotal()
            self.beakers[techID].setCurrentTechOrder()
            self.clearMouseSelection()
        except:
            self.modeMsgBox('refreshTechOrder error ')
            
    def addTechOrder(self, amount, techID):
        """Send an Add Tech Request to the Server"""
        try:
            dOrder = {'type':techID, 'value':amount, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addTechOrder(self.game.authKey, dOrder)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
                self.clearMouseSelection()
            else:
                self.modeMsgBox('Tech Order Request Sent Successfully')
                self.refreshTechOrder(techID)
        except:
            self.modeMsgBox('addTechOrder->Connection to Server Lost, Login Again')