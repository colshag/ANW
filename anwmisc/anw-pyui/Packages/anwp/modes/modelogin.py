# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modelogin.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Login Mode in ANW
# ---------------------------------------------------------------------------
import pygame
import time
import types
import string

import pyui
import anwp.sl.engine
import anwp.sl.world
import anwp.gui.login
import mode
import anwp.func.imaging
import anwp.func.storedata
import anwp.func.globals
import anwp.func.funcs
    
class ModeLogin(mode.Mode):
    """This is the Login Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'LOGIN'
        self.empireLoginFrame = None
        self.galaxyLoginFrame = None
        
        # create server list, read ini file
        serverDict = {}
        for serverName in self.game.app.serverAddressList:
            serverDict[serverName] = serverName
        self.serverLoginFrame = anwp.gui.login.LoginFrame(self, self.game.app, 'Please Choose a Server', 'Available Servers:', serverDict, 'loginToServer')
        
        # create the world
        self.worldWidth = self.game.displayWidth
        self.worldHeight = self.game.displayHeight
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight))
        self.renderer.setBackMethod(self.draw)
        
    def createEmpireLogin(self, galaxyName, galaxyPass):
        """Create the empire login panel"""
        # attempt to Login to a Server with Galaxy Name and Password
        # if success, retrieve empire information for empire login
        self.game.authKey['galaxyName'] = galaxyName
        self.game.galaxyPass = galaxyPass
        empireDict = self.game.server.getEmpires(galaxyName, galaxyPass)
        if type(empireDict) == types.StringType:
            self.modeMsgBox(empireDict)
        else:
            # login success, create Empire Panel
            self.empireLoginFrame = anwp.gui.login.LoginFrame(self, self.game.app, 'Please Choose an Empire', 'Galaxy Selected: %s' % galaxyName, empireDict, 'loginToGame')
            self.galaxyLoginFrame.destroy()
    
    def loginToGame(self, empireID, empirePass):
        """Attempt to Login to a Server with Empire Name and Password"""
        # build authentication key
        self.game.empirePass = empirePass
        self.game.authKey['empireID'] = empireID
        self.game.authKey['galaxyPass'] = self.game.galaxyPass
        self.game.authKey['empirePass'] = empirePass
        self.game.authKey['ip'] = self.game.myIP
        self.game.authKey['round'] = 0
        self.game.authKey['version'] = self.game.version
        
        result = self.game.server.login(self.game.authKey)
        
        if type(result) == types.DictType:
            self.modeMsgBox(result['error'])
        else:
            # decompress encoded string
            result = anwp.func.funcs.decompressString(result)
            myDataDict = eval(result)
            
            # remove passwords from key, no longer needed
            del self.game.authKey['galaxyPass']
            del self.game.authKey['empirePass']
            
            # login worked, set game data to client
            self.loadDataToGame(myDataDict, empireID)
            
            # add round number to authkey
            self.game.authKey['round'] = self.game.currentRound
            
            # build all game images required
            self.buildGameImages()

            # perform game level generation of data
            self.game.createTechLines()
            self.game.createWarpLines()        

            # aquire session key
            self.game.authKey['key'] = self.game.myEmpire['key']

            #goto galaxy mode
            import modemap
            newMode = modemap.ModeMap(self.game)
            self.game.enterMode(newMode)
    
    def loginToServer(self, serverAddress):
        """Use Server Address to attempt to login to server and ask for galaxy list"""
        self.game.setServerConnection(serverAddress)
        # bring up galaxy login panel
        try:
            galaxyDict = self.game.server.getGalaxies()
            if type(galaxyDict) == types.StringType:
                self.modeMsgBox(galaxyDict)
            else:
                self.serverLoginFrame.destroy()
                self.galaxyLoginFrame = anwp.gui.login.LoginFrame(self, self.game.app, 'Please Choose a Galaxy', serverAddress, galaxyDict, 'createEmpireLogin')
        except:
            self.modeMsgBox('Connection to Server unavailable')
    
    def loadDataToGame(self, myDataDict, empireID):
        """Server passes dataDict to game, split dict into manageable Dicts
        that stores itself in the game object for client use"""
        self.game.myGalaxy = myDataDict['myGalaxy']
        self.game.currentRound = self.game.myGalaxy['currentRound']
        self.game.allEmpires = myDataDict['allEmpires']
        self.game.myEmpire = self.game.allEmpires[empireID]
        self.game.myEmpire['viewRadar'] = 1 #TODO: insert this into the server side
        self.game.myMailBox = self.game.myEmpire['mailBox']
        self.game.myEmpireID = empireID
        self.game.allSystems = myDataDict['allSystems']
        self.game.myTech = myDataDict['myTech']
        self.game.tradeRoutes = myDataDict['tradeRoutes']
        self.game.marketOrders = myDataDict['marketOrders']
        self.game.marketStats = myDataDict['marketStats']
        self.game.shipDesigns = myDataDict['shipDesignsDict']
        self.game.myCaptains = myDataDict['myCaptains']
        self.game.myShips = myDataDict['myShips']
        self.game.myArmadas = myDataDict['myArmadas']
        self.game.otherArmadas = myDataDict['otherArmadas']
        self.game.shipBattleDict = myDataDict['shipBattleDict']
        self.game.myRegiments = myDataDict['myRegiments']
        self.game.myArmies = myDataDict['myArmies']
        self.game.otherArmies = myDataDict['otherArmies']
    
    def buildGameImages(self):
        """Check Client and build all game images that could be required during game play"""
        # systems
        for systemID, systemDict in self.game.allSystems.iteritems():
            filename = systemDict['imageFile'] + '.png'
            imageFileName = '%s%s' % (self.game.app.simImagePath, filename)
            # see if image required is available
            if filename not in self.game.imageFileList:
                anwp.func.imaging.CreateSystemImage(systemDict['imageFile'], self.game.app.genImagePath, self.game.app.simImagePath)
                self.game.imageFileList.append(filename)
                
        # empires
        for empireID, empireDict in self.game.allEmpires.iteritems():
            filename = empireDict['imageFile'] + '.png'
            imageFileName = '%s%s' % (self.game.app.simImagePath, filename)          
            # see if image required is available
            if filename not in self.game.imageFileList:
                anwp.func.imaging.CreateEmpireImage(empireDict['imageFile'], self.game.app.genImagePath, self.game.app.simImagePath)
                self.game.imageFileList.append(filename)
                
        # tech
        for techID, techDict in self.game.myTech.iteritems():
            filename = techDict['imageFile'] + '.png'
            imageFileName = '%s%s' % (self.game.app.simImagePath, filename)          
            # see if image required is available
            if filename not in self.game.imageFileList:
                anwp.func.imaging.CreateTechImage(techDict['imageFile'], self.game.app.genImagePath, self.game.app.simImagePath)
                self.game.imageFileList.append(filename)
        
        # ship images
        for shipID, myShipHull in self.game.shiphulldata.iteritems():
            color1 = self.game.myEmpire['color1']
            color2 = self.game.myEmpire['color2']
            name1 = '%sb_%s_%s' % (string.lower(myShipHull.abr), color1, color2)
            name2 = '%s_%s_%s' % (string.lower(myShipHull.abr), color1, color2)
            name3 = '%s_%s_%s' % (string.lower(myShipHull.abr), anwp.func.globals.simEmpireColors['1']['color1'],anwp.func.globals.simEmpireColors['1']['color2'])
            name4 = '%s_%s_%s' % (string.lower(myShipHull.abr), anwp.func.globals.simEmpireColors['2']['color1'],anwp.func.globals.simEmpireColors['2']['color2'])
            self.createGenericImage(name1)
            self.createGenericImage(name2)
            self.createGenericImage(name3)
            self.createGenericImage(name4)
        
        # selectors
        color1 = self.game.myEmpire['color1']
        color2 = self.game.myEmpire['color2']
        name = 'selector_%s_%s' % (color1, color2)
        self.createGenericImage(name)
        
        # shipyards
        name = 'shipyards_%s_%s' % (color1, color2)
        self.createGenericImage(name)
        
        # military installations
        name = 'militaryinst_%s_%s' % (color1, color2)
        self.createGenericImage(name)
        
        # warp gates
        for empireID, empireDict in self.game.allEmpires.iteritems():
            name = 'warpgate_%s_%s' % (empireDict['color1'], empireDict['color2'])
            self.createGenericImage(name)
        
        # armadas
        for empireID, empireDict in self.game.allEmpires.iteritems():
            name = 'armada_%s_%s' % (empireDict['color1'], empireDict['color2'])
            self.createGenericImage(name)
        
        # armies
        for empireID, empireDict in self.game.allEmpires.iteritems():
            name = 'army_%s_%s' % (empireDict['color1'], empireDict['color2'])
            self.createGenericImage(name)
            
    def draw(self):
        """Draw Login World information each frame"""
        now = time.localtime(time.time())
        anwp.sl.engine.clear()
        buffer = 20
        width = self.worldWidth - self.viewX + self.bufferX
        height = self.worldHeight - self.viewY + self.bufferY

        anwp.sl.engine.drawImage(0, 0, self.appWidth, self.appHeight, self.backgroundImage)
        pyui.desktop.getRenderer().drawText('WELCOME TO ARMADA NET WARS - Version %s' % self.game.version, (10, 10), anwp.func.globals.colors['blue'], self.game.app.systemFont, flipped = 1)
        pyui.desktop.getRenderer().drawText(time.asctime(now), (10, self.worldHeight-30), anwp.func.globals.colors['blood'], self.game.app.systemFont, flipped = 1)
        
        anwp.sl.engine.render()
    
    def onMouseMove(self, event):
        """Remove default MouseMove access"""
        pass

    def onKey(self):
        """Remove default keyboard access"""
        pass

        