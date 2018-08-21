# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# mode.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is the base mode class in ANW
# ---------------------------------------------------------------------------
import random
import pygame
import types
import logging

import pyui
import anwp.sl.entity
import anwp.sl.engine
import anwp.gui.msgbox
import anwp.gui.yesnobox
import anwp.gui.shipinfo
import anwp.war.shipdesign

class Updater(anwp.sl.entity.Entity):
    """make sure notify is called every frame"""
    def update(self, interval, world):
        self.dirty = 1
        return anwp.sl.entity.Entity.update(self, interval, world)

class Mode(object):
    """This is the base Mode class"""
    def __init__(self, game):
        # default mode attributes
        self.name = "MODE"
        self.game = game
        self.world = None # world represents the engine generated game area, can be larger/smaller then app dimensions
        self.worldWidth = 0
        self.worldHeight = 0
        self.appWidth = self.game.displayWidth
        self.appHeight = self.game.displayHeight
        self.backgroundImage = '%sbackground.png' % self.game.app.genImagePath
        self.myShipDesign = None
            
        self.bufferX = self.appWidth/2
        self.bufferY = self.appHeight/2
        self.viewX = self.bufferX
        self.viewY = self.bufferY
        self.scrollSpeed = 50 # speed of keyboard scrolling
        
        # create default gui panels
        self.panels = []
        self.shipInfoFrame = None
        
        # store temp frames for later destruction
        self.tempFrames = []
        
        # default sim creation
        self.sims = []
        self.selected = 0
        self.simSelector = None
        
        # logging
        self.log = logging.getLogger('mode')        
    
    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['log']             # remove stuff not to be pickled
        return odict

    def __setstate__(self,dict):
        log=logging.getLogger('mode')
        self.__dict__.update(dict)
        self.log=log
    
    def askForHelp(self):
        """Ask the Server to analyse Player and provide help"""
        try:
            serverResult = self.game.server.askForHelp(self.game.authKey)
            if type(serverResult) == types.ListType:
                (message, self.game.myEmpire['help']) = serverResult
                self.modeMsgBox(message)
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('askForHelp->Connection to Server Lost')
    
    def getShipDesign(self, shipHullID, compDict, weapDict, name=''):
        """Take the provided design information and build the Ship Design for viewing"""
        myShipDesign = anwp.war.shipdesign.ShipDesign({'id':'1', 'shipHullID':shipHullID})
        myShipDesign.name = name
        myShipDesign.weapondata = self.game.weapondata
        myShipDesign.componentdata = self.game.componentdata
        myShipDesign.myShipHull = self.game.shiphulldata[shipHullID]
        myShipDesign.setMyDesign(shipHullID, compDict, weapDict)
        return myShipDesign
        
    def createGetGridFrame(self, gridNum, maxNum, title, activeGrids=[]):
        """Create a Get Grid Frame for Fleet Configuration"""
        self.gridInfo = anwp.gui.getgrid.GetGridFrame(self, self.game.app, gridNum, maxNum, title, activeGrids)
        self.tempFrames.append(self.gridInfo)
        
    def createSelector(self):
        """Create the Selector Sim"""
        import anwp.sims
        if self.simSelector == None:
            simFileName = 'selector_%s_%s' % (self.game.myEmpire['color1'], self.game.myEmpire['color2'])
            self.simSelector = anwp.sl.entity.Entity(anwp.sims.categories.SelectorCategory('%s%s.png' % (self.game.app.simImagePath, simFileName),'big'))
            x = -1000
            y = -1000
            facing = 0
            speed = 0
            self.simSelector.turnRate = 20
            self.world.addToWorld(self.simSelector, x, y, facing, speed)
    
    def createSelector2(self):
        """Create the Selector Sim"""
        import anwp.sims
        if self.simSelector == None:
            self.simSelector = anwp.sl.entity.Entity(anwp.sims.categories.SelectorCategory('%sselector2.png' % (self.game.app.genImagePath),'small'))
            x = -1000
            y = -1000
            facing = 0
            speed = 0
            self.simSelector.turnRate = 40
            self.world.addToWorld(self.simSelector, x, y, facing, speed)
    
    def removeSelector(self):
        """Remove Selector from mode"""
        if self.simSelector <> None:
            self.world.removeFromWorld(self.simSelector)
            self.simSelector = None
    
    def centerCamera(self, x, y):
        """Center Camera on x,y given"""
        if x < self.bufferX:
            self.viewX = self.bufferX
        else:
            self.viewX = x
        if y < self.bufferY:
            self.viewY = self.bufferY
        else:
            self.viewY = y
    
    def checkEndTurn(self):
        """Do a Server Assesment of turn before ending the turn"""
        try:
            if 'EndTurn' in self.game.myEmpire['help']:
                # turn not ended yet
                (serverResult, self.game.myEmpire['help']) = self.game.server.askForHelp(self.game.authKey)
                if serverResult == 'Server Assessment: WARNINGS:0, CRITICAL:0 (Check Mail for Assesment)':
                    # server assessment is good, end the turn without asking
                    self.endMyTurn()
                else:
                    # server assessment has not come back without warnings ask for confirmation
                    self.modeYesNoBox('%s - Do you still want to end your turn?' % serverResult, 'endturnYes', 'yesNoBoxNo')
            else:
                # turn already ended, unend turn
                self.modeYesNoBox('Do you want to cancel your end turn?' , 'endturnYes', 'yesNoBoxNo')
        except:
            self.modeMsgBox('checkEndTurn->Connection to Server Lost, Login Again')
    
    def createDebugPanel(self):
        """Create the debugging panel"""
        self.debugFrame = pyui.widgets.Frame(20,20,260,180, 'Object Info');
        self.debugPanel = anwp.gui.debug.DebugPanel()
        self.debugFrame.replacePanel(self.debugPanel)
        self.panels.append(self.debugFrame)
    
    def createSims(self):
        """Create the simulation objects"""
        import anwp.sims
        for i in range(0,100):
            sim = Updater(anwp.sims.categories.Quad())
            self.sims.append(sim)
            x = random.randint(0,self.worldWidth-20)
            y = random.randint(0,self.worldHeight-20)
            facing = random.randint(0,360)
            speed = random.randint(0,200)
            sim.turnRate = 200
            self.world.addToWorld(sim ,x, y, facing, speed)
        
        self.selected = self.sims[0]
        self.selected.addObserver(self.debugPanel)
    
    def createGenericImage(self, name):
        """Create a genertic 2 color image from a template image
        name = abr_color1_color2"""
        imageFileName = '%s%s.png' % (self.game.app.simImagePath, name)
        # see if image required is available
        filename = '%s.png' % name
        if filename not in self.game.imageFileList:
            try:
                anwp.func.imaging.CreateGenericImage(name, self.game.app.genImagePath, self.game.app.simImagePath)
                self.game.imageFileList.append(filename)
            except:
                print 'cannot build image:%s' % name
    
    def createShipInfoFrameFromShip(self, myShip):
        """Actually Create Ship Info Frame from ship"""
        # create panel if it does not exist
        self.shipInfoFrame = anwp.gui.shipinfo.ShipInfoFrame(self, self.game.app, myShip, 2)
        self.tempFrames.append(self.shipInfoFrame)
        self.shipInfoFrame.panel.populate()
    
    def drawEmpireValues(self, x, y):
        """Display the total ship values for each empire and compare to its original values"""
        i = 0
        for empireID, myEmpire in self.empires.iteritems():
            currentBV=0.0
            currentCR=0.0
            currentAL=0.0
            currentEC=0.0
            currentIA=0.0
            color = anwp.func.globals.colors[myEmpire.color1]
            if myEmpire.maxBV == 0.0:
                # set max value of empire fleets if first run
                myEmpire.setMyValue()
            # now get current value of empire's ships
            for shipID, myShip in self.ships.iteritems():
                if myShip.empireID == empireID and myShip.__module__ <> 'anwp.war.drone':
                    (BV,CR,AL,EC,IA) = myShip.getMyValue()
                    currentBV += BV
                    currentCR += CR
                    currentAL += AL
                    currentEC += EC
                    currentIA += IA
            
            # display results
            x = x + (i*260)
            pyui.desktop.getRenderer().drawText('%s' % myEmpire.name, (x,y), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('TOTAL ARMADA VALUE:', (x,y+20), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('-----------------------------', (x,y+40), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('BV: %d / %d' % (currentBV,myEmpire.maxBV), (x,y+60), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('CR: %d / %d' % (currentCR,myEmpire.maxCR), (x,y+80), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('AL: %d / %d' % (currentAL,myEmpire.maxAL), (x,y+100), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('EC: %d / %d' % (currentEC,myEmpire.maxEC), (x,y+120), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('IA: %d / %d' % (currentIA,myEmpire.maxIA), (x,y+140), color, self.game.app.smallFont, flipped = 1)
            pyui.desktop.getRenderer().drawText('-----------------------------', (x,y+160), color, self.game.app.smallFont, flipped = 1)
            if myEmpire.maxBV > 0 and currentBV <= myEmpire.maxBV:
                pyui.desktop.getRenderer().drawText('%.1f%% ARMADA STRENGTH' % (100.0*(currentBV/myEmpire.maxBV)), (x,y+180), color, self.game.app.smallFont, flipped = 1)
            i += 1
    
    def endturnYes(self):
        """End the turn"""
        self.yesnoBox.destroy()
        self.endMyTurn()
        
    def yesNoBoxNo(self):
        """Close Yes No Box"""
        self.yesnoBox.destroy()
    
    def exitGame(self):
        """Exit the game"""
        try:
            # Logout of game
            self.setEmpireDefaults(self.game.authKey)
            self.setLogout(self.game.authKey)
            pyui.quit()
        except:
            pyui.quit()
    
    def getEmpireUpdate(self, listAttr):
        """Ask the Server for updated Empire info"""
        try:
            serverResult = self.game.server.getEmpireUpdate(listAttr, self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                for key, value in serverResult.iteritems():
                    self.game.myEmpire[key] = value
        except:
            self.modeMsgBox('getEmpireUpdate->Connection to Server Lost')
    
    def getMailUpdate(self):
        """Ask the Server for any updated mail"""
        try:
            myMailDict = self.game.myEmpire['mailBox']
            serverResult = self.game.server.getMailUpdate(self.game.authKey, myMailDict.keys())
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                for key, value in serverResult.iteritems():
                    myMailDict[key] = value
        except:
            self.modeMsgBox('getMailUpdate->Connection to Server Lost')
    
    def getGalaxyUpdate(self, listAttr):
        """Ask the Server for updated Galaxy info"""
        try:
            serverResult = self.game.server.getGalaxyUpdate(listAttr, self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                for key, value in serverResult.iteritems():
                    self.game.myGalaxy[key] = value
        except:
            self.modeMsgBox('getGalaxyUpdate->Connection to Server Lost')
    
    def getSystemUpdate(self, listAttr, systemID):
        """Ask the Server for updated System info"""
        try:
            serverResult = self.game.server.getSystemUpdate(listAttr, systemID, self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                mySystemDict = self.game.allSystems[systemID]
                for key, value in serverResult.iteritems():
                    mySystemDict[key] = value
        except:
            self.modeMsgBox('getSystemUpdate->Connection to Server Lost')   
    
    def draw(self):
        """Draw standard World information each frame"""
        self.bufferX = (self.appWidth/2) - self.viewX
        self.bufferY = (self.appHeight/2) - self.viewY
        anwp.sl.engine.clear()
        self.drawBorders()
        anwp.sl.engine.render()
    
    def drawBox(self, x, y, width, height, color):
        """Draw a box"""
        #LEFT
        anwp.sl.engine.drawLine(x,y,x,y+height,color)
        #TOP
        anwp.sl.engine.drawLine(x,y+height,x+width,y+height,color)
        #RIGHT
        anwp.sl.engine.drawLine(x+width,y+height,x+width,y,color)
        #BOTTOM
        anwp.sl.engine.drawLine(x+width,y,x,y,color)
    
    def drawBorders(self):
        """Check to see how borders should be drawn around World"""
        self.drawBox(self.bufferX, self.bufferY, self.worldWidth, self.worldHeight, pyui.colors.yellow)
        
    def endMyTurn(self):
        """End the players Turn"""
        try:
            result = self.game.server.endEmpireTurn(self.game.authKey)
            if result == 0:
                (serverResult, self.game.myEmpire['help']) = self.game.server.askForHelp(self.game.authKey)
                if 'EndTurn' in self.game.myEmpire['help']:
                    self.modeMsgBox('You have now un-ended your turn, please remember to end your turn')
                else:
                    self.modeMsgBox('Your turn has been ended, please wait for others to end their turn')
            elif result == 1:
                # turn has ended, let player enter game again
                self.reloginToGame()
            elif result == 2:
                # server is multithreading end of turn message user
                self.modeMsgBox('You were the last to end your turn, Server is now ending turn, please wait for email and press STATUS once recieved')
            elif type(result) == types.StringType:
                self.modeMsgBox(result)
        except:
            self.modeMsgBox('endMyTurn->Connection to Server Lost')
        
    def enterMode(self):
        """Enter the mode."""
        # set the Mouse
        pyui.desktop.getDesktop().registerHandler(pyui.locals.LMOUSEBUTTONDOWN, self.onMouseDown)
    
    def exitMode(self):
        """Exit the mode"""
        # release the Mouse
        pyui.desktop.getDesktop().unregisterHandler(pyui.locals.LMOUSEBUTTONDOWN)
        
        # remove the gui panels
        for item in self.panels:
            if item:
                item.destroy()
        
        # remove the world objects
        self.removeWorld()
    
    def onMouseDown(self, event):
        """Allow dynamic picking of an object within world"""
        pass
    
    def updateSelector(self):
        """Update the x, y position of the selector to point to the selector"""
        # check that simSelector exists
        if not self.simSelector:
            self.createSelector()
        
        # update position of simSelector
        self.simSelector.posX = self.selected.posX
        self.simSelector.posY = self.selected.posY
    
    def updateObserver(self, sim, panelName):
        """Update Observer to panelName given"""
        myPanel = getattr(self, panelName)
        sim.addObserver(myPanel)
        self.selected = sim
        self.selected.notify()
        self.updateSelector()

    def onKey(self):
        """process keys within world"""
        key = pygame.key.get_pressed()
        vx = 0
        vy = 0
        if key[pygame.K_LEFT]:
            vx -= self.scrollSpeed
        if key[pygame.K_RIGHT]:
            vx += self.scrollSpeed
        if key[pygame.K_UP]:
            vy += self.scrollSpeed
        if key[pygame.K_DOWN]:
            vy -= self.scrollSpeed
        
        # constrain camera view to stay within world borders
        if ((self.viewX + vx) <= (self.worldWidth) ) and ((self.viewX + vx) >= self.bufferX):
            self.viewX += vx
        if ((self.viewY + vy) <= (self.worldHeight) ) and ((self.viewY + vy) >= self.bufferY):
            self.viewY += vy
        anwp.sl.engine.setView(self.viewX, self.viewY)
    
    def update(self, interval):
        """update the mode, return the status, 0 means stop game"""
        # continue music
        self.game.app.continueMusic('song1')
        if self.world:
            result = self.world.update(interval)
            return result
        else:
            return 0

    def setEmpireDefaults(self, clientKey):
        """Read the defaults currently set and change them in the database"""
        try:
            # setup attributes to send to server
            defaults = ['viewIndustry', 'viewMilitary', 'viewResources', 'viewTradeRoutes']
            d = {}
            for item in defaults:
                d[item] = self.game.myEmpire[item]
            serverResult = self.game.server.setEmpire(clientKey, d)
            if serverResult == 1:
                print 'Setup Empire Defaults Success'
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('SetEmpireDefaults->Connection to Server Lost, Login Again')

    def setLogout(self, clientKey):
        """Send a Logout Request to the Server"""
        try:
            serverResult = self.game.server.logout(clientKey)
            if serverResult == 1:
                print 'Logout Successful, Exit Program'
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('setLogout->Connection to Server Lost, Login Again')

    def setWorld(self, newWorld):
        """set the world within mode"""
        self.world = newWorld
    
    def submitDesign(self, name):
        """Take Ship Design and submit it to Server for verification and storage"""
        (oldName, hullID, compDict, weaponDict) = self.myShipDesign.getMyDesign()
        dOrder = {'name':name, 'hullID':hullID, 'compDict':compDict, 'weaponDict':weaponDict}
        try:
            serverResult = self.game.server.addShipDesign(self.game.authKey, dOrder)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                # design has been accepted by server, retrieve design ID and add to client
                (ID,name) = serverResult
                self.game.shipDesigns[ID] = (name, hullID, compDict, weaponDict)
                self.getEmpireUpdate(['designsLeft'])
        except:
            self.modeMsgBox('submitDesign->Connection to Server Lost, Login Again')
    
    def reloginToGame(self, invalid=0):
        """Allow player to relogin to game"""
        loginMode = anwp.modes.modelogin.ModeLogin(self.game)
        loginMode.serverLoginFrame.destroy()
        loginMode.loginToGame(self.game.myEmpireID, self.game.empirePass)
        if invalid == 0:
            self.modeMsgBox('You are now in a new round of play, please finish your turn')
        else:
            self.modeMsgBox('The Server has been reset since you last communicated, your session has been reset')
    
    def removeWorld(self):
        """remove the world objects within mode"""
        if self.world:
            self.world.removeAll()
    
    def destroyTempFrames(self):
        """Destroy any Temp Frames"""
        for frame in self.tempFrames:
            frame.destroy()
        self.tempFrames = []
    
    def modeMsgBox(self, messageText):
        """Create a message for the user"""
        if messageText[:12] == 'invalid key:':
            # this means the server is not accepting the client key, reset client
            self.reloginToGame(1)
        else:
            self.msgBox = anwp.gui.msgbox.MessageBox(self, self.game.app, self.name, messageText)
            self.tempFrames.append(self.msgBox)
    
    def modeYesNoBox(self, messageText, onYesMethod, onNoMethod):
        """Create a Yes/No Box for the user, pass in the string of yes and no methods (methods must be in this mode)"""
        self.yesnoBox = anwp.gui.yesnobox.YesNoBox(self, self.game.app, self.name, messageText, onYesMethod, onNoMethod)
        self.tempFrames.append(self.yesnoBox)

class TestMode(Mode):
    """Test Mode"""
    def __init__(self, game):
        self.name = 'TESTMODE'
        self.game = game