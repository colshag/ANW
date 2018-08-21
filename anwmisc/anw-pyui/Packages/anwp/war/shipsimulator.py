# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# shipsimulator.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Ship Battle Simulator in ANW
# ---------------------------------------------------------------------------
import string
import pygame
import types
import random

import pyui
import anwp.gui.simmenu
import anwp.gui.shipinfo
import anwp.func.storedata
import anwp.func.globals
import anwp.func.funcs
import anwp.func.root
import anwp.sl.engine
import anwp.sl.world
import anwp.sl.entity
import anwp.sl.sim
import anwp.modes.mode
import anwp.modes.modelogin
import anwp.war.captain
import anwp.war.component
import anwp.war.empire
import anwp.war.quad
import anwp.war.ship
import anwp.war.shipdesign
import anwp.war.dronedesign
import anwp.war.weapon
import anwp.war.weaparc

class shipEventManager(object):
    def __init__(self):
        self.gEvents = []     # list of events sorted by time
        self.gEventTic = 0  # current event tic
    
    def postEvent(self, gid, action, delayInTics, args):
        """Post an event to be processed. insert in sorted order"""
        from event import GameInterEvent
        from bisect import insort_right
        
        event = GameInterEvent(gid, action, self.gEventTic+delayInTics, args)
        insort_right(self.gEvents, event)
        #print gid, action
        return event

    def processEvents(self, currentTic):
        """process all of the pending events up to the current time.
        """
        self.gEventTic = currentTic
        
        while len(self.gEvents) > 0:
            # grab the next event
            event = self.gEvents.pop(0)
            if event.callTic <= self.gEventTic:
                # time to call it
                event()
            else:
                # not time to call it, put it back in the list.
                self.gEvents.insert(0, event)
                break
        
    def clearEventsFor(self, gid, action=''):
        """clear all pending events for a game object ID.
        """
        if action == '':
            self.gEvents = filter(lambda event: event.gid != gid, self.gEvents)
        else:
            # clear all events for a certain gid of a certain action
            self.gEvents = filter(lambda event: not(event.gid == gid and event.action == action), self.gEvents)
    
    def clearAllEvents(self):
        """Clear all events"""
        self.gEvents = []
        self.gEventTic = 0

class Explosion(anwp.sl.sim.Animated):
    """Represents an Explosion in the simulation"""
    def __init__(self, category):
        anwp.sl.sim.Animated.__init__(self, category, .125)

class ShipSimulator(anwp.modes.mode.Mode, anwp.func.root.Root):
    """This is the Ship Simulator"""
    def __init__(self, game, shipBattle, toLogin=False, myGalaxy=None):
        # init the mode
        anwp.modes.mode.Mode.__init__(self, game)
        self.myGalaxy = myGalaxy
        if self.myGalaxy == None:
            self.simMode = 'client'
            self.pause = 1
        else:
            self.simMode = 'server'
            self.pause = 0
        self.toLogin = toLogin
        self.name = 'SHIPSIMULATOR'
        self.scrollSpeed = 10 # keyboard scrollspeed
        self.end = 0 # 1=simulation ended
        self.count = 0 # number of iterations through simulation
        self.maxCount = 40000 # max iterations allowed before simulation end
        self.lines = [] # list of direct fire lines [weapon , target, life] TODO: Replace with sims
        self.damages = {} # key=ship gid(int), value = [ship, damage, color, life]
        self.resultList = [] # log of battle
        self.shipEventManager = shipEventManager()
        self.weaparcs = []
        
        # create gui panels
        if self.simMode == 'client':
            self.simMenu = anwp.gui.simmenu.SimMenu(self, self.game.app)
        
        # setup log
        self.resultList.append('SHIP BATTLE SUMMARY: Round:%d, On: %s Seed:(%.9f)' % (shipBattle.round, shipBattle.systemName, shipBattle.seed))
        self.resultList.append('===========================================================')
        self.shipInfo = None
        
        # load simulator Data from shipBattle
        self.componentdata = shipBattle.componentdata
        self.shiphulldata = shipBattle.shiphulldata
        self.dronehulldata = shipBattle.dronehulldata
        self.weapondata = shipBattle.weapondata
        
        # load empires
        self.shipBattle = shipBattle
        self.rand = random.Random(shipBattle.seed)
        self.empires = {} # Dict key = empire id, value = empire object
        self.createEmpires()
        
        # load Captains
        self.captains = {} # all captains created key=id, value=obj
        self.createCaptains()
        
        # load ships
        self.ships = {} # Dict key = ship id, value = ship object
        self.createShips()
        
        # create images if needed
        if self.simMode == 'client':
            self.createShipImages()
            self.createMissileImages()
            self.createDroneImages()
            self.createDirectImages()
            self.createJunkImages()
        
        # create the world
        self.worldWidth = 10000
        self.worldHeight = 10000
        if self.simMode == 'client':
            self.renderer = pyui.desktop.getRenderer()
            self.renderer.setBackMethod(self.draw)
            self.game.app.desiredFPS = 60.0
        else:
            self.game.app.desiredFPS = 10000
            
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight))
        
        # use a 50:1 ratio
        self.ratio = 50
        self.miniWidth = self.worldWidth/self.ratio
        self.miniHeight = self.worldHeight/self.ratio
        self.viewerWidth = self.appWidth/self.ratio
        self.viewerHeight = self.appHeight/self.ratio
        
        # create ship sims
        self.createShipSims()
        
        # begin simulation
        self.begin()
        
        # default select
        myShip = self.ships[self.ships.keys()[0]]
        if self.simMode == 'client':
            self.onSelectShipSim(myShip)
        
        # set debug
        self.world.setDebug(0)
    
    def begin(self):
        """Start Simulation"""
        shipList = anwp.func.funcs.sortStringList(self.ships.keys())
        for shipID in shipList:
            myShip = self.ships[shipID]
            myShip.begin()
    
    def createDroneImages(self):
        """Create all Drone Images required for display"""
        if self.simMode == 'server':
            return
        
        # create drone images
        for empireID, myEmpire in self.empires.iteritems():
            for designID, myDesign in myEmpire.droneDesigns.iteritems():
                name = myDesign.getImageFileName()
                self.createGenericImage(name)
    
    def createDirectImages(self):
        """Create all Direct Images required for display"""
        if self.simMode == 'server':
            return
        
        # create direct images
        for empireID, myEmpire in self.empires.iteritems():
            for num in [1]:
                name = 'zdirect%d_%s_%s' % (num, myEmpire.color1, myEmpire.color2)
                self.createGenericImage(name)
    
    def createJunkImages(self):
        """Create all Junk Images required for display"""
        if self.simMode == 'server':
            return
        
        # create ship images
        for empireID, myEmpire in self.empires.iteritems():
            for num in range(1,4):
                name = 'junk%d_%s_%s' % (num, myEmpire.color1, myEmpire.color2)
                self.createGenericImage(name)
    
    def createShipImages(self):
        """Create all Ship Images required for display"""
        if self.simMode == 'server':
            return
        
        # create ship images
        for empireID, myEmpire in self.empires.iteritems():
            for designID, myDesign in myEmpire.shipDesigns.iteritems():
                name = myDesign.getImageFileName()
                self.createGenericImage(name)
    
    def createMissileImages(self):
        """Create all Missile Images required for display"""
        if self.simMode == 'server':
            return
        
        # create missile images
        for empireID, myEmpire in self.empires.iteritems():
            for num in [1,2]:
                name = 'missile%d_%s_%s' % (num, myEmpire.color1, myEmpire.color2)
                self.createGenericImage(name)
    
    def createEmpires(self):
        """Take shipBattle empires dict and add Empires to Simulator"""
        for empireID, myEmpireDict in self.shipBattle.empiresDict.iteritems():
            myEmpire = anwp.war.empire.Empire(myEmpireDict)
            myEmpire.setMyGalaxy(self)
            for shipDesignID, myShipDesignDict in myEmpireDict['shipDesigns'].iteritems():
                myShipDesign = anwp.war.shipdesign.ShipDesign(myShipDesignDict)
                myShipDesign = self.createShipDesign(myShipDesignDict, myEmpire)
            for droneDesignID, myDroneDesignDict in myEmpireDict['droneDesigns'].iteritems():
                myDroneDesign = anwp.war.dronedesign.DroneDesign(myDroneDesignDict)
                myDroneDesign = self.createDroneDesign(myDroneDesignDict, myEmpire)
    
    def createShipDesign(self, myShipDesignDict, myEmpire):
        """Create Ship Design, place in myEmpire object"""
        myShipDesign = anwp.war.shipdesign.ShipDesign(myShipDesignDict)
        myShipDesign.setMyEmpire(myEmpire)
        
        for quadID, myQuadDict in myShipDesignDict['quads'].iteritems():
            myQuad = anwp.war.quad.Quad(myQuadDict)
            myQuad.setMyParent(myShipDesign)
            # weapons have to be created first
            for weaponID, myWeaponDict in myQuadDict['weapons'].iteritems():
                myWeapon = anwp.war.weapon.Weapon(myWeaponDict)
                myWeapon.setMyQuad(myQuad)
            for componentID, myComponentDict in myQuadDict['components'].iteritems():
                myComponent = anwp.war.component.Component(myComponentDict)
                myComponent.setMyQuad(myQuad)
                
        myShipDesign.setMyStatus()
        return myShipDesign
          
    def createDroneDesign(self, myDroneDesignDict, myEmpire):
        """Create Drone Design, place in myEmpire object"""
        myDroneDesign = anwp.war.dronedesign.DroneDesign(myDroneDesignDict)
        myDroneDesign.setMyEmpire(myEmpire)
        
        for quadID, myQuadDict in myDroneDesignDict['quads'].iteritems():
            myQuad = anwp.war.quad.Quad(myQuadDict)
            myQuad.setMyParent(myDroneDesign)
            # weapons have to be created first
            for weaponID, myWeaponDict in myQuadDict['weapons'].iteritems():
                myWeapon = anwp.war.weapon.Weapon(myWeaponDict)
                myWeapon.setMyQuad(myQuad)
            for componentID, myComponentDict in myQuadDict['components'].iteritems():
                myComponent = anwp.war.component.Component(myComponentDict)
                myComponent.setMyQuad(myQuad)
                
        myDroneDesign.setMyStatus()
        return myDroneDesign
          
    def createCaptains(self):
        """Create captains"""
        for captainID, myCaptainDict in self.shipBattle.captainsDict.iteritems():
            myCaptain = anwp.war.captain.Captain(myCaptainDict)
            myEmpire = self.empires[myCaptainDict['empireID']]
            myCaptain.setMyEmpire(myEmpire)
            
    def createShips(self):
        """Take shipBattle ships dict and add Ships to Simulator"""
        for shipID, myShipDict in self.shipBattle.shipsDict.iteritems():
            myShip = anwp.war.ship.Ship(myShipDict)
            myShip.targets = myShipDict['targets']
            myShip.setMyGalaxy(self)
            myEmpire = self.empires[myShip.empireID]
            myCaptain = self.captains[myShip.captainID]
            myShip.setMyCaptain(myCaptain)
            myShipDesign = myEmpire.shipDesigns[myShip.designID]
            myShip.setFromDict(myShipDesign, myShipDict)
            self.ships[shipID] = myShip
    
    def createShipSims(self):
        """Create the Ship Sims"""
        import anwp.sims
        # create ships
        shipIDList = anwp.func.funcs.sortStringList(self.ships.keys())
        for shipID in shipIDList:
            myShip = self.ships[shipID]
            imageFileName = '%s%s.png' % (self.game.app.simImagePath, myShip.myDesign.getImageFileName())
            # create sim
            myShip.setMyEntity(anwp.sims.categories.ShipCategory(imageFileName, string.lower(myShip.myShipHull.abr)), myShip.posX, myShip.posY, myShip.facing)
                            
            # add sim to world
            speed = 0
            force = 1
            self.world.addToWorld(myShip, myShip.posX, myShip.posY, myShip.facing, speed, force)
            
            # create captain sim
            myCaptain = myShip.myCaptain
            imageFileName = '%szcaptain%d.png' % (self.game.app.genImagePath, myCaptain.rankID)
            myCaptain.setMyEntity(anwp.sims.categories.CaptainCategory(imageFileName),0,0,0)
            self.world.addToWorld(myCaptain, myCaptain.posX ,myCaptain.posY, 1)
    
    def createWeapArcs(self):
        """Create the Ship Weapon Arc Sims"""
        import anwp.sims
        # create arcs
        myShip = self.selected
        for myWeapon in myShip.activeWeapons:
            speed = 0
            force = 1
            imageFileName = '%szarc2.png' % self.game.app.genImagePath
            category = anwp.sims.categories.WeaponArcCategory(imageFileName, 2)
            
            sim = anwp.war.weaparc.WeaponArc(category, myWeapon)
            (wX, wY) = sim.myWeapon.getMyXY()
            sim.facing = sim.myWeapon.getMyFacing()
            (tX, tY) = anwp.func.funcs.getXYfromAngle(wX, wY, sim.distance, sim.facing)
            centerX = (wX+tX)/2
            centerY = (wY+tY)/2
            self.world.addToWorld(sim, centerX, centerY, sim.facing, speed, force)
            self.weaparcs.append(sim)
        
        for myWeapon in myShip.amsWeapons:
            speed = 0
            force = 1
            imageFileName = '%szarc1.png' % self.game.app.genImagePath
            category = anwp.sims.categories.WeaponArcCategory(imageFileName, 1)
            sim = anwp.war.weaparc.WeaponArc(category, myWeapon)
            (wX, wY) = sim.myWeapon.getMyXY()
            sim.facing = sim.myWeapon.getMyFacing()
            (tX, tY) = anwp.func.funcs.getXYfromAngle(wX, wY, sim.distance, sim.facing)
            centerX = (wX+tX)/2
            centerY = (wY+tY)/2
            self.world.addToWorld(sim, centerX, centerY, sim.facing, speed, force)
            self.weaparcs.append(sim)
            
    
    def draw(self):
        """Draw Ship Sim World information each frame"""
        self.bufferX = (self.appWidth/2) - self.viewX
        self.bufferY = (self.appHeight/2) - self.viewY
        anwp.sl.engine.clear()
        anwp.sl.engine.drawImage(0, 0, self.appWidth, self.appHeight, self.backgroundImage)

        self.drawBorders()
        self.drawMiniMap()
        self.drawLines()
        self.drawDamages()
        self.drawSelector()
        self.drawOrders()
            
        if self.end == 1:
            self.pause = 1
            anwp.sl.engine.drawImage((self.appWidth/2)-256, (self.appHeight/2)-10, 512, 23, '%sendsimulation.png' % self.game.app.genImagePath)
        if self.pause == 1:
            anwp.sl.engine.drawImage((self.appWidth/2)-256, 10, 512, 23, '%spausesimulation.png' % self.game.app.genImagePath)
            self.drawEmpireValues(260, 40)
            ##if self.shipInfo <> None:
                ##self.drawFleetStats(self.shipInfo.ship.myFleet)
        
        # move view to follow selected ship if selected
        ##if self.simSelector <> None and self.selected <> 0:
            ##self.viewX = self.selected.posX
            ##self.viewY = self.selected.posY
        anwp.sl.engine.render()

    def removeWeapArcs(self):
        """remove weapon arc sims"""
        for sim in self.weaparcs:
            self.world.removeFromWorld(sim)
        self.weaparcs = []

    def drawOrders(self):
        """Show Ships orders"""
        for shipID, myShip in self.ships.iteritems():
            ##if myShip.__module__ == 'anwp.war.ship':
            color = anwp.func.globals.colors[self.empires[myShip.empireID].color1]
            if myShip.alive == 1:
                (x,y) = anwp.sl.engine.worldToScreen(myShip.posX, myShip.posY)
                pyui.desktop.getRenderer().drawText(myShip.mode, (x+myShip.graphicsObject.sourceObject.width/2.5, y), color, self.game.app.smallFont, flipped = 1)

    def drawDamages(self):
        """Draw Damage to Ships"""
        for key in self.damages.keys():
            damageList = self.damages[key]
            if damageList[3] > 0:
                if self.pause == 0:
                    damageList[3] -= 1
                (id, position) = string.split(key, '-')
                ship = damageList[0]
                damage = damageList[1]
                color = anwp.func.globals.colors[damageList[2]]
                direction = (ship.facing + anwp.func.globals.quadAngles[position])
                (x,y) = ship.findOffset(direction, ship.graphicsObject.sourceObject.width/1.5)
                (x,y) = anwp.sl.engine.worldToScreen(x,y)
                pyui.desktop.getRenderer().drawText('%s%s' % (position,damage), (x, y), color, self.game.app.smallFont, flipped = 1)
            else:
                del self.damages[key]	    

    ##def drawFleetStats(self, myFleet):
        ##"""Display the fleet stats of fleet given"""
        ##x = 0
        ##y = 40
        ##color = anwp.func.globals.colors[self.empires[myFleet.empireID].color1]
        ##pyui.desktop.getRenderer().drawText('%s SUMMARY:' % myFleet.name, (x,y), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('COMMAND:%s' % myFleet.myCommander.myCaptain.name, (x,y+20), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('-----------------------------', (x,y+40), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('AMS acc:          %.2f%%' % myFleet.stats.getAccuracyAMS(), (x,y+60), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('shotsAMS:         %04d' % myFleet.stats.getShotsAMS(), (x,y+80), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('hitsAMS:          %04d' % myFleet.stats.getHitsAMS(), (x,y+100), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('damageAMS:        %04d' % myFleet.stats.getDamageAMS(), (x,y+120), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('Direct acc:       %.2f%%' % myFleet.stats.getAccuracyDirect(), (x,y+160), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('shotsDirect:      %04d' % myFleet.stats.getShotsDirect(), (x,y+180), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('hitsDirect:       %04d' % myFleet.stats.getHitsDirect(), (x,y+200), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('damageDirect:     %04d' % myFleet.stats.getDamageDirect(), (x,y+220), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('Missile acc:      %.2f%%' % myFleet.stats.getAccuracyMissile(), (x,y+260), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('shotsMissile:     %04d' % myFleet.stats.getShotsMissile(), (x,y+280), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('hitsMissile:      %04d' % myFleet.stats.getHitsMissile(), (x,y+300), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('damageMissile:    %04d' % myFleet.stats.getDamageMissile(), (x,y+320), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('DroneAMS acc:     %.2f%%' % myFleet.stats.getAccuracyDroneAMS(), (x,y+360), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('shotsDroneAMS:    %04d' % myFleet.stats.shotsDroneAMS, (x,y+380), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('hitsDroneAMS:     %04d' % myFleet.stats.hitsDroneAMS, (x,y+400), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('damageDroneAMS:   %04d' % myFleet.stats.damageDroneAMS, (x,y+420), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('DroneDirect acc:  %.2f%%' % myFleet.stats.getAccuracyDroneDirect(), (x,y+460), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('shotsDroneDirect: %04d' % myFleet.stats.shotsDroneDirect, (x,y+480), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('hitsDroneDirect:  %04d' % myFleet.stats.hitsDroneDirect, (x,y+500), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('damageDroneDirect:%04d' % myFleet.stats.damageDroneDirect, (x,y+520), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('-----------------------------', (x,y+540), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('COUNT: (%d/%d)' % (self.count, self.maxCount), (x,y+560), color, self.game.app.smallFont, flipped = 1)
        ##pyui.desktop.getRenderer().drawText('SEED: (%.9f)' % self.shipBattle.seed, (x,y+580), color, self.game.app.smallFont, flipped = 1)
        
    def drawMiniMap(self):
        """Draw a mini map displaying the simulator borders and the sims within the game"""
        viewerBufferX = (self.viewX-self.appWidth/2)/self.ratio
        viewerBufferY = (self.viewY-self.appHeight/2)/self.ratio
        # draw main box
        self.drawBox(0,0,self.miniWidth,self.miniHeight,pyui.colors.red)
        # draw grid
        for gridNum, (x,y) in anwp.func.globals.battlemapQuadrants.iteritems():
            # draw box
            self.drawBox(x/self.ratio, y/self.ratio, 2000/self.ratio, 2000/self.ratio, pyui.colors.red)
        # draw viewing box
        self.drawBox(viewerBufferX,viewerBufferY,self.viewerWidth, self.viewerHeight, pyui.colors.white)
        # draw sims
        for sim in self.world.mobiles:
            if sim.alive == 1 and sim.__module__ in('anwp.war.ship', 'anwp.war.drone'):
                color = anwp.func.globals.colors[self.empires[sim.empireID].color1]
                anwp.sl.engine.drawRect(sim.posX/self.ratio, sim.posY/self.ratio, 2, 2, color)

    def drawLines(self):
        """Draw Direct Fire Lines"""
        for line in self.lines:
            if line[2] > 0:
                if self.pause == 0:
                    line[2] -= 1
                weapon = line[0]
                target = line[1]
                color = anwp.func.globals.colors[self.empires[weapon.myShip.empireID].color1]
                (x,y) = weapon.getMyXY()
                anwp.sl.engine.drawLine(x+self.bufferX, y+self.bufferY, target.posX+self.bufferX, target.posY+self.bufferY, color)
            else:
                del line        

    def drawSelector(self):
        """Draw the Selector"""
        if self.simSelector <> None:
            self.updateSelector()
                
    def endSimulation(self):
        """End the simulation"""
        if self.end == 0:
            self.end = 1
            # clear any remaining events
            self.shipEventManager.clearAllEvents()
            
            if self.simMode == 'client':
                self.simMenu.panel.btnPause.disable()
                # client mode print out ship results
                file_object = open('shipBattles.log', 'w')
                for line in self.resultList:
                    file_object.write(line+'\n')
                file_object.close()
            
            # if this is the server, update all objects in myGalaxy
            if self.simMode == 'server' and self.myGalaxy <> None:
                self.updateMyGalaxy()
                self.removeWorld()
                self.world = None
    
    def enterMode(self):
        anwp.modes.mode.Mode.enterMode(self)
        # set the game interval to a set level
        self.game.app.setIntervalValue(anwp.func.globals.intervalValue)
        self.game.app.playMusic('song1')
    
    def exitMode(self):
        """Exit the mode"""
        anwp.modes.mode.Mode.exitMode(self)
        # reset interval value
        self.game.app.setIntervalValue(0)
        self.game.app.desiredFPS = 60.0
        self.game.app.stopSound('song2')
        self.game.app.playMusic('song1')
    
    def getNextD100(self):
        """Get next D100 Roll from Simulator"""
        # use count to wrap through roll list
        value = self.rand.randint(1,100)
        ##self.resultList.append('COUNT:%d, ROLL:%d' % (self.count, value))
        return value
    
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
        
        ### constrain camera view to stay within world borders
        ##if ((self.viewX + vx) <= (self.worldWidth) ) and ((self.viewX + vx) >= self.bufferX):
        self.viewX += vx
        ##if ((self.viewY + vy) <= (self.worldHeight) ) and ((self.viewY + vy) >= self.bufferY):
        self.viewY += vy
        anwp.sl.engine.setView(self.viewX, self.viewY)
    
    def onMouseDown(self, event):
        """Allow dynamic picking of an object within world"""
        # determine where mouse is
        (worldX, worldY) = anwp.sl.engine.screenToWorld(event.pos[0], event.pos[1])
        sim = self.world.checkPoint(worldX, worldY)
        
        # if selecting nothing, remove panel and selector
        if sim == None:
            self.onSelectNoSim()
            # check if mouse clicking on mini-map
            x = event.pos[0]
            y = self.appHeight - event.pos[1]
            if x <= 200 and y <= 200:
                self.viewX = x*self.ratio
                self.viewY = y*self.ratio
        elif sim.__module__ == 'anwp.war.ship':
            self.onSelectShipSim(sim)       
    
    def onSelectNoSim(self):
        """No Sim Selected clear panels and selector"""
        if self.shipInfo <> None:
            self.shipInfo.destroy()
            self.shipInfo = None
        self.removeSelector()
        self.removeWeapArcs()
    
    def onSelectShipSim(self, sim):
        """Ship Sim selected"""
        # create panel and selector if they do not exist
        if self.shipInfo == None:
            self.shipInfo = anwp.gui.shipinfo.ShipInfoFrame(self, self.game.app, sim)
        self.createSelector2()
        
        # update observer
        if self.shipInfo <> None and sim <> None:
            self.updateObserver(sim, 'shipInfo')
        
        # move camera to ship
        self.centerCamera(sim.posX, sim.posY)
        
        # update arcs
        if self.simSelector <> None and self.selected <> 0:
            self.removeWeapArcs()
            self.createWeapArcs()
    
    def pauseResume(self):
        """Pause/Resume the Simulation"""
        if self.pause == 0:
            self.pause = 1
        else:
            self.pause = 0
            self.game.app.stopSound('song1')
            self.game.app.playMusic('song2')
    
    def update(self, interval):
        """update the mode, return the status, 0 means stop game, allow pause"""
        # continue music
        self.game.app.continueMusic('song2')
        if self.count >= self.maxCount:
            self.endSimulation()
        if self.world:
            if self.pause == 1:
                # only update selector
                result = self.world.update(interval, 'selector')
                if self.selected:
                    self.selected.notify()
                return result
            else:
                # update all sims
                self.count += 1
                self.shipEventManager.processEvents(self.count)
                result = self.world.update(interval)
                if self.selected:
                    self.selected.notify()
                return result
        else:
            return 0
    
    def updateMyGalaxy(self):
        """Update all game objects at the galaxy level"""
        for shipID, myShip in self.ships.iteritems():
            if myShip.alive == 0:
                self.myGalaxy.removeShip(shipID)
            else:
                alive = 1
                # update surviving captain stats
                myCaptain = myShip.myCaptain
                actualCaptain = self.myGalaxy.captains[myCaptain.id]
                actualCaptain.setExperience(myCaptain.experience)
                
                # update surviving ship stats
                actualShip = self.myGalaxy.ships[shipID]
                for position, myQuad in myShip.quads.iteritems():
                    oldQuad = actualShip.quads[position]
                    myQuad.setMyParent(actualShip)
                actualShip.setMyStatus()
                actualShip.setRepairCost()
                
                # check regiments
                if actualShip.currentTransport > actualShip.maxTransport:
                    results = actualShip.sacrificeRegiments()
                    self.resultList = self.resultList + results
        
        # mail results to empires involved
        s = 'SHIP BATTLE RESULTS ON:%s, Round:%dm' % (self.shipBattle.systemName, self.shipBattle.round)
        for empireID, myEmpireDict in self.shipBattle.empiresDict.iteritems():
            dMail = {'fromEmpire':empireID, 'round':self.myGalaxy.currentRound+1,
                     'messageType':'fleet', 'subject':s, 'body':str(self.resultList)}
            myEmpire = self.myGalaxy.empires[empireID]
            myEmpire.genMail(dMail)
            
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_shipsimulator.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
