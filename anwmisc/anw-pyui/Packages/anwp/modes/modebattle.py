# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modebattle.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the view past battles, simulated battles mode
# ---------------------------------------------------------------------------
import pygame
import random

import pyui
import anwp.sl.world
import anwp.sl.engine
import mode
import anwp.gui.footer
import anwp.gui.battlemenu
import anwp.gui.pastbattleinfo
import anwp.gui.simbattleinfo
import anwp.func.storedata
import anwp.war.shipsimulator
import anwp.war.ship
import anwp.war.captain
import anwp.war.empire
import anwp.war.shipdesign
import anwp.war.quad
import anwp.war.weapon
import anwp.war.component
import anwp.war.shipbattle

class ModeBattle(mode.Mode):
    """This represents the View Battles Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'BATTLES'
        self.shipBattle = None
        self.shiphulldata = self.game.shiphulldata
        self.weapondata = self.game.weapondata
        self.componentdata = self.game.componentdata
        self.dronehulldata = self.game.dronehulldata
        
        # simulation
        self.fleets = {} # stores fleet objects
        self.empires = {} # stores simulated empires
        self.captains = {} # stores captain objects
        self.createEmpires()
        
        # create gui panels
        self.mainMenu = anwp.gui.battlemenu.MainMenuBattle(self, self.game.app)
        self.mainFooter = anwp.gui.footer.Footer(self, self.game.app)
        self.simBattleInfo = None
        self.pastBattleInfo = None
        self.fleetInfo = None
        
        # create the world
        self.worldWidth = self.appWidth
        self.worldHeight = self.appHeight
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight, 25))
        self.renderer.setBackMethod(self.draw)
    
    def clearPanels(self):
        """Clear the main panels"""
        if self.pastBattleInfo <> None:
            self.pastBattleInfo.destroy()
            self.pastBattleInfo = None
        if self.simBattleInfo <> None:
            self.simBattleInfo.destroy()
            self.simBattleInfo = None
    
    def copyDesignYes(self):
        """Copy Ship Design"""
        try:
            if self.myShipDesign == None:
                self.modeMsgBox('ship design no longer selected')
            else:
                self.submitDesign(self.myShipDesign.name)
                self.yesnoBox.destroy()
        except:
            self.modeMsgBox('modebattle-> copyDesignYes Error')
    
    def copyDesignNo(self):
        """Do not copy Ship Design"""
        self.yesnoBox.destroy()
    
    def createEmpires(self):
        """Create the simulated empires"""
        myEmpire = anwp.war.empire.Empire({'id':'1', 'name':'Sim Empire 1', 
                                           'color1':anwp.func.globals.simEmpireColors['1']['color1'], 'color2':anwp.func.globals.simEmpireColors['1']['color2']})
        self.empires['1'] = myEmpire
        myEmpire = anwp.war.empire.Empire({'id':'2', 'name':'Sim Empire 2', 
                                           'color1':anwp.func.globals.simEmpireColors['2']['color1'], 'color2':anwp.func.globals.simEmpireColors['2']['color2']})
        self.empires['2'] = myEmpire
        
        for empireID, myEmpire in self.empires.iteritems():
            myEmpire.myGalaxy = self
    
    def createFleet(self, empireID):
        """Create a new fleet for empire specified"""
        id = str(len(self.fleets.keys())+1)
        # give fleet best formation available
        num = 0
        techTree = self.game.myTech
        for key, value in anwp.func.globals.fleetFormations.iteritems():
            if techTree[value['techReq']]['complete'] == 1 and num < value['maxUnits']:
                num = value['maxUnits']
        myFleet = anwp.war.fleet.Fleet({'id':id, 'name':'Fleet%s' % id, 'formationID':'box%d' % num, 'empireID':empireID, 
                                        'quadrant':random.randint(1,25), 'rangeSolution':'max', 
                                        'rangePercent':80, 'fireSolution':'focused', 
                                        'retargetSolution':0, 'patternMovement':'[]', 
                                        'targetType':'any', 'facing':90})
        myFleet.myGalaxy = self
        myFleet.setMyFormation(myFleet.formationID)
        self.fleets[id] = myFleet
    
    def createFleetInfoFrame(self, fleetID):
        """Create the Fleet Info Config Frame"""
        self.destroyTempFrames()
        myFleet = self.fleets[fleetID]
        myFleetDict = myFleet.getMyFleetInfo()
        self.fleetInfo = anwp.gui.fleetinfo.FleetInfoFrame(self, self.game.app, myFleetDict)
        self.tempFrames.append(self.fleetInfo)
    
    def createShip(self, fleetID, shipDesignID):
        """Create a Ship object, place within fleet"""
        myFleet = self.fleets[fleetID]
        myEmpire = self.empires[myFleet.empireID]
        shipID = myFleet.getNextID(myFleet.ships)
        # create ship design
        shipDesignDict = self.game.shipDesigns[shipDesignID]
        self.myShipDesign = self.getShipDesign(shipDesignDict[1], shipDesignDict[2], shipDesignDict[3], shipDesignDict[0])
        self.myShipDesign.id = shipDesignID
        self.myShipDesign.setMyEmpire(myEmpire)
        # create captain
        captainID = 'F%sS%s' % (fleetID,shipID)
        myCaptain = anwp.war.captain.Captain({'id':captainID, 'name':'Captain%s' % captainID})
        myCaptain.setMyEmpire(myEmpire)
        # create ship
        myShip = anwp.war.ship.Ship({'id':shipID})
        position = myFleet.getAvailPosition()
        if position == -1:
            self.modeMsgBox('Max Ships already in fleet, choose larger formation')
        else:
            myShip.setMyPosition(myFleet.getAvailPosition())
            myShip.setMyCaptain(myCaptain)
            myShip.setMyFleet(myFleet)
            myShip.setMyDesign(self.myShipDesign)
    
    def createShipInfoFrame(self, myShipDict, myCaptainDict, myShipDesignDict, myEmpireDict):
        """Build a Ship Info Frame based on fleet and shipID's given"""
        self.destroyTempFrames()
        self.myShipDesign = None
        # create ship instance
        myEmpire = anwp.war.empire.Empire(myEmpireDict)
        myEmpire.myGalaxy = self.game
        
        # setup the ship design
        self.myShipDesign = anwp.war.shipdesign.ShipDesign(myShipDesignDict)
        self.myShipDesign.setMyEmpire(myEmpire)
        for quadID, myQuadDict in myShipDesignDict['quads'].iteritems():
            myQuad = anwp.war.quad.Quad(myQuadDict)
            myQuad.setMyParent(self.myShipDesign)
            # weapons have to be created first
            for weaponID, myWeaponDict in myQuadDict['weapons'].iteritems():
                myWeapon = anwp.war.weapon.Weapon(myWeaponDict)
                myWeapon.setMyQuad(myQuad)
            for componentID, myComponentDict in myQuadDict['components'].iteritems():
                myComponent = anwp.war.component.Component(myComponentDict)
                myComponent.setMyQuad(myQuad)
        self.myShipDesign.setMyStatus()
        
        self.myShip = anwp.war.ship.Ship(myShipDict)
        myCaptain = anwp.war.captain.Captain(myCaptainDict)
        self.myShip.setMyCaptain(myCaptain)
        self.myShip.setFromDict(self.myShipDesign, myShipDict)
        
        self.createShipInfoFrameFromShip(self.myShip)
    
    def draw(self):
        """Draw standard World information each frame"""
        anwp.sl.engine.clear()
        if self.simBattleInfo <> None:
            self.drawEmpireValues(200, 100)
        
        # render engine
        anwp.sl.engine.render()
    
    def genShipBattle(self):
        """Generate a ShipBattle object for the simulator to run"""
        d = {}
        d['id'] = '1'
        d['systemID'] = '1'
        d['systemName'] = 'TestLand'
        d['round'] = 1
        myShipBattle = anwp.war.shipbattle.ShipBattle(d)
        myShipBattle.setSeed()
        empiresDict = {} # dict breakdown of empires involved
        fleetsDict = {} # dict breakdown of fleets involved
        captainsDict = {} # dict breakdown of captains involved
        # loop through all fleets
        for fleetID, myFleet in self.fleets.iteritems():
            if len(myFleet.ships.keys()) > 0:
                # set fleet position for battle
                myFleet.setPosition()
                
                # determine target fleets
                myFleet.clearTargetFleets()
                for otherfleetID, otherFleet in self.fleets.iteritems():
                    if (otherFleet.empireID <> myFleet.empireID and
                        len(otherFleet.ships.keys()) > 0):
                        myFleet.addTargetFleet(otherfleetID)
                        
                # retrieve fleet info
                fleetsDict[fleetID] = myFleet.getMyFleetInfo()                
                # empire involved in battle
                if not empiresDict.has_key(myFleet.empireID):
                    # only retrieve ship designs involved in battle
                    sd = {}
                    for empireFleetID, myEmpireFleet in self.fleets.iteritems():
                        if myEmpireFleet.empireID == myFleet.empireID:
                            for shipID, myShip in myEmpireFleet.ships.iteritems():
                                captainsDict[myShip.captainID] = self.captains[myShip.captainID].getMyInfoAsDict()
                                if not sd.has_key(myShip.designID):
                                    sd[myShip.designID] = myShip.myDesign.getMyShipDesignInfo()
                    myEmpire = self.empires[myFleet.empireID]
                    e = {}
                    e['id'] = myEmpire.id
                    e['name'] = myEmpire.name
                    e['color1'] = myEmpire.color1
                    e['color2'] = myEmpire.color2
                    e['imageFile'] = myEmpire.imageFile
                    e['shipDesigns'] = sd
                    empiresDict[myFleet.empireID] = e
        # if a battle has taken place in this system, create ship battle
        if len(empiresDict.keys()) > 1:
            myShipBattle.setEmpiresDict(empiresDict)
            myShipBattle.setFleetsDict(fleetsDict)
            myShipBattle.setCaptainsDict(captainsDict)
            myShipBattle.setData(self.game.componentdata, self.game.shiphulldata, self.game.dronehulldata, self.game.weapondata)
            # ask the server if player can view ship battle
            if self.game.myEmpire['simulationsLeft'] > 0:
                try:
                    # set the server simulations left
                    result = self.game.server.setEmpire(self.game.authKey, {'simulationsLeft':self.game.myEmpire['simulationsLeft']-1})
                    if result == 1:
                        # view the ship battle
                        newMode = anwp.war.shipsimulator.ShipSimulator(self.game, myShipBattle)
                        self.game.enterMode(newMode)
                        self.game.myEmpire['simulationsLeft'] -= 1
                    else:
                        self.modeMsgBox(result)
                except:
                    self.modeMsgBox('genShipBattle->Connection to Server Lost, Login Again')
            else:
                self.modeMsgBox('You do not have any simulations left this round, build more simulation centers')
        else:
            self.modeMsgBox('Please setup a battle with at least 1 fleets of ships on either side')
    
    def getShipBattle(self, shipBattleKey):
        """Ask the Server for the Ship Battle Object"""
        try:
            serverResult = self.game.server.getShipBattle(self.game.authKey, shipBattleKey)
            if type(serverResult) == -1:
                self.modeMsgBox('getShipBattle->error')
            else:
                self.shipBattle = anwp.func.storedata.loadFromString(serverResult)
        except:
            self.modeMsgBox('getShipBattle->Connection to Server Lost')
    
    def viewShipBattle(self):
        """Actually View the ShipBattle"""
        if self.shipBattle == None:
            self.modeMsgBox('please select a ship battle to view')
        else:
            self.shipBattle.setData(self.game.componentdata, self.game.shiphulldata, self.game.dronehulldata, self.game.weapondata)
            newMode = anwp.war.shipsimulator.ShipSimulator(self.game, self.shipBattle)
            self.game.enterMode(newMode)
    
    def removeShip(self, fleetID, shipID):
        """Remove ship from simulation"""
        myFleet = self.fleets[fleetID]
        myFleet.removeShip(shipID)
    
    def setFleet(self, fleetID, dAttributes):
        """Set Fleet Attributes"""
        myFleet = self.fleets[fleetID]
        newMaxUnits = anwp.func.globals.fleetFormations[dAttributes['formationID']]['maxUnits']
        oldMaxUnits = anwp.func.globals.fleetFormations[myFleet.formationID]['maxUnits']
        if (newMaxUnits < oldMaxUnits):
            # new formation is smaller then earlier formation, remove ships as required
            for shipID in myFleet.ships.keys():
                myShip = myFleet.ships[shipID]
                if myShip.position >= newMaxUnits:
                    myFleet.removeShip(shipID)
        
        myFleet.setAttributes(dAttributes)
        myFleet.setMyFormation(myFleet.formationID)
        self.destroyTempFrames()
        self.simBattleInfo.panel.populate()
    
    def setFleetGrid(self, gridNum):
        """take the gridnumber given and set the grid Quadrant for fleet selected"""
        if self.simBattleInfo <> None and self.gridInfo <> None:
            if self.gridInfo.maxNum == 6:
                # this is coming from simBattleInfo panel
                try:
                    myFleet = self.fleets[self.simBattleInfo.panel.lstFleets.getSelectedItem().data]
                    myFleet.systemGrid = int(gridNum)
                    self.simBattleInfo.panel.populate()
                except:
                    pass
            else:
                # this is coming from fleetInfo panel
                # set grid quad point for fleet displayed
                fleetID = self.fleetInfo.panel.myFleetDict['id']
                self.fleetInfo.panel.lblQuad.setText(gridNum)
        
        # remove setgrid frame
        self.gridInfo.destroy()
    
    def setSimBattle(self):
        """Setup the Sim Battle GUI"""
        self.clearPanels()
        self.simBattleInfo = anwp.gui.simbattleinfo.SimBattleInfoFrame(self, self.game.app)
    
    def setPastBattle(self):
        """Setup the Past Battle GUI"""
        self.clearPanels()
        self.pastBattleInfo = anwp.gui.pastbattleinfo.PastBattleInfoFrame(self, self.game.app)
    
    def shareShipBattle(self, empireID, shipBattleKey):
        """Share the ShipBattle selected with another Empire"""
        try:
            serverResult = self.game.server.shareShipBattle(self.game.authKey, empireID, shipBattleKey)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Battle can now be viewed by Empire:%s' % self.game.allEmpires[empireID]['name'])
        except:
            self.modeMsgBox('shareShipBattle->Connection to Server Lost, Login Again')
