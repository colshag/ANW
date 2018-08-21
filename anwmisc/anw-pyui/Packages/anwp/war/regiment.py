# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# regiment.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a regiment of star marines
# ---------------------------------------------------------------------------
import string

import anwp.func.root
import anwp.func.globals
import anwp.func.funcs

class Regiment(anwp.func.root.Root):
    """A Star Marine Regiment is used to invade or defend Star Systems"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.name = str() # regiment name
        self.empireID = str() # empire owner (id)
        self.typeID = str() # type of regiment
        self.fromSystem = str() # id of system regiment came from
        self.toSystem = str() # id of system regiment went to this round
        self.fromShip = str() # id of ship regiment is on, or came from (shipID)
        self.shipMoved = int() # ship holding regiment has moved
        self.state = int() # current state of regiment (1-on system,2-onship,3-shipmoved,4-on another system)
        self.glory = int() # total battle glory of regiment
        self.strength = float() # percentage of strength (1-100)
        self.rank = str() # current rank of regiment
        self.restoreCost = list() # cost to restore [CR,AL,EC,IA]
        self.unloadToSystem = '' # system ID that regiment can unload to
        self.defaultAttributes = ('id', 'name', 'empireID', 'fromSystem', 
                                  'toSystem', 'fromShip', 'shipMoved', 'state',
                                  'strength', 'rank', 'restoreCost', 'typeID', 
                                  'glory', 'unloadToSystem')
        self.setAttributes(args)
        
        self.myGalaxy = None # Actual Galaxy this Regiment is in
        self.loadToShips = [] # list of shipID that regiment can load into
        self.myRegimentData = None # reference the regiment type
        self.fullName = ''
        self.setRank()

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
        bonus = anwp.func.globals.rankMods[self.rank]['bonus']

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
        self.name = '%s-%s-%s-%s' % (string.upper(myEmpire.name[:6]), self.myRegimentData.abr, name, self.id)

    def setRank(self):
        """Set the Rank"""
        # glory is used to decide the rank of a marine regiment
        if self.glory < 5:
            self.rank = anwp.func.globals.armyRank0
        elif self.glory < 7:
            self.rank = anwp.func.globals.armyRank1
        elif self.glory < 11:
            self.rank = anwp.func.globals.armyRank2
        elif self.glory < 20:
            self.rank = anwp.func.globals.armyRank3
        else:
            self.rank = anwp.func.globals.armyRank4
        
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
        d['loadToShips'] = self.loadToShips
        return d

    def getMyCurrentSystemID(self):
        """Get the current System ID regiment is in (even if on a ship)"""
        systemID = 'getMyCurrentSystemID error'
        if self.state == 1:
            systemID = self.fromSystem
        elif self.state in [2,3]:
            systemID = self.myGalaxy.ships[self.fromShip].toSystem
        elif self.state == 4:
            systemID = self.toSystem
        return systemID
    
    def getMyValue(self):
        """Return the (valueBV, valueCR, valueAL, valueEC, valueIA) in a tuple
        valueBV = credit conversion of regiment"""
        valueBV = 0.0
        valueCR = 0.0
        valueAL = 0.0
        valueEC = 0.0
        valueIA = 0.0
        factorAL = anwp.func.globals.cityCRGen/anwp.func.globals.cityALGen
        factorEC = anwp.func.globals.cityCRGen/anwp.func.globals.cityECGen
        factorIA = anwp.func.globals.cityCRGen/anwp.func.globals.cityIAGen
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
        type = self.myRegimentData.abr[2]
        for id in anwp.func.funcs.sortStringList(self.myGalaxy.regimentdata.keys()):
            myRegimentData = self.myGalaxy.regimentdata[id]
            if myRegimentData.abr[2] == type and myRegimentData.id > myRegiment.myRegimentData.id:
                return myRegimentData.id
        
        # no upgrade available
        return -1
    
    def resetData(self):
        """Reset the regiment data on end round"""
        if self.state == 3:
            # regiment is still on a ship that has moved, reset to state 2
            self.state = 2
            self.shipMoved = 0
            self.fromSystem = self.myGalaxy.ships[self.fromShip].toSystem
        elif self.state == 4:
            # regiment is on a new system reset to state 1
            self.state = 1
            self.fromSystem = self.toSystem
            self.toSystem = ''
            self.fromShip = ''
            self.shipMoved = 0

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
    
    def setMyOrder(self, order):
        """Set the current order for this regiment based on order given and regiment state
        order given is either a 'load-id' or 'unload-id'"""
        try:
            (type,id) = string.split(order, '-')
            if type == 'load':
                myTransport = self.myGalaxy.ships[id]
                if myTransport.currentTransport <= myTransport.maxTransport:
                    return 'invalid order: regiment: %s cannot load onto ship:%s no room' % (self.id, id)
                if self.state in (1,2,4): # load to transport
                    if self.state == 1:
                        self.state = 2
                    elif self.state == 2: # load from other transport
                        oldTransport = self.myGalaxy.ships[self.fromShip]
                        if oldTransport.fromSystem <> oldTransport.toSystem:
                            return 'invalid order: transport %s has moved' % self.fromShip
                        oldTransport.currentTransport -= 1
                    else:
                        self.state = 3
                    self.fromShip = id
                    myTransport.currentTransport += 1
                else:
                    return 'invalid order: %s for regiment: %s' % (order, self.id)
            elif type == 'unload':
                mySystem = self.myGalaxy.systems[id]
                ##TODO: check if transport can land here via diplomacy?
                if self.state in (2,3):
                    oldTransport = self.myGalaxy.ships[self.fromShip]
                    if (oldTransport.fromSystem == oldTransport.toSystem and
                        oldTransport.toSystem == id):
                        if self.state == 2:
                            self.fromShip = ''
                            self.fromSystem = id
                            self.state = 1
                            oldTransport.currentTransport -= 1
                        elif self.state == 3:
                            self.toSystem = id
                            self.state = 4
                            oldTransport.currentTransport -= 1
                else:
                    return 'invalid order: %s for regiment: %s' % (order, self.id)
            
            self.setMyPotentialOrders()
        except:
            return 'invalid order given'
    
    def setMovement(self):
        """Regiment is going into system movement because its transport is moving"""
        if self.state == 2 and self.shipMoved == 0:
            # must be going to a new system
            self.state = 3
            self.shipMoved = 1
        elif self.state == 3 and self.shipMoved == 1:
            # must be going back to original system
            self.state = 2
            self.shipMoved = 0
        
        self.setMyPotentialOrders()
    
    def setMyPotentialOrders(self):
        """Set the potential Orders of Regiment, orders are a list:
        'load-id' - > ship ID, means regiment can load onto this ship
        'unload-id' -> system ID, means regiment can unload onto this system"""
        if self.state in (1,4):
            # regiment is on system
            self.unloadToSystem = ''
        if self.state in (1,2):
            listShips = []
            # find all available transports that have not moved and have space
            for shipID, myShip in self.myGalaxy.ships.iteritems():
                if (myShip.fromSystem == myShip.toSystem and myShip.toSystem == self.fromSystem
                    and myShip.empireID == self.empireID and myShip.currentTransport < myShip.maxTransport):
                    listShips.append(shipID)
            self.loadToShips = listShips
        if self.state in (2,3):
            myShip = self.myGalaxy.ships[self.fromShip]
            self.unloadToSystem = myShip.toSystem
        if self.state == 3:
            self.loadToShips = []
        if self.state == 4:
            self.loadToShips = [self.fromShip]
    
    def setMyName(self, name):
        """Set the name of the regiment"""
        self.name = name
    
    def upgradeMe(self):
        """Upgrade the Regiment to the next level"""
        typeID = self.getMyNextUpgrade()
        if typeID <> -1:
            self.setMyRegimentData(typeID)

def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_regiment.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        
