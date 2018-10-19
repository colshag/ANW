# ---------------------------------------------------------------------------
# Cosmica - All rights reserved by NeuroJump Trademark 2018
# ship.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a starship
# ---------------------------------------------------------------------------
import math
import random
import logging
import copy

from anw.func import root, funcs, globals
import kobj
import quad
import component
import weapon
import shield
import statistics

class Ship(root.Root, kobj.KObj):
    """A StarShip contains quads, components, weapons, and a captain"""
    def __init__(self, args):
        # Attributes
        self.log=logging.getLogger('ship')
        self.id = str() # Unique Game Object ID
        self.name = str() # ship name
        self.designID = str() # ship Design (id)
        self.captainID = str() # captain commanding ship (id)
        self.currentISP = float() # current ship internal structure points
        self.currentBattery = float() # current battery power available
        self.currentPower = float() # current power available (in kW)
        self.mass = float() # current mass of ship (use ship hull and component num)
        self.maxBattery = float() # max battery power available
        self.thrust = float() # ship thrust
        self.rotation = float() # ship rotation thrust
        self.radar = int() # ships radar value
        self.jamming = int() # ships jamming value
        self.repair = int () # ships repair ability
        self.facing = float() # ship facing
        self.posX = float() # ship x position
        self.posY = float() # ship y position
        self.setX = float() # ship desired x position in grid
        self.setY = float() # ship desired y position in grid
        self.strength = float() # ship strength status total components/design components
        self.maxAssault = int() # max marine assault strength
        self.repairCost = [0,0,0,0] # cost to repair [CR,AL,EC,IA]
        self.empireID = str() # empire owner (id)
        self.systemGrid = int() # grid of ship within system (1-9)
        self.fromSystem = str() # id of planet ship was at
        self.toSystem = str() # id of planet ship moved to
        self.range = float() # range ship wants to stay at with target ship
        self.facing = float() # initial ship facing (degrees, 0 faces north)
        self.stats = statistics.Statistics()
        self.accel = float() # current max acceleration of ship
        self.isTransport = 0 # is this ship a transport
        self.isAssault = 0 # is this ship an assault ship
        self.underAssault = 0 # is this ship in a marine assault battle currently
        self.assaultStrength = 0 # ships assault strength before going into assault mode
        self.currentAssault = 0 # ships current marine strength during an assault
        self.finishedAssault = 0 # assault ships can only assault one ship per battle
        self.takenOverByEmpire = '' # ship taken over by another empire

        self.defaultAttributes = ('id', 'name', 'designID', 'captainID', 'currentISP',
                                  'currentBattery', 'maxBattery', 'currentPower', 'mass',
                                  'thrust', 'rotation', 'radar', 'jamming', 'repair', 'facing', 
                                  'posX', 'posY', 'setX', 'setY', 'strength', 'maxAssault', 
                                  'repairCost','empireID',
                                  'systemGrid','fromSystem','toSystem','range','facing','accel','isTransport','isAssault','takenOverByEmpire')
        self.setAttributes(args)

        self.myGalaxy = None # Actual Galaxy object this Ship contained in
        self.myCaptain = None # Referenced
        self.myDesign = None # Referenced
        self.componentdata = None # referenced
        self.weapondata = None # referenced
        self.myShipHull = None # referenced
        self.currentTarget = None # current Target of Ship
        self.drones = [] # list of drones launched from ship
        self.targets = [] # list of target ship ID's
        self.shipsTargetingMe = [] # list of all enemy ships targetting me
        self.availSystems = [] # list of all potential systems ship can warp to
        self.oldAvailSystems = []
        self.systemGrid = 5 # start in middle grid
        self.toSystem = self.fromSystem

        self.quads = {} # key='fore','aft','port','star', value = quad obj
        self.count = int() # ships current iteration through simulation
        self.dx = float() # ships x movement
        self.dy = float() # ships y movement
        self.dRotation = int() # ships desired rotation direction
        self.allWeaponsPowered = int() # 1=all weapons powered
        self.alive = 1 # is ship alive
        self.currentAccel = 0 # keeps track of ships current accel

        self.amsTargets = [] # list of missiles currently in range of ams guns
        self.amsWeapons = [] 
        self.activeWeapons = [] # list of weapons sorted by priority
        self.amsWeapons = [] # list of ams weapons sorted by priority
        self.readyWeapons = [] # list of weapons sorted by priority and ready to fire
        self.mode = 'close' # modes are close, escape, engage, assault

        self.setX = self.setX
        self.setY = self.setY
        self.retargetGoal = 0
        self.retargetCount = 0
        self.radius = 0
        self.externalRadius = 0
        self.alternateTargets = [] # list of other ship/drone objects to fire at
        self.positions = ['fore','aft','port','star']

    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['log']             # remove stuff not to be pickled
        return odict

    def __setstate__(self,dict):
        log=logging.getLogger('ship')
        self.__dict__.update(dict)
        self.log=log

    def tellNewFriendsToStopTargeting(self, empireID):
        """Ship has changed sides, tell new friends to stop shooting at ship"""
        self.shipsTargetingMe = []
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if myShip.empireID == empireID:
                if self.id in myShip.targets:
                    myShip.targets.remove(self.id)
                    self.shipsTargetingMe.append(shipID)
                if self.id in myShip.alternateTargets:
                    myShip.alternateTargets.remove(self.id)
                if myShip.currentTarget == self:
                    myShip.setCurrentTarget()     
        
    def copyWhoTargetsMe(self, winningShipID):
        """Ship has changed sides, make all ships target this ship same as winningShip"""
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if self.id in myShip.targets:
                myShip.targets.remove(self.id)
            if self.id in myShip.alternateTargets:
                myShip.alternateTargets.remove(self.id)
                
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if winningShipID in myShip.targets:
                myShip.targets.append(self.id)
            if winningShipID in myShip.alternateTargets:
                myShip.alternateTargets.append(self.id)
            if myShip.currentTarget == self:
                myShip.setCurrentTarget()
    
    def tellEnemiesToTargetMeAgain(self):
        """I won an assault so I have to be targetable again"""
        for shipID in self.shipsTargetingMe:
            myShip = self.myGalaxy.ships[shipID]
            if self.id not in myShip.targets:
                myShip.targets.append(self.id)
        self.shipsTargetingMe = []
        
    def updateAllGUIValues(self):
        """If ship is selected and has GUI update it"""
        if self.myGalaxy.shipSelected == self:
            d = {'shipISP':self.currentISP,
                 'shipStrength':self.strength,
                 'shipAccel':self.accel,
                 'shipRotation':self.rotation,
                 'shipPower':self.currentPower,
                 'shipBattery':self.currentBattery,
                 'maxAssault':self.maxAssault}
            for position in self.positions:
                myQuad = self.quads[position]
                d[position+'Shields'] = myQuad.currentSP
                d[position+'Armor'] = myQuad.currentAP
                d[position+'Comps'] = myQuad.currentComps
            self.myGalaxy.shipInfo.updateAttributes(d)

    def updateMyGUIValue(self, attributeName, newValue):
        """Send signal to update only one value"""
        if self.myGalaxy.shipSelected == self:
            d = {attributeName:newValue}
            self.myGalaxy.shipInfo.updateAttributes(d)

    def setCollidemask(self):
        """Set the Ships Collidemask, which is a combination of ships allies"""
        friends = self.createFriendlyEmpireList()
        mask = 0
        for id in friends:
            id = int(id)
            mask = mask + (1<<id)
        self.collidemask = mask

    def createFriendlyEmpireList(self):
        """Return empireID list of all friendly empires"""
        friends = []
        for shipID, myShip in self.myGalaxy.ships.iteritems():
            if shipID not in self.targets and myShip.empireID not in friends:
                friends.append(myShip.empireID)
        return friends

    def setMyShipCounts(self):
        """Setup the Ship Counts and Goals based on Captain rank"""
        self.retargetGoal = globals.rankMods[self.myCaptain.rank]['retarget']
        self.retargetCount = globals.rankMods[self.myCaptain.rank]['retarget']

    def setKObj(self):
        size = {'tiny':0.35, 'small':0.5, 'large':1.0}
        kobj.KObj.__init__(self, self.name, self.posX, self.posY, size[self.myShipHull.size], self.facing, self.accel)

    def hitExternalRadius(self, myMissile):
        """Ships external Radius (AMS) has been breached"""
        if len(self.amsWeapons) == 0:
            self.amsTargets = []
        else:
            if myMissile not in self.amsTargets:
                self.amsTargets.append(myMissile)
    
    def hitWeaponRetargetRadius(self, otherShip):
        if otherShip not in self.alternateTargets:
            self.alternateTargets.append(otherShip)

    def hitRadius(self, myMissile):
        """Ships Radius (Hull) has been breached"""
        myMissile.hit(self)

    def addTargetShip(self, targetID):
        """Add Target Ship ID to list of targets for this ship"""
        self.targets.append(targetID)

    def addDrone(self, myDrone):
        """Keep Track of Drones being launched from ship"""
        self.drones.append(myDrone)

    def begin(self):
        """Initial ship commands at begining of simulation"""
        self.setMyShipCounts()
        self.setMyStatus()
        self.setTotalAmmoForWeapons()
        self.chargeBatteries()

    def setTotalAmmoForWeapons(self):
        """Set the Weapons totalAmmo state"""
        for myWeapon in self.activeWeapons:
            myWeapon.setTotalAmmo()
        for myWeapon in self.amsWeapons:
            myWeapon.setTotalAmmo()

    def chargeBatteries(self):
        """Charge the batteries before battle begins"""
        self.currentBattery = self.maxBattery
            
    def clearTargetShips(self):
        """Clear all Target Ships"""
        self.targets = []
        self.currentTarget = None

    def clearMyStatus(self):
        """Clear Calcualted Ship Attributes"""
        self.maxBattery = 0
        self.currentPower = 0
        self.thrust = 0.0
        self.rotation = 0.0
        self.radar = 0
        self.jamming = 0
        self.repair = 0
        self.mass = 0.0
        self.accel = 0.0
        self.maxAssault = 0
        self.assaultStrength = 0

    def destroyMe(self):
        """Destroy Ship"""
        if self.alive == 1:
            self.alive = 0
            if globals.serverMode == 0:
                self.shipsim.explode()
                self.shipsim.destroy()
                if self.jamming > 0:
                    self.myGalaxy.jamming[self.empireID] -= self.jamming
                if self.radar > 0 and self.empireID == self.myGalaxy.game.myEmpireID:
                    self.myGalaxy.myRadar -= self.radar

            # if I have any drones destroy them
            if len(self.drones) > 0:
                self.myGalaxy.removeDronesFromDestroyedCarrier(self)
            
            # remove my captain
            self.myCaptain.destroyMe()
            
            if self.underAssault == 1:
                self.myGalaxy.cancelAssault(self)
            self.myGalaxy.resultList.append('SHIP:%s DESTROYED, Count:%d' % (self.name, self.myGalaxy.count))
            self.myGalaxy.playSound('bomb7')       
            
    def retarget(self):
        """Look for nearest target"""
        if self.retargetCount < self.retargetGoal:
            self.retargetCount += 1
        else:
            self.retargetCount = 0
            self.setCurrentTarget()
            self.setMode()

    def setMode(self):
        """Set the ships mode"""
        if self.currentTarget != None and self.finishedAssault == 0:
            if self.isAssault == 1:
                if self.currentTarget != None:
                    self.mode = 'assault'
                else:
                    self.mode = 'escape'
            else:
                self.log.debug('COUNT: %s: %s TARGET-> %s' % (self.myGalaxy.count, self.name, self.currentTarget.name))
                ##self.myGalaxy.resultList.append('COUNT: %s: %s TARGET-> %s' % (self.myGalaxy.count, self.name, self.currentTarget.name))
                if ((len(self.activeWeapons) == 0 or (self.currentISP/self.myShipHull.maxISP) < 0.7)) and self.__module__ == 'anw.war.ship':
                    self.mode = 'escape'
                else:
                    range = funcs.getTargetRange(self.posX, self.posY, self.currentTarget.posX, self.currentTarget.posY)
                    if range <= self.range:
                        self.mode = 'engage'
                    else:
                        self.mode = 'close'
        else:
            self.mode == 'escape'
        if globals.serverMode == 0:
            self.shipsim.updateShipMode()

    def updateWeapons(self):
        """Go through all active weapons and check if they are ready"""
        self.readyWeapons = []
        self.setWeaponStatus()

        for myWeapon in self.activeWeapons:
            if myWeapon.preFireCheck() == 1:
                self.readyWeapons.append(myWeapon)
        self.alternateTargets = []

        if self.amsTargets != []:
            for myWeapon in self.amsWeapons:
                if myWeapon.preFireCheck() == 1:
                    self.readyWeapons.append(myWeapon)
            self.amsTargets = []

    def takeHit(self, amount, type, position, enemyShip):
        """Take damage from incoming weapon, direct damage to appropriate quadrant"""
        self.log.debug('COUNT: %s: %s TAKE HIT, Amount:%d, enemy:%s' % (self.myGalaxy.count, self.name, amount, enemyShip.name))
        myQuad = self.getQuadHit(position)

        if myQuad.currentSP > 0:
            hasShields = 1
            if myQuad.currentSP == myQuad.maxSP:
                sColor = 'g'
            elif myQuad.currentSP < (myQuad.maxSP/2):
                sColor = 'r'
            else:
                sColor = 'y'
        else:
            hasShields = 0
        if myQuad.currentAP > 0:
            hasArmor = 1
        else:
            hasArmor = 0

        myQuad.takeHit(amount, type, enemyShip)

        currentAmount = 0
        if hasShields == 1:
            color = 'guigreen'
        elif hasArmor == 1:
            color = 'guiblue1'
        else:
            color = 'guired'

        if globals.serverMode == 0:
            self.shipsim.displayDamage(amount, color, myQuad.position)

    def getQuadHit(self, position):
        return self.quads[position]

    def fireMyWeapons(self):
        """Fire all weapons that can fire"""
        for myWeapon in self.readyWeapons:
            myWeapon.fire()

        self.readyWeapons = []

    def getMyValue(self):
        """Return the (valueBV, valueCR, valueAL, valueEC, valueIA) in a tuple
        valueBV = credit conversion of ship"""
        valueBV = 0.0
        valueCR = 0.0
        valueAL = 0.0
        valueEC = 0.0
        valueIA = 0.0
        factorAL = globals.cityCRGen/globals.cityALGen
        factorEC = globals.cityCRGen/globals.cityECGen
        factorIA = globals.cityCRGen/globals.cityIAGen
        ratio = self.strength/100.0
        valueCR += self.myDesign.costCR*ratio
        valueAL += self.myDesign.costAL*ratio
        valueEC += self.myDesign.costEC*ratio
        valueIA += self.myDesign.costIA*ratio
        valueBV += (valueCR +
                    valueAL*factorAL +
                    valueEC*factorEC +
                    valueIA*factorIA) / 1000.0
        return (valueBV, valueCR, valueAL, valueEC, valueIA)

    def getMyShipInfo(self):
        """Return Ship info as dict"""
        d = self.getMyInfoAsDict()
        d['quads'] = self.getMyDictInfo('quads', 'getMyQuadInfo')
        d['targets'] = self.targets
        d['availSystems'] = self.availSystems
        d['oldAvailSystems'] = self.oldAvailSystems
        return d

    def getNearestTarget(self):
        """Look for nearest target of target type"""
        if self.myShipHull.abr in globals.targetPreference.keys():
            closestShip = self.getNearestPreference(self.myShipHull.abr)
            if closestShip != None:
                return closestShip
        closestRange = 99999
        closestShip = None
        for shipID in self.targets:
            enemyShip = self.myGalaxy.ships[shipID]
            if enemyShip.alive == 1:
                range = funcs.getTargetRange(self.posX, self.posY, enemyShip.posX, enemyShip.posY)
                if range < closestRange:
                    closestRange = range
                    closestShip = enemyShip
        if closestShip == None and self.myGalaxy.shipsUnderAssault() == 0:
            try:
                self.myGalaxy.endSimulation(self.empireID)
            except:
                pass
        return closestShip

    def getNearestPreference(self, myABR):
        """Get the nearest target of preferred hull type"""
        closestRange = 99999
        closestShip = None
        for shipID in self.targets:
            enemyShip = self.myGalaxy.ships[shipID]
            if enemyShip.alive == 1 and (enemyShip.myShipHull.abr in globals.targetPreference[myABR]):
                range = funcs.getTargetRange(self.posX, self.posY, enemyShip.posX, enemyShip.posY)
                if range < closestRange:
                    closestRange = range
                    closestShip = enemyShip
        return closestShip
    
    def getRepairCapacity(self):
        """Return the shipyard capacity required to perform full repairs"""
        return int(self.myDesign.getSYCRequired() * (1-(self.strength/100.0)))

    def hit(self, other, newPosX, newPosY, newFacing):
        """Called when I hit another object within collision system"""
        pass

    def lockWeapons(self, interval):
        """Cycle through operational weapons and increment target lock if required"""
        i = 0
        for myWeapon in self.activeWeapons:
            i += 1
            myWeapon.lockTarget(interval)
        for myWeapon in self.amsWeapons:
            myWeapon.lockTarget(interval)

    def updateWeaponStatus(self):
        """Update Weapons status if ship selected"""
        if self.myGalaxy.shipSelected == self:
            for position in self.positions:
                myQuad = self.quads[position] 
                for id in funcs.sortStringList(myQuad.weapons.keys()):
                    myWeapon = myQuad.weapons[id]
                    self.updateMyGUIValue('%sweapon%sStatus' % (position,id), myWeapon.operational)
                    self.updateMyGUIValue('%sweapon%sLock' % (position,id), myWeapon.currentLock)
                    self.updateMyGUIValue('%sweapon%sPower' % (position,id), myWeapon.currentPower)
                    if myWeapon.myWeaponData.ammo == 1 or myWeapon.droneID != '':
                        self.updateMyGUIValue('%sweapon%sAmmo' % (position,id), myWeapon.availAmmo)

    def move(self, interval, world):
        """Perform the Ship's Movement for one interval of time"""
        self.setCurrentAccel()
        self.decelOutsideBorder()
        self.dx = math.sin(math.radians(self.facing))
        self.dy = math.cos(math.radians(self.facing))

        if self.dRotation != 0:
            self.facing += (self.dRotation * self.rotation * interval)

        self.posX += (self.dx * interval * self.currentAccel)
        self.posY += (self.dy * interval * self.currentAccel)
        self.updatePos(self.posX, self.posY, self.facing)

    def setCurrentAccel(self):
        """If engines knocked out decelerate slowly"""
        if self.currentAccel != self.accel:
            if self.currentAccel != round(self.accel,1):
                if self.currentAccel < self.accel:
                    self.currentAccel += 0.01
                elif self.currentAccel > self.accel:
                    self.currentAccel -= 0.01

    def decelOutsideBorder(self):
        """If ship is outside border slow it down"""
        if self.isOutsideBorder():
            if self.rotation == 0:
                self.currentAccel = 0
            else:
                self.currentAccel = self.currentAccel/1.01

    def moveToSystem(self, systemGrid, systemID):
        """Move Ship to System"""
        self.systemGrid = systemGrid
        self.toSystem = systemID
        self.setAvailSystems()

    def removeDrone(self, myDrone):
        """Remove Drone from ships tracking of its drones"""
        self.drones.remove(myDrone)

    def resetData(self):
        """Reset ship data on end round"""
        self.alive = 1
        self.fromSystem = self.toSystem
        self.systemGrid = 5
        mySystem = self.myGalaxy.systems[self.toSystem]
        mySystem.availSYC += self.repair

    def powerWeapons(self, interval, availPower):
        """Power all available weapons, then return any unused power"""
        if self.allWeaponsPowered == 0:
            weaponList = []
            for position, myQuad in self.quads.iteritems():
                weaponIDList = []
                weaponIDList.extend(funcs.sortStringList(myQuad.weapons.keys()))
                for wID in weaponIDList:
                    weaponList.append(myQuad.weapons[wID])

            while availPower > 0 and self.allWeaponsPowered == 0:
                toCharge = []
                toChargeAMS = []
                # go through each quadrant looking for weapons to power
                for myWeapon in weaponList:
                    if myWeapon.operational == 1 and myWeapon.currentPower < myWeapon.myWeaponData.maxPower:
                        if 1 == myWeapon.myWeaponData.AMS:
                            toChargeAMS.append(myWeapon)
                        else:
                            toCharge.append(myWeapon)

                if len(toChargeAMS) == 0 and len(toCharge) == 0:
                    self.allWeaponsPowered = 1
                    return availPower

                #AMS are charged first and sequentially
                if len(toChargeAMS) != 0:
                    if availPower !=0:
                        for myW in toChargeAMS:
                            defecit=myW.myWeaponData.maxPower - myW.currentPower
                            if defecit >= availPower:
                                myW.currentPower+=availPower
                                availPower=0
                                break
                            else:
                                myW.currentPower=myW.myWeaponData.maxPower
                                availPower-=defecit

                #non-AMS weapons are charged concurrently; each gets an equal share of the available power 
                if len(toCharge) != 0:
                    kW=availPower/len(toCharge)
                    if kW !=0:
                        #print "tT:",len(toCharge),"aP:",availPower,"kW each:",kW
                        for myW in toCharge:
                            defecit=myW.myWeaponData.maxPower - myW.currentPower
                            if defecit >= kW:
                                myW.currentPower+=kW
                                availPower-=kW
                            else:
                                myW.currentPower=myW.myWeaponData.maxPower
                                availPower-=kW-defecit
                    else:
                        availPower=0

        return availPower

    def regenShields(self, interval, availPower):
        """Regenerate Shields"""
        remainder = availPower 
        if availPower != 0:
            toCharge = []
            for position, myQuad in self.quads.iteritems():
                if myQuad.maxSP > 0:
                    toCharge.append(myQuad)
            if len(toCharge) != 0:
                kW=availPower/len(toCharge)
                if kW != 0:
                    remainder = 0
                    for myQ in toCharge:
                        remainder += myQ.regenShields(kW, globals.rankMods[self.myCaptain.rank]['kWtoSPfactor'])
        return remainder

    def rotateToTarget(self):
        """Rotate ship depending on mode:
        'close' -> rotate towards target
        'assault' -> rotate towards target
        'escape' -> rotate away from target
        'engage' -> rotate best weapon towards target"""
        rotate = 0
        if self.isOutsideBorder():
            rotate = funcs.getTargetRotate(self.posX, self.posY, 0, 0, self.facing)
        elif self.currentTarget == None or self.myDesign.myShipHull.function == 'carrier':
            rotate = 1
        else:
            targetX = self.currentTarget.posX
            targetY = self.currentTarget.posY
            if self.mode in ['close','assault']:
                rotate = funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, self.facing)
            elif self.mode == 'escape':
                rotate = funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, self.facing)
                rotate = -rotate
            elif self.mode == 'engage':
                if len(self.readyWeapons) > 0:
                    myWeapon = self.readyWeapons[0]
                    rotate = funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, myWeapon.getMyFacing())
                elif len(self.activeWeapons) > 0:
                    myWeapon = self.activeWeapons[0]
                    rotate = funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, myWeapon.getMyFacing())

        self.dRotation = rotate

    def isOutsideBorder(self):
        """Return 1 if ship is outside border of simulator"""
        if (self.posX < -self.myGalaxy.worldWidth or self.posX > self.myGalaxy.worldWidth or
            self.posY < -self.myGalaxy.worldHeight or self.posY > self.myGalaxy.worldHeight):
            return 1
        return 0

    def setAvailSystems(self):
        """Determine which systems ship can warp to currently"""
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
            
    def shallIAssault(self, enemyShip):
        """Ship is colliding with enemy ship, decide if assault will take place"""
        if (self.isAssault == 1 and enemyShip.isAssault == 0 and 
            self.underAssault == 0 and enemyShip.underAssault == 0 and
            self.currentTarget == enemyShip):
            self.myGalaxy.setupAssaultBattle(self, enemyShip)
            
    def setCurrentTarget(self):
        """Set Current Target based on ship type"""
        if self.isAssault:
            self.setAssaultTarget()
        else:
            self.setWarshipTarget()
    
    def setAssaultTarget(self):
        """Set Current Target for Assault Ships"""
        if self.underAssault == 1:
            return
        closestRange = 99999
        closestShip = None
        for shipID in self.targets:
            enemyShip = self.myGalaxy.ships[shipID]
            if (enemyShip.alive == 1 and enemyShip.strength < 100 and
                enemyShip.underAssault == 0 and enemyShip.isTransport == 0
                and enemyShip.isAssault == 0 and enemyShip.positions != ['fore'] and
                self.canItakeEnemyShip(enemyShip) == 1):
                range = funcs.getTargetRange(self.posX, self.posY, enemyShip.posX, enemyShip.posY)
                if range < closestRange:
                    closestRange = range
                    closestShip = enemyShip
        if closestShip != None:
            self.currentTarget = closestShip
        return closestShip
    
    def canItakeEnemyShip(self, enemyShip):
        """Assault ships will only attack enemy ships that they have an advantage on"""
        if self.assaultStrength/enemyShip.getPersonStrength() > 1.5:
            return 1
        return 0
            
    def getPersonStrength(self):
        """All ships other then assault ships have a internal defence of its navel personel"""
        strength = self.myDesign.myShipHull.mass/200
        return strength
            
    def setWarshipTarget(self):
        """Set Ship Target based on nearest valid target"""
        # first look for closest target of target type
        closestShip = self.getNearestTarget()

        if closestShip == None and (self.targets != [] or self.takenOverByEmpire != ''):
            # No Targets available
            if self.myGalaxy.shipsUnderAssault() == 0:
                self.myGalaxy.count = self.myGalaxy.maxCount
        else:
            if self.currentTarget != closestShip:
                # target aquired
                self.currentTarget = closestShip

    def setExperience(self, damage, enemyShip):
        """Any Ship Captain that hits with a weapon, or gets hit by a weapon gains experience"""
        experience = damage/25.0
        if experience > 0:
            self.myCaptain.addExperience(experience)
            enemyShip.myCaptain.addExperience(experience)

    def setMyGalaxy(self, galaxyObject):
        """Set the Galaxy Object Owner of this Ship"""
        self.myGalaxy = galaxyObject
        galaxyObject.ships[self.id] = self

    def setMyCaptain(self, captainObject):
        """Assign the Captain to this ship"""
        self.myCaptain = captainObject
        self.captainID = captainObject.id
        captainObject.setMyShip(self.id)

    def setMyDesign(self, designObject):
        """Copy the Ship Design Attributes, Quads to ship"""
        self.myDesign = designObject
        self.designID = designObject.id
        self.componentdata = designObject.componentdata
        self.weapondata = designObject.weapondata
        self.myShipHull = designObject.myShipHull
        designAttrDict = designObject.getMyInfoAsDict()
        self.currentISP = self.myShipHull.maxISP
        self.currentPower = designAttrDict['maxPower']
        self.maxBattery = designAttrDict['maxBattery']
        self.thrust = designAttrDict['thrust']
        self.rotation = designAttrDict['rotation']
        self.radar = designAttrDict['radar']
        self.jamming = designAttrDict['jamming']
        self.repair = designAttrDict['repair']
        self.maxAssault = designAttrDict['maxAssault']
        self.mass = self.myShipHull.mass

        for position, dQuad in designObject.quads.iteritems():
            newQuad = quad.Quad(dQuad.getMyInfoAsDict())
            newQuad.setMyParent(self)
            # weapons have to be created first
            for id, weap in dQuad.weapons.iteritems():
                newWeap = weapon.Weapon(weap.getMyInfoAsDict())
                newWeap.setMyQuad(newQuad)
            for id, comp in dQuad.components.iteritems():
                newComp = component.Component(comp.getMyInfoAsDict())
                newComp.setMyQuad(newQuad)
            newQuad.setMyStatus()
            self.quads[newQuad.position] = newQuad
            newQuad.resetDefences()
            newQuad.reloadAmmo()

        self.name = designObject.name + '-' + self.id
        self.setMyStrength()
        if 'AS' in self.myShipHull.abr:
            self.isAssault = 1
        else:
            self.isAssault = 0

    def setFromDict(self, designObject, myShipDict):
        """setup this ship according to the design object and ship dictionary info given"""
        self.myDesign = designObject
        self.designID = designObject.id
        self.componentdata = designObject.componentdata
        self.weapondata = designObject.weapondata
        self.myShipHull = designObject.myShipHull
        designAttrDict = designObject.getMyInfoAsDict()
        self.currentISP = myShipDict['currentISP']

        for position, dQuad in myShipDict['quads'].iteritems():
            newQuad = quad.Quad(dQuad)
            newQuad.setMyParent(self)
            # weapons have to be created first
            for id, dWeap in dQuad['weapons'].iteritems():
                newWeap = weapon.Weapon(dWeap)
                newWeap.setMyQuad(newQuad)
            for id, dComp in dQuad['components'].iteritems():
                newComp = component.Component(dComp)
                newComp.setMyQuad(newQuad)
            newQuad.setMyStatus()
            self.quads[newQuad.position] = newQuad
            newQuad.resetDefences()
            newQuad.reloadAmmo()

        self.setMyStatus()
        self.name = designObject.name + '-' + self.id

    def setMyStrength(self):
        """Set the ships strength from 1 to 100%"""
        ispRatio = float(self.currentISP/self.myShipHull.maxISP)
        myComponents = 0
        designComponents = 0
        for position, myQuad in self.quads.iteritems():
            myComponents += len(myQuad.components)
        for position, myQuad in self.myDesign.quads.iteritems():
            designComponents += len(myQuad.components)

        self.strength = (ispRatio * float(myComponents)/float(designComponents))*100.0

    def setMyStatus(self):
        """Set the status of all calculated attributes"""
        self.clearMyStatus()
        self.mass = self.myShipHull.mass
        for position, myQuad in self.quads.iteritems():
            self.maxBattery += myQuad.maxBattery
            self.currentPower += myQuad.maxPower
            self.thrust += myQuad.thrust
            self.rotation += myQuad.rotation
            self.radar += myQuad.radar
            self.jamming += myQuad.jamming
            self.repair += myQuad.repair
            self.mass += myQuad.mass
            self.maxAssault += myQuad.maxAssault

        # scale back attributes if internal structure has been hit
        ratio = self.currentISP/self.myShipHull.maxISP
        self.currentPower = self.currentPower * ratio
        self.thrust = self.thrust * ratio
        self.rotation = self.rotation * ratio

        self.accel = self.myDesign.getAccel(self.thrust, self.mass)
        self.accel = self.accel

        self.rotation = self.myDesign.getRotation(self.rotation, self.mass)
        self.rotation = self.rotation
        self.setMyStrength()
        self.setWeaponStatus()
        self.setRange()
        self.setAssaultStrength(ratio)
        
    def setAssaultStrength(self, ratio):
        """Determine the Assault Strength of ship based on damage"""
        assaultStrength = int(float(self.maxAssault) * ratio)
        if self.isAssault == 1:
            self.assaultStrength = assaultStrength
        else:
            self.assaultStrength = assaultStrength + self.getPersonStrength()

    def setRepairCost(self):
        """Set the repair cost of Starship"""
        # first take into account the ship hull which is based on internal structure points
        ratio = 1.0 - (self.currentISP/self.myShipHull.maxISP)
        CR = int(self.myShipHull.costCR*ratio)
        AL = int(self.myShipHull.costAL*ratio)
        EC = int(self.myShipHull.costEC*ratio)
        IA = int(self.myShipHull.costIA*ratio)

        # compare to ship design, add costs of replacement
        for position, myQuad in self.quads.iteritems():
            designQuad = self.myDesign.quads[position]
            weaponsInQuad = []
            # look for missing components
            for componentID in designQuad.components.keys():
                if componentID not in myQuad.components:
                    missingComponent = designQuad.components[componentID]
                    if missingComponent.weaponID == '':
                        # regular component
                        CR += missingComponent.myComponentData.costCR
                        AL += missingComponent.myComponentData.costAL
                        EC += missingComponent.myComponentData.costEC
                        IA += missingComponent.myComponentData.costIA
                    elif missingComponent.weaponID not in weaponsInQuad:
                        # component part of weapon, weapon must be replaced
                        weaponsInQuad.append(missingComponent.weaponID)

            # go through weapons that were damaged in this quadrant
            for weaponID in weaponsInQuad:
                damagedWeapon = designQuad.weapons[weaponID]
                CR += damagedWeapon.myWeaponData.costCR
                AL += damagedWeapon.myWeaponData.costAL
                EC += damagedWeapon.myWeaponData.costEC
                IA += damagedWeapon.myWeaponData.costIA

        self.repairCost = [CR,AL,EC,IA]

    def getCurrentResourceValue(self):
        """Return current value including repairs required in (AL, EC, IA)"""
        AL = self.myDesign.costAL - self.repairCost[1]
        EC = self.myDesign.costEC - self.repairCost[2]
        IA = self.myDesign.costIA - self.repairCost[3]
        return (AL, EC, IA)

    def setSystemGrid(self):
        """Take the ship from and to system to decide its systemGrid Attribute"""
        fromSystem = self.myGalaxy.systems[self.fromSystem]
        toSystem = self.myGalaxy.systems[self.toSystem]
        self.systemGrid = funcs.getMapQuadrant(toSystem, self, fromSystem.x, fromSystem.y,
                                               toSystem.x, toSystem.y)

    def setDesiredPosition(self, x, y):
        """Set the Ships desired position in quadrant"""
        (self.setX, self.setY) = (x , y)

    def setPosition(self):
        """Set the ship posX, posY for battle using setX, setY, and fromSystem, toSystem"""
        # determine posX, posY for battle
        (x1,y1) = globals.battlemapQuadrants[self.systemGrid]
        self.posX = x1+self.setX
        self.posY = y1+self.setY

    def setRange(self):
        """Determine Ship Range to my Target"""
        # first determine ranges
        if len(self.activeWeapons) > 0:
            myPrimaryWeapon = self.activeWeapons[0]
            self.range = myPrimaryWeapon.myWeaponData.range * 1.0
        else:
            # no weapons left RUN
            self.mode = 'escape'
            self.range = 99999

    def setWeaponStatus(self):
        """Go through all ship weapons and order them from most damaging to least
        ignore ones that are damaged or out of ammo"""
        self.readyWeapons = []
        self.activeWeapons = []
        self.amsWeapons = []
        weaponValues = {}
        self.externalRadius = self.radius
        for position, myQuad in self.quads.iteritems():
            for id, myWeapon in myQuad.weapons.iteritems():
                if myWeapon.operational == 1:
                    if myWeapon.myWeaponData.AMS == 0:
                        weaponValue = myWeapon.getMyValue()
                        weaponValues[myWeapon.myQuad.position + '-' + myWeapon.id] = weaponValue
                        i = 0
                        for weapon in self.activeWeapons:
                            if weaponValues[weapon.myQuad.position + '-' + weapon.id] < weaponValue:
                                self.activeWeapons.insert(i, myWeapon)
                                break
                            i += 1
                        if myWeapon not in self.activeWeapons:
                            self.activeWeapons.append(myWeapon)
                    else:
                        self.amsWeapons.append(myWeapon)
                        self.externalRadius = myWeapon.myWeaponData.range

    def unloadRegiment(self, regimentID):
        """Attempt to unload Regiment from Ship"""
        if regimentID in self.myRegiments:
            self.myRegiments.remove(regimentID)
            return 1
        else:
            return 'unable to unload Regiment'

    def update(self, interval, world):
        """perform all ship commands for an interval of time"""
        self.count += 1
        if self.underAssault == 1 or self.alive == 0:
            return
        self.retarget()
        self.updateWeapons()

        availPower = self.currentBattery + (self.currentPower * interval)
        self.currentBattery = 0
        
        availPower = self.regenShields(interval, availPower)
        availPower = self.powerWeapons(interval, availPower)

        self.lockWeapons(interval)
        self.updateWeaponStatus()

        # place remaining power into batteries
        if self.maxBattery > 0 and availPower > 0:
            self.currentBattery += availPower
            if self.currentBattery > self.maxBattery:
                self.currentBattery = self.maxBattery

        if self.maxBattery > 0:
            self.updateMyGUIValue('shipBattery', self.currentBattery)

        # fire weapons
        if len(self.readyWeapons) > 0:
            self.fireMyWeapons()

        # rotate ship to target
        self.rotateToTarget()

        # move ship
        self.move(interval, world)

        ### calculate the variable delay
        ##if self.threshold:
            ##value = max( abs(self.velocityX), abs(self.velocityY), abs(self.turnRate) )
            ##if value < self.threshold:
                ##self.uDelay = 1.0 - (value / self.threshold)
            ##else:
                ##self.uDelay = 0

        ##return self.alive
