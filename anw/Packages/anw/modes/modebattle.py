# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modebattle.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This allows ship designs to be simulated
# ---------------------------------------------------------------------------
import random
import math

import mode
from anw.func import storedata, globals, root, funcs
from anw.war import shipsimulator, ship, captain, empire
from anw.war import shipdesign, quad, weapon, component, shipbattle

class ModeBattle(mode.Mode, root.Root):
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
        self.ships = {} # stores ship objects
        self.empires = {} # stores simulated empires
        self.captains = {} # stores captain objects
        self.createEmpires()
        
    def createEmpires(self):
        """Create the simulated empires"""
        myEmpire = empire.Empire({'id':'1', 'name':'Sim Empire 1', 
                                           'color1':globals.empires[1]['color1'], 'color2':globals.empires[1]['color2']})
        self.empires['1'] = myEmpire
        myEmpire = empire.Empire({'id':'2', 'name':'Sim Empire 2', 
                                           'color1':globals.empires[4]['color1'], 'color2':globals.empires[4]['color2']})
        self.empires['2'] = myEmpire
        
        for empireID, myEmpire in self.empires.iteritems():
            myEmpire.myGalaxy = self
    
    def simulateShipDesigns(self, multiSimDict):
        """Take two ships designs and setup a battle between them"""
        self.createShips(multiSimDict)
        self.genShipBattle('1')
        self.viewShipBattle()
    
    def createShips(self, multiSimDict):
        """Create ships needed for simulation"""
        for designID, shipNum in multiSimDict[1].iteritems():
            try:
                myShipDesign = self.game.shipDesignObjects[designID]
            except:
                myShipDesign = designID
                self.game.currentDesign = myShipDesign
            self.addShip(shipNum,'1', myShipDesign)
        for designID, shipNum in multiSimDict[2].iteritems():
            try:
                myShipDesign = self.game.shipDesignObjects[designID]
            except:
                myShipDesign = designID
            self.addShip(shipNum,'2', myShipDesign)
    
    def addShip(self, amount, empireID, myShipDesign):
        """Add Ship"""
        myEmpire = self.empires[empireID]
        rowNum = int(math.sqrt(amount))
        x = 0
        y = 0
        i = 0
        while i < amount:
            id = self.getNextID(self.captains)
            name = '%s Captain-%d' % (myEmpire.color1, i)
            myCaptain = captain.Captain({'id':id, 'name':name})
            myCaptain.setMyEmpire(myEmpire)
            shipID = self.getNextID(self.ships)
            myShip = ship.Ship({'id':shipID, 'fromSystem':'1', 'empireID':empireID})
            myShip.setMyCaptain(myCaptain)
            myShip.myCaptain.addExperience(800)
            myShip.setMyGalaxy(self)
            myShip.setMyDesign(myShipDesign)
            myShip.setMyStatus()
            myShip.setX = random.randint(-100,-70) + (int(empireID)-1)*150 + 2*x
            myShip.setY = random.randint(-30,0) + 2*y
            if x > rowNum:
                x = 0
                y += 1
            else:
                x += 1
            i += 1
    
    def genShipBattle(self, systemID):
        """Generate a ShipBattle object for the simulator to run"""
        d = {}
        d['id'] = '1'
        d['systemID'] = '1'
        d['systemName'] = 'Simu-System'
        d['cities'] = 20
        d['round'] = 1
        d['empireID'] = '1'
        d['x'] = 54
        d['y'] = 6
        myShipBattle = shipbattle.ShipBattle(d)
        myShipBattle.setSeed()
        empiresDict = {}
        shipsDict = {}
        captainsDict = {}
        targets = 0
        
        for shipID, myShip in self.ships.iteritems():
            if myShip.toSystem == '1':
                myShip.systemGrid = funcs.getSimQuadrant(myShip)
                myShip.setPosition()
                myShip.clearTargetShips()
                for othershipID, otherShip in self.ships.iteritems():
                    if (otherShip.toSystem == systemID and 
                        otherShip.empireID != myShip.empireID):
                        myShip.addTargetShip(othershipID)
                
                targets += len(myShip.targets)

                if not empiresDict.has_key(myShip.empireID):
                    myEmpire = self.empires[myShip.empireID]
                    e = {}
                    e['id'] = myEmpire.id
                    e['name'] = myEmpire.name
                    e['color1'] = myEmpire.color1
                    e['color2'] = myEmpire.color2
                    e['imageFile'] = myEmpire.imageFile
                    e['shipDesigns'] = {}
                    e['droneDesigns'] = {}
                    for droneDesignID, droneDesign in self.game.droneDesignObjects.iteritems():
                        e['droneDesigns'][droneDesignID] = droneDesign.getMyShipDesignInfo()
                    
                    empiresDict[myShip.empireID] = e
                
                shipsDict[shipID] = myShip.getMyShipInfo()
                captainsDict[myShip.captainID] = self.captains[myShip.captainID].getMyInfoAsDict()
                
                if myShip.designID not in empiresDict[myShip.empireID]['shipDesigns'].keys():
                    empiresDict[myShip.empireID]['shipDesigns'][myShip.designID] = myShip.myDesign.getMyShipDesignInfo()

        if len(empiresDict.keys()) > 1 and targets > 0:
            myShipBattle.setEmpiresDict(empiresDict)
            myShipBattle.setShipsDict(shipsDict)
            myShipBattle.setCaptainsDict(captainsDict)
            self.shipBattle = myShipBattle
    
    def getShipBattle(self, shipBattleKey):
        """Ask the Server for the Ship Battle Object"""
        try:
            serverResult = self.game.server.getShipBattle(self.game.authKey, shipBattleKey)
            if type(serverResult) == -1:
                self.modeMsgBox('getShipBattle->error')
            else:
                self.shipBattle = storedata.loadFromString(serverResult)
        except:
            self.modeMsgBox('getShipBattle->Connection to Server Lost')
    
    def viewShipBattle(self):
        """Actually View the ShipBattle"""
        if self.shipBattle == None:
            self.modeMsgBox('please select a ship battle to view')
        else:
            self.game.app.enableMouseCamControl()
            newMode = shipsimulator.ShipSimulator(self.game, self.shipBattle)
            self.game.enterMode(newMode)
            
    def shareShipBattle(self, empireID, shipBattleKey):
        """Share the ShipBattle selected with another Empire"""
        try:
            serverResult = self.game.server.shareShipBattle(self.game.authKey, empireID, shipBattleKey)
            if serverResult != 1:
                self.modeMsgBox(serverResult)
            else:
                self.modeMsgBox('Battle can now be viewed by Empire:%s' % self.game.allEmpires[empireID]['name'])
        except:
            self.modeMsgBox('shareShipBattle->Connection to Server Lost, Login Again')
