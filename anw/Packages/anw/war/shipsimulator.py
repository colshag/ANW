# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# shipsimulator.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Ship Battle Simulator in ANW
# ---------------------------------------------------------------------------
import string
import types
import copy
from random import randint, choice, random, Random
from math import pi

from anw.func import storedata, globals, funcs, root
from anw.modes import mode
from anw.war import captain, component, empire, quad, weaparc
from anw.war import shipdesign, dronedesign, weapon, kworld, ship

if globals.serverMode == 0:
    from anw.gui import shipsim, textonscreen, line, shipinfo, minimap, mapmove, system
    from pandac.PandaModules import Vec4, Vec3
       
class ShipSimulator(mode.Mode, root.Root):
    """This is the Ship Simulator"""
    def __init__(self, game, shipBattle, toLogin=False, myGalaxy=None):
        mode.Mode.__init__(self, game)
        self.debug = 0
        self.zoomSpeed = 2.0
        self.zoomCameraDepth = -20.0
        self.zoomCameraOutDepth = -50.0
        self.enableMouseCamControl = 1
        self.myGalaxy = myGalaxy
        self.pause = 0
        self.textPause = None
        self.stat0 = None
        self.stat1 = None
        self.stat2 = None
        self.stat3 = None
        self.stat4 = None
        self.stat5 = None
        self.stat6 = None
        self.stat7 = None
        self.stat8 = None
        
        if self.myGalaxy == None and globals.serverMode == 0:
            base.enableParticles()
            self.createSelector('select2',5)
            self.createMainMenu('W')
            self.mainmenu.setPause()
            
        self.toLogin = toLogin # if True display login buttons
        self.name = 'SHIPSIMULATOR'
        self.scrollSpeed = 10 # keyboard scrollspeed
        self.end = 0 # 1=simulation ended
        self.count = 0 # number of iterations through simulation
        self.maxCount = 40000 # max iterations allowed before simulation end
        self.lines = [] # list of direct fire lines [weapon , target, life] TODO: Replace with sims
        self.damages = {} # key=ship gid(int), value = [ship, damage, color, life]
        self.resultList = [] # log of battle
        self.weaparcs = []
        self.myTech = None
        self.empireEndSim = {}
        self.myRadar = 0
        self.jamming = {}
        
        # create the world
        self.worldWidth = 200
        self.worldHeight = 200
        
        if globals.serverMode == 0:
            self.createBorders()
            self.createQuadrants()
        self.kworld = kworld.KWorld(self.worldWidth, self.worldHeight)
        
        # setup log
        self.resultList.append('SHIP BATTLE %s SUMMARY: Round:%d, On: %s Seed:(%.9f)' % (shipBattle.id, shipBattle.round, shipBattle.systemName, shipBattle.seed))
        self.resultList.append('===========================================================')
        self.shipInfo = None
        
        # load simulator Data from shipBattle
        self.componentdata = game.componentdata
        self.shiphulldata = game.shiphulldata
        self.dronehulldata = game.dronehulldata
        self.weapondata = game.weapondata
        
        self.selectTypes = ['ships']
        self.shipSelected = None
        self.assaultTick = 0
        self.assaultDelay = 10 # number of ticks between each assault action
        
        # load empires
        self.shipBattle = shipBattle
        self.rand = Random(shipBattle.seed)
        self.empires = {} # Dict key = empire id, value = empire object
        self.createEmpires()
        
        # load Captains
        self.captains = {} # all captains created key=id, value=obj
        self.createCaptains()
        
        # load ships
        self.ships = {} # Dict key = ship id, value = ship object
        self.createShips()
        self.setShipCollideMasks()
        if self.ships == {}:
            self.maxCount = 10
            
        if globals.serverMode == 0:
            self.setupCamera()
            self.setupMinimap()
            self.setupMapMove()
            self.setBackgroundSystem()
            self.explosions = []
            self.setupRadar()
            
        self.begin()
        
        if globals.serverMode == 0:
            self.pauseResume()

    def setupRadar(self):
        """Setup the Radar of the battle"""
        for shipID, ship in self.ships.iteritems():
            if ship.radar > 0 and ship.empireID == self.game.myEmpireID:
                self.myRadar += ship.radar
            if ship.jamming > 0:
                self.jamming[ship.empireID] += ship.jamming
            
    def setBackgroundSystem(self):
        """A spinning System will be in the background"""
        systemDict = {'id':self.shipBattle.systemID, 
                      'myEmpireID':self.shipBattle.empireID,
                      'cities':self.shipBattle.cities,
                      'x':self.shipBattle.x,
                      'y':self.shipBattle.y,
                      'name':self.shipBattle.systemName}
        mySystem = system.BackgroundSystem(self.guiMediaPath, self, systemDict, glow=0)
        mySystem.setMyMode(self)
        mySystem.setMyGame(self.game)
        self.gui.append(mySystem)
            
    def setMyBackground(self):
        """Set the Background of mode"""
        base.setBackgroundColor(globals.colors['guiblack'])
            
    def createMainMenu(self, key):
        mode.Mode.createMainMenu(self, key)
        self.mainmenu.ignoreShortcuts()
            
    def setupMapMove(self):
        self.mapmove = mapmove.MapMove(self.guiMediaPath, -0.5, -0.7, self.ships.values())
        self.mapmove.setMyMode(self)
        self.gui.append(self.mapmove)

    def setupCamera(self):
        self.game.app.disableMouseCamControl()
        camera.setY(-20.0)
        camera.setX(0.0)
        camera.setZ(0.0)
        if self.enableMouseCamControl == 1:
            self.game.app.enableMouseCamControl()

    def setupMinimap(self):
        #Here is the explaination of the values passed to the minimap
        #   targets = all the nodepaths you want to minimap to track. They should be in an array as above
        #   cpos = This is the world coordinates for the center of the world. The minimap needs to know the center point of the world as a reference
        #   scale = This function is not used here. This is the number of pixels across that you want your map. Default is 200
        #   mapimage = This function again is not used here. It loads up the given image as the background to the map
        self.createMiniMapTargets()
        self.map = minimap.Minimap(self.guiMediaPath, 200)
        
        self.setMiniMapTargets()
        self.map.setBezel(image = '%s/bezel.png' % self.guiMediaPath, scale = 1.1)
        self.gui.append(self.map)

    def setMiniMapTargets(self):
        """If there are ships in empire, set the minimap targets"""
        for empireID, shipList in self.targets.iteritems():
            if shipList != []:
                self.map.setTargets(shipList, int(empireID))

    def createMiniMapTargets(self):
        """Create all the targets for the minimap to track"""
        self.targets = {'0':[],'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[]}
        for shipID, myShip in self.ships.iteritems():
            self.targets[myShip.empireID].append(myShip.sim)

    def addMiniMapTarget(self, myShip):
        if self.map != None:
            self.map.appendTarget(myShip.sim, int(myShip.empireID))
            self.mapmove.appendTarget(myShip)
            
    def removeMiniMapTarget(self, myShip):
        if self.map != None:
            self.map.removeTarget(myShip.sim, int(myShip.empireID))

    def clearMouseSelection(self):
        """Clear mouse selection before selecting something new"""
        self.hideMySelector()
        self.clearSelectedShip()
        self.removeShipInfo()
        self.enableScrollWheelZoom = 1

    def validateSelection(self):
        """Can something be selected right now"""
        return 1

    def clearSelectedShip(self):
        """Clear the selected ship"""
        if self.shipSelected != None:
            self.shipSelected.shipsim.removeMySelector()
            self.shipSelected = None

    def createBorders(self):
        """Display the borders of the Battle Map"""
        self.drawBox(-self.worldWidth,-self.worldHeight,self.worldWidth*2,self.worldHeight*2)

    def createQuadrants(self):
        """Display the Battle Map quadrants"""
        for i in range (1,10):
            (x,y) = globals.battlemapQuadrants[i]
            self.drawBox(x-globals.midQuadDistance,y-globals.midQuadDistance,globals.battlemapQuadSize,globals.battlemapQuadSize,'guigreen',0.12)

    def writeTextPause(self):
        text = 'Simulation Paused:  My Current Total Ship Radar = %d' % self.myRadar
        
        self.textPause = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                                   scale=0.06, font=5, parent=aspect2d)
        self.textPause.writeTextToScreen(x=-1, y=0, z=+0.8, wordwrap=40)
        color = globals.empires[int(self.game.myEmpireID)]['color1']
        self.textPause.setColor(globals.colors[color])
        self.gui.append(self.textPause)
        self.writeStats()
        
    def writeStats(self):
        """Write the empire stats"""
        x = 0
        y = 0
        count = 0
        for empireID in self.empires.keys():
            if x > 2.1:
                y -= 0.5
                x = 0
            methodToCall = getattr(self, 'writeEmpireStat%d' % count)
            result = methodToCall(empireID, x-1.2, y+0.7)
            x += 0.7
            count += 1

    def getMyStats(self, empireID):
        """each empire can give some stats based on paused state"""
        text = """
        %s STATS:\n
        ========================\n
        JAMMING = %d\n
        %s""" % (self.empires[empireID].name, 
                self.jamming[empireID],
                self.empires[empireID].stats.getSummary())
        return text
            
    def writeEmpireStat0(self, empireID, x, y):
        if self.stat0 != None:
            self.removeMyGui('stat0')
        text = self.getMyStats(empireID)
        self.stat0 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat0.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat0.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat0)

    def writeEmpireStat1(self, empireID, x, y):
        if self.stat1 != None:
            self.removeMyGui('stat1')
        text = self.getMyStats(empireID)
        self.stat1 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat1.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat1.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat1)
        
    def writeEmpireStat2(self, empireID, x, y):
        if self.stat2 != None:
            self.removeMyGui('stat2')
        text = self.getMyStats(empireID)
        self.stat2 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat2.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat2.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat2)
        
    def writeEmpireStat3(self, empireID, x, y):
        if self.stat3 != None:
            self.removeMyGui('stat3')
        text = self.getMyStats(empireID)
        self.stat3 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat3.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat3.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat3)
        
    def writeEmpireStat4(self, empireID, x, y):
        if self.stat4 != None:
            self.removeMyGui('stat4')
        text = self.getMyStats(empireID)
        self.stat4 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat4.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat4.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat4)
        
    def writeEmpireStat5(self, empireID, x, y):
        if self.stat5 != None:
            self.removeMyGui('stat5')
        text = self.getMyStats(empireID)
        self.stat5 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat5.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat5.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat5)
        
    def writeEmpireStat6(self, empireID, x, y):
        if self.stat6 != None:
            self.removeMyGui('stat6')
        text = self.getMyStats(empireID)
        self.stat6 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat6.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat6.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat6)
        
    def writeEmpireStat7(self, empireID, x, y):
        if self.stat1 != None:
            self.removeMyGui('stat7')
        text = self.getMyStats(empireID)
        self.stat7 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat7.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat7.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat7)
        
    def writeEmpireStat8(self, empireID, x, y):
        if self.stat8 != None:
            self.removeMyGui('stat8')
        text = self.getMyStats(empireID)
        self.stat8 = textonscreen.TextOnScreen(self.guiMediaPath, text,
                                            scale=0.03, font=5, parent=aspect2d)
        self.stat8.writeTextToScreen(x=x, y=0, z=y, wordwrap=100)
        self.stat8.setColor(globals.colors[self.empires[empireID].color1])
        self.gui.append(self.stat8)
        
    def begin(self):
        """Start Simulation"""
        shipList = funcs.sortStringList(self.ships.keys())
        for shipID in shipList:
            myShip = self.ships[shipID]
            myShip.begin()
    
    def createEmpires(self):
        """Take shipBattle empires dict and add Empires to Simulator"""
        for empireID, myEmpireDict in self.shipBattle.empiresDict.iteritems():
            self.jamming[empireID] = 0
            myEmpire = empire.Empire(myEmpireDict)
            myEmpire.setMyGalaxy(self)
            self.empireEndSim[empireID] = 0
            for droneDesignID, myDroneDesignDict in myEmpireDict['droneDesigns'].iteritems():
                myDroneDesign = dronedesign.DroneDesign(myDroneDesignDict)
                myDroneDesign = self.createDroneDesign(myDroneDesignDict, myEmpire)
            for shipDesignID, myShipDesignDict in myEmpireDict['shipDesigns'].iteritems():
                myShipDesign = shipdesign.ShipDesign(myShipDesignDict)
                myShipDesign = self.createShipDesign(myShipDesignDict, myEmpire)
            
    def createShipDesign(self, myShipDesignDict, myEmpire):
        """Create Ship Design, place in myEmpire object"""
        myShipDesign = shipdesign.ShipDesign(myShipDesignDict)
        myShipDesign.setMyEmpire(myEmpire)
        
        for quadID, myQuadDict in myShipDesignDict['quads'].iteritems():
            myQuad = quad.Quad(myQuadDict)
            myQuad.setMyParent(myShipDesign)
            # weapons have to be created first
            for weaponID, myWeaponDict in myQuadDict['weapons'].iteritems():
                myWeapon = weapon.Weapon(myWeaponDict)
                myWeapon.setMyQuad(myQuad)
            for componentID, myComponentDict in myQuadDict['components'].iteritems():
                myComponent = component.Component(myComponentDict)
                myComponent.setMyQuad(myQuad)
                
        myShipDesign.setMyStatus()
        return myShipDesign
          
    def createDroneDesign(self, myDroneDesignDict, myEmpire):
        """Create Drone Design, place in myEmpire object"""
        myDroneDesign = dronedesign.DroneDesign(myDroneDesignDict)
        myDroneDesign.setMyEmpire(myEmpire)
        
        for quadID, myQuadDict in myDroneDesignDict['quads'].iteritems():
            myQuad = quad.Quad(myQuadDict)
            myQuad.setMyParent(myDroneDesign)
            # weapons have to be created first
            for weaponID, myWeaponDict in myQuadDict['weapons'].iteritems():
                myWeapon = weapon.Weapon(myWeaponDict)
                myWeapon.setMyQuad(myQuad)
            for componentID, myComponentDict in myQuadDict['components'].iteritems():
                myComponent = component.Component(myComponentDict)
                myComponent.setMyQuad(myQuad)
                
        myDroneDesign.setMyStatus()
        return myDroneDesign
          
    def createCaptains(self):
        """Create captains"""
        for captainID, myCaptainDict in self.shipBattle.captainsDict.iteritems():
            myCaptain = captain.Captain(myCaptainDict)
            myEmpire = self.empires[myCaptainDict['empireID']]
            myCaptain.setMyEmpire(myEmpire)
        
    def createShips(self):
        """Take shipBattle ships dict and add Ships to Simulator"""
        for shipID in funcs.sortStringList(self.shipBattle.shipsDict.keys()):
            myShipDict = self.shipBattle.shipsDict[shipID]
            myShip = ship.Ship(myShipDict)
            myShip.setMyGalaxy(self)
            myShip.targets = myShipDict['targets']
            myCaptain = self.captains[myShip.captainID]
            myShip.setMyCaptain(myCaptain)
            myEmpire = self.empires[myShip.empireID]
            myShipDesign = myEmpire.shipDesigns[myShip.designID]
            myShip.setFromDict(myShipDesign, myShipDict)
            myShip.setKObj()
            
            if globals.serverMode == 0:
                myShip.sim = shipsim.ShipSim(self.guiMediaPath, self, myShip)
                myShip.setShipsim(myShip.sim)
                if myShip.isTransport == 1:
                    texture = myShip.shipsim.texture[:-9] + 'transport_%s.png' % myShip.empireID
                    myShip.shipsim.texture = texture
                    myShip.shipsim.loadMyTexture()

            self.kworld.addShip(myShip)
            
            if globals.serverMode == 0:
                self.setPlanePickable(myShip, 'ships')
                self.sims.append(myShip.sim)
    
    def setShipCollideMasks(self):
        for shipID, myShip in self.ships.iteritems():
            myShip.setCollidemask()
    
    def shipsSelected(self, myShip):
        """Ship Selected"""
        if myShip != self.shipSelected:
            if self.canIviewShip(myShip):
                self.playSound('beep01')
                self.clearSelectedShip()
                self.shipSelected = myShip
                if self.setMySelector(myShip.sim.getX(), myShip.sim.getY(), myShip.sim.getZ(), scale=2.2):
                    self.createShipInfo(myShip)
                    self.centerCameraOnSim(myShip.sim)
                    myShip.shipsim.setMySelector(self.selector)
            else:
                self.modeMsgBox('Insufficient Ship Radar to view Ship')
    
    def canIviewShip(self, myShip):
        """Ships can only be viewed in simulator mode or if player has proper radar"""
        if self.shipBattle.systemName == 'Simu-System':
            return 1
        if self.game.myEmpireID == myShip.empireID:
            return 1
        if self.myRadar > self.jamming[myShip.empireID]:
            return 1
        return 0
                
    def createShipInfo(self, myShip):
        """Create the Ship Description GUI to allow for ship information in detail"""
        self.removeShipInfo()
        self.shipInfo = shipinfo.ShipInfo(self.guiMediaPath, myShip, 0.4, 0.85)
        self.shipInfo.setMyMode(self)
        self.gui.append(self.shipInfo)
    
    def removeShipInfo(self):
        if self.shipInfo != None:
            self.removeMyGui('shipInfo')
    
    def endSimulation(self, empireID='0'):
        """End the simulation, each empire has to say they are done the simulation"""
        self.empireEndSim[empireID] = 1
        if (self.end == 0 and self.areAllEmpiresDone() == 1) or empireID == '0':
            file_object = open('shipBattles%s.log' % self.shipBattle.id, 'w')
            for line in self.resultList:
                file_object.write(line+'\n')
            file_object.close()

            if globals.serverMode == 1 and self.myGalaxy != None:
                if self.end == 0:
                    self.updateMyGalaxy()
                    self.kworld = None
                    self.end = 1
                return 0
            self.end = 1
            self.pauseResume()
    
    def areAllEmpiresDone(self):
        for empireID, endSim in self.empireEndSim.iteritems():
            if endSim == 0:
                return 0
        return 1
            
    def enterMode(self):
        mode.Mode.enterMode(self)
        self.game.app.setIntervalValue(globals.intervalValue)
        self.kworld.setMode(self)
    
    def exitMode(self):
        """Exit the mode"""
        self.removeShips()
        mode.Mode.exitMode(self)
        self.removeMissiles()
        self.removeExplosions()
        self.game.app.setIntervalValue(0)
    
    def removeShips(self):
        """Remove all ship sims"""
        for shipID, myShip in self.ships.iteritems():
            if myShip.alive == 1:
                myShip.shipsim.destroy()
        self.ships = {}
    
    def removeDronesFromDestroyedCarrier(self, myCarrier):
        """Remove any drones that are attached to destroyed carrier"""
        for shipID, myShip in self.ships.iteritems():
            if myShip.positions == ['fore']:
                if myShip.myShip == myCarrier:
                    myShip.destroyMe()
    
    def removeMissiles(self):
        """Remove all missile sims"""
        for myMissile in self.kworld.missiles:
            myMissile.shipsim.destroy()
    
    def removeExplosions(self):
        """Remove all explosion sims"""
        for myExplosion in self.explosions:
            myExplosion.destroy()
        self.explosions = []
    
    def getNextD100(self):
        """Get next D100 Roll from Simulator"""
        value = self.rand.randint(1,100)
        return value
    
    def pauseResume(self):
        """Pause/Resume the Simulation"""
        if self.pause == 0:
            self.pause = 1
            if globals.serverMode == 0:
                self.writeTextPause()
            self.pauseGameLoop()
        else:
            self.pause = 0
            if globals.serverMode == 0:
                self.removeMyGui('textPause')
                for i in range(9):
                    self.removeMyGui('stat%s' % i)
            self.resumeGameLoop()
    
    def pauseGameLoop(self):
        self.game.app.gameLoopInterval.pause()

    def resumeGameLoop(self):
        self.game.app.gameLoopInterval.resume()
    
    def update(self, interval):
        """update the mode, return the status, 0 means stop game, allow pause"""
        if self.end == 1:
            return 0
        if self.count >= self.maxCount:
            return self.endSimulation()
        if self.pause == 1:
            return 1
        else:
            self.count += 1
            result = self.kworld.update(interval)
            if self.assaultTick == self.assaultDelay:
                self.assaultTick = 0
                self.processAssaults()
            else:
                self.assaultTick += 1
            if globals.serverMode == 0:
                for myExplosion in self.explosions:
                    if myExplosion.update() == 0:
                        self.explosions.remove(myExplosion)
            return result
    
    def processAssaults(self):
        """Go through each assault and decide one casualty"""
        for shipID, assaultShip in self.ships.iteritems():
            if assaultShip.alive == 1 and assaultShip.isAssault == 1 and assaultShip.underAssault == 1:
                otherShip = assaultShip.currentTarget
                if otherShip.alive == 1 and otherShip.underAssault == 1:
                    self.processAssault(assaultShip, otherShip)
    
    def processAssault(self, assaultShip, otherShip):
        """Decide one round of battle"""
        if assaultShip.currentAssault == 0:
            self.endAssault(assaultShip, otherShip, otherShip)
        elif otherShip.currentAssault == 0:
            self.endAssault(assaultShip, otherShip, assaultShip)
        else:
            if self.getNextD100() <= 50:
                otherShip.currentAssault -= 1
                color = 'guired'
            else:
                assaultShip.currentAssault -= 1
                color = 'guigreen'
            if globals.serverMode == 0:
                otherShip.shipsim.writeAssault(self.getAssaultString(assaultShip, otherShip),color)
    
    def getAssaultString(self, assaultShip, otherShip):
        """Return a descriptive string of current Assault taking place"""
        assaultstars = ''
        defenderstars = ''
        assaultnum = int(assaultShip.currentAssault/2.0)
        defendernum = int(otherShip.currentAssault/2.0)
        for i in range(assaultnum):
            assaultstars += '*'
        for i in range(defendernum):
            defenderstars += '*'
            
        s = 'Assaulter = [ %s ]\nDefender  = [ %s ]' % (assaultstars, defenderstars)
        return s
            
    def endAssault(self, assaultShip, otherShip, winnerShip):
        """Assault is over process winner and loser"""
        self.cancelAssault(assaultShip)
        assaultShip.finishedAssault = 1
        if winnerShip == assaultShip:
            self.switchShipOwner(otherShip, assaultShip)
        else:
            self.switchShipOwner(assaultShip, otherShip)
    
    def cancelAssault(self, myShip):
        """cancel the assault"""
        assaultShip = None
        otherShip = None
        if myShip.isAssault == 1:
            assaultShip = myShip
            otherShip = assaultShip.currentTarget
        else:
            otherShip = myShip
            assaultShip = self.getMyAssaultShip(otherShip)
        if otherShip == None or assaultShip == None:
            return
        if globals.serverMode == 0:
            otherShip.shipsim.removeAssaultText()
            
        for ship in [otherShip, assaultShip]:
            ship.underAssault = 0
            ship.currentTarget = None
            if ship.alive == 1:
                ship.setMyStatus()
                ship.retarget()
        otherShip.tellEnemiesToTargetMeAgain()
        
    def getMyAssaultShip(self, otherShip):
        """Find the assault ship for this ship"""
        for shipID, myShip in self.ships.iteritems():
            if myShip.isAssault == 1 and myShip.currentTarget == otherShip and myShip.underAssault == 1:
                return myShip
        
    def switchShipOwner(self, losingShip, winningShip):
        """Ship has been taken over by empire given"""
        empireID = copy.copy(winningShip.empireID)
        losingShip.takenOverByEmpire = empireID
        
        if losingShip.id in winningShip.targets:
            winningShip.targets.remove(losingShip.id)
        losingShip.targets = copy.copy(winningShip.targets)
        
        losingShip.shipsTargetingMe = []
        losingShip.copyWhoTargetsMe(winningShip.id)
        
        losingShip.empireID = empireID
        losingShip.alternateTargets = []
        losingShip.collidemask = winningShip.collidemask
        losingShip.setCurrentTarget()
        if globals.serverMode == 0:
            self.sims.remove(losingShip.sim)
            losingShip.shipsim.sim.removeNode()
            losingShip.shipsim.destroy()
            losingShip.sim = shipsim.ShipSim(self.guiMediaPath, self, losingShip)
            losingShip.setShipsim(losingShip.sim)
            self.setPlanePickable(losingShip, 'ships')
            self.sims.append(losingShip.sim)
            self.addMiniMapTarget(losingShip)
                
    def addExplosion(self, myExplosion):
        self.explosions.append(myExplosion)
    
    def setCameraToSelected(self):
        """Setup the camera to follow the selected ship and its target"""
        if self.shipSelected != None:
            x = self.shipSelected.shipsim.x
            z = self.shipSelected.shipsim.z
            camera.setX(x)
            camera.setZ(z)
    
    def updateMyGalaxy(self):
        """Update all game objects at the galaxy level"""
        self.updateShipsInGalaxy()
        
        for shipID, myShip in self.ships.iteritems():
            if shipID in self.myGalaxy.ships.keys() and myShip.positions != ['fore']:
                if myShip.alive == 0:
                    if myShip.isTransport == 1:
                        num = 0
                        key = '%s-%s' % (myShip.empireID, myShip.fromSystem)
                        if key in self.shipBattle.regimentsExposed.keys():
                            if self.shipBattle.regimentsExposed[key] > 10:
                                num = 10
                                self.shipBattle.regimentsExposed[key] -= 10
                            else:
                                num = self.shipBattle.regimentsExposed[key]
                                del self.shipBattle.regimentsExposed[key]
                            self.updateRegimentsToDestroy(myShip.name, num, myShip.empireID, myShip.fromSystem)
                    else:
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
                    
                    if myShip.takenOverByEmpire != '':
                        self.myGalaxy.switchShiptoNewEmpire(myShip.id, myShip.takenOverByEmpire)
                    
        # mail results to empires involved
        s = 'SHIP BATTLE RESULTS ON:%s, Round:%d' % (self.shipBattle.systemName, self.shipBattle.round)
        for empireID, myEmpireDict in self.shipBattle.empiresDict.iteritems():
            dMail = {'fromEmpire':empireID, 'round':self.myGalaxy.currentRound+1,
                     'messageType':'fleet', 'subject':s, 'body':str(self.resultList)}
            myEmpire = self.myGalaxy.empires[empireID]
            myEmpire.genMail(dMail)

    def updateRegimentsToDestroy(self, transportName, regNum, empireID, fromSystem):
        """Destroy number of regiments from system and empireID given"""
        body = []
        count = 0
        body.append('%s -> %s was DESTROYED in Battle ON %s' % (transportName, self.myGalaxy.systems[fromSystem].name,
                                                                self.myGalaxy.systems[self.shipBattle.systemID].name))
        body.append('%d Marine Regiments were on board %s:' % (regNum, transportName))
        for regID in self.myGalaxy.regiments.keys():
            myRegiment = self.myGalaxy.regiments[regID]
            if (myRegiment.empireID == empireID and myRegiment.fromSystem == fromSystem
                and myRegiment.toSystem == self.shipBattle.systemID
                and myRegiment.fromSystem != myRegiment.toSystem):
                body.append('%s DESTROYED' % myRegiment.name)
                self.myGalaxy.removeRegiment(regID)
                count += 1
                if count >= regNum:
                    self.myGalaxy.mailRegimentsLostInTransport(empireID, body)
                    return
    
    def shipsUnderAssault(self):
        """Check if any ships under assault currently"""
        for shipID, myShip in self.ships.iteritems():
            if myShip.underAssault == 1 and myShip.alive == 1:
                return 1
        return 0
           
    def setupAssaultBattle(self, assaultShip, otherShip):
        """Assault ship is about to board other ship"""
        assaultShip.underAssault = 1
        otherShip.underAssault = 1
        assaultShip.currentAssault = assaultShip.assaultStrength
        otherShip.currentAssault = otherShip.assaultStrength
        otherShip.tellNewFriendsToStopTargeting(assaultShip.empireID)
                
    def updateShipsInGalaxy(self):
        """Update ships in actual galaxy based on ships destroyed"""
        for shipID, myShip in self.ships.iteritems():
            if myShip.__module__ == 'anw.war.ship':
                if shipID in self.myGalaxy.ships.keys():
                    if myShip.alive == 0:
                        self.myGalaxy.ships[shipID].alive = 0
        
    def onSpaceBarClear(self):
        """Space bar should not clear anythign in the simulator!"""
        pass
    
    def onMouse2Down(self):
        """clear only the selected ship! nothing else"""
        if self.validateSelection():
            self.clearMouseSelection()
            