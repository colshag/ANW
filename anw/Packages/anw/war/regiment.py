# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# regiment.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a regiment of star marines
# ---------------------------------------------------------------------------
import string
import copy
import random

from anw.func import root, globals, funcs

class Regiment(root.Root):
    """A Star Marine Regiment is used to invade or defend Star Systems"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # regiment name
        self.empireID = str() # empire owner (id)
        self.typeID = str() # type of regiment
        self.fromSystem = str() # id of system regiment came from
        self.toSystem = str() # id of system regiment went to this round
        self.glory = int() # total battle glory of regiment
        self.strength = float() # percentage of strength (1-100)
        self.rank = str() # current rank of regiment
        self.restoreCost = list() # cost to restore [CR,AL,EC,IA]
        self.defaultAttributes = ('id', 'name', 'empireID', 'fromSystem', 
                                  'toSystem', 'strength', 'rank',
                                  'restoreCost', 'typeID', 'glory')
        self.setAttributes(args)
        
        self.myGalaxy = None 
        self.myRegimentData = None # reference the regiment type
        self.fullName = ''
        self.availSystems = [] # list of all potential systems regiment can warp to
        self.oldAvailSystems = []
        self.setRank()

    def moveToSystem(self, systemID):
        """Move Regiment to System"""
        self.toSystem = systemID
        self.setAvailSystems()
    
    def setAvailSystems(self):
        """Determine which systems regiment can warp to currently"""
        self.availSystems = []
        if self.toSystem != self.fromSystem:
            self.availSystems.append(self.fromSystem)
            return
        else:
            mySystem = self.myGalaxy.systems[self.fromSystem]
            if mySystem.myEmpireID == self.empireID or globals.diplomacy[self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.empireID].diplomacyID]['alliance'] == 1:
                self.availSystems = mySystem.getAllConnections()
            else:
                for otherSystemID in mySystem.connectedSystems:
                    otherSystem = self.myGalaxy.systems[otherSystemID]
                    if otherSystem.myEmpireID == self.empireID or globals.diplomacy[self.myGalaxy.empires[otherSystem.myEmpireID].diplomacy[self.empireID].diplomacyID]['move'] == 1:
                        self.availSystems.append(otherSystemID)
            self.oldAvailSystems = copy.copy(self.availSystems)
            
    def addGlory(self, amount, init=0):
        """When a Regiment wins a battle it gains glory, trained marines gain glory on construction"""
        self.glory += amount
        self.setRank()

    def destroyMe(self):
        """Remove Regiment from galaxy"""
        self.myGalaxy.removeRegiment(self.id)

    def getBonusStrength(self, enemyRegiment):
        """Return the combined bonus strength for Regiment, used for engagement with enemy"""
        # first retrieve bonus based on rank
        bonus = globals.rankMods[self.rank]['bonus']

        # second retrieve bonus based on the inherent enemy regiment type vs this regiment type
        type = enemyRegiment.myRegimentData.abr[2:]
        vsBonus = getattr(self.myRegimentData, type)
        bonus += vsBonus

        return float(1 + (bonus/100))

    def engageRegiment(self, enemyRegiment):
        """Engage in ground conflict with enemy Regiment"""
        myStrength = self.strength * self.getBonusStrength(enemyRegiment)
        enemyStrength = enemyRegiment.strength * enemyRegiment.getBonusStrength(self)
        
        myRollNeeded = int((myStrength/(myStrength+enemyStrength)) * 100)
        D100Roll = random.randint(1,100)
        if D100Roll <= myRollNeeded:
            # I won battle
            casualties = random.randint(0, 100-myRollNeeded)
            s = '%s(%d%s) DEFEATED %s(%d%s) -> %s%s Casualties' % (self.name, myStrength, '%', 
                                                                   enemyRegiment.name, enemyStrength, '%',
                                                                   casualties, '%')
            self.setMyCasualties(casualties)
            self.addGlory(1)
            return (1,s)
            
        else:
            # enemy won battle
            casualties = random.randint(0, myRollNeeded)
            s = '%s(%d%s) DEFEATED %s(%d%s) -> %s%s Casualties' % (enemyRegiment.name, enemyStrength, '%',
                                                                   self.name, myStrength, '%',
                                                                   casualties, '%')
            enemyRegiment.setMyCasualties(casualties)
            enemyRegiment.addGlory(1)
            return (0,s)

    def setMyRegimentData(self, regimentDataID):
        """Set the regiment type for this regiment"""
        self.typeID = regimentDataID
        self.myRegimentData = self.myGalaxy.regimentdata[self.typeID]
    
    def setMyStatus(self, name='Marines'):
        """Set the default status of this Regiment"""
        self.strength = 100 # regiment starts at 100% strength
        self.setMyRegimentData(self.typeID)
        myEmpire = self.myGalaxy.empires[self.empireID]
        self.name = '%s-%s-%s-%s' % (string.upper(myEmpire.name[:3]), self.myRegimentData.abr, name, self.id)

    def setRank(self):
        """Set the Rank"""
        # glory is used to decide the rank of a marine regiment
        if self.glory < 5:
            self.rank = globals.armyRank0
        elif self.glory < 7:
            self.rank = globals.armyRank1
        elif self.glory < 11:
            self.rank = globals.armyRank2
        elif self.glory < 20:
            self.rank = globals.armyRank3
        else:
            self.rank = globals.armyRank4
        
        self.fullName = '<%s> %s' % (self.rank, self.name)
    
    def setRestorationCost(self):
        """Set the Restoration Cost for this regiment"""
        ratio = 1.0 - (self.strength/100.0)
        CR = int(self.myRegimentData.costCR*ratio)
        AL = int(self.myRegimentData.costAL*ratio)
        EC = int(self.myRegimentData.costEC*ratio)
        IA = int(self.myRegimentData.costIA*ratio)
        self.restoreCost = [CR,AL,EC,IA]
        
    def getMyRegimentInfo(self):
        """Return Regiment info as dict"""
        d = self.getMyInfoAsDict()
        d['availSystems'] = self.availSystems
        d['oldAvailSystems'] = self.oldAvailSystems
        return d
    
    def getMyValue(self):
        """Return the (valueBV, valueCR, valueAL, valueEC, valueIA) in a tuple
        valueBV = credit conversion of regiment"""
        valueBV = 0.0
        valueCR = 0.0
        valueAL = 0.0
        valueEC = 0.0
        valueIA = 0.0
        factorAL = globals.cityCRGen/globals.cityALGen
        factorEC = globals.cityCRGen/globals.cityECGen
        factorIA = globals.cityCRGen/globals.cityIAGen
        ratio = self.strength/100.0
        valueCR += self.myRegimentData.costCR*ratio
        valueAL += self.myRegimentData.costAL*ratio
        valueEC += self.myRegimentData.costEC*ratio
        valueIA += self.myRegimentData.costIA*ratio
        valueBV += (valueCR +
                    valueAL*factorAL +
                    valueEC*factorEC +
                    valueIA*factorIA)
        return (valueBV, valueCR, valueAL, valueEC, valueIA)
    
    def getMyNextUpgrade(self):
        """Return the Regiment type ID that Regiment would require to upgrade"""
        myType = self.myRegimentData.abr[1]
        if myType == 'P':
            return -1
        else:
            nextID = int(self.myRegimentData.id) + 10
            return str(nextID)
        
    def resetData(self):
        """Reset the regiment data on end round"""
        self.fromSystem = self.toSystem

    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner"""
        self.myGalaxy = galaxyObject
        galaxyObject.regiments[self.id] = self
    
    def setMyCasualties(self, casualties):
        """Give Regiment Casualties"""
        if casualties > self.strength:
            self.destroyMe()
        else:
            self.strength -= casualties
            self.setRestorationCost()
    
    def setMyName(self, name):
        """Set the name of the regiment"""
        self.name = name
    
    def upgradeMe(self):
        """Upgrade the Regiment to the next level"""
        typeID = self.getMyNextUpgrade()
        if typeID != -1:
            self.setMyRegimentData(typeID)
            self.setMyStatus()
        
