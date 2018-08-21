# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# system.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a system
# ---------------------------------------------------------------------------
import random
import string

import anwp.war.captain
import anwp.war.ship
import anwp.war.regiment
import anwp.func.root
import city
import industry
import anwp.func.globals

class System(anwp.func.root.Root):
    """A System Represents one Territory Object in ANW.  A System will
    contain Industry, Armies, Fleets, etc.  Systems also have coordinates 
    on the Galactic Map.  These Coordinates decide which Systems are adjacent"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Given System Name
        self.x = int() # x Coordinate of System on Map (Top Left Corner)
        self.y = int() # y Coordinate of System on Map (Top Left Corner)
        self.myEmpireID = str() # Empire ID that owns system
        self.AL = float() # Total System Alloys
        self.EC = float() # Total System Energy Crystals
        self.IA = float() # Total System Arrays
        self.prodCR = float() # Total Produced CR this round
        self.prodAL = float()
        self.prodEC = float()
        self.prodIA = float()
        self.cities = int() # Total Cities within System
        self.citiesUsed = int() # Total Cities Used in Industry within System
        self.militiaStrength = int() # Total Militia Strength in Units
        self.fleetCadets = int() # Total Fleet Cadets Available
        self.armyCadets = int() # Total Army Cadets Available
        self.usedSYC = int() # used Shipyard Capacity this round
        self.availSYC = int() # available shipyard Capacity this round
        self.usedMIC = int() # used Military Installation Capacity this round
        self.availMIC = int() # avail Military Installation Capacity this round
        self.usedWGC = int() # used Warp Gate Capacity this round
        self.availWGC = int() # avail Warp Gate Capacity this round
        self.jammingStrength = int() # Total Jamming Strength of System
        self.radarStrength = int() # Total Radar Strength of System
        self.connectedSystems = list() # List of connected Systems, item = system id
        self.warpGateSystems = list() # List of connected Systems via warp gates (FOR TRADE ONLY NOT USED FOR MOVEMENT)
        self.intelReport = {} # Dict key = empire id, value = report dict
        self.imageFile = str() # image file of System
        self.defaultAttributes = ('id', 'name', 'x', 'y', 'myEmpireID', 'AL', 'EC', 'IA', 'prodCR', 'prodAL', 'prodEC', 'prodIA', 'cities', 'citiesUsed', 'militiaStrength', 'fleetCadets',
                             'armyCadets', 'usedSYC', 'availSYC', 'usedMIC', 'availMIC', 'usedWGC', 'availWGC', 'jammingStrength', 'radarStrength', 'connectedSystems', 'warpGateSystems', 'intelReport', 'imageFile')
        self.setAttributes(args)

        self.myEmpire = None # Actual Empire Object that owns system
        self.myGalaxy = None # Acutal Galaxy Object that owns system
        self.myCities = {} # Dict key = city id, value = city obj
        self.myIndustry = {} # Dict key = industry id, value = industry object
        
        # generate city objects
        self.genMyCities()
        
        # setup intel report
        self.blankIntelReport = {'industryReport':{}, 'shipReport':{}, 'marineReport':{}, 'round':0}

    def resetData(self):
        """Reset system Data on end round"""
        self.prodCR = 0.0
        self.prodAL = 0.0
        self.prodEC = 0.0
        self.prodIA = 0.0
        self.usedSYC = 0
        self.availSYC = 0
        self.usedMIC = 0
        self.availMIC = 0
        self.usedWGC = 0
        self.availWGC = 0
        self.jammingStrength = 0
        self.radarStrength = 0
        for attr in ['AL','EC','IA']:
            self.clearAttribute(attr)
        # reset cities used
        self.citiesUsed = 0
        for id, myIndustry in self.myIndustry.iteritems():
            myIndustryData = self.myGalaxy.industrydata[myIndustry.industrytype]
            self.citiesUsed += myIndustryData.cities

    def setMyEmpire(self, empireObject):
        """Set the Empire Owner object of this System"""
        self.myEmpireID = empireObject.id
        self.myEmpire = empireObject
        self.getImageFileName() # reset the image filename
    
    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this System"""
        self.myGalaxy = galaxyObject
        galaxyObject.systems[self.id] = self
        # reset intel reports
        for empireID in self.myGalaxy.empires.keys():
            self.intelReport[empireID] = self.blankIntelReport
    
    def setSYC(self, amount):
        """Set the Shipyard Capacity for the system"""
        # used should be reset to 0
        self.usedSYC = 0
        self.availSYC = amount
    
    def setFleetCadets(self, amount):
        """Set the current available fleet cadets"""
        # fleet cadets remain available after a round has gone by
        self.fleetCadets += amount
    
    def setMIC(self, amount):
        """Set the Military Installation Capacity for the system"""
        # used should be reset to 0
        self.usedMIC = 0
        self.availMIC = amount
    
    def setWGC(self, amount):
        """Set the Warp Gate Capacity for the system"""
        # used should be reset to 0
        self.usedWGC = 0
        self.availWGC = amount
    
    def setArmyCadets(self, amount):
        """Set the current available army cadets"""
        # army cadets remain available after a round has gone by
        self.armyCadets += amount

    def setJammingStrength(self, amount):
        """Set the current Jamming Strength of System"""
        self.jammingStrength = amount

    def setRadarStrength(self, amount):
        """Set the current Radar Strength of System"""
        self.radarStrength = amount

    def setIntelReports(self):
        """Make sure all Intel Reports are up to date"""
        myIntelReport = {}

        # make sure all Empires have proper intel report
        for empireID in self.myGalaxy.empires.keys():
            radarStrength = 0
            shipJammingStrength = 0
            
            # calculate radar strength of empire to this system
            for systemID in self.connectedSystems:
                mySystem = self.myGalaxy.systems[systemID]
                if mySystem.myEmpireID == empireID:
                    radarStrength += mySystem.radarStrength
            
            # add radar strength of own system
            if self.myEmpireID == empireID:
                radarStrength += self.radarStrength
            
            # go through orbiting ships on this system
            for shipID, myShip in self.myGalaxy.ships.iteritems():
                if myShip.toSystem == self.id:
                    if myShip.empireID == empireID:
                        # ship from this empire, add its radar strength
                        radarStrength += myShip.radar
                    else:
                        # ship not from this empire add its jamming strength to system
                        shipJammingStrength += myShip.jamming
            
            if ((radarStrength > self.jammingStrength+shipJammingStrength) 
                or (self.myEmpireID == empireID and radarStrength > shipJammingStrength)):
                # give this empire a recent intel report of this system
                if myIntelReport == {}:
                    # only generate intel report once
                    myIntelReport = self.genIntelReport()
                    
                self.intelReport[empireID] = myIntelReport

    def getMySystemInfo(self):
        """Return detailed system information, this goes to system owner"""
        dict = self.getSelectedAttr(list(self.defaultAttributes))
        dict['myCities'] = self.getMyDictInfo('myCities')
        dict['myIndustry'] = self.getMyDictInfo('myIndustry')
        return dict
    
    def getAllConnections(self):
        """get all systems connected to this system based on diplomacy type include warp gates
        This is used for ship movement only, not for trade"""
        systemList = []
        # first go through warp connections
        if self.usedWGC < self.availWGC:
            for systemID, mySystem in self.myGalaxy.systems.iteritems():
                if ((mySystem.myEmpireID == self.myEmpireID or anwp.func.globals.diplomacy[self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.myEmpireID].diplomacyID]['alliance'] == 1) 
                    and mySystem.usedWGC < mySystem.availWGC 
                    and mySystem.id <> self.id
                    and mySystem.id not in self.connectedSystems):
                    systemList.append(mySystem.id)
                    
        # then go through basic connections
        for systemID in self.connectedSystems:
            mySystem = self.myGalaxy.systems[systemID]
            if mySystem.myEmpireID == self.myEmpireID or anwp.func.globals.diplomacy[self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.myEmpireID].diplomacyID]['move'] == 1:
                systemList.append(systemID)
        return systemList
    
    def setWarpConnections(self):
        """set warpconnected list of System ID's this system is connected to via warp gates
        This is only used for trade route calculations, not for ship movement"""
        self.warpGateSystems = []
        if self.availWGC > 0:
            for systemID, mySystem in self.myGalaxy.systems.iteritems():
                if ((mySystem.myEmpireID == self.myEmpireID or anwp.func.globals.diplomacy[self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.myEmpireID].diplomacyID]['trade'] == 1) 
                    and mySystem.availWGC > 0 
                    and mySystem.id <> self.id
                    and mySystem.id not in self.connectedSystems):
                    self.warpGateSystems.append(mySystem.id)
    
    def getOtherSystemInfo(self):
        """Return general system information"""
        list = ['id', 'name', 'x', 'y', 'cities', 'connectedSystems', 'myEmpireID', 'intelReport', 'imageFile']
        dict = self.getSelectedAttr(list)
        return dict
    
    def genIntelReport(self):
        """Generate the intel report for system in relation to each empire
        report is a Dict with the key being empire id, then the report
        breaks down into sub dictionarys:
        - industryReport -> dict of industry on planet
        - shipReport -> dict of StarShips on planet
        - marineReport -> dict of Marines on planet
        - round -> round this report was generated"""
        # industry
        dIndustry = {}
        industryKeys = anwp.func.funcs.sortStringList(self.myIndustry.keys())
        i = 0
        for industryID in industryKeys:
            i += 1
            myIndustry = self.myIndustry[industryID]
            myIndustrydata = self.myGalaxy.industrydata[myIndustry.industrytype]
            dIndustry[str(i)] = myIndustrydata.name
        
        # starships
        dShips = {}
        i = 0
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.toSystem == self.id:
                i += 1
                dShips[str(i)] = myShip.name
                    
        # marines
        dMarines = {}
        i = 0
        for regimentID, myRegiment in self.myGalaxy.regiments.iteritems():
            if myRegiment.fromSystem == self.id:
                i += 1
                dMarines[str(i)] = myRegiment.name
        
        myIntelReport = {'industryReport':dIndustry, 'shipReport':dShips, 'marineReport':dMarines, 'round':self.myGalaxy.currentRound}
        return myIntelReport
        
    def getImageFileName(self):
        """Generate the image filename depends on:
        - System Color1, Color2, CityNum"""
        # decide on system look (4 point, 6 point, 8 point star)
        x = 0
        if self.cities <= 10:
            x = 4
        elif self.cities <= 15:
            x = 6
        else:
            x = 8
        
        # create image file
        self.imageFile = 'sys_%s_%s_%s' % (x, self.myEmpire.color1, self.myEmpire.color2)
        
    def genMyCities(self):
        """Take the cities total and use it to generate actual city objects
        to place under the System object"""
        i = 1
        while i <= self.cities:
            resource = 'CR'
            id = self.getNextID(self.myCities)
            d = {'id':id, 'resourceFocus':resource, 'state':1, 'name':'City %s' % id}
            thisCity = city.City(d)
            self.myCities[id] = thisCity
            i += 1
    
    def checkResources(self, reqCR, reqAL, reqEC, reqIA):
        """Checks if given required resources are available"""
        try:
            if (self.myEmpire.CR >= reqCR and
                    self.AL >= reqAL and
                    self.EC >= reqEC and
                    self.IA >= reqIA):
                return 1
            else:
                return 'You Require: (CR:%d),(AL:%d),(EC:%d),(IA:%d) Resources' % (reqCR, reqAL, reqEC, reqIA)
        except:
            return 'system->checkResources error'
    
    def payResources(self, reqCR, reqAL, reqEC, reqIA):
        """Pay the required resources, take from system and empire"""
        try:
            self.myEmpire.CR -= reqCR
            self.AL -= reqAL
            self.myEmpire.AL -= reqAL
            self.EC -= reqEC
            self.myEmpire.EC -= reqEC
            self.IA -= reqIA
            self.myEmpire.IA -= reqIA
            return 1
        except:
            return 'system->payResources error'

    def modifyResource(self, resource, amount):
        """Set the specified resource (AL, EC, IA) by the amount specified"""
        systemResource = getattr(self, resource)
        empireResource = getattr(self.myEmpire, resource)
        setattr(self, resource, systemResource + amount)
        setattr(self.myEmpire, resource, empireResource + amount)

    def addIndustry(self, amount, industrytype):
        """Build Industry in this System, 
        input: amount - > amount of industry (int)
               industryType -> type of industry (id)
        DONE ON ROUND END
        """
        try:
            # add industry
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            i = 0
            while i < amount:
                id = self.getNextID(self.myIndustry)
                d = {'id':id, 'industrytype':industrytype, 'state':1}
                thisIndustry = industry.Industry(d)
                self.myIndustry[id] = thisIndustry
                i += 1
            return 'ADDED %d %s ON:%s' % (amount, industryDataObj.name, self.name)
        except:
            return 'system->addIndustry error'
    
    def addRegiment(self, amount, empireID, regimentTypeID):
        """Add Regiments to this System from Military Installations, 
        input: amount - > number of regiments to add (int)
               empireID -> empire id
               regimentTypeID -> regiment type id
        DONE ON ROUND END
        """
        try:
            # reference objects required
            myEmpire = self.myGalaxy.empires[empireID]
            myRegimentData = self.myGalaxy.regimentdata[regimentTypeID]
            
            i = 0
            while i < amount:
                # create the regiment
                myRegiment = self.myGalaxy.setNewRegiment(empireID, self.id, regimentTypeID, 'Marine')
                if self.armyCadets > 0:
                    self.armyCadets -= 1
                    myRegiment.addGlory(5,1)
                i += 1
            return 'ADDED %d %s ON:%s' % (amount, myRegiment.name, self.name)
        except:
            return 'system->addRegiment error'
    
    def addShip(self, amount, empireID, shipDesignID):
        """Add Ships to this System from Shipyards, 
        input: amount - > number of ships to add (int)
               empireID -> empire id
               shipDesignID -> ship design id
        DONE ON ROUND END
        """
        try:
            # reference objects required
            myEmpire = self.myGalaxy.empires[empireID]
            myShipDesign = myEmpire.shipDesigns[shipDesignID]
            
            i = 0
            while i < amount:
                # first create captain
                id = self.myGalaxy.getNextID(self.myGalaxy.captains)
                name = self.myGalaxy.getCaptainName()
                myCaptain = anwp.war.captain.Captain({'id':id, 'name':name})
                myCaptain.setMyEmpire(myEmpire)
                if self.fleetCadets > 0:
                    self.fleetCadets -= 1
                    myCaptain.addExperience(100)
                
                # create the ship
                shipID = self.myGalaxy.getNextID(self.myGalaxy.ships)
                myShip = anwp.war.ship.Ship({'id':shipID, 'fromSystem':self.id, 'empireID':empireID})
                myShip.setMyCaptain(myCaptain)
                myShip.setMyGalaxy(self.myGalaxy)
                myShip.setMyDesign(myShipDesign)
                myShip.setMyStatus()
                i += 1
            return myShip
        except:
            return 'system->addShip error'
    
    def payForAddIndustry(self, amount, industrytype):
        """Actually pay to add industry, (pay in resources and citiesUsed)"""
        try:
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            self.citiesUsed += (industryDataObj.cities * amount)
            return self.payResources(industryDataObj.costCR * amount,
                                     industryDataObj.costAL * amount,
                                     industryDataObj.costEC * amount,
                                     industryDataObj.costIA * amount)
        except:
            return 'system->payForAddIndustry error'
    
    def payForAddRegiment(self, amount, typeID):
        """Actually pay for regiment in resources and MIC"""
        try:
            myRegimentData = self.myGalaxy.regimentdata[typeID]
            self.usedMIC += 100 * amount
            return self.payResources(myRegimentData.costCR * amount,
                                     myRegimentData.costAL * amount,
                                     myRegimentData.costEC * amount,
                                     myRegimentData.costIA * amount)
        except:
            return 'system->payForAddRegiment error'
    
    def payForAddShip(self, amount, shipDesignID):
        """Actually pay for star ship in resources and SYC"""
        try:
            myShipDesign = self.myEmpire.shipDesigns[shipDesignID]
            self.usedSYC += myShipDesign.getSYCRequired() * amount
            return self.payResources(myShipDesign.costCR * amount,
                                     myShipDesign.costAL * amount,
                                     myShipDesign.costEC * amount,
                                     myShipDesign.costIA * amount)
        except:
            return 'system->payForAddShip error'
    
    def payForRestoreRegiment(self, regimentID):
        """Actually pay for restoring regiment in resources and MIC"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            [CR,AL,EC,IA] = myRegiment.restoreCost
            self.usedMIC += (100 - myRegiment.strength)
            return self.payResources(CR,AL,EC,IA)
        except:
            return 'system->payForRestoreRegiment error'
    
    def payForUpgradeRegiment(self, regimentID):
        """pay for upgrading regiment in resources and MIC"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            [BV,CR,AL,EC,IA] = myRegiment.getMyValue()
            self.usedMIC += 50
            return self.payResources(CR, AL, EC, IA)
        except:
            return 'system->payForUpgradeRegiment error'
    
    def payForRepairStarship(self, shipID):
        """Actually pay for starship repair in resources and SYC"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            [CR,AL,EC,IA] = myShip.repairCost
            self.usedSYC += myShip.getRepairCapacity()
            return self.payResources(CR,AL,EC,IA)
        except:
            return 'system->payForRepairStarship error'
    
    def payForUpgradeStarship(self, shipID, newDesignID):
        """Actually pay for starship upgrade in resources and SYC"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            myEmpire = self.myGalaxy.empires[myShip.empireID]
            newDesign = myEmpire.shipDesigns[newDesignID]
            [CR,AL,EC,IA,capacity] = myShip.myDesign.getUpgradeCost(newDesign)
            self.usedSYC += capacity
            return self.payResources(CR,AL,EC,IA)
        except:
            return 'system->payForUpgradeStarship error'
    
    def processGroundInvasion(self):
        """An enemy Army has invaded this system, process this Ground Invasion"""
        try:
            engage = 1
            stats = []
            empireList = []
            empireList.append(self.myEmpireID)
            # ground battle stats
            attackMarines = 0
            attackLosses = 0
            defMilitia = 0
            defMarines = 0
            defLosses = 0
            
            # first create militia regiments if applicable
            for industryID, myIndustry in self.myIndustry.iteritems():
                if self.myGalaxy.industrydata[myIndustry.industrytype].abr[1:] == 'MF':
                    # create militia regiments
                    militiaNum = int(self.myGalaxy.industrydata[myIndustry.industrytype].output)
                    for i in range(militiaNum):
                        # create militia regiment
                        myRegiment = self.myGalaxy.setNewRegiment(self.myEmpireID, self.id, anwp.func.globals.militiaType[militiaNum], 'Militia')
                        defMilitia += 1
            
            # setup stats
            for regimentID in self.myGalaxy.regiments.keys():
                myRegiment = self.myGalaxy.regiments[regimentID]
                if ((myRegiment.state == 1 and myRegiment.fromSystem == self.id) or
                         (myRegiment.state == 4 and myRegiment.toSystem == self.id)):
                    # regiment is on system, check if its an enemy
                    if (myRegiment.empireID <> self.myEmpireID and
                        anwp.func.globals.diplomacy[self.myGalaxy.empires[myRegiment.empireID].diplomacy[self.myEmpireID].diplomacyID]['invade'] == 1):
                        attackMarines += 1
                    else:
                        defMarines += 1
            
            # loop through all regiments that are attacking/defending system until battle resolved
            while engage == 1:
                myRegiments = []
                enemyRegiments = []
                enemyRegimentCount = {}
                # sort all regiments in galaxy into either defending, attacking, or neither
                for regimentID in self.myGalaxy.regiments.keys():
                    myRegiment = self.myGalaxy.regiments[regimentID]
                    if ((myRegiment.state == 1 and myRegiment.fromSystem == self.id) or
                        (myRegiment.state == 4 and myRegiment.toSystem == self.id)):
                        # regiment is on system, check if its an enemy
                        if (myRegiment.empireID <> self.myEmpireID and
                            anwp.func.globals.diplomacy[self.myGalaxy.empires[myRegiment.empireID].diplomacy[self.myEmpireID].diplomacyID]['invade'] == 1):
                            enemyRegiments.append(myRegiment.id)
                            if myRegiment.empireID not in enemyRegimentCount.keys():
                                enemyRegimentCount[myRegiment.empireID] = 1
                            else:
                                enemyRegimentCount[myRegiment.empireID] += 1
                        else:
                            myRegiments.append(myRegiment.id)
                        # add empire to empireList for later mailing
                        if myRegiment.empireID not in empireList:
                            empireList.append(myRegiment.empireID)
    
                # go through each regiment and match up
                count = 0
                myDeathCount = 0
                enemyDeathCount = 0
                for myRegimentID in myRegiments:
                    try:
                        myRegiment = self.myGalaxy.regiments[myRegimentID]
                        enemyRegiment = self.myGalaxy.regiments[enemyRegiments[count]]
                        (result, description) = myRegiment.engageRegiment(enemyRegiment)
                        stats.append(description)
                        if result == 1:
                            enemyDeathCount += 1
                            enemyRegiment.destroyMe()
                        else:
                            myDeathCount += 1
                            myRegiment.destroyMe()
                    except:
                        # no more enemy regiments to match up this iteration
                        break
                    count += 1
                
                # check if all regiments gone from either side
                if len(enemyRegiments) == enemyDeathCount:
                    s = '%s INVASION has been defended' % self.name
                    engage = 0
                    break
                elif len(myRegiments) == myDeathCount:
                    # system taken over, give to largest enemy regiment
                    empireKeys = anwp.func.funcs.sortDictByValue(enemyRegimentCount,True)
                    enemyEmpire = self.myGalaxy.empires[empireKeys[0]]
                    s = '%s has been taken over by: %s' % (self.name, enemyEmpire.name)
                    self.setMyEmpire(enemyEmpire)
                    # remove all trade routes associated with this system
                    for tradeRouteID in self.myGalaxy.tradeRoutes.keys():
                        myTradeRoute = self.myGalaxy.tradeRoutes[tradeRouteID]
                        (systemFrom, systemTo, type) = string.split(myTradeRoute.id, '-')
                        if self.id in [systemFrom, systemTo]:
                            # remove trade route
                            result = self.myGalaxy.cancelTradeRoute(tradeRouteID, self.myGalaxy.currentRound)
                    engage = 0
                    break
            
            # remove all militia regiments
            for regimentID in self.myGalaxy.regiments.keys():
                myRegiment = self.myGalaxy.regiments[regimentID]
                if myRegiment.myRegimentData.abr[1:] == 'ML':
                    self.myGalaxy.removeRegiment(regimentID)
            
            # calculate stats
            defMarines = defMarines - defMilitia
            stats.append('')
            stats.append('==========================================================')
            stats.append('BATTLE RESULTS:')
            stats.append('==========================================================')
            stats.append('Attacking Marine Regiments:  %d' % attackMarines)
            stats.append('Defending Militia Regiments: %d' % defMilitia)
            stats.append('Defending Marine Regiments:  %d' % defMarines)
            stats.append('==========================================================')
            stats.append('Attacking Marine Regiment Losses: %d' % attackLosses)
            stats.append('Defending Total Regiment Losses:  %d' % defLosses)
            stats.append('==========================================================')
            
            # email stats of invasion to each empire
            for empireID in empireList:
                dMail = {'fromEmpire':empireID, 'round':self.myGalaxy.currentRound+1,
                         'messageType':'army', 'subject':s, 'body':str(stats)}
                myEmpire = self.myGalaxy.empires[empireID]
                myEmpire.genMail(dMail)
            
            # return result of invasion to galaxy
            return s
        except:
            return 'system->processGroundInvasion error: %s' % self.name
    
    def refundAddIndustry(self, amount, industrytype):
        """refund adding industry, (pay in resources and citiesUsed)"""
        try:
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            self.citiesUsed -= (industryDataObj.cities * amount)
            return self.payResources(-1 * industryDataObj.costCR * amount,
                                     -1 * industryDataObj.costAL * amount,
                                     -1 * industryDataObj.costEC * amount,
                                     -1 * industryDataObj.costIA * amount)
        except:
            return 'system->refundAddIndustry error'

    def refundAddRegiment(self, amount, typeID):
        """refund for adding regiment in resources and MIC"""
        try:
            myRegimentData = self.myGalaxy.regimentdata[typeID]
            self.usedMIC -= 100 * amount
            return self.payResources(-1 * myRegimentData.costCR * amount,
                                     -1 * myRegimentData.costAL * amount,
                                     -1 * myRegimentData.costEC * amount,
                                     -1 * myRegimentData.costIA * amount)
        except:
            return 'system->refundAddRegiment error'

    def refundRestoreRegiment(self, regimentID):
        """refund for restoring regiment in resources and MIC"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            [CR,AL,EC,IA] = myRegiment.restoreCost
            self.usedMIC -= (100 - myRegiment.strength)
            return self.payResources(-1*CR, -1*AL, -1*EC, -1*IA)
        except:
            return 'system->refundRestoreRegiment error'
    
    def refundUpgradeRegiment(self, regimentID):
        """refund for upgrading regiment in resources and MIC"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            [BV,CR,AL,EC,IA] = myRegiment.getMyValue()
            self.usedMIC -= 50
            return self.payResources(-1*CR, -1*AL, -1*EC, -1*IA)
        except:
            return 'system->refundUpgradeRegiment error'
    
    def refundRepairStarship(self, shipID):
        """refund for repairing ship in resources and SYC"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            [CR,AL,EC,IA] = myShip.repairCost
            self.usedSYC -= myShip.getRepairCapacity()
            return self.payResources(-1*CR,-1*AL,-1*EC,-1*IA)
        except:
            return 'system->refundRepairStarship error'

    def refundUpgradeStarship(self, shipID, newDesignID):
        """refund for upgrading ship in resources and SYC"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            myEmpire = self.myGalaxy.empires[myShip.empireID]
            newDesign = myEmpire.shipDesigns[newDesignID]
            [CR,AL,EC,IA,capacity] = myShip.myDesign.getUpgradeCost(newDesign)
            self.usedSYC -= capacity
            return self.payResources(-1*CR,-1*AL,-1*EC,-1*IA)
        except:
            return 'system->refundUpgradeStarship error'

    def refundAddShip(self, amount, shipDesignID):
        """refund for adding star ship in resources and SYC"""
        try:
            myShipDesign = self.myEmpire.shipDesigns[shipDesignID]
            self.usedSYC -= myShipDesign.getSYCRequired() * amount
            return self.payResources(-1 * myShipDesign.costCR * amount,
                                     -1 * myShipDesign.costAL * amount,
                                     -1 * myShipDesign.costEC * amount,
                                     -1 * myShipDesign.costIA * amount)
        except:
            return 'system->refundAddShip error'
        
    def removeIndustry(self, industryID):
        """Remove Industry in this System, 
        input: industryID -> Industry ID (ID of system.myIndustry)
        DONE ON ROUND END
        """
        try:
            thisIndustry = self.myIndustry[industryID]
            industryDataObj = self.myGalaxy.industrydata[thisIndustry.industrytype]
            del self.myIndustry[industryID]
            self.citiesUsed -= industryDataObj.cities
            return 'REMOVED 1 %s ON:%s' % (industryDataObj.name, self.name)
        except:
            return 'system->removeIndustry error'
    
    def restoreRegiment(self, regimentID):
        """Restore the strength of a regiment to 100%
        DONE ON ROUND END"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            myRegiment.strength = 100
            return 'RESTORED %s to 100%s strength' % (myRegiment.name, '%')
        except:
            return 'system->restoreRegiment error'
    
    def repairStarship(self, shipID):
        """Repair Starship to 100%
        DONE ON ROUND END"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            myCaptain = myShip.myCaptain
            myDesign = myShip.myDesign
            # create new fixed ship with same attributes
            newShip = anwp.war.ship.Ship(myShip.getMyInfoAsDict())
            newShip.setMyCaptain(myCaptain)
            newShip.setMyGalaxy(self.myGalaxy)
            newShip.setMyDesign(myDesign)
            # pass over any quadrant info to new ship
            newShip.setMyDictInfo(myShip.getMyShipInfo())
            newShip.setRepairCost()
            newShip.setMyStrength()
            myShip = None
            
            return 'REPAIRED %s to 100%s strength' % (newShip.name, '%')
        except:
            return 'system->repairStarship error'
    
    def upgradeStarship(self, shipID, newDesignID):
        """Upgrade the Starship to the new Design
        DONE ON ROUND END"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            myEmpire = self.myGalaxy.empires[myShip.empireID]
            newDesign = myEmpire.shipDesigns[newDesignID]
            myCaptain = myShip.myCaptain
            # create new fixed ship with same attributes
            newShip = anwp.war.ship.Ship(myShip.getMyInfoAsDict())
            newShip.setMyCaptain(myCaptain)
            newShip.setMyGalaxy(self.myGalaxy)
            newShip.setMyDesign(newDesign)
            newShip.setRepairCost()
            newShip.setMyStrength()
            myShip = None
            
            return 'UPGRADED %s to TYPE = %s' % (newShip.name, newShip.myDesign.name)
        except:
            return 'system->upgradeStarship error'
    
    def upgradeRegiment(self, regimentID):
        """Upgrade the Regiment to the new type
        DONE ON ROUND END"""
        try:
            # regiment can be upgraded
            myRegiment = self.myGalaxy.regiments[regimentID]
            myRegiment.upgradeMe()
            return 'UPGRADED %s TO:%s ON:%s' % (myRegiment.name, myRegiment.myRegimentData.name, self.name)
        except:
            return 'system->upgradeRegiment error'
    
    def upgradeIndustry(self, industryID):
        """Upgrade Industry in this System, 
        input: industryID -> Industry ID (ID of system.myIndustry)
        DONE ON ROUND END
        """
        try:
            # industry can be upgraded
            myIndustry = self.myIndustry[industryID]
            myIndustryData = self.myGalaxy.industrydata[myIndustry.industrytype]
            myUpgradedIndustryDataID = str(int(myIndustryData.id) + 1)
            # change industry type to new type
            myIndustry.industrytype = myUpgradedIndustryDataID
            return 'UPGRADED 1 %s TO:%s ON:%s' % (myIndustryData.name, self.myGalaxy.industrydata[myUpgradedIndustryDataID].name, self.name)
        except:
            return 'system->removeIndustry error'
    
    def validateAddIndustry(self, amount, industrytype):
        """Validate if industry can be added, return 1=pass, string=fail"""
        try:
            if amount == 0:
                return 'You cannot add 0 Industry'
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            # check if enough cities available
            if (industryDataObj.cities * amount) > (self.cities - self.citiesUsed):
                return 'Not enough Cities to build %s on %s' % (industryDataObj.name, self.name)
            else:
                # check if enough resources available
                return self.checkResources(industryDataObj.costCR * amount, industryDataObj.costAL * amount, 
                                           industryDataObj.costEC * amount, industryDataObj.costIA * amount)
        except:
            return 'system->validateAddIndustry error'
    
    def validateAddRegiment(self, amount, typeID):
        """Validate if regiment can be added, return 1=pass, string=fail"""
        try:
            if amount == 0:
                return 'You cannot add 0 Regiments'
            myRegimentData = self.myGalaxy.regimentdata[typeID]
            # check if enough military installation space available
            spaceRequired = 100*amount # one new regiment takes 100% refit points
            if (self.availMIC-self.usedMIC) < spaceRequired:
                return 'Not have enough Military Installation Capacity to build %d %s on %s' % (amount, myRegimentData.name, self.name)
            
            # check if enough resources available
            return self.checkResources(myRegimentData.costCR * amount, myRegimentData.costAL * amount, 
                                       myRegimentData.costEC * amount, myRegimentData.costIA * amount)
        except:
            return 'system->validateAddRegiment error'
    
    def validateAddShip(self, amount, shipDesignID):
        """Validate if ship can be added, return 1=pass, string=fail"""
        try:
            if amount == 0:
                return 'You cannot add 0 Ships'
            myShipDesign = self.myEmpire.shipDesigns[shipDesignID]
            # check if enough shipyard space available
            spaceRequired = myShipDesign.getSYCRequired()*amount
            if (self.availSYC-self.usedSYC) < spaceRequired:
                return 'Not have enough Shipyard Capacity to build %d %s on %s' % (amount, myShipDesign.name, self.name)
            
            # check if enough resources available
            return self.checkResources(myShipDesign.costCR * amount, myShipDesign.costAL * amount, 
                                       myShipDesign.costEC * amount, myShipDesign.costIA * amount)
        except:
            return 'system->validateAddShip error'
    
    def validateRestoreRegiment(self, regimentID):
        """Validate if regiment can be restored, return 1=pass, string=fail"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            if myRegiment.empireID <> self.myEmpireID:
                return 'regiment is not owned by system'
            # check if regiment has 100 percent strength
            if myRegiment.strength == 100:
                return 'regiment already at 100% strength'
            # check if enough military installation space available
            spaceRequired = 100 - myRegiment.strength
            if (self.availMIC-self.usedMIC) < spaceRequired:
                return 'Not have enough Military Installation Capacity to restore %s to 100%s' % (myRegiment.name, '%')
            
            # check if enough resources available
            [CR,AL,EC,IA] = myRegiment.restoreCost
            return self.checkResources(CR,AL,EC,IA)
        except:
            return 'system->validateRestoreRegiment error'
    
    def validateUpgradeRegiment(self, regimentID):
        """Validate if regiment can be upgraded, return 1=pass, string=fail"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            if myRegiment.empireID <> self.myEmpireID:
                return 'regiment is not owned by system'
            # check if regiment has 100 percent strength
            if myRegiment.strength <> 100:
                return 'regiment needs to be at 100% strength to be upgraded'
            # check if empire has the technology to upgrade regiment
            typeID = myRegiment.getMyNextUpgrade()
            if typeID == -1:
                return 'regiment cannot be upgraded any further'
            else:
                myRegimentData = self.myGalaxy.regimentdata[typeID]
                myTech = self.myEmpire.techTree[myRegimentData.techReq]
                if myTech.complete == 0:
                    return '%s must be researched before Regiment can be upgraded' % myTech.name
            
            # check if enough military installation space available
            spaceRequired = 50
            if (self.availMIC-self.usedMIC) < spaceRequired:
                return 'You need 50 capacity points to upgrade regiment'
            # check if enough resources available
            [BV,CR,AL,EC,IA] = myRegiment.getMyValue()
            return self.checkResources(CR,AL,EC,IA)
       
        except:
            return 'system->validateUpgradeRegiment error'
    
    def validateRepairStarship(self, shipID):
        """Validate if ship can be repaired, return 1=pass, string=fail"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            if myShip.empireID <> self.myEmpireID:
                return 'ship is not owned by system'
            # check if ship is already at 100% strength
            if myShip.strength == 100:
                return 'ship already at 100% strength'
            # check if enough shipyard space available
            spaceRequired = myShip.getRepairCapacity()
            if (self.availSYC-self.usedSYC) < spaceRequired:
                return 'Not have enough Shipyard Capacity to repair %s on %s' % (myShip.name, self.name)

            # check if enough resources available
            [CR,AL,EC,IA] = myShip.repairCost
            return self.checkResources(CR,AL,EC,IA)
            
        except:
            return 'system->validateRepairStarship error'
    
    def validateUpgradeStarship(self, shipID, newDesignID):
        """Validate if ship can be upgraded, return 1=pass, string=fail"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            myEmpire = self.myGalaxy.empires[myShip.empireID]
            newDesign = myEmpire.shipDesigns[newDesignID]
            if myShip.empireID <> self.myEmpireID:
                return 'ship is not owned by system'
            # check if ship is not at 100% strength
            if myShip.strength <> 100:
                return 'ship must be at 100% strength to be upgraded'
            # check if new design hull different
            if myShip.myDesign.myShipHull.id <> newDesign.myShipHull.id:
                return 'ship hulls different'
            # check if enough shipyard space available
            [CR,AL,EC,IA,capacity] = myShip.myDesign.getUpgradeCost(newDesign)
            if (self.availSYC-self.usedSYC) < capacity:
                return 'Not have enough Shipyard Capacity to upgrade %s TO %s' % (myShip.name, newDesign.name)
            # check if enough resources available
            return self.checkResources(CR,AL,EC,IA)
            
        except:
            return 'system->validateUpgradeStarship error'
    
    def validateUpgradeIndustry(self, industryID):
        """Can industry currently be upgraded, return 1 if yes, string if no"""
        try:
            myIndustry = self.myIndustry[industryID]
            myIndustryData = self.myGalaxy.industrydata[myIndustry.industrytype]
            # check if industry already being upgraded this turn
            for orderID, myOrder in self.myEmpire.industryOrders.iteritems():
                if (myOrder.round == self.myGalaxy.currentRound and 
                    myOrder.type == 'Upgrade Industry' and
                    myOrder.value == industryID and
                    myOrder.system == self.id):
                    return 'Industry is already being upgraded this turn'
            
            # check if industry already fully upgraded
            if myIndustryData.name[0] == 'I':
                return 'Industry cannot be upgraded any further'
            else:
                myUpgradedIndustryDataID = str(int(myIndustryData.id) + 1)
                myUpgradedIndustryData = self.myGalaxy.industrydata[myUpgradedIndustryDataID]
                myTech = self.myEmpire.techTree[myUpgradedIndustryData.techReq]
                if myTech.complete == 0:
                    return 'Technology must be researched before Industry can be upgraded'
                else:
                    return self.checkResources(myUpgradedIndustryData.costCR-myIndustryData.costCR, myUpgradedIndustryData.costAL-myIndustryData.costAL,
                                               myUpgradedIndustryData.costEC-myIndustryData.costEC, myUpgradedIndustryData.costIA-myIndustryData.costIA)
        except:
            return 'system->validateUpgradeIndustry error'
    
    def payForUpgradeIndustry(self, industryID):
        """Pay to Upgrade Industry"""
        try:
            # calc required resources
            myIndustry = self.myIndustry[industryID]
            myIndustryData = self.myGalaxy.industrydata[myIndustry.industrytype]
            myUpgradedIndustryDataID = str(int(myIndustryData.id) + 1)
            myUpgradedIndustryData = self.myGalaxy.industrydata[myUpgradedIndustryDataID]
            return self.payResources(myUpgradedIndustryData.costCR-myIndustryData.costCR, myUpgradedIndustryData.costAL-myIndustryData.costAL,
                                               myUpgradedIndustryData.costEC-myIndustryData.costEC, myUpgradedIndustryData.costIA-myIndustryData.costIA)
        except:
            return 'system->payForUpgradeIndustry error'

    def refundUpgradeIndustry(self, industryID):
        """Refund Upgrade Industry"""
        try:
            # calc required resources
            myIndustry = self.myIndustry[industryID]
            myIndustryData = self.myGalaxy.industrydata[myIndustry.industrytype]
            myUpgradedIndustryDataID = str(int(myIndustryData.id) + 1)
            myUpgradedIndustryData = self.myGalaxy.industrydata[myUpgradedIndustryDataID]
            return self.payResources(-1*(myUpgradedIndustryData.costCR-myIndustryData.costCR), -1*(myUpgradedIndustryData.costAL-myIndustryData.costAL),
                                               -1*(myUpgradedIndustryData.costEC-myIndustryData.costEC), -1*(myUpgradedIndustryData.costIA-myIndustryData.costIA))
        except:
            return 'system->refundUpgradeIndustry error'
    
    def addCity(self, resourceFocus):
        """Build City in this System, 
        input: resourceFocus -> ('CR', 'AL', 'IA', 'EC')
        DONE ON ROUND END
        """
        try:
            id = self.getNextID(self.myCities)
            d = {'id':id, 'resourceFocus':resourceFocus, 'state':1, 'name':'City %s' % id}
            thisCity = city.City(d)
            self.myCities[id] = thisCity
            self.cities += 1
            return 'ADD 1 CITY TO:%s' % self.name
        except:
            return 'system->addCity error'
    
    def validateAddCity(self):
        """Validate if city can be added, return 1=pass, string=fail"""
        try:
            # calc required resources
            reqCR = anwp.func.globals.addCityResource['CR']
            reqAL = anwp.func.globals.addCityResource['AL']
            reqEC = anwp.func.globals.addCityResource['EC']
            reqIA = anwp.func.globals.addCityResource['IA']
            if self.myEmpire.CR >= reqCR and self.AL >= reqAL and self.EC >= reqEC and self.IA >= reqIA:
                return 1
            else:
                return 'You Require: (CR:%d),(AL:%d),(EC:%d),(IA:%d) to add City' % (reqCR, reqAL, reqEC, reqIA)
        except:
            return 'system->validateAddCity error'
    
    def payForAddCity(self):
        """Actually pay to add city"""
        try:
            # calc required resources
            return self.payResources(anwp.func.globals.addCityResource['CR'],
                                     anwp.func.globals.addCityResource['AL'],
                                     anwp.func.globals.addCityResource['EC'],
                                     anwp.func.globals.addCityResource['IA'])
        except:
            return 'system->payForAddCity error'
    
    def refundAddCity(self):
        """refund add city"""
        try:
            # calc required resources
            return self.payResources(-1 * anwp.func.globals.addCityResource['CR'],
                                     -1 * anwp.func.globals.addCityResource['AL'],
                                     -1 * anwp.func.globals.addCityResource['EC'],
                                     -1 * anwp.func.globals.addCityResource['IA'])
        except:
            return 'system->refundAddCity error'
    
    def updateCityResource(self, cityID, resourceFocus):
        """Update City Resource in this System, 
        input: resourceFocus -> ('CR', 'AL', 'IA', 'EC')
               cityID -> id of city
        DONE ON ROUND END
        """
        try:
            myCity = self.myCities[cityID]
            myCity.resourceFocus = resourceFocus
            if self.myGalaxy.currentRound > 1:
                myCity.state = 0
            return 'CHANGED City-%s RESOURCE TO:%s ON:%s' % (cityID, resourceFocus, self.name)
        except:
            return 'system->updateCityResource error'
    
    def validateUpdateCity(self, value):
        """Validate if city resource can be updated, return 1=pass, string=fail"""
        try:
            # check if trying to update to same resource type
            (cityNum, resource) = string.split(value, '-')
            myCity = self.myCities[cityNum]
            if myCity.resourceFocus == resource:
                return 'You are trying to update City to its current Resource:%s' % resource
            # check if another order in place for this city resource combo
            for id, myIndustryOrder in self.myEmpire.industryOrders.iteritems():
                if (myIndustryOrder.round == self.myGalaxy.currentRound and 
                    myIndustryOrder.value == value and myIndustryOrder.system == self.id):
                    return 'You already have an industry order to convert City-%s ->%s' % (cityNum, resource)
            if self.myGalaxy.currentRound > 1:
                # calc required resources
                reqCR = anwp.func.globals.updateCityResource['CR']
                reqAL = anwp.func.globals.updateCityResource['AL']
                reqEC = anwp.func.globals.updateCityResource['EC']
                reqIA = anwp.func.globals.updateCityResource['IA']
                if self.myEmpire.CR >= reqCR and self.AL >= reqAL and self.EC >= reqEC and self.IA >= reqIA:
                    return 1
                else:
                    return 'You Require: (CR:%d),(AL:%d),(EC:%d),(IA:%d) to update City Resource' % (reqCR, reqAL, reqEC, reqIA) 
            else:
                # allow free updates in first round only
                return 1
        except:
            return 'system->validateUpdateCity error'
    
    def payForUpdateCity(self):
        """Actually pay to update city resource focus"""
        try:
            if self.myGalaxy.currentRound > 1:
                # calc required resources
                return self.payResources(anwp.func.globals.updateCityResource['CR'],
                                         anwp.func.globals.updateCityResource['AL'],
                                         anwp.func.globals.updateCityResource['EC'],
                                         anwp.func.globals.updateCityResource['IA'])
            else:
                # allow free updates in first round only
                return 1
        except:
            return 'system->payForUpdateCity error'
    
    def refundUpdateCity(self):
        """refund add city"""
        try:
            if self.myGalaxy.currentRound > 1:
                # calc required resources
                return self.payResources(-1 * anwp.func.globals.updateCityResource['CR'],
                                         -1 * anwp.func.globals.updateCityResource['AL'],
                                         -1 * anwp.func.globals.updateCityResource['EC'],
                                         -1 * anwp.func.globals.updateCityResource['IA'])
            else:
                return 1
        except:
            return 'system->refundUpdateCity error'
    
    def genWealth(self):
        """Generate Wealth for System, done once each round, wealth consists of
        Credits(CR) - these go to the System Empire Owner
        (AL)(EC)(IA) - these resources are added to the systems totals
        (prodCR, prodAL, prodEC, prodIA) are all updated, these declare how much was
        generated for each resource by this system this round"""
        try:
            dResources = {'CR':0, 'AL':0, 'EC':0, 'IA':0}
            dFactor = {'CR':1, 'AL':1, 'EC':1, 'IA':1}
            # store number of cities that are producing each resource
            for cityID, myCity in self.myCities.iteritems():
                if (myCity.state == 1 or self.myGalaxy.currentRound == 1):
                    dResources[myCity.resourceFocus] += 1
                else:
                    # set city state back to 1
                    myCity.state = 1
            
            # store factors of any industry on system
            for industryID, myIndustry in self.myIndustry.iteritems():
                if myIndustry.state == 1:
                    myIndustryType = self.myGalaxy.industrydata[myIndustry.industrytype]
                    if myIndustryType.abr[1:3] == 'CC':
                        dFactor['CR'] += myIndustryType.output
                    elif myIndustryType.abr[1:3] == 'AF':
                        dFactor['AL'] += myIndustryType.output
                    elif myIndustryType.abr[1:3] == 'CM':
                        dFactor['EC'] += myIndustryType.output
                    elif myIndustryType.abr[1:3] == 'SS':
                        dFactor['IA'] += myIndustryType.output
            
            # create resource wealth
            self.prodCR = dResources['CR'] * anwp.func.globals.cityCRGen * dFactor['CR']
            self.prodAL = dResources['AL'] * anwp.func.globals.cityALGen * dFactor['AL']
            self.prodEC = dResources['EC'] * anwp.func.globals.cityECGen * dFactor['EC']
            self.prodIA = dResources['IA'] * anwp.func.globals.cityIAGen * dFactor['IA']
            
            # update resources for system and empire
            self.myEmpire.CR += self.prodCR
            self.myEmpire.AL += self.prodAL
            self.myEmpire.EC += self.prodEC
            self.myEmpire.IA += self.prodIA
            self.AL += self.prodAL
            self.EC += self.prodEC
            self.IA += self.prodIA
            
            return 'System:%s Has Produced->(CR=%d, AL=%d, EC=%d, IA=%d) Resources' % (self.name, self.prodCR, self.prodAL, self.prodEC, self.prodIA)
        except:
            return 'system->genWealth error'

    def returnIndustryOutput(self, abr, type):
        """Check for certain Industry abr and return its total output (of type) for system"""
        try:
            total = 0
            for id, thisIndustry in self.myIndustry.iteritems():
                myIndustryData = self.myGalaxy.industrydata[thisIndustry.industrytype]
                if (myIndustryData.abr == 'B%s' % (abr) or
                    myIndustryData.abr == 'A%s' % (abr) or
                    myIndustryData.abr == 'I%s' % (abr)):
                    # add to total Points
                    total += int(myIndustryData.output)
            # return total
            return (total, 'System:%s Has Produced->%d %s' % (self.name, total, type))
        except:
            return 'system->returnIndustryOutput error'

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_system.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        