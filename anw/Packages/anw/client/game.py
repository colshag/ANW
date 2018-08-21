# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# game.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of one game of ANW
# ---------------------------------------------------------------------------
import sys
from xmlrpclib import ServerProxy
import socket
import random
import os
import types
import time

from anw.func import globals
if globals.serverMode == 0:
    from anw.modes import modetech, modemail, modebattle, modelogin
from anw.func import globals, funcs, storedata
from anw.war import shipdesign, dronedesign, empire, tech, shipsimulator

class ANWGame:
    """A game of ANW"""
    def __init__(self, app, shipBattle):
        self.version = globals.currentVersion
        self.shipBattle = shipBattle
        self.app = app
        self.mode = None # game can only be in one mode at a time        
        self.server = None  # server object used for server communication
        self.myIP = self.getMyIP() # client ip address
        self.galaxyPass = ''
        self.empirePass = ''
        self.authKey = {} # authentication key, used in most client/server communication
        self.myGalaxy = {} # contains galaxy specific info from server
        self.currentRound = 0 # current round of play
        self.myEmpire = {} # contains my empire info from server
        self.myMailBox = {} # contains all mail for my empire
        self.myEmpireID = '' # ID of Empire logged in
        self.allEmpires = {} # contains all empire info from server
        self.allSystems = {} # contains all system info from server
        self.myCaptains = {} # contains my captain info from server
        self.myShips = {} # contains my ship info from server
        self.myRegiments = {} # contains my regiment info from server
        self.myArmadas = {} # SystemID(key), value=list of ship id's
        self.myArmies = {} # SystemID(key), value=list of regiment id's
        self.otherArmadas = {} # SystemID(key), value=list of empire id's
        self.otherArmies = {} # SystemID(key), value=list of empire id's
        self.myTech = {} # contains my tech info from server
        self.industrydata = {} # Industry Data info
        self.tradeRoutes = {} # all trade route info
        self.marketOrders = {} # all relevant market Orders
        self.marketStats = {} # dict contains market stats for each round, id=round
        self.empireStats = {} # dict contains empire stats
        self.warpLines = [] # contains line information
        self.techLines = [] # Tech connection lines    
        self.componentdata = {} # component data objects
        self.weapondata = {} # weapon data objects
        self.shiphulldata = {} # ship hull data objects
        self.dronehulldata = {} # drone hull data objects
        self.regimentdata = {} # regiment data objects
        self.shipDesigns = {} # ship design dict d[id] = (name, hullID, compDict, weaponDict)
        self.droneDesigns = {} # drone design dict
        self.shipBattleDict = {} # dict of available ship battles to view key=shipbattlekey, value=description
        self.shipDesignObjects = {} # key = design id, value = built ship design object
        self.droneDesignObjects = {} # key = design id, value = built in drone design object
        self.myEmpireObj = None
        self.currentDesign = None
        self.ships = {} # placeholder only
        self.empires = {}
        self.prices = {}
        
        self.loadClientData()
        if globals.serverMode == 0:
            self.loginToSplashScreen()
    
    def loginToSplashScreen(self):
        startMode = modelogin.ModeLogin(self, 20)
        self.enterMode(startMode)
            
    def setMyTech(self, myTechDict):
        """Build My Tech based on Dict given from server"""
        for id, techDict in myTechDict.iteritems():
            myTech = tech.Tech(techDict)
            self.myTech[id] = myTech
    
    def setMyEmpireObj(self):
        """Set the Empire Object"""
        self.myEmpireObj = empire.Empire({'id':self.myEmpire['id'],
                                          'name':self.myEmpire['name'],
                                          'color1':self.myEmpire['color1'],
                                          'color2':self.myEmpire['color2'],
                                          'imageFile':self.myEmpire['imageFile']})
        self.myEmpireObj.setMyGalaxy(self)
    
    def createShipDesigns(self):
        """Create all Ship Design Objects that Player currently uses"""
        for designID, designInfo in self.shipDesigns.iteritems():
            myDesign = self.getShipDesign(designID, designInfo[1],designInfo[2],designInfo[3],designInfo[0])
            self.shipDesignObjects[designID] = myDesign
                
    def createDroneDesigns(self):
        """Create all Drone Design Objects that Player currently uses"""
        for designID, designInfo in self.droneDesigns.iteritems():
            myDesign = self.getDroneDesign(designID, designInfo[1],designInfo[2],designInfo[3],designInfo[0])
            self.droneDesignObjects[designID] = myDesign

    def getShipDesign(self, designID, shipHullID, compDict, weapDict, name):
        """Take the provided design information and build the Ship Design for viewing"""
        myShipDesign = shipdesign.ShipDesign({'id':designID, 'shipHullID':shipHullID})
        myShipDesign.setMyEmpire(self.myEmpireObj)
        myShipDesign.myShipHull = self.shiphulldata[shipHullID]
        myShipDesign.setMyDesign(shipHullID, compDict, weapDict)
        myShipDesign.name = name
        return myShipDesign
    
    def getDroneDesign(self, designID, droneHullID, compDict, weapDict, name):
        """Take the provided design information and build the Drone Design for viewing"""
        myDroneDesign = dronedesign.DroneDesign({'id':designID, 'shipHullID':droneHullID})
        myDroneDesign.setMyEmpire(self.myEmpireObj)
        myDroneDesign.myShipHull = self.dronehulldata[droneHullID]
        myDroneDesign.setMyDesign(droneHullID, compDict, weapDict)
        myDroneDesign.name = name
        return myDroneDesign

    def loadClientData(self):
        """Load all client data from client.data file instead of grabbing from server
        to save bandwidth"""
        try:
            # load client data
            data = storedata.loadFromFile('%s/client.data' % self.app.path)
            self.componentdata = data['componentdata']
            self.weapondata = data['weapondata']
            self.shiphulldata = data['shiphulldata']
            self.dronehulldata = data['dronehulldata']
            self.regimentdata = data['regimentdata']
            self.industrydata = data['industrydata']
        except TypeError:
            pass
        
    def loginToGame(self):
        """Attempt to login to the game using supplied command line arguments"""
        if self.shipBattle != None:
            self.myEmpireID = '1'
            self.myEmpire['name'] = 'Test Simulator'
            self.myEmpire['CR'] = 0
            self.myGalaxy['currentHoursLeft'] = 0
            startMode = shipsimulator.ShipSimulator(self, self.shipBattle)
            self.enterMode(startMode)
        else:
            self.setServerConnection(self.app.server)
            self.setAuthorizationKey()
            self.getLoginDataFromServer()
    
    def setServerConnection(self, serverAddress):
        """Set the server for connection purposes"""
        self.server = ServerProxy(serverAddress)
    
    def setAuthorizationKey(self):
        """Create a key for further client server validation"""
        self.authKey = {}
        self.authKey['galaxyName'] = self.app.galaxy
        self.empirePass = self.app.password
        self.authKey['empireID'] = self.app.empire
        self.authKey['galaxyPass'] = self.galaxyPass
        self.authKey['empirePass'] = self.empirePass
        self.authKey['ip'] = self.myIP
        self.authKey['round'] = 0
        self.authKey['version'] = self.version
    
    def getLoginDataFromServer(self):
        """Actually ask Server for Login information as a compressed string of data"""
        try:
            result = self.server.login(self.authKey)
            if result == {'error':'Cannot Login, Galaxy currently ending Round, please wait for email'}:
                result = self.waitForRoundToEnd()
                self.processSuccessfulLogin(result)
            elif type(result) == types.DictType:
                self.gotoErrorMode(result['error'])
            else:
                self.processSuccessfulLogin(result)
        except:
            self.gotoErrorMode('Login Error, please contact Admin [{}]'.format(sys.exc_info()))
    
    def processSuccessfulLogin(self, result):
        """Login worked, process the data"""
        self.processLoginInfo(result)
        startMode = modemail.ModeMail(self)
        self.enterMode(startMode)
        
    def waitForRoundToEnd(self):
        """Round is ending loop until it stops"""
        while 1:
            result = self.server.login(self.authKey)
            if result == {'error':'Cannot Login, Galaxy currently ending Round, please wait for email'}:
                time.sleep(10)
            else:
                return result
            
    def gotoErrorMode(self, errorMessage):
        """Goto Login mode and display Error"""
        import sys
        print errorMessage
        self.app.quit()
            
    def processLoginInfo(self, data):
        """Setup login data for game memory access"""
        myDataDict = self.decompressLoginInfo(data)
        self.loadDataToGame(myDataDict, self.authKey['empireID'])
        self.setWarpLines()
        self.setSessionKey()

    def decompressLoginInfo(self, data):
        """decompress login info turn back into dictionary"""
        data = funcs.decompressString(data)
        myDataDict = eval(data)
        return myDataDict
    
    def loadDataToGame(self, myDataDict, empireID):
        """Server passes dataDict to game, split dict into manageable Dicts
        that stores itself in the game object for client use"""
        self.myGalaxy = myDataDict['myGalaxy']
        self.currentRound = self.myGalaxy['currentRound']
        self.allEmpires = myDataDict['allEmpires']
        self.myEmpire = self.allEmpires[empireID]
        self.myEmpire['viewRadar'] = 1 #TODO: insert this into the server side
        self.myMailBox = self.myEmpire['mailBox']
        self.myEmpireID = empireID
        self.allSystems = myDataDict['allSystems']
        self.setMyTech(myDataDict['myTech'])
        self.tradeRoutes = myDataDict['tradeRoutes']
        self.marketOrders = myDataDict['marketOrders']
        self.marketStats = myDataDict['marketStats']
        self.prices = myDataDict['prices']
        self.shipDesigns = myDataDict['shipDesignsDict']
        self.droneDesigns = myDataDict['droneDesignsDict']
        self.myCaptains = myDataDict['myCaptains']
        self.myShips = myDataDict['myShips']
        self.myArmadas = myDataDict['myArmadas']
        self.otherArmadas = myDataDict['otherArmadas']
        self.warpedArmadas = myDataDict['warpedArmadas']
        self.shipBattleDict = myDataDict['shipBattleDict']
        self.myRegiments = myDataDict['myRegiments']
        self.myArmies = myDataDict['myArmies']
        self.otherArmies = myDataDict['otherArmies']
        self.warpedArmies = myDataDict['warpedArmies']
        self.empireStats = myDataDict['empireStats']
        
        self.setMyEmpireObj()
        self.createDroneDesigns()
        self.createShipDesigns()
    
    def setWarpLines(self):
        """Perform game level generation of warp lines using system data"""
        self.createTechLines()
        self.createWarpLines()
    
    def setSessionKey(self):
        """Aquire Session Key"""
        del self.authKey['galaxyPass']
        del self.authKey['empirePass']
        self.authKey['round'] = self.currentRound
        self.authKey['key'] = self.myEmpire['key']
    
    def createWarpLines(self):
        """Create the Space Map System Connection Lines once in the game object"""
        # create warp lines list
        for systemID, systemDict in self.allSystems.iteritems():
            for itemID in systemDict['connectedSystems']:
                if itemID > systemID:
                    # store line
                    systemDict2 = self.allSystems[itemID]
                    x1 = systemDict['x']
                    y1 = systemDict['y']
                    x2 = systemDict2['x']
                    y2 = systemDict2['y']
                    self.warpLines.append((x1, y1, x2, y2))
    
    def createTechLines(self):
        """Create the Tech Tree Connection Lines once in the game object"""
        # create tech lines list
        for techID, myTech in self.myTech.iteritems():
            for itemID in myTech.preTechs:
                myTech2 = self.myTech[itemID]
                if myTech.id != myTech2.id:
                    x1 = myTech.x
                    y1 = myTech.y
                    x2 = myTech2.x
                    y2 = myTech2.y
                    self.techLines.append((x1, y1, x2, y2,myTech.complete))
    
    def createShipSimulation(self, multiSimDict):
        """Create a Ship Simulation between two ship designs"""
        newMode = modebattle.ModeBattle(self)
        self.enterMode(newMode)
        newMode.simulateShipDesigns(multiSimDict)
    
    def getMyIP(self):
        """Return IP Address of client"""
        try:  # only need to get the IP addresss once
            ip = socket.gethostbyaddr(socket.gethostname())[-1][0]
        except: # if we don't have an ip, default to someting in the 10.x.x.x private range
            ip = '10'
            rand = random.Random()
            for i in range(3):
                ip += '.' + str(rand.randrange(1, 254))
        return ip
    
    def update(self, interval):
        """Update the current game mode, return the status, 0 means stop game"""
        if self.mode:
            result = self.mode.update(interval)
            return 1
        else:
            return 0

    def draw(self):
        """Envoke current mode draw"""
        self.mode.draw()
        
    def enterMode(self, newMode):
        """Exit existing mode, enter new mode"""
        if self.mode:
            print 'Exiting mode:', self.mode.name
            self.mode.exitMode()
        self.mode = newMode
        print 'Entering mode:', newMode.name        
        self.mode.enterMode()
    
    def getRegInfo(self, regID):
        """Return a string detailing Regiment info for lists"""
        myReg = self.myRegiments[regID]
        info = '<%s>%s' % (myReg['rank'], myReg['name'])
        if myReg['strength'] < 100:
            info = '<%d' % myReg['strength'] + '%>' + info
        return info
    
    def getShipInfo(self, shipID):
        """Return a string detailing Ship info for lists"""
        myShip = self.myShips[shipID]
        myCaptain = self.myCaptains[myShip['captainID']]
        info = '<%s>%s' % (myCaptain['rank'], myShip['name'])
        if myShip['strength'] < 100:
            info = '<%d' % myShip['strength'] + '%>' + info
        return info
        
        
