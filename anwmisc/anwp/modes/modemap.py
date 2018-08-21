# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# modemap.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This is representation of the Galactic Map in ANW
# ---------------------------------------------------------------------------
import pygame
import types
import string

import pyui
import mode
import anwp.sims
import anwp.sl.entity
import anwp.sl.world
import anwp.sl.engine
import anwp.gui.addcity
import anwp.gui.addindustry
import anwp.gui.footer
import anwp.gui.viewtrade
import anwp.gui.mapmenu
import anwp.gui.systeminfo
import anwp.gui.shipyardsinfo
import anwp.gui.militaryinstinfo
import anwp.gui.armadainfo
import anwp.gui.armyinfo
import anwp.gui.getgrid
import anwp.gui.empiredip
import anwp.gui.sendmailinfo
import anwp.func.globals
import anwp.func.funcs

class RadarEntity(anwp.sl.entity.Entity):
    """Represents a Radar Indicator on the Map"""
    def __init__(self, mode, category):
        self.mode = mode
        self.type = 'RadarEntity'
        anwp.sl.entity.Entity.__init__(self, category, None)

class ResourceEntity(anwp.sl.entity.Entity):
    """Represents a Resource on the Map"""
    def __init__(self, mode, category):
        self.mode = mode
        self.type = 'ResourceEntity'
        anwp.sl.entity.Entity.__init__(self, category, None)

class TradeEntity(anwp.sl.entity.Entity):
    """Represents a Trade Route on the Map"""
    def __init__(self, mode, category, myTradeDict):
        self.mode = mode
        self.type = 'TradeEntity'
        self.myTradeDict = myTradeDict
        
        # set color of any text
        color = ''
        try:
            (a,color,x) = string.split(myTradeDict['imageFile'], '_')
        except:
            (a,color) = string.split(myTradeDict['imageFile'], '_')
        self.color = anwp.func.globals.colors[color]
        self.offsetX = 0
        self.offsetY = 0
        anwp.sl.entity.Entity.__init__(self, category, None)

class SystemEntity(anwp.sl.entity.Entity):
    """Represents a System on the Map"""
    def __init__(self, mode, category, mySystemDict, myEmpireDict):
        self.mode = mode
        self.type = 'SystemEntity'
        self.mySystemDict = mySystemDict
        self.myEmpireDict = myEmpireDict
        self.systemID = mySystemDict['id']
        self.color1 = anwp.func.globals.colors[self.myEmpireDict['color1']]
        self.color2 = anwp.func.globals.colors[self.myEmpireDict['color2']]
        anwp.sl.entity.Entity.__init__(self, category, None)        

class ShipyardEntity(anwp.sl.entity.Entity):
    """Represents a Shipyard on the Map"""
    def __init__(self, mode, category, mySystemDict):
        self.mode = mode
        self.type = 'ShipyardEntity'
        self.mySystemDict = mySystemDict
        self.systemID = mySystemDict['id']
        anwp.sl.entity.Entity.__init__(self, category, None)
        
class MilitaryInstEntity(anwp.sl.entity.Entity):
    """Represents a Military Installation on the Map"""
    def __init__(self, mode, category, mySystemDict):
        self.mode = mode
        self.type = 'MilitaryInstEntity'
        self.mySystemDict = mySystemDict
        self.systemID = mySystemDict['id']
        anwp.sl.entity.Entity.__init__(self, category, None)

class WarpGateEntity(anwp.sl.entity.Entity):
    """Represents a Warp Gate on the Map"""
    def __init__(self, mode, category):
        self.mode = mode
        self.type = 'WarpGateEntity'
        anwp.sl.entity.Entity.__init__(self, category, None)

class ArmadaEntity(anwp.sl.entity.Entity):
    """Represents an Armada (a group of fleets) on the Map"""
    def __init__(self, mode, category, mySystemDict, myEmpireDict):
        self.mode = mode
        self.type = 'ArmadaEntity'
        self.mySystemDict = mySystemDict
        self.myEmpireDict = myEmpireDict
        self.systemID = mySystemDict['id']
        anwp.sl.entity.Entity.__init__(self, category, None)

class ArmyEntity(anwp.sl.entity.Entity):
    """Represents an Army (a group of regiments) on the Map"""
    def __init__(self, mode, category, mySystemDict, myEmpireDict):
        self.mode = mode
        self.type = 'ArmyEntity'
        self.mySystemDict = mySystemDict
        self.myEmpireDict = myEmpireDict
        self.systemID = mySystemDict['id']
        anwp.sl.entity.Entity.__init__(self, category, None)

class ModeMap(mode.Mode):
    """This is the Galactic World Map Mode"""
    def __init__(self, game):
        # init the mode
        mode.Mode.__init__(self, game)
        self.name = 'MAP'
        self.systemSims = []
        self.tradeRouteSims = []
        self.radarSims = []
        self.resourceSims = []
        self.shipyardSims = []
        self.militaryinstSims = []
        self.warpgateSims = []
        self.armadaSims = {}
        self.armySims = {}
        
        # create gui panels
        self.mainMenu = anwp.gui.mapmenu.MainMenuMap(self, self.game.app)        
        self.mainFooter = anwp.gui.footer.Footer(self, self.game.app)
        self.systemInfo = None
        self.shipyardsInfo = None
        self.militaryinstInfo = None
        self.armadaInfo = None
        self.armyInfo = None
        self.sendMailInfo = None
        self.diplomacyPanels = [] # list of all diplomacy panels
        self.viewDiplomacy = 0
        
        # create the world
        self.worldWidth = self.game.myGalaxy['xMax']
        self.worldHeight = self.game.myGalaxy['yMax']
        self.renderer = pyui.desktop.getRenderer()
        self.setWorld(anwp.sl.world.World(self.worldWidth, self.worldHeight, 25))
        self.renderer.setBackMethod(self.draw)
        
        # create the sims for the world
        self.createSystemSims()
        self.createRadarSims()
        self.createShipyardSims()
        self.createMilitaryInstSims()
        self.createWarpGateSims()
        self.createArmadaSims()
        self.createArmySims()
        for systemID in self.game.allSystems.keys():
            self.repositionMilitaryIcons(systemID)
        
        # move screen to view nearest friendly system
        self.viewSystems()
        
        # set the default viewing preferences
        if self.game.myEmpire['viewResources'] == 1:
            self.createResourceSims()
        if self.game.myEmpire['viewTradeRoutes'] == 1:
            self.createTradeRouteSims()
        
        # create ship design objects currently in use
        self.createShipDesigns()
    
    def createShipDesigns(self):
        """Create all Ship Design Objects that Player currently uses"""
        for designID, designInfo in self.game.shipDesigns.iteritems():
            if designID not in self.game.shipDesignObjects.keys():
                myDesign = self.getShipDesign(designInfo[1],designInfo[2],designInfo[3],designInfo[0])
                self.game.shipDesignObjects[designID] = myDesign
    
    def createSystemSims(self):
        """Create the System Sims"""
        # create systems
        import anwp.sims
        self.systemSims = []
        for systemID, systemDict in self.game.allSystems.iteritems():
            empireDict = self.game.allEmpires[systemDict['myEmpireID']]
            imageFileName = '%s%s.png' % (self.game.app.simImagePath, systemDict['imageFile'])          
                
            # create sim
            sim = SystemEntity(self, anwp.sims.categories.ClickableCategory(imageFileName,'system'), systemDict, empireDict)
                            
            # add sim to world
            self.systemSims.append(sim)
            x = systemDict['x']
            y = systemDict['y']
            facing = 0
            speed = 0
            sim.turnRate = 0
            self.world.addToWorld(sim, x, y, facing, speed)
    
    def createShipyardSims(self):
        """Create the Shipyard Sims"""
        # create shipyards
        import anwp.sims
        self.shipyardSims = []
        for systemID, systemDict in self.game.allSystems.iteritems():
            if systemDict['myEmpireID'] == self.game.myEmpireID and systemDict['availSYC'] > 0:
                # shipyard capacity found, create sim and exit
                imageFileName = '%sshipyards_%s_%s.png' % (self.game.app.simImagePath, self.game.myEmpire['color1'], self.game.myEmpire['color2'])
                sim = ShipyardEntity(self, anwp.sims.categories.ClickableCategory(imageFileName, 'shipyard'), systemDict)
                    
                # add sim to world
                self.shipyardSims.append(sim)
                x = systemDict['x']-65
                y = systemDict['y']+25
                facing = 0
                speed = 0
                sim.turnRate = 0
                force = 1
                self.world.addToWorld(sim, x, y, facing, speed, force)
                    
    def createMilitaryInstSims(self):
        """Create the Military Installation Sims"""
        # create shipyards
        import anwp.sims
        self.militaryinstSims = []
        for systemID, systemDict in self.game.allSystems.iteritems():
            if systemDict['myEmpireID'] == self.game.myEmpireID and systemDict['availMIC'] > 0:
                # military installation capacity found, create sim and exit
                imageFileName = '%smilitaryinst_%s_%s.png' % (self.game.app.simImagePath, self.game.myEmpire['color1'], self.game.myEmpire['color2'])
                sim = MilitaryInstEntity(self, anwp.sims.categories.ClickableCategory(imageFileName, 'shipyard'), systemDict)
                    
                # add sim to world
                self.militaryinstSims.append(sim)
                x = systemDict['x']-65
                y = systemDict['y']-10
                facing = 0
                speed = 0
                sim.turnRate = 0
                force = 1
                self.world.addToWorld(sim, x, y, facing, speed, force)
    
    def createArmadaSims(self):
        """Create all Armada Sims"""
        # create armada sims for player
        for systemID in self.game.myArmadas.keys():
            self.createPlayerArmadaSim(systemID)
        
        # create armada sims representing other empires
        for systemID in self.game.otherArmadas.keys():
            self.createOtherArmadaSim(systemID)
    
    def createArmySims(self):
        """Create all Army Sims"""
        # create army sims for player
        for systemID in self.game.myArmies.keys():
            self.createPlayerArmySim(systemID)
        
        # create army sims representing other empires
        for systemID in self.game.otherArmies.keys():
            self.createOtherArmySim(systemID)
    
    def createOtherArmadaSim(self, systemID):
        """Create other Armada Sim"""
        systemDict = self.game.allSystems[systemID]
        empireList = self.game.otherArmadas[systemID]
        i = 1
        for empireID in empireList:
            empireDict = self.game.allEmpires[empireID]
            imageFileName = '%sarmada_%s_%s.png' % (self.game.app.simImagePath, empireDict['color1'], empireDict['color2'])
            sim = ArmadaEntity(self, anwp.sims.categories.ClickableMobileCategory(imageFileName, 'armada'), systemDict, empireDict)
            # add sim to world
            self.armadaSims['%s-%s' % (empireID, systemID)] = sim
            x = systemDict['x']+90
            y = systemDict['y']+35 - (i*35)
            facing = 0
            speed = 0
            sim.turnRate = 0
            force = 1
            self.world.addToWorld(sim, x, y, facing, speed, force)
            i += 1
    
    def createOtherArmySim(self, systemID):
        """Create other Army Sim"""
        systemDict = self.game.allSystems[systemID]
        empireList = self.game.otherArmies[systemID]
        i = 1
        for empireID in empireList:
            empireDict = self.game.allEmpires[empireID]
            imageFileName = '%sarmy_%s_%s.png' % (self.game.app.simImagePath, empireDict['color1'], empireDict['color2'])
            sim = ArmyEntity(self, anwp.sims.categories.ClickableMobileCategory(imageFileName, 'armada'), systemDict, empireDict)
            # add sim to world
            self.armySims['%s-%s' % (empireID, systemID)] = sim
            x = systemDict['x']+65
            y = systemDict['y']+35 - (i*35)
            facing = 0
            speed = 0
            sim.turnRate = 0
            force = 1
            self.world.addToWorld(sim, x, y, facing, speed, force)
            i += 1
    
    def createPlayerArmadaSim(self, systemID):
        """Create Player Armada Sim"""
        systemDict = self.game.allSystems[systemID]
        empireDict = self.game.myEmpire
        imageFileName = '%sarmada_%s_%s.png' % (self.game.app.simImagePath, empireDict['color1'], empireDict['color2'])
        sim = ArmadaEntity(self, anwp.sims.categories.ClickableMobileCategory(imageFileName, 'armada'), systemDict, empireDict)
        # add sim to world
        self.armadaSims['%s-%s' % (self.game.myEmpireID, systemID)] = sim
        x = systemDict['x']+90
        y = systemDict['y']+25
        facing = 0
        speed = 0
        sim.turnRate = 0
        force = 1
        self.world.addToWorld(sim, x, y, facing, speed, force)
    
    def createPlayerArmySim(self, systemID):
        """Create Player Army Sim"""
        systemDict = self.game.allSystems[systemID]
        empireDict = self.game.myEmpire
        imageFileName = '%sarmy_%s_%s.png' % (self.game.app.simImagePath, empireDict['color1'], empireDict['color2'])
        sim = ArmyEntity(self, anwp.sims.categories.ClickableMobileCategory(imageFileName, 'armada'), systemDict, empireDict)
        # add sim to world
        self.armySims['%s-%s' % (self.game.myEmpireID, systemID)] = sim
        x = systemDict['x']+65
        y = systemDict['y']+25
        facing = 0
        speed = 0
        sim.turnRate = 0
        force = 1
        self.world.addToWorld(sim, x, y, facing, speed, force)
    
    def createTradeRouteSims(self):
        """Create the Trade Route Sims"""
        import anwp.sims
        # remove old trade route sims if any
        self.removeTradeRouteSims()
        # create trade route sims
        self.tradeRouteSims = []
        for trID, tradeRouteDict in self.game.tradeRoutes.iteritems():
            imageFileName = '%s%s.png' % (self.game.app.genImagePath, tradeRouteDict['imageFile'])
                
            # create sim
            sim = TradeEntity(self, anwp.sims.categories.TradeRouteCategory(imageFileName), tradeRouteDict)
                            
            # add sim to world
            self.tradeRouteSims.append(sim)
            fromSystemDict = self.game.allSystems[tradeRouteDict['fromSystem']]
            toSystemDict = self.game.allSystems[tradeRouteDict['toSystem']]
            xFrom = fromSystemDict['x']
            yFrom = fromSystemDict['y']
            xTo = toSystemDict['x']
            yTo = toSystemDict['y']
            facing = anwp.func.funcs.getRelativeAngle(xFrom, yFrom, xTo, yTo)
            # calculate offset
            (xTo, yTo) = anwp.func.funcs.findOffset(xFrom, yFrom, facing, self.game.myGalaxy['systemSize'])
            (x,y) = anwp.func.funcs.getOffsetPoint(xFrom, yFrom, xTo, yTo, 10)
            (sim.offsetX, sim.offsetY) = anwp.func.funcs.getOffsetPoint(xFrom, yFrom, xTo, yTo, 15)
            speed = 0
            force = 1
            sim.turnRate = 0
            self.world.addToWorld(sim, x, y, facing, speed, force)
    
    def createResourceSims(self):
        """Create the Resource Sims"""
        if self.game.myEmpire['viewResources'] == 0:
            return
        import anwp.sims
        # remove old sims if any
        self.removeResourceSims()
        # create resource sims
        self.resourceSims = []
        for systemID, systemDict in self.game.allSystems.iteritems():
            if systemDict['myEmpireID'] == self.game.myEmpireID:
                # create resource sims representing resources on system
                i = 0
                for attr in ['AL', 'EC', 'IA']:
                    if systemDict[attr] > 0:
                        # system produces this resource create sim
                        name = string.lower(attr[-2:])
                        imageFileName = '%smini_%s.png' % (self.game.app.genImagePath, name)
                
                        # create sim
                        sim = ResourceEntity(self, anwp.sims.categories.StaticCategory(imageFileName, 'resource'))
                                        
                        # add sim to world
                        self.resourceSims.append(sim)
                        x = systemDict['x'] - 15
                        y = systemDict['y'] - 45 - 20*i
                        facing = 0
                        speed = 0
                        force = 1
                        self.world.addToWorld(sim, x, y, facing, speed, force)
                        i += 1
                        
                # create resource sims representing resources being generated
                i = 0
                for attr in ['prodAL', 'prodEC', 'prodIA', 'prodCR']:
                    if systemDict[attr] > 0:
                        # system produces this resource create sim
                        name = string.lower(attr[-2:])
                        imageFileName = '%smini_%s_gen.png' % (self.game.app.genImagePath, name)
                
                        # create sim
                        sim = ResourceEntity(self, anwp.sims.categories.StaticCategory(imageFileName, 'resource'))
                                        
                        # add sim to world
                        self.resourceSims.append(sim)
                        x = systemDict['x'] + 15
                        y = systemDict['y'] - 45 - 20*i
                        facing = 0
                        speed = 0
                        force = 1
                        self.world.addToWorld(sim, x, y, facing, speed, force)
                        i += 1
                
    def createRadarSims(self):
        """Create the Radar Sims"""
        import anwp.sims
        # remove old sims if any
        self.removeRadarSims()
        # create resource sims
        self.radarSims = []
        for systemID, systemDict in self.game.allSystems.iteritems():
            imageFileName = ''
            
            if systemDict['intelReport']['round'] == self.game.currentRound:
                # there is a current report from this system indicate with green radar
                imageFileName = '%sradar_green.png' % self.game.app.genImagePath
                
            if systemDict['myEmpireID'] == self.game.myEmpireID:
                if systemDict['radarStrength'] > 0:
                    # players system has radar indicate with blue radar
                    imageFileName = '%sradar_blue.png' % self.game.app.genImagePath
            
            if imageFileName <> '':
                # create sim
                sim = RadarEntity(self, anwp.sims.categories.StaticCategory(imageFileName, 'radar'))
                                
                # add sim to world
                self.radarSims.append(sim)
                x = systemDict['x']-46
                y = systemDict['y']+65
                facing = 0
                speed = 0
                force = 1
                self.world.addToWorld(sim, x, y, facing, speed, force)
    
    def createWarpGateSims(self):
        """Create the War Gate Sims"""
        # create warpgates
        import anwp.sims
        self.warpgateSims = []
        for systemID, systemDict in self.game.allSystems.iteritems():
            systemEmpireDict = self.game.allEmpires[systemDict['myEmpireID']]
            if systemDict['myEmpireID'] == self.game.myEmpireID or anwp.func.globals.diplomacy[self.game.myEmpire['diplomacy'][systemDict['myEmpireID']]['diplomacyID']]['trade'] == 1:
                # look for warp gates
                for indID, myIndustryDict in systemDict['myIndustry'].iteritems():
                    myIndustryDataDict = self.game.industrydata[myIndustryDict['industrytype']]
                    if myIndustryDataDict['abr'][1:] == 'WG':
                        # warp gate industry found, create sim and exit
                        imageFileName = '%swarpgate_%s_%s.png' % (self.game.app.simImagePath, systemEmpireDict['color1'], systemEmpireDict['color2'])
                        sim = WarpGateEntity(self, anwp.sims.categories.StaticCategory(imageFileName, 'warpgate'))
                            
                        # add sim to world
                        self.warpgateSims.append(sim)
                        x = systemDict['x']-65
                        y = systemDict['y']-42
                        facing = 0
                        speed = 0
                        sim.turnRate = 0
                        force = 1
                        self.world.addToWorld(sim, x, y, facing, speed, force)
                        break
    
    def removeArmadaSim(self, systemID):
        """Remove Armada Sim at system in question"""
        for key in self.armadaSims.keys():
            sim = self.armadaSims[key]
            if sim.systemID == systemID and sim.myEmpireDict['id'] == self.game.myEmpireID:
                self.world.removeFromWorld(sim)
                del self.armadaSims[key]
        self.repositionMilitaryIcons(systemID)
    
    def removeArmySim(self, systemID):
        """Remove Army Sim at system in question"""
        for key in self.armySims.keys():
            sim = self.armySims[key]
            if sim.systemID == systemID and sim.myEmpireDict['id'] == self.game.myEmpireID:
                self.world.removeFromWorld(sim)
                del self.armySims[key]
        self.repositionMilitaryIcons(systemID)
    
    def removeTradeRouteSims(self):
        """Remove the Trade Route Sims"""
        for sim in self.tradeRouteSims:
            self.world.removeFromWorld(sim)
        self.tradeRouteSims = []
    
    def removeResourceSims(self):
        """Remove the Resource Sims"""
        for sim in self.resourceSims:
            self.world.removeFromWorld(sim)
        self.resourceSims = []
    
    def removeRadarSims(self):
        """Remove the Radar Sims"""
        for sim in self.radarSims:
            self.world.removeFromWorld(sim)
        self.radarSims = []
    
    def createAddCityFrame(self, systemID, systemName):
        """Build an Add City Frame for adding a city to a system"""
        self.destroyTempFrames()
        self.addCityFrame = anwp.gui.addcity.AddCityFrame(self, self.game.app, 'Add City', None, systemID, systemName)
        self.tempFrames.append(self.addCityFrame)

    def createAddIndustryFrame(self, systemID, systemName):
        """Build an Add Industry Frame for adding an Industry to a system"""
        self.destroyTempFrames()
        self.addIndustryFrame = anwp.gui.addindustry.AddIndustryFrame(self, self.game.app, 'Add Industry to: %s' % systemName, systemID)
        self.tempFrames.append(self.addIndustryFrame)
    
    def createChangeCityFrame(self, cityList, systemID, systemName):
        """Build a Change City Frame for changing city resource"""
        self.destroyTempFrames()
        self.changeCityFrame = anwp.gui.addcity.AddCityFrame(self, self.game.app, 'Change City Resource', cityList, systemID, systemName)
        self.tempFrames.append(self.changeCityFrame)
    
    def createSendMailFrame(self, empireDict):
        """Create Send Mail Frame to empire given"""
        self.destroyTempFrames()
        self.sendMailInfo = anwp.gui.sendmailinfo.SendMailInfoFrame(self, self.game.app, empireDict)
        self.tempFrames.append(self.sendMailInfo)
    
    def createRegiment(self, regimentID):
        """Ask Server to create a new regiment at system specified"""
        try:
            systemID = self.game.myRegiments[regimentID]['fromSystem']
            serverResult = self.game.server.createRegiment(self.game.authKey, systemID)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            elif type(serverResult) == types.DictType:
                # success, update regiments and refresh
                self.game.myRegiments[serverResult['id']] = serverResult
                self.game.myArmies[systemID].append(serverResult['id'])
                self.armyInfo.panel.populate(self.armyInfo.panel.myEmpireDict, self.armyInfo.panel.mySystemDict)
        except:
            self.modeMsgBox('createRegiment->Connection to Server Lost')
    
    def createShipInfoFrame(self, shipID, fleetID):
        """Build a Ship Info Frame based on fleet and shipID's given"""
        self.destroyTempFrames()
        self.myShipDesign = None
        # create ship instance
        import anwp.war.ship
        import anwp.war.captain
        import anwp.war.empire
        myShipDict = myFleetDict['ships'][shipID]
        myCaptainDict = self.game.myCaptains[myShipDict['captainID']]
        shipDesignDict = self.game.shipDesigns[myShipDict['designID']]
        
        myEmpire = anwp.war.empire.Empire(self.game.myEmpire)
        self.myShipDesign = self.getShipDesign(shipDesignDict[1],shipDesignDict[2],shipDesignDict[3],shipDesignDict[0])
        self.myShipDesign.myEmpire = myEmpire
        self.myShip = anwp.war.ship.Ship(myShipDict)
        myCaptain = anwp.war.captain.Captain(myCaptainDict)
        self.myShip.setMyCaptain(myCaptain)
        self.myShip.setFromDict(self.myShipDesign, myShipDict)
        
        self.createShipInfoFrameFromShip(self.myShip)
        
    def addTradeRoute(self, AL, EC, IA, fromSystem, toSystem, type, oneTime=0):
        """Send an Add Trade Route Request to the Server"""
        try:
            dOrder = {'AL':AL, 'EC':EC, 'IA':IA, 'fromSystem':fromSystem, 'toSystem':toSystem, 'type':type, 'oneTime':oneTime}
            serverResult = self.game.server.addTradeRoute(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.refreshTradeRoutes(fromSystem)
        except:
            self.modeMsgBox('addTradeRoute->Connection to Server Lost, Login Again') 

    def addMarketOrder(self, type, value, min, max, amount, system):
        """Send an Add Market Order to Server"""
        try:
            dOrder = {'type':type, 'value':value, 'min':min, 'max':max, 'amount':amount, 'system':system}
            serverResult = self.game.server.addMarketOrder(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.refreshMarketOrders(system)
        except:
            self.modeMsgBox('addMarketOrder->Connection to Server Lost, Login Again') 
            
    def addCity(self, resource, systemID):
        """Send an Add City Request to the Server"""
        try:
            dOrder = {'type':'Add City', 'value':resource,
                      'system':systemID, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)                
            else:
                self.addCityFrame.destroy()
                self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('addCity->Connection to Server Lost, Login Again')
    
    def addIndustry(self, amount, industryType, systemID):
        """Send an Add Industry Request to the Server"""
        try:
            dOrder = {'type':'Add Industry', 'value':'%s-%s' % (str(amount), industryType),
                      'system':systemID, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.addIndustryFrame.destroy()
                self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('addIndustry->Connection to Server Lost, Login Again')
    
    def addShipOrder(self, amount, shipDesignID, systemID):
        """Send an Add Ship Request to the Server"""
        try:
            dOrder = {'type':'Add Ship', 'value':'%s-%s' % (str(amount), shipDesignID),
                      'system':systemID, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('addShipOrder->Connection to Server Lost, Login Again')
    
    def addRegimentOrder(self, amount, typeID, systemID):
        """Send an Add Regiment Request to the Server"""
        try:
            dOrder = {'type':'Add Regiment', 'value':'%s-%s' % (str(amount), typeID),
                      'system':systemID, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('addRegimentOrder->Connection to Server Lost, Login Again')
    
    def restoreRegimentOrder(self, regimentList, systemID):
        """Send a Restore Regiment Request to the Server"""
        try:
            for value in regimentList:
                dOrder = {'type':'Restore Regiment', 'value':value,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('restoreRegimentOrder->Connection to Server Lost, Login Again')
    
    def repairStarshipOrder(self, shipList, systemID):
        """Send a Repair Starship Request to the Server"""
        try:
            for value in shipList:
                dOrder = {'type':'Repair Starship', 'value':value,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('repairStarshipOrder->Connection to Server Lost, Login Again')
    
    def upgradeStarshipOrder(self, value, newDesignID, systemID):
        """Send a Upgrade Starship Request to the Server"""
        try:
            dOrder = {'type':'Upgrade Starship', 'value':'%s-%s' % (value, newDesignID),
                      'system':systemID, 'round':self.game.myGalaxy['currentRound']}
            serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('repairStarshipOrder->Connection to Server Lost, Login Again')
    
    def changeCity(self, resource, cityList, systemID):
        """Send a Change City Request to the Server"""
        try:
            for cityID in cityList:
                dOrder = {'type':'Change City', 'value':'%s-%s' % (cityID, resource),
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.changeCityFrame.destroy()
            self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('changeCity->Connection to Server Lost, Login Again')
    
    def upgradeIndustry(self, industryList, systemID):
        """Send an Upgrade Industry Request to the Server"""
        try:
            for industryID in industryList:
                dOrder = {'type':'Upgrade Industry', 'value':'%s' % industryID,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('upgradeIndustry->Connection to Server Lost, Login Again')

    def removeIndustry(self, industryList, systemID):
        """Send a Remove Industry Request to the Server"""
        try:
            for industryID in industryList:
                dOrder = {'type':'Remove Industry', 'value':'%s' % industryID,
                          'system':systemID, 'round':self.game.myGalaxy['currentRound']}
                serverResult = self.game.server.addIndustryOrder(self.game.authKey, dOrder)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('removeIndustry->Connection to Server Lost, Login Again')

    def cancelIndustryOrder(self, orderList, systemID):
        """Send a Cancel Industry Order to Server"""
        try:
            for orderID in orderList:
                serverResult = self.game.server.cancelIndustryOrder(self.game.authKey, orderID)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshIndustryOrder(systemID)
        except:
            self.modeMsgBox('cancelIndustryOrder->Connection to Server Lost, Login Again')

    def cancelMarketOrder(self, orderList, systemID):
        """Send a Market Order to Server"""
        try:
            for orderID in orderList:
                serverResult = self.game.server.cancelMarketOrder(self.game.authKey, orderID)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshMarketOrders(systemID)
        except:
            self.modeMsgBox('cancelMarketOrder->Connection to Server Lost, Login Again')
            
    def cancelTradeRoute(self, tradeList, systemID):
        """Send a Cancel Trade Route to Server"""
        try:
            for orderID in tradeList:
                serverResult = self.game.server.cancelTradeRoute(self.game.authKey, orderID)
                if serverResult <> 1:
                    self.modeMsgBox(serverResult)
                    break
            self.refreshTradeRoutes(systemID)
        except:
            self.modeMsgBox('cancelTradeRoute->Connection to Server Lost, Login Again')
    
    def refreshArmadas(self, myFleetID, fromSystemID, toSystemID):
        """refresh Armadas in both systems given"""
        try:
            # get system update if nessessary
            myShipDict = self.game.myShips[myFleetID]
            if toSystemID not in self.game.allSystems[fromSystemID]['connectedSystems'] and fromSystemID <> toSystemID:
                # warp must have been used, update
                self.getSystemUpdate(['usedWGC'], fromSystemID)
                self.getSystemUpdate(['usedWGC'], toSystemID)
            
            # update myFleet dict from server
            fleetList = self.game.myArmadas[fromSystemID]
            if len(fleetList) > 0:
                self.getFleetUpdate(fleetList)
        
            # update myRegiment dict from server
            reg1 = []
            reg2 = []
            if fromSystemID in self.game.myArmies:
                reg1 = self.game.myArmies[fromSystemID]
            if toSystemID in self.game.myArmies:
                reg2 = self.game.myArmies[toSystemID]
            regimentList = reg1 + reg2
            self.getRegimentUpdate(regimentList)
            
            # update fromSystem Armada
            if self.game.myArmadas.has_key(fromSystemID):
                fleetList = self.game.myArmadas[fromSystemID]
                if len(fleetList) > 1:
                    fleetList.remove(myFleetID)
                else:
                    # only one fleet in armada, remove armada
                    del self.game.myArmadas[fromSystemID]
                    self.removeArmadaSim(fromSystemID)
                    
            # update toSystem Armada
            if self.game.myArmadas.has_key(toSystemID):
                fleetList = self.game.myArmadas[toSystemID]
                fleetList.append(myFleetID)
            else:
                # no armada present, create
                self.game.myArmadas[toSystemID] = [myFleetID]
                self.createPlayerArmadaSim(toSystemID)
            
            # refresh armies
            for shipID, myShipDict in myFleetDict['ships'].iteritems():
                for position, myQuadDict in myShipDict['quads'].iteritems():
                    for componentID, regimentIDList in myQuadDict['regimentsInHold'].iteritems():
                        for regimentID in regimentIDList:
                            # update fromSystem Army
                            if self.game.myArmies.has_key(fromSystemID):
                                regimentList = self.game.myArmies[fromSystemID]
                                if len(regimentList) > 1:
                                    regimentList.remove(regimentID)
                                else:
                                    # only one regiment in army, remove army
                                    del self.game.myArmies[fromSystemID]
                                    self.removeArmySim(fromSystemID)
                                    
                            # update toSystem Army
                            if self.game.myArmies.has_key(toSystemID):
                                regimentList = self.game.myArmies[toSystemID]
                                regimentList.append(regimentID)
                            else:
                                # no army present, create
                                self.game.myArmies[toSystemID] = [regimentID]
                                self.createPlayerArmySim(toSystemID)
            
            # unselect gui
            self.onSelectNoSim()
            
            # refresh icons
            self.repositionMilitaryIcons(fromSystemID)
            self.repositionMilitaryIcons(toSystemID)
            
        except:
            self.modeMsgBox('refreshArmadas error ')
    
    def refreshIndustryOrder(self, systemID):
        """Perform refresh to accomodate industry Order"""
        try:
            # get empire update
            self.getEmpireUpdate(['CR','AL','EC','IA'])
            
            # refresh gui
            self.mainFooter.panel.populate()
            
            # refresh panel if still hovering over it
            if self.systemInfo <> None:
                # get system update
                self.getSystemUpdate(['AL','EC','IA'], systemID)
                self.getEmpireOrders('industryOrders')
                if self.systemInfo.currentID == systemID:
                    self.systemInfo.panel.populate(self.systemInfo.panel.myEmpireDict, self.systemInfo.panel.mySystemDict)
            elif self.shipyardsInfo <> None:
                self.getSystemUpdate(['AL','EC','IA','usedSYC'], systemID)
                self.getEmpireOrders('industryOrders')
                if self.shipyardsInfo.currentID == systemID:
                    self.shipyardsInfo.panel.populate(self.shipyardsInfo.panel.mySystemDict)
            elif self.militaryinstInfo <> None:
                self.getSystemUpdate(['AL','EC','IA','usedMIC'], systemID)
                self.getEmpireOrders('industryOrders')
                if self.militaryinstInfo.currentID == systemID:
                    self.militaryinstInfo.panel.populate(self.militaryinstInfo.panel.mySystemDict)
            # refresh resource sims
            self.removeResourceSims()
            self.createResourceSims()
        except:
            self.modeMsgBox('refreshIndustryOrder error ')
    
    def refreshTradeRoutes(self, systemID):
        """Perform refresh to trade routes"""
        try:
            # get empire update
            self.getTradeRoutes()
            
            # show trade routes if not already shown
            if self.game.myEmpire['viewTradeRoutes'] == 0:
                self.toggleTradeRoutes()
            else:
                self.createTradeRouteSims()
            
            # refresh system panel if still hovering over it
            if self.systemInfo.currentID == systemID:
                self.systemInfo.panel.populate(self.systemInfo.panel.myEmpireDict, self.systemInfo.panel.mySystemDict)
        except:
            self.modeMsgBox('refreshTradeRoutes error ')
    
    def refreshMarketOrders(self, systemID):
        """Perform refresh to market orders"""
        try:
            # get empire update
            self.getMarketOrders()
            
            # get empire update
            self.getEmpireUpdate(['CR','AL','EC','IA'])
            
            # get system update
            self.getSystemUpdate(['AL','EC','IA'], systemID)
            self.getEmpireOrders('industryOrders')
            
            # refresh gui
            self.mainFooter.panel.populate()
            
            # refresh system panel if still hovering over it
            if self.systemInfo.currentID == systemID:
                self.systemInfo.panel.populate(self.systemInfo.panel.myEmpireDict, self.systemInfo.panel.mySystemDict)
        except:
            self.modeMsgBox('refreshMarketOrders error ')
    
    def repositionMilitaryIcons(self, systemID):
        """Make sure all Army and Armada Icons are in the proper place at System"""
        empireKeys = anwp.func.funcs.sortStringList(self.game.allEmpires.keys())
        systemDict = self.game.allSystems[systemID]
        i = 0
        
        for empireID in empireKeys:
            if empireID == self.game.myEmpireID:
                # players Icons
                x = systemDict['x'] + 65
                y = systemDict['y'] + 35
                if systemID in self.game.myArmadas:
                    armadaSim = self.armadaSims['%s-%s' % (empireID, systemID)]
                    if systemID in self.game.myArmies:
                        # place army icon and armada icon
                        armySim = self.armySims['%s-%s' % (empireID, systemID)]
                        armySim.setState(x,y,armySim.facing)
                        armadaSim.setState(x+25,y,armadaSim.facing)
                    else:
                        # no army, just place armada sim
                        armadaSim.setState(x,y,armadaSim.facing)
                elif systemID in self.game.myArmies:
                    # no armada, just place army sim
                    armySim = self.armySims['%s-%s' % (empireID, systemID)]
                    armySim.setState(x,y,armySim.facing)
            else:
                # other Empire Icons
                x = systemDict['x'] + 65
                y = systemDict['y'] + 35
                try:
                    armadaEmpireList = self.game.otherArmadas[systemID]
                except:
                    armadaEmpireList = []
                try:
                    armyEmpireList = self.game.otherArmies[systemID]
                except:
                    armyEmpireList = []
                # does empire have armada in system?
                if empireID in armadaEmpireList:
                    armadaSim = self.armadaSims['%s-%s' % (empireID, systemID)]
                    i += 1
                    # does empire have army in system?
                    if empireID in armyEmpireList:
                        # place army and armada icon
                        armySim = self.armySims['%s-%s' % (empireID, systemID)]
                        armySim.setState(x,y-(i*25),armySim.facing)
                        armadaSim.setState(x+25,y-(i*25),armadaSim.facing)
                    else:
                        # place armada icon
                        armadaSim.setState(x,y-(i*25),armadaSim.facing)
                elif empireID in armyEmpireList:
                    i += 1
                    # place army icon
                    armySim = self.armySims['%s-%s' % (empireID, systemID)]
                    armySim.setState(x,y-(i*25),armySim.facing)
    
    def getTradeRoutes(self):
        """Ask the Server for an updated Trade Routes list from galaxy"""
        try:
            serverResult = self.game.server.getTradeRoutes(self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.game.tradeRoutes = serverResult
        except:
            self.modeMsgBox('getTradeRoutes->Connection to Server Lost')
    
    def getMarketOrders(self):
        """Ask the Server for an updated Market Orders list from galaxy"""
        try:
            serverResult = self.game.server.getMarketOrders(self.game.authKey)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.game.marketOrders = serverResult
        except:
            self.modeMsgBox('getMarketOrders->Connection to Server Lost')
            
    def getEmpireOrders(self, orderType):
        """Ask the Server for an updated Industry Orders list"""
        try:
            serverResult = self.game.server.getEmpireOrders(self.game.authKey, orderType)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            else:
                self.game.myEmpire[orderType] = serverResult
        except:
            self.modeMsgBox('getEmpireOrders->Connection to Server Lost')
    
    def getShipUpdate(self, shipList):
        """Ask the Server for an update on ships specified"""
        try:
            serverResult = self.game.server.getShipUpdate(self.game.authKey, shipList)
            if type(serverResult) == types.DictType:
                for shipID, shipDict in serverResult.iteritems():
                    self.game.myShips[shipID] = shipDict
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('getShipUpdate->Connection to Server Lost')
    
    def getRegimentUpdate(self, regimentList):
        """Ask the Server for an update on regiments specified"""
        try:
            serverResult = self.game.server.getRegimentUpdate(self.game.authKey, regimentList)
            if type(serverResult) == types.DictType:
                for key, data in serverResult.iteritems():
                    self.game.myRegiments[key] = data
            else:
                self.modeMsgBox(serverResult)
        except:
            self.modeMsgBox('getRegimentUpdate->Connection to Server Lost')
    
    def moveShips(self, shipList, systemID):
        """Attempt to move ships to system specified"""
        try:
            serverResult = self.game.server.moveShips(self.game.authKey, shipList, systemID)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            elif type(serverResult) == types.DictType:
                # success, update ships and refresh
                for id, dict in serverResult:
                    self.game.myShips[id] = dict
        except:
            self.modeMsgBox('moveShips->Connection to Server Lost')
    
    def onMouseDown(self, event):
        """Allow dynamic picking of an object within world"""
        # determine where mouse is
        (worldX, worldY) = anwp.sl.engine.screenToWorld(event.pos[0], event.pos[1])
        sim = self.world.checkPoint(worldX, worldY)
        
        # if selecting nothing, remove panel and selector
        if sim == None:
            self.onSelectNoSim()
        elif sim.type == 'SystemEntity':
            self.onSelectSystemSim(sim)
        elif sim.type == 'TradeEntity':
            pass
        elif sim.type == 'ShipyardEntity':
            self.onSelectShipyardSim(sim)
        elif sim.type == 'ArmadaEntity':
            self.onSelectArmadaSim(sim)
        elif sim.type == 'ArmyEntity':
            self.onSelectArmySim(sim)
        elif sim.type == 'MilitaryInstEntity':
            self.onSelectMilitaryInstSim(sim)
        
    def onSelectArmadaSim(self, sim):
        """Armada Sim selected"""
        # create panel and selector if they do not exist
        self.onSelectNoSim()
        self.armadaInfo = anwp.gui.armadainfo.ArmadaInfoFrame(self, self.game.app)
        self.createSelector2()
        
        # update observer
        if self.armadaInfo <> None and sim <> None:
            self.updateObserver(sim, 'armadaInfo')
    
    def onSelectArmySim(self, sim):
        """Army Sim selected"""
        # create panel and selector if they do not exist
        self.onSelectNoSim()
        self.armyInfo = anwp.gui.armyinfo.ArmyInfoFrame(self, self.game.app)
        self.createSelector2()
        
        # update observer
        if self.armyInfo <> None and sim <> None:
            self.updateObserver(sim, 'armyInfo')
    
    def onSelectSystemSim(self, sim):
        """System Sim selected"""
        # create panel and selector if they do not exist
        self.onSelectNoSim()
        self.systemInfo = anwp.gui.systeminfo.SystemInfoFrame(self, self.game.app)
        self.createSelector()
        
        # update observer
        if self.systemInfo <> None and sim <> None:
            self.updateObserver(sim, 'systemInfo')
    
    def onSelectShipyardSim(self, sim):
        """Shipyard Sim selected"""
        # create panel and selector if they do not exist
        self.onSelectNoSim()
        self.shipyardsInfo = anwp.gui.shipyardsinfo.ShipyardsInfoFrame(self, self.game.app)
        self.createSelector2()
        
        # update observer
        if self.shipyardsInfo <> None and sim <> None:
            self.updateObserver(sim, 'shipyardsInfo')
    
    def onSelectMilitaryInstSim(self, sim):
        """Military Installation Sim selected"""
        # create panel and selector if they do not exist
        self.onSelectNoSim()
        self.militaryinstInfo = anwp.gui.militaryinstinfo.MilitaryInstInfoFrame(self, self.game.app)
        self.createSelector2()
        
        # update observer
        if self.militaryinstInfo <> None and sim <> None:
            self.updateObserver(sim, 'militaryinstInfo')
    
    def onSelectNoSim(self):
        """No Sim Selected clear panels and selector"""
        if self.systemInfo <> None:
            self.systemInfo.destroy()
            self.systemInfo = None
        if self.shipyardsInfo <> None:
            self.shipyardsInfo.destroy()
            self.shipyardsInfo = None
        if self.armadaInfo <> None:
            self.armadaInfo.destroy()
            self.armadaInfo = None
        if self.armyInfo <> None:
            self.armyInfo.destroy()
            self.armyInfo = None
        if self.militaryinstInfo <> None:
            self.militaryinstInfo.destroy()
            self.militaryinstInfo = None
        self.removeSelector()
        self.destroyTempFrames()
    
    def draw(self):
        """Draw standard World information each frame"""
        self.bufferX = (self.appWidth/2) - self.viewX
        self.bufferY = (self.appHeight/2) - self.viewY
        anwp.sl.engine.clear()
        anwp.sl.engine.drawImage(0, 0, self.appWidth, self.appHeight, self.backgroundImage)
        self.drawWarpLines()
        
        # render engine
        anwp.sl.engine.render()
        self.drawSystemInfo()
        self.drawWarpGateInfo()
        self.drawWarpTradeInfo()
    
    def drawSystemInfo(self):
        """System Info are rendered outside system drawcallback due to 
        problems drawing in drawcallback of system"""
        for sim in self.systemSims:
            # draw name
            (x,y) = anwp.sl.engine.worldToScreen(sim.mySystemDict['x'], sim.mySystemDict['y'])
            pyui.desktop.getRenderer().drawText(sim.mySystemDict['name'], 
                                                (x-30,y-70),
                                                sim.color1, self.game.app.planetFont, 
                                                flipped = 1)
            # draw city number
            pyui.desktop.getRenderer().drawText(str(sim.mySystemDict['cities']), 
                                                (x-10,y-6),
                                                sim.color2, self.game.app.systemFont, 
                                                flipped = 1)

    def drawWarpTradeInfo(self):
        """Display any Warp Trade information on a system by system basis"""
        for sim in self.tradeRouteSims:
            if sim.myTradeDict['warpReq'] > 0:
                # trade route requires warp points, display them
                (x,y) = anwp.sl.engine.worldToScreen(sim.posX, sim.posY)
                (offsetX, offsetY) = anwp.sl.engine.worldToScreen(sim.offsetX,sim.offsetY)
                pyui.desktop.getRenderer().drawText('%d' % sim.myTradeDict['warpReq'], 
                                                    (offsetX,offsetY),
                                                    sim.color, self.game.app.systemFont, 
                                                    flipped = 1)

    def drawWarpGateInfo(self):
        """Display any Warp Gate information on a system by system basis"""
        for sim in self.systemSims:
            if sim.mySystemDict['myEmpireID'] == self.game.myEmpireID or anwp.func.globals.diplomacy[self.game.myEmpire['diplomacy'][sim.mySystemDict['myEmpireID']]['diplomacyID']]['trade'] == 1:
                if sim.mySystemDict['availWGC'] > 0:
                    # warp gate(s) at system, draw available capacity
                    (x,y) = anwp.sl.engine.worldToScreen(sim.mySystemDict['x'], sim.mySystemDict['y'])
                    pyui.desktop.getRenderer().drawText('%d' % (sim.mySystemDict['availWGC']-sim.mySystemDict['usedWGC']), 
                                                        (x-62,y+40),
                                                        sim.color1, self.game.app.systemFont, 
                                                        flipped = 1)
                
    def drawWarpLines(self):
        """Draw the System Warp Lines"""
        # draw warp lines
        for item in self.game.warpLines:
            anwp.sl.engine.drawLine(item[0]+self.bufferX, item[1]+self.bufferY, item[2]+self.bufferX, item[3]+self.bufferY, pyui.colors.blue)

    def sendMail(self, empireID, message):
        """Send a message to empire"""
        try:
            serverResult = self.game.server.sendMail(self.game.authKey, empireID, message)
            if serverResult <> 1:
                self.modeMsgBox(serverResult)
            else:
                self.destroyTempFrames()
        except:
            self.modeMsgBox('sendMail->Connection to Server Lost, Login Again')

    def setRegimentOrder(self, regimentList, order):
        """Set Regiment Order"""
        try:
            fleetList = []
            # check to make sure the state is the same for each regiment
            sameState = 1
            state = 0
            for regimentID in regimentList:
                if state == 0:
                    state = self.game.myRegiments[regimentID]['state']
                elif state <> self.game.myRegiments[regimentID]['state']:
                    sameState = 0
                    break
            if sameState == 0:
                self.modeMsgBox('The Regiments you selected cannot be given the same order')
            else:
                for regimentID in regimentList:
                    serverResult = self.game.server.setRegimentOrders(self.game.authKey, regimentList, order)
                    if type(serverResult) == types.StringType:
                        self.modeMsgBox(serverResult)
                        break
                    elif type(serverResult) == types.ListType:
                        # success, update regiment/fleets and refresh
                        (self.game.myRegiments[regimentID], fleetList) = serverResult
                
                # update entire fleet information
                self.getFleetUpdate(fleetList, 1)
                
                self.armyInfo.panel.populate(self.armyInfo.panel.myEmpireDict, self.armyInfo.panel.mySystemDict)
                self.destroyTempFrames()
        except:
            self.modeMsgBox('setRegimentOrder->Connection to Server Lost')

    def swapCaptains(self, shipOneID, shipTwoID):
        """Attempt to swap ship captains"""
        try:
            serverResult = self.game.server.swapCaptains(self.game.authKey, shipOneID, shipTwoID)
            if type(serverResult) == types.StringType:
                self.modeMsgBox(serverResult)
            elif serverResult == 1:
                # success, update and refresh
                myShipOneDict = self.game.myShips[shipOneID]
                myShipTwoDict = self.game.myShips[shipTwoID]
                shipTwoCaptain = myShipTwoDict['captainID']
                myShipTwoDict['captainID'] = myShipOneDict['captainID']
                myShipOneDict['captainID'] = shipTwoCaptain
        except:
            self.modeMsgBox('swapCaptains->Connection to Server Lost')

    def toggleDiplomacy(self):
        """Toggle the viewing of other empire diplomacy panels"""
        if self.viewDiplomacy == 0:
            self.viewDiplomacy = 1
            # setup diplomacy panels
            buffer = 10
            x = buffer
            y = self.mainMenu.height+buffer
            for empireID, empireDict in self.game.allEmpires.iteritems():
                if empireID <> '1' and empireID <> self.game.myEmpireID:
                    myFrame = anwp.gui.empiredip.EmpireDipFrame(self, self.game.app, empireDict, x, y)
                    self.diplomacyPanels.append(myFrame)
                    if (x+myFrame.width+buffer) < (self.appWidth-myFrame.width-buffer):
                        x += (myFrame.width+buffer)
                    else:
                        x = buffer
                        y += (myFrame.height+buffer)
        else:
            # remove diplomacy panels
            self.viewDiplomacy = 0
            for myFrame in self.diplomacyPanels:
                myFrame.destroy()

    def toggleTradeRoutes(self):
        """Toggle the viewing of trade route sims"""
        if self.game.myEmpire['viewTradeRoutes'] == 0:
            self.game.myEmpire['viewTradeRoutes'] = 1
            self.createTradeRouteSims()
        else:
            self.game.myEmpire['viewTradeRoutes'] = 0
            self.removeTradeRouteSims()
    
    def toggleRadar(self):
        """Toggle the viewing of Resources"""
        if self.game.myEmpire['viewRadar'] == 0:
            self.game.myEmpire['viewRadar'] = 1
            self.createRadarSims()
        else:
            self.game.myEmpire['viewRadar'] = 0
            self.removeRadarSims()
    
    def toggleResources(self):
        """Toggle the viewing of Resources"""
        if self.game.myEmpire['viewResources'] == 0:
            self.game.myEmpire['viewResources'] = 1
            self.createResourceSims()
        else:
            self.game.myEmpire['viewResources'] = 0
            self.removeResourceSims()

    def viewSystems(self):
        """Goto Capital System and center camera there"""
        capitalSystem = ''
        cityNum = 0
        for systemID, mySystemDict in self.game.allSystems.iteritems():
            if (mySystemDict['myEmpireID'] == self.game.myEmpireID and
                mySystemDict['cities'] > cityNum):
                cityNum = mySystemDict['cities']
                capitalSystem = mySystemDict['id']
        
        if capitalSystem <> '':
            mySystemDict = self.game.allSystems[capitalSystem]
            self.centerCamera(mySystemDict['x'], mySystemDict['y'])