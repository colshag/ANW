# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# game.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of one game of ANW
# ---------------------------------------------------------------------------
from xmlrpclib import ServerProxy
import socket
import random
import os

import anwp.func.storedata
import anwp.war.shipsimulator
import anwp.func.globals
import anwp.func.funcs

class ANWGame:
    """A game of ANW"""
    def __init__(self, app, displayWidth, displayHeight):
        self.version = anwp.func.globals.currentVersion
        self.app = app
        self.mode = None # game can only be in one mode at a time        
        self.displayWidth = displayWidth # app width
        self.displayHeight = displayHeight #app height
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
        self.warpLines = [] # contains line information
        self.techLines1 = [] # Tech Age 1 connection lines
        self.techLines2 = [] # Tech Age 2 connection lines
        self.techLines3 = [] # Tech Age 3 connection lines        
        self.imageFileList = self.getImageFileList(self.app.simImagePath) # list of image file names in the sims/images directory
        self.imageGenFileList = self.getImageFileList(self.app.genImagePath) # list of image file names in the images directory
        self.componentdata = {} # component data objects
        self.weapondata = {} # weapon data objects
        self.shiphulldata = {} # ship hull data objects
        self.dronehulldata = {} # drone hull data objects
        self.regimentdata = {} # regiment data objects
        self.shipDesigns = {} # ship design dict d[id] = (name, hullID, compDict, weaponDict)
        self.shipBattleDict = {} # dict of available ship battles to view key=shipbattlekey, value=description
        self.shipDesignObjects = {} # key = design id, value = built ship design object
        
        try:
            # load client data
            data = anwp.func.storedata.loadFromFile('%s/client.data' % self.app.path)
            self.componentdata = data['componentdata']
            self.weapondata = data['weapondata']
            self.shiphulldata = data['shiphulldata']
            self.dronehulldata = data['dronehulldata']
            self.regimentdata = data['regimentdata']
            self.industrydata = data['industrydata']
        except TypeError:
            pass
        
        # enter starting mode
        if self.displayWidth > 0 and self.displayHeight > 0:
            # check if auto-login values used
            if self.app.server <> '' and self.app.galaxy <> '' and self.app.empire <> '':
                # auto-login to game using command line arguments
                self.setServerConnection(self.app.server)
                self.authKey['galaxyName'] = self.app.galaxy
                startMode = anwp.modes.modelogin.ModeLogin(self)
                startMode.serverLoginFrame.destroy()
                startMode.loginToGame(self.app.empire, self.app.password)
                self.app.playMusic('song1')
            else:
                # grab a random supplied ship battle file
                shipBattleList = list(anwp.func.funcs.all_files('../Database', '*.ship'))
                shipBattleName = random.choice(shipBattleList)
                shipBattle = anwp.func.storedata.loadFromFile(shipBattleName)
                shipBattle.setData(self.componentdata, self.shiphulldata, self.dronehulldata, self.weapondata)
                # grab the last battle
                startMode = anwp.war.shipsimulator.ShipSimulator(self, shipBattle, True)
                self.enterMode(startMode)
    
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
        for techID, techDict in self.myTech.iteritems():
            for itemID in techDict['preTechs']:
                # store line if in same age of technology
                techDict2 = self.myTech[itemID]
                if techDict['techAge'] == techDict2['techAge'] and techDict['id'] <> techDict2['id']:
                    x1 = techDict['x']
                    y1 = techDict['y']
                    x2 = techDict2['x']
                    y2 = techDict2['y']
                    techLinesObj = getattr(self, 'techLines%d' % techDict['techAge'])
                    techLinesObj.append((x1, y1, x2, y2))
    
    def getImageFileList(self, path):
        """Return list of image files in path directory"""        
        for root, dirs, files in os.walk(path):
            return files
    
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
    
    def setServerConnection(self, serverAddress):
        """Set the server for connection purposes"""
        if self.displayWidth > 0 and self.displayHeight > 0:
            self.server = ServerProxy(serverAddress)
        else:
            self.server = None
    
    def update(self, interval):
        """Update the current game mode, return the status, 0 means stop game"""
        if self.mode:
            result = self.mode.update(interval)
            return result
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

class TestGame(ANWGame):
    """Test Game"""
    def __init__(self, app, w, h):
        self.mode = None
        self.authKey = {'galaxyName':'None', 'empireID':'0', 'key':'123', 'ip':'1.2.3.4'}
        self.myGalaxy = {'currentRound': 0, 'yMax': 0, 'version': '0.0.1', 'xMax': 0, 'currentHoursLeft': 11, 'systemSize': 100, 'name': 'Aliciela'}
        self.myEmpire = {'name': 'Kurita', 'ip': '', 'AL': 0, 'EC': 0, 'color1': '', 'simulationsLeft': 0, 'color2': '', 'emailAddress': '', 'key': '', 'designsLeft': 0, 'IA': 0, 'CR': 0, 'cities': 0}
        self.myTech = {'216': {'name': 'Intelligent Shipyards', 'currentPoints': 0, 'imageFile': 'tech_red', 'y': 1800, 'id': '216', 'preTechs': ['208'], 'complete': 0, 'requiredPoints': 400, 'x': 300, 'preTechNum': 1, 'techAge': 3, 'description': 'Intelligent Shipyards\n'}, '217': {'name': 'Intelligent Military Installations', 'currentPoints': 0, 'imageFile': 'tech_red', 'y': 2000, 'id': '217', 'preTechs': ['208'], 'complete': 0, 'requiredPoints': 400, 'x': 300, 'preTechNum': 1, 'techAge': 3, 'description': 'Intelligent Military Installations\n'}, '214': {'name': 'Intelligent Jamming', 'currentPoints': 0, 'imageFile': 'tech_red', 'y': 900, 'id': '214', 'preTechs': ['204'], 'complete': 0, 'requiredPoints': 400, 'x': 300, 'preTechNum': 1, 'techAge': 3, 'description': 'Intelligent Jamming\n'}, '215': {'name': 'Plasma Starship Weapons', 'currentPoints': 0, 'imageFile': 'tech_red', 'y': 1000, 'id': '215', 'preTechs': ['206'], 'complete': 0, 'requiredPoints': 400, 'x': 300, 'preTechNum': 1, 'techAge': 3, 'description': 'Plasma Starship Weapons\n'}}