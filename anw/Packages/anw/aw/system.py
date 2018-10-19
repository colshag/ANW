# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# system.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a system
# ---------------------------------------------------------------------------
import random
import string
import copy

from anw.func import root, funcs, globals
from anw.war import captain, ship

class System(root.Root):
    """A System Represents one Territory Object in ANW.  A System will
    contain Industry, Armies, Fleets, etc.  Systems also have coordinates 
    on the Galactic Map.  These Coordinates decide which Systems are adjacent"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # Given System Name
        self.x = float() # x Coordinate of System on Map (Top Left Corner)
        self.y = float() # y Coordinate of System on Map (Top Left Corner)
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
        self.myIndustry = {} # Dict key = industrydata id, value = number of industry (int)
        self.myOldIndustry = {} # Dict key = industrydata id, value = number of industry (int)
        
        self.blankIntelReport = {'industryReport':{}, 'shipReport':{}, 'marineReport':{}, 'round':0}
        self.cityIndustry = [self.cities, 0, 0] # AL, EC, IA
        self.oldCityIndustry = [self.cities, 0, 0] # AL, EC, IA

    def getCurrentIndustryResourceValue(self):
        """Return total Resources by summing all industry from system"""
        myResources = [0,0,0]
        for id, industryNum in self.myIndustry.iteritems():
            myIndustryData = self.myGalaxy.industrydata[id]
            myResources[0] += myIndustryData.costAL*industryNum
            myResources[1] += myIndustryData.costEC*industryNum
            myResources[2] += myIndustryData.costIA*industryNum
        return myResources

    def setMyIndustry(self, industryDataIDList):
        """Setup myIndustry Dict with key of each industrydatakey"""
        for id in industryDataIDList:
            self.myIndustry[id] = 0

    def addIndustry(self, amount, industrytype):
        """Build Industry in this System, 
        input: amount - > amount of industry (int)
               industryType -> type of industry (id)
        """
        try:
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            self.myIndustry[industrytype] += amount
            return 1
        except:
            return 'system->addIndustry error'
    
    def removeIndustry(self, amount, industrytype):
        """Remove Industry in this System, 
        input: industryID -> Industry ID (ID of system.myIndustry)
        """
        try:
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            self.myIndustry[industrytype] -= amount
            return 1
        except:
            return 'system->removeIndustry error'

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
        self.oldCityIndustry = copy.copy(self.cityIndustry)
        self.myOldIndustry = copy.copy(self.myIndustry)
        for attr in ['AL','EC','IA']:
            self.clearAttribute(attr)
        self.resetCitiesUsed()
    
    def resetCitiesUsed(self):
        """Reset cities used"""
        # reset cities used
        self.citiesUsed = 0
        for id, myIndustryNum in self.myIndustry.iteritems():
            if myIndustryNum > 0:
                myIndustryData = self.myGalaxy.industrydata[id]
                self.citiesUsed += myIndustryData.cities*myIndustryNum

    def setMyEmpire(self, empireObject):
        """Set the Empire Owner object of this System"""
        self.myEmpireID = empireObject.id
        self.myEmpire = empireObject
        self.setImageFileName() # reset the image filename
        self.resetData()
    
    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this System"""
        self.myGalaxy = galaxyObject
        galaxyObject.systems[self.id] = self
        self.resetIntelReports()
    
    def resetIntelReports(self):
        """reset intel reports"""
        for empireID in self.myGalaxy.empires.keys():
            self.intelReport[empireID] = self.blankIntelReport
    
    def setSYC(self, amount):
        """Set the Shipyard Capacity for the system"""
        # used should be reset to 0
        self.usedSYC = 0
        self.availSYC = amount
    
    def addFleetCadets(self, amount):
        """Add to the current available fleet cadets"""
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
    
    def addArmyCadets(self, amount):
        """Add to the current available army cadets"""
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
        # make sure all Empires have proper intel report
        for empireID in self.myGalaxy.empires.keys():
            radarStrength = 0
            
            # calculate radar strength of empire to this system
            for systemID in self.connectedSystems:
                mySystem = self.myGalaxy.systems[systemID]
                if mySystem.myEmpireID == empireID:
                    radarStrength += mySystem.radarStrength
            
            # add radar strength of own system
            if self.myEmpireID == empireID:
                radarStrength += self.radarStrength
            
            if radarStrength > self.jammingStrength:
                self.intelReport[empireID] = self.genIntelReport(empireID)
            else:
                self.intelReport[empireID] = self.blankIntelReport

    def getMySystemInfo(self):
        """Return detailed system information, this goes to system owner"""
        dict = self.getSelectedAttr(list(self.defaultAttributes))
        dict['myIndustry'] = self.myIndustry
        dict['myOldIndustry'] = self.myOldIndustry
        dict['cityIndustry'] = self.cityIndustry
        dict['oldCityIndustry'] = self.oldCityIndustry
        return dict
    
    def getAllConnections(self):
        """Get all systems connected to this system based on diplomacy type include warp gates
        This is used for ship movement only, not for trade"""
        systemList = []
        # first go through warp connections
        if self.usedWGC < self.availWGC:
            for systemID, mySystem in self.myGalaxy.systems.iteritems():
                if ((mySystem.myEmpireID == self.myEmpireID or globals.diplomacy[self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.myEmpireID].diplomacyID]['alliance'] == 1) 
                    and mySystem.usedWGC < mySystem.availWGC 
                    and mySystem.id != self.id
                    and mySystem.id not in self.connectedSystems):
                    systemList.append(mySystem.id)
                    
        # then go through basic connections
        for systemID in self.connectedSystems:
            mySystem = self.myGalaxy.systems[systemID]
            myDiplomacy = self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.myEmpireID].diplomacyID
            if mySystem.myEmpireID == self.myEmpireID or globals.diplomacy[myDiplomacy]['move'] == 1:
                systemList.append(systemID)
        return systemList
    
    def setWarpConnections(self):
        """Set warpconnected list of System ID's this system is connected to via warp gates
        This is only used for trade route calculations, not for ship movement"""
        self.warpGateSystems = []
        if self.availWGC > 0:
            for systemID, mySystem in self.myGalaxy.systems.iteritems():
                if ((mySystem.myEmpireID == self.myEmpireID or globals.diplomacy[self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.myEmpireID].diplomacyID]['trade'] == 1) 
                    and mySystem.availWGC > 0 
                    and mySystem.id != self.id
                    and mySystem.id not in self.connectedSystems):
                    self.warpGateSystems.append(mySystem.id)
    
    def getOtherSystemInfo(self):
        """Return general system information"""
        list = ['id', 'name', 'x', 'y', 'cities', 'connectedSystems', 'myEmpireID', 'intelReport', 'imageFile']
        dict = self.getSelectedAttr(list)
        return dict
    
    def genIntelReport(self, empireID):
        """Generate the intel report for system in relation to each empire
        report is a Dict with the key being empire id, then the report
        breaks down into sub dictionarys:
        - industryReport -> dict of industry on planet
        - shipReport -> dict of StarShips on planet
        - marineReport -> dict of Marines on planet
        - round -> round this report was generated"""
        dIndustry = {}
        industryKeys = funcs.sortStringList(self.myIndustry.keys())
        i = 0
        for industryID in industryKeys:
            if self.myIndustry[industryID] > 0:
                i += 1
                myIndustrydata = self.myGalaxy.industrydata[industryID]
                dIndustry[str(i)] = '%s - %s' % (self.myIndustry[industryID], myIndustrydata.name)
        
        dShips = self.getStarshipReport(empireID)
                    
        dMarines = self.getMarineReport(empireID)
        
        myIntelReport = {'industryReport':dIndustry, 'shipReport':dShips, 'marineReport':dMarines, 'round':self.myGalaxy.currentRound}
        return myIntelReport
        
    def getStarshipReport(self, empireID):
        """Return a generic starship report not including ships from empireID"""
        d = {}
        dShips = {}
        
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.toSystem == self.id and myShip.empireID != empireID:
                hullID = myShip.myShipHull.id
                if hullID not in dShips.keys():
                    dShips[hullID] = [1, myShip.myShipHull.name]
                else:
                    dShips[hullID] = [dShips[hullID][0] + 1, myShip.myShipHull.name]
        i = 0
        for hullID in self.myGalaxy.shiphulldata.keys():
            if hullID in dShips.keys():
                d[str(i)] = '%d - %s' % (dShips[hullID][0], dShips[hullID][1])
                i += 1
        return d
    
    def getMarineReport(self, empireID):
        """Return a generic Marine repot not including marines from empireID"""
        d = {}
        dMarines = {}
        
        for regID, myReg in self.myGalaxy.regiments.iteritems():
            if myReg.fromSystem == self.id and myReg.empireID != empireID:
                typeID = myReg.typeID
                if typeID not in dMarines.keys():
                    dMarines[typeID] = [1, self.myGalaxy.regimentdata[typeID].name]
                else:
                    dMarines[typeID] = [dMarines[typeID][0] + 1, self.myGalaxy.regimentdata[typeID].name]
        i = 0
        for typeID in self.myGalaxy.regimentdata.keys():
            if typeID in dMarines.keys():
                d[str(i)] = '%d - %s' % (dMarines[typeID][0], dMarines[typeID][1])
                i += 1
        return d
    
    def setImageFileName(self):
        """Set the image filename depends on:
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
    
    def checkResources(self, reqCR, reqAL, reqEC, reqIA):
        """Checks if given required resources are available"""
        try:
            if self.myEmpire.CR < 0:
                myCR = 0
            else:
                myCR = self.myEmpire.CR
            if (myCR >= reqCR and
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
            if reqCR < 0:
                result = self.myEmpire.depositCR(abs(reqCR))
            else:
                result = self.myEmpire.withdrawCR(reqCR)
            if result == 1:
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
    
    def addShip(self, amount, empireID, shipDesignID, addCadet=1):
        """Add Ships to this System from Shipyards, 
        input: amount - > number of ships to add (int)
               empireID -> empire id
               shipDesignID -> ship design id
        DONE ON ROUND END
        """
        try:
            myEmpire = self.myGalaxy.empires[empireID]
            myShipDesign = myEmpire.shipDesigns[shipDesignID]
            i = 0
            while i < amount:
                myCaptain = self.createCaptain(myEmpire, addCadet)
                shipID = self.myGalaxy.getNextID(self.myGalaxy.ships)
                myShip = ship.Ship({'id':shipID, 'fromSystem':self.id, 'toSystem':self.id, 'empireID':empireID})
                myShip.setMyCaptain(myCaptain)
                myShip.setMyGalaxy(self.myGalaxy)
                myShip.setMyDesign(myShipDesign)
                myShip.setMyStatus()
                i += 1
            return myShip
        except:
            return 'system->addShip error'
    
    def createCaptain(self, myEmpire, addCadet=0):
        """create a new ship captain crew"""
        id = self.myGalaxy.getNextID(self.myGalaxy.captains)
        name = self.myGalaxy.getCaptainName()
        myCaptain = captain.Captain({'id':id, 'name':name})
        myCaptain.setMyEmpire(myEmpire)
        if self.fleetCadets > 0 and addCadet == 1:
            self.fleetCadets -= 1
            myCaptain.addExperience(100)
        return myCaptain
        
    def payForAddIndustry(self, amount, industrytype):
        """Actually pay to add industry, (pay in resources and citiesUsed)"""
        try:
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            self.citiesUsed += (industryDataObj.cities * amount)
            totalCRAmountToCharge = self.getCRToChargeToAddIndustry(amount, industrytype)
            return self.payResources(industryDataObj.costCR * totalCRAmountToCharge,
                                     industryDataObj.costAL * amount,
                                     industryDataObj.costEC * amount,
                                     industryDataObj.costIA * amount)
        except:
            return 'system->payForAddIndustry error'
    
    def refundForRemoveIndustry(self, amount, industrytype):
        """Actually refund to remove industry, (refund in resources and citiesUsed)"""
        try:
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            self.citiesUsed -= (industryDataObj.cities * amount)
            totalCRAmountToRefund = self.getCRToRefundToRemoveIndustry(amount, industrytype)
            return self.payResources(-1 * industryDataObj.costCR * totalCRAmountToRefund,
                                     -1 * industryDataObj.costAL * amount,
                                     -1 * industryDataObj.costEC * amount,
                                     -1 * industryDataObj.costIA * amount)
        except:
            return 'system->refundForRemoveIndustry error'
    
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
            return self.payResources(CR/2.0, AL/2.0, EC/2.0, IA/2.0)
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
            for industryID, myIndustryNum in self.myIndustry.iteritems():
                if myIndustryNum > 0:
                    abr = self.myGalaxy.industrydata[industryID].abr
                    if abr[1:] == 'MF':
                        # create militia regiments
                        fortressOutput = int(self.myGalaxy.industrydata[industryID].output)
                        militiaNum = (fortressOutput)*myIndustryNum
                        for i in range(militiaNum):
                            # create militia regiment
                            myRegiment = self.myGalaxy.setNewRegiment(self.myEmpireID, self.id, globals.militiaType[abr], 'Militia')
                            defMilitia += 1
            
            # setup stats
            for regimentID in self.myGalaxy.regiments.keys():
                myRegiment = self.myGalaxy.regiments[regimentID]
                if myRegiment.toSystem == self.id:
                    # regiment is on system, check if its an enemy
                    if (myRegiment.empireID != self.myEmpireID and
                        globals.diplomacy[self.myGalaxy.empires[myRegiment.empireID].diplomacy[self.myEmpireID].diplomacyID]['invade'] == 1):
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
                    if myRegiment.toSystem == self.id:
                        # regiment is on system, check if its an enemy
                        if (myRegiment.empireID != self.myEmpireID and
                            globals.diplomacy[self.myGalaxy.empires[myRegiment.empireID].diplomacy[self.myEmpireID].diplomacyID]['invade'] == 1):
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
                            attackLosses += 1
                            enemyRegiment.destroyMe()
                        else:
                            myDeathCount += 1
                            defLosses += 1
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
                    empireKeys = funcs.sortDictByValue(enemyRegimentCount,True)
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
            newShip = ship.Ship(myShip.getMyInfoAsDict())
            newShip.setMyCaptain(myCaptain)
            newShip.setMyGalaxy(self.myGalaxy)
            newShip.setMyDesign(myDesign)
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
            oldname = myShip.myDesign.name
            myEmpire = self.myGalaxy.empires[myShip.empireID]
            newDesign = myEmpire.shipDesigns[newDesignID]
            myCaptain = myShip.myCaptain
            # create new fixed ship with same attributes
            newShip = ship.Ship(myShip.getMyInfoAsDict())
            newShip.toSystem = myShip.toSystem
            newShip.setMyCaptain(myCaptain)
            newShip.setMyGalaxy(self.myGalaxy)
            newShip.setMyDesign(newDesign)
            newShip.setRepairCost()
            newShip.setMyStrength()
            myShip = None
            
            return 'UPGRADED %s to TYPE = %s' % (oldname, newShip.myDesign.name)
        except:
            return 'system->upgradeStarship error'
    
    def upgradeRegiment(self, regimentID):
        """Upgrade the Regiment to the new type
        DONE ON ROUND END"""
        try:
            myRegiment = self.myGalaxy.regiments[regimentID]
            oldname = myRegiment.myRegimentData.name
            myRegiment.upgradeMe()
            return 'UPGRADED %s TO:%s ON:%s' % (oldname, myRegiment.myRegimentData.name, self.name)
        except:
            return 'system->upgradeRegiment error'
    
    def validateAddIndustry(self, empireID, amount, industrytype):
        """Validate if industry can be added, return 1=pass, string=fail"""
        try:
            if amount < 0:
                return 'Cannot add negative amounts'
            if empireID != self.myEmpireID:
                return 'You are trying to add industry on System not owned by you'
            if amount == 0:
                return 'You cannot add 0 Industry'
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            
            if (industryDataObj.cities * amount) > (self.cities - self.citiesUsed):
                return 'Not enough Cities to build %s on %s' % (industryDataObj.name, self.name)
            
            myTech = self.myEmpire.techTree[industryDataObj.techReq]
            if myTech.complete == 0 and self.myOldIndustry[industrytype] < amount:
                return '%s must be researched before industry can be added' % myTech.name
            
            totalCRAmountToCharge = self.getCRToChargeToAddIndustry(amount, industrytype)
            return self.checkResources(industryDataObj.costCR * totalCRAmountToCharge, industryDataObj.costAL * amount, 
                                       industryDataObj.costEC * amount, industryDataObj.costIA * amount)
        except:
            return 'system->validateAddIndustry error'

    def validateRemoveIndustry(self, empireID, amount, industrytype):
        """Validate if industry can be removed, return 1=pass, string=fail"""
        try:
            if amount < 0:
                return 'Cannot remove negative amounts'
            if empireID != self.myEmpireID:
                return 'You are trying to remove industry on System not owned by you'
            if amount == 0:
                return 'You cannot remove 0 Industry'
            industryDataObj = self.myGalaxy.industrydata[industrytype]
            
            if self.myIndustry[industrytype] < amount:
                return 'Not enough %s on %s' % (industryDataObj.name, self.name)
            
            return 1
        except:
            return 'system->validateAddIndustry error'

    def getCRToChargeToAddIndustry(self, amount, industrytype):
        """Look at industry from last round, only charge CR on new industry"""
        diff = self.myOldIndustry[industrytype]-self.myIndustry[industrytype]
        if diff > 0:
            if diff < amount:
                result = amount - diff
            else:
                result = 0
        else:
            result = amount
        return result
    
    def getCRToRefundToRemoveIndustry(self, amount, industrytype):
        """Look at industry from last round, only refund CR on new industry"""
        diff = self.myOldIndustry[industrytype]-self.myIndustry[industrytype]
        if diff > 0:
            result = 0
        else:
            result = amount
        return result
        
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
            if myRegiment.empireID != self.myEmpireID:
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
            if myRegiment.empireID != self.myEmpireID:
                return 'regiment is not owned by system'
            # check if regiment has 100 percent strength
            if myRegiment.strength != 100:
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
                return 'You do not have enough capacity to upgrade all selected Regiments'
            # check if enough resources available
            [BV,CR,AL,EC,IA] = myRegiment.getMyValue()
            return self.checkResources(CR,AL,EC,IA)
       
        except:
            return 'system->validateUpgradeRegiment error'
    
    def validateRepairStarship(self, shipID):
        """Validate if ship can be repaired, return 1=pass, string=fail"""
        try:
            myShip = self.myGalaxy.ships[shipID]
            if myShip.empireID != self.myEmpireID:
                return 'ship is not owned by system'
            # check if ship is already at 100% strength
            if myShip.strength == 100:
                return 'ship already at 100% strength'
            # check if enough shipyard space available
            spaceRequired = myShip.getRepairCapacity()
            if (self.availSYC-self.usedSYC) < spaceRequired:
                return 'Not have enough Shipyard Capacity to repair %s on %s' % (myShip.name, self.name)
            
            if myShip.myDesign.hasAllTech == 0:
                return 'Advanced Ships cannot be repaired, replace damaged quadrants with low tech and upgrade'
            
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
            if self.canIUpgradeAdvancedShip(myShip, newDesign) == 0:
                return 'Ship Design has unresearched technology'
            if myShip.empireID != self.myEmpireID:
                return 'ship is not owned by system'
            # check if ship is not at 100% strength
            if myShip.strength != 100 and myShip.myDesign.hasAllTech == 1:
                return 'ship must be at 100% strength to be upgraded'
            # check if new design hull different
            if myShip.myDesign.myShipHull.id != newDesign.myShipHull.id:
                return 'ship hulls different'
            # check if enough shipyard space available
            [CR,AL,EC,IA,capacity] = myShip.myDesign.getUpgradeCost(newDesign)
            if (self.availSYC-self.usedSYC) < capacity:
                return 'Not have enough Shipyard Capacity to upgrade %s TO %s' % (myShip.name, newDesign.name)
            # check if enough resources available
            return self.checkResources(CR,AL,EC,IA)
            
        except:
            return 'system->validateUpgradeStarship error'
    
    def canIUpgradeAdvancedShip(self, myShip, newDesign):
        """Advanced Ships taken in combat can be repaired by upgrading them to a design
        that allows for a repair of sorts where the damaged sections are replaced with
        available parts, if quadrant damaged then it has to be completely replaced in new design
        with valid old tech parts for this hybrid repair to be valid"""
        if myShip.strength == 100.0 and newDesign.hasAllTech == 0:
            return 0
        for position, myQuad in myShip.quads.iteritems():
            if myQuad.currentComps < myShip.myDesign.quads[position].currentComps:
                if self.checkNewDesignQuadValid(newDesign, position) == 0:
                    return 0
        return 1
    
    def checkNewDesignQuadValid(self, newDesign, position):
        """New Design quadrant position (fore, aft, port, star) should have all valid
        components tech wise"""
        myQuad = newDesign.quads[position]
        for componentID, myComponent in myQuad.components.iteritems():
            if myComponent.myComponentData in self.myEmpire.techTree.keys():
                if self.myEmpire.techTree[myComponent.myComponentData.techReq].complete == 0:
                    return 0
            
        for weaponID, myWeapon in myQuad.weapons.iteritems():
            if self.myEmpire.techTree[myWeapon.myWeaponData.techReq].complete == 0:
                return 0
        return 1
        
    def addCity(self, resourceFocus):
        """Build City in this System, 
        input: resourceFocus -> ('CR', 'AL', 'IA', 'EC')
        DONE ON ROUND END
        """
        try:
            self.cities += 1
            self.cityIndustry[resourceFocus] += 1
            return 'ADD 1 CITY TO:%s' % self.name
        except:
            return 'system->addCity error'
    
    def validateAddCity(self):
        """Validate if city can be added, return 1=pass, string=fail"""
        try:
            # calc required resources
            reqCR = globals.addCityResource['CR']
            reqAL = globals.addCityResource['AL']
            reqEC = globals.addCityResource['EC']
            reqIA = globals.addCityResource['IA']
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
            return self.payResources(globals.addCityResource['CR'],
                                     globals.addCityResource['AL'],
                                     globals.addCityResource['EC'],
                                     globals.addCityResource['IA'])
        except:
            return 'system->payForAddCity error'
    
    def refundAddCity(self):
        """refund add city"""
        try:
            # calc required resources
            return self.payResources(-1 * globals.addCityResource['CR'],
                                     -1 * globals.addCityResource['AL'],
                                     -1 * globals.addCityResource['EC'],
                                     -1 * globals.addCityResource['IA'])
        except:
            return 'system->refundAddCity error'
    
    def updateCityIndustry(self, newIndustryList):
        """Update City Industry for this system newIndustryList=[CR,AL,EC,IA]
        """
        try:
            self.cityIndustry = newIndustryList
            return 1
        except:
            return 'system->updateCityIndustry error'
    
    def validateUpdateCityIndustry(self, empireID, newIndustryList):
        """Validate if city resource can be updated, return 1=pass, string=fail"""
        try:
            if empireID != self.myEmpireID:
                return 'You are trying to update City Industry on System not owned by you'
            # make sure sum of cities is the same
            numCities = 0
            for num in newIndustryList:
                numCities += num
            if numCities != self.cities:
                return 'You are trying to update City Industry where total cities(%s) not equal to %s' % (numCities, self.cities)
            return 1
        except:
            return 'system->validateUpdateCityIndustry error'
    
    def genWealth(self):
        """Generate Wealth for System, done once each round, wealth consists of
        (AL)(EC)(IA) - these resources are added to the systems totals
        (prodAL, prodEC, prodIA) are all updated, these declare how much was
        generated for each resource by this system this round"""
        try:
            dResources = {'AL':self.cityIndustry[0],
                          'EC':self.cityIndustry[1],
                          'IA':self.cityIndustry[2]}
            dFactor = {'AL':1, 'EC':1, 'IA':1}
            
            # store factors of any industry on system
            for industryID, myIndustryNum in self.myIndustry.iteritems():
                if myIndustryNum > 0:
                    myIndustryType = self.myGalaxy.industrydata[industryID]
                    if myIndustryType.abr[1:3] == 'AF':
                        dFactor['AL'] += myIndustryType.output*myIndustryNum
                    elif myIndustryType.abr[1:3] == 'CM':
                        dFactor['EC'] += myIndustryType.output*myIndustryNum
                    elif myIndustryType.abr[1:3] == 'SS':
                        dFactor['IA'] += myIndustryType.output*myIndustryNum
            
            # create resource wealth
            self.prodAL = dResources['AL'] * globals.cityALGen * dFactor['AL']
            self.prodEC = dResources['EC'] * globals.cityECGen * dFactor['EC']
            self.prodIA = dResources['IA'] * globals.cityIAGen * dFactor['IA']

            # update resources for system and empire
            self.myEmpire.AL += self.prodAL
            self.myEmpire.EC += self.prodEC
            self.myEmpire.IA += self.prodIA
            self.AL += self.prodAL
            self.EC += self.prodEC
            self.IA += self.prodIA
            
            return 'System:%s Has Produced->(AL=%d, EC=%d, IA=%d) Resources' % (self.name, self.prodAL, self.prodEC, self.prodIA)
        except:
            return 'system->genWealth error'

    def returnIndustryOutput(self, abr, type):
        """Check for certain Industry abr and return its total output (of type) for system"""
        try:
            total = 0
            for id, myIndustryNum in self.myIndustry.iteritems():
                if myIndustryNum > 0:
                    myIndustryData = self.myGalaxy.industrydata[id]
                    if (myIndustryData.abr == 'B%s' % (abr) or
                        myIndustryData.abr == 'A%s' % (abr) or
                        myIndustryData.abr == 'I%s' % (abr)):
                        # add to total Points
                        total += int(myIndustryData.output)*myIndustryNum
            # return total
            return (total, 'System:%s Has Produced->%d %s' % (self.name, total, type))
        except:
            return 'system->returnIndustryOutput error'
        