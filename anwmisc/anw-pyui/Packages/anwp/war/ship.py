# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# ship.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a starship
# ---------------------------------------------------------------------------
import types
import math
import random
import logging

import anwp.sl.utils
import anwp.sl.sim
import anwp.sl.entity
import anwp.func.root
import quad
import component
import weapon
import shield
import anwp.func.funcs
import anwp.war.statistics

class Ship(anwp.func.root.Root, anwp.sl.entity.Entity):
    """xA StarShip contains quads, components, weapons, and a captain"""
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
        self.maxTransport = int() # max regiments that can be transported
        self.currentTransport = int() # current number of regiments in pods on ship
        self.repairCost = list() # cost to repair [CR,AL,EC,IA]
        self.empireID = str() # empire owner (id)
        self.systemGrid = int() # grid of ship within system (1-9)
        self.fromSystem = str() # id of planet ship was at
        self.toSystem = str() # id of planet ship moved to
        self.range = int() # range ship wants to stay at with target ship
        self.facing = float() # initial ship facing (degrees, 0 faces north)
        self.stats = anwp.war.statistics.Statistics()
        self.myRegiments = list() # list of regiments ship is currently transporting
        self.accel = float() # current max acceleration of ship
        
        self.defaultAttributes = ('id', 'name', 'designID', 'captainID', 'currentISP',
                                  'currentBattery', 'maxBattery', 'currentPower', 'mass',
                                  'thrust', 'rotation', 'radar', 'jamming', 'repair', 'facing', 
                                  'posX', 'posY', 'setX', 'setY', 'strength', 'maxTransport', 
                                  'currentTransport', 'repairCost','empireID',
                                  'systemGrid','fromSystem','toSystem','range','facing','accel')
        self.setAttributes(args)
        
        self.myGalaxy = None # Actual Galaxy object this Ship contained in
        self.myCaptain = None # Referenced
        self.myDesign = None # Referenced
        self.componentdata = None # referenced
        self.weapondata = None # referenced
        self.myShipHull = None # referenced
        self.currentTarget = None # current Target of Ship
        self.missiles = {} # key = gid, value = missile object
        self.drones = {} # key = gid, value = drone object
        self.targets = [] # list of target ship ID's
        self.amsTargets = [] # list of all potential AMS Targets
        self.shipsTargetingMe = [] # list of all enemy ships targetting me
        self.availSystems = [] # list of all potential systems ship can warp to
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

        self.amsWeapons = [] 
        self.activeWeapons = [] # list of weapons sorted by priority
        self.amsWeapons = [] # list of ams weapons sorted by priority
        self.readyWeapons = [] # list of weapons sorted by priority and ready to fire
        self.mode = 'close' # modes are close, escape, engage
        
        self.spewWait = 1.0
        self.timeSinceSpew = 0.0 
        self.spewRange = 0
        self.spewQuadrant = None
        self.spewQuadrantOffset = None
        self.spewQuadrantAngle = None
    
    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['log']             # remove stuff not to be pickled
        return odict

    def __setstate__(self,dict):
        log=logging.getLogger('ship')
        self.__dict__.update(dict)
        self.log=log
    
    def addAMSTarget(self, newTarget):
        """xAdd a new target to AMS list"""
        self.amsTargets.append(newTarget)
        if self not in newTarget.shipsTargetingMe:
            newTarget.shipsTargetingMe.append(self)
    
    def addTargetShip(self, targetID):
        """xAdd Target Ship ID to list of targets for this ship"""
        self.targets.append(targetID)
    
    def addMissile(self, missile):
        """xAdd Missile to world"""
        self.missiles[missile.gid] = missile
        
    def addDrone(self, drone):
        """xAdd Drone to world"""
        self.drones[drone.gid] = drone
    
    def begin(self):
        """xInitial ship commands at begining of simulation"""
        self.setMyStatus()
        self.postEvent('retarget', 0)
        self.postEvent('updateWeapons', 0)
    
    def clearEvents(self, action=''):
        self.myGalaxy.shipEventManager.clearEventsFor(self.gid, action)
    
    def clearTargetShips(self):
        """xClear all Target Ships"""
        self.targets = []
        self.currentTarget = None
    
    def clearMyStatus(self):
        """xClear Calcualted Ship Attributes"""
        self.maxBattery = 0
        self.currentPower = 0
        self.thrust = 0.0
        self.rotation = 0.0
        self.radar = 0
        self.jamming = 0
        self.repair = 0
        self.mass = 0.0
        self.accel = 0.0
        self.maxTransport = 0
        self.currentTransport = 0
    
    def destroyMe(self):
        """xDestroy Ship"""
        if self.alive == 1:
            self.alive = 0
            
            # set an explosion sim
            if self.myShipHull.size == 'small':
                self.explode(random.randrange(15,25,1), 30, True)
            elif self.myShipHull.size == 'large':
                length = self.graphicsObject.sourceObject.width/4
                self.explode(random.randrange(40, 80, 1), 60, True)
            
            # tell simulator to remove selector if its on me
            if self.myGalaxy.shipInfo <> None:
                if self.myGalaxy.shipInfo.ship == self:
                    self.myGalaxy.onSelectNoSim()
            
            # if I have any drones destroy them
            for droneGID in self.drones.keys():
                myDrone = self.drones[droneGID]
                myDrone.destroyMe()
            
            # remove my captain
            self.myCaptain.destroyMe()
            
            # log
            self.myGalaxy.resultList.append('SHIP:%s DESTROYED, Count:%d' % (self.name, self.myGalaxy.count))
            if self.myGalaxy.simMode == 'server':
                # if I have any regiments destroy them
                for regimentID in self.myRegiments:
                    myRegiment = self.myGalaxy.myGalaxy.regiments[regimentID]
                    self.myGalaxy.resultList.append('REGIMENT:%s DESTROYED, Count:%d' % (myRegiment.name, self.myGalaxy.count))
                    myRegiment.destroyMe()
                
                # if I unloaded any regiments this round, destroy them
                for regimentID in self.myGalaxy.myGalaxy.regiments.keys():
                    myRegiment = self.myGalaxy.myGalaxy.regiments[regimentID]
                    if myRegiment.fromShip == self.id:
                        self.myGalaxy.resultList.append('REGIMENT:%s DESTROYED, Count:%d' % (myRegiment.name, self.myGalaxy.count))
                        myRegiment.destroyMe()
                            
            self.myGalaxy.game.app.playSound('bomb7')    

    def explode(self, bits=10, speed=10, multiring=False):
        """xCreate the an Explosion Sims"""
        if self.myGalaxy.simMode == 'client':
            import anwp.sims
            # create sim
            x = self.posX
            y = self.posY
            color1 = self.myGalaxy.empires[self.empireID].color1
            color2 = self.myGalaxy.empires[self.empireID].color2
            sizeimage = [1,1,1,1,1,1,2,2,2,3]
            images = []
            for size in sizeimage:
                images.append("%sjunk%d_%s_%s.png" % (self.myGalaxy.game.app.simImagePath, size, color1, color2))

            angle = 0
            dontblow = self.facing + self.spewQuadrantAngle
            dontblow = dontblow % 360
            arc = random.randrange(0, 90, 1)
            for r in range(bits):
                angle += 360 / bits
                high = dontblow + arc
                low = dontblow - arc
                if angle < high and angle > low:
                    # do not explode, as we are in that arc.
                    continue
                
                selection = random.randrange(0, len(sizeimage), 1)
                explosion = anwp.sl.sim.SimObject(anwp.sims.categories.JunkCategory(images[selection], sizeimage[selection]), None)
                explosion.turnRate = random.randrange(-360, 360, 1)
                explosion.life = random.randrange(1,5,1)
                force = 2
                sp = speed + random.randrange(speed-speed/2,speed*1.5,1)

                self.myGalaxy.world.addToWorld(explosion, x, y, angle, sp, force)
                if multiring:
                    sp2 = speed/2 + random.randrange(-speed/2,speed,1)
                    explosion2 = anwp.sl.sim.SimObject(anwp.sims.categories.JunkCategory(images[selection], sizeimage[selection]), None)
                    explosion2.turnRate = random.randrange(-360, 360, 1)
                    explosion2.life = random.randrange(1,5,1)
                    self.myGalaxy.world.addToWorld(explosion2, x, y, angle, sp2, force/2)
    
    def event_retarget(self):
        """xLook for nearest target"""
        self.setCurrentTarget()
        if self.currentTarget <> None:
            self.log.debug('COUNT: %s: %s TARGET-> %s' % (self.myGalaxy.count, self.name, self.currentTarget.name))
            # choose proper mode
            if ((len(self.activeWeapons) == 0 or (self.currentISP/self.myShipHull.maxISP) < 0.7)) and self.__module__ == 'anwp.war.ship':
                self.mode = 'escape'
            else:
                range = anwp.func.funcs.getTargetRange(self.posX, self.posY, self.currentTarget.posX, self.currentTarget.posY)
                if range <= self.range:
                    self.mode = 'engage'
                else:
                    self.mode = 'close'
        
        # decide when to next look for another target
        retarget = anwp.func.globals.rankMods[self.myCaptain.rank]['retarget']
        self.postEvent('retarget', retarget)
    
    def event_updateWeapons(self):
        """xGo through all active weapons and check if they are ready"""
        self.readyWeapons = []
        self.setWeaponStatus()
        
        for myWeapon in self.activeWeapons:
            if myWeapon.preFireCheck() == 1:
                self.readyWeapons.append(myWeapon)
        
        for myWeapon in self.amsWeapons:
            if myWeapon.preFireCheck() == 1:
                self.readyWeapons.append(myWeapon)
        
        # decide when to next ready weapons
        retarget = anwp.func.globals.rankMods[self.myCaptain.rank]['weaptarget']
        self.postEvent('updateWeapons', retarget)
    
    def event_takeHit(self, amount, type, position, enemyShip):
        """xTake damage from incoming weapon, direct damage to appropriate quadrant"""
        self.log.debug('COUNT: %s: %s TAKE HIT, Amount:%d, enemy:%s' % (self.myGalaxy.count, self.name, amount, enemyShip.name))
        myQuad = self.quads[position]
        
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
        id = '%s-%s' % (self.gid, position)
        if id in self.myGalaxy.damages:
            currentAmount = self.myGalaxy.damages[id][1]
        
        self.myGalaxy.damages[id] = [self, currentAmount+amount,'', 40]

        # decide damage color (green=shields/armor, red=internal)
        if hasShields == 1:
            color = 'green'
            # add shield sim
            imageFileName = '%sshield_%s.png' % (self.myGalaxy.game.app.genImagePath, sColor)
            category = anwp.sims.categories.DirectFireCategory(imageFileName, 'm')
            sim = shield.Shield(category, myQuad)
            self.myGalaxy.world.addToWorld(sim, sim.posX, sim.posY, sim.facing, 0, 1)
        elif hasArmor == 1:
            color = 'blue'
        else:
            color = 'red'
        self.myGalaxy.damages[id][2] = color
    
    def fireMyWeapons(self):
        """xFire all weapons that can fire"""
        # perform preFire Checks on each weapon
        for myWeapon in self.readyWeapons:
            myWeapon.fire()
        
        self.readyWeapons = []
    
    def getMyValue(self):
        """xReturn the (valueBV, valueCR, valueAL, valueEC, valueIA) in a tuple
        valueBV = credit conversion of ship"""
        valueBV = 0.0
        valueCR = 0.0
        valueAL = 0.0
        valueEC = 0.0
        valueIA = 0.0
        factorAL = anwp.func.globals.cityCRGen/anwp.func.globals.cityALGen
        factorEC = anwp.func.globals.cityCRGen/anwp.func.globals.cityECGen
        factorIA = anwp.func.globals.cityCRGen/anwp.func.globals.cityIAGen
        ratio = self.strength/100.0
        valueCR += self.myDesign.costCR*ratio
        valueAL += self.myDesign.costAL*ratio
        valueEC += self.myDesign.costEC*ratio
        valueIA += self.myDesign.costIA*ratio
        valueBV += (valueCR +
                    valueAL*factorAL +
                    valueEC*factorEC +
                    valueIA*factorIA)
        return (valueBV, valueCR, valueAL, valueEC, valueIA)

    def getMyShipInfo(self):
        """xReturn Ship info as dict"""
        d = self.getMyInfoAsDict()
        d['quads'] = self.getMyDictInfo('quads', 'getMyQuadInfo')
        d['targets'] = self.targets
        d['availSystems'] = self.availSystems
        return d

    def getNearestTarget(self):
        """xLook for nearest target of target type"""
        closestRange = 99999
        closestShip = None
        for shipID in self.targets:
            enemyShip = self.myGalaxy.ships[shipID]
            if enemyShip.alive == 1:
                range = anwp.func.funcs.getTargetRange(self.posX, self.posY, enemyShip.posX, enemyShip.posY)
                if range < closestRange:
                    closestRange = range
                    closestShip = enemyShip
        return closestShip

    def getRepairCapacity(self):
        """xReturn the shipyard capacity required to perform full repairs"""
        return int(self.myDesign.getSYCRequired() * (1-(self.strength/100.0)))

    def hit(self, other, newPosX, newPosY, newFacing):
        """xCalled when I hit another object within collision system"""
        pass
    
    def loadRegiment(self, regimentID):
        """xAttempt to load a regiment into an available ship pod"""
        if self.currentTransport < self.maxTransport and regimentID not in self.myRegiments:
            self.myRegiments.append(regimentID)
            return 1
        else:
            return 'Unable to load regiment into ship'
    
    def lockWeapons(self, interval):
        """xCycle through operational weapons and increment target lock if required"""
        for myWeapon in self.activeWeapons:
            myWeapon.lockTarget(interval)
        for myWeapon in self.amsWeapons:
            myWeapon.lockTarget(interval)

    def move(self, interval, world):
        """xPerform the Ship's Movement for one interval of time"""
        if self.currentAccel <> self.accel:
            if self.currentAccel < self.accel:
                self.currentAccel = self.accel
            else:
                self.currentAccel -= 1
        accel = self.currentAccel
        
        # movement is intirely based on current facing
        self.dx = math.cos(anwp.sl.utils.toRadians(self.facing))
        self.dy = math.sin(anwp.sl.utils.toRadians(self.facing))
        
        # split accel into x and y directions based on desires of ship ai
        xAccel = self.dx*accel
        yAccel = self.dy*accel
        
        # velocity = accel * time
        dx = xAccel * interval
        dy = yAccel * interval
        
        # velocity = accel * time
        self.velocityX = xAccel * interval
        self.velocityY = yAccel * interval
        
        # move ship position (distance = velocity * time)
        newPosX = self.posX + (self.velocityX * interval)
        newPosY = self.posY + (self.velocityY * interval)

        if self.dRotation <> 0:
            newFacing = self.facing + (self.dRotation * self.rotation * interval)
            newFacing = newFacing % 360
        else:
            newFacing = self.facing
            
        if world.canMove(self, newPosX, newPosY, newFacing):
            self.posX = newPosX
            self.posY = newPosY
            self.facing = newFacing
            world.move(self, newPosX, newPosY, newFacing)
            self.graphicsObject.setState(newPosX, newPosY, newFacing)

    def moveToSystem(self, systemGrid, systemID):
        """xMove Ship to System"""
        self.systemGrid = systemGrid
        self.toSystem = systemID
        # update the status of any regiments
        for regimentID, myRegiment in self.myGalaxy.regiments.iteritems():
            if myRegiment.empireID == self.empireID:
                if myRegiment.fromShip == self.id and myRegiment.state == 2:
                    myRegiment.setMovement()
                if myRegiment.state in (1,2) and myRegiment.fromSystem == self.fromSystem:
                    myRegiment.setMyPotentialOrders()
        self.setAvailSystems()

    def damageSpew(self, interval, world):
        if float(self.currentISP) / float(self.myShipHull.maxISP) < self.spewWait: 
            self.spewWait = (float(self.currentISP) / float(self.myShipHull.maxISP)) / 6

        if self.spewWait < 1.0 and self.timeSinceSpew >= self.spewWait:
            #spew
            imageFileName = '%ssmoke.png' % self.myGalaxy.game.app.genImagePath     


            explosion = anwp.sl.sim.SimObject(anwp.sims.categories.JunkCategory(imageFileName, 2), None)
            explosion.life = 3
            explosion.turnRate = random.randrange(-360, 360, 1)
            x, y = self.findOffset(self.facing + self.spewQuadrantOffset, self.spewRange)
            explosion.setState(x, y, self.rotation, self.accel)
            explosion.facing = random.randrange(0, 360, 1)
            force = 2
            world.addToWorld(explosion, x, y, explosion.facing + random.randrange(-8, 8, 1), 6, force)
            self.timeSinceSpew = 0
        else:
            self.timeSinceSpew += interval
        
    def postEvent(self, action, delay, *args):
        return self.myGalaxy.shipEventManager.postEvent(self.gid, action, delay ,args)

    def removeMissile(self, gid):
        """xRemove Missile object from dict"""
        try:
            del self.missiles[gid]
        except:
            pass
    
    def removeDrone(self, gid):
        """xRemove Drone object from dict"""
        try:
            del self.drones[gid]
        except:
            pass

    def resetData(self):
        """xReset ship data on end round"""
        # reset movement
        self.fromSystem = self.toSystem
        self.systemGrid = 5
        
        # set shipyard capacity for ships with repair ability
        mySystem = self.myGalaxy.systems[self.toSystem]
        mySystem.availSYC += self.repair

    def powerWeapons(self, interval, availPower):
        """xPower all available weapons, then return any unused power """
        #print "cB:",self.currentBattery,"i:",interval,"cP:",self.currentPower
        #availPower = self.currentBattery + (self.currentPower * interval)
        self.currentBattery = 0
        # only proceed if weapons are not powered up

        if self.allWeaponsPowered == 0:
            weaponList = []
            for position, myQuad in self.quads.iteritems():
                weaponIDList = []
                weaponIDList.extend(anwp.func.funcs.sortStringList(myQuad.weapons.keys()))
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
        """xRegenerate Shields"""
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
                       remainder += myQ.regenShields(kW, anwp.func.globals.rankMods[self.myCaptain.rank]['kWtoSPfactor'])
        return remainder

    def rotateToTarget(self):
        """xRotate ship depending on mode:
        'close' -> rotate towards target
        'escape' -> rotate away from target
        'engage' -> rotate best weapon towards target
        """x
        rotate = 0
        dist = 0
        if self.accel == 0:
            dist = 200
        else:
            dist = 20000.0 * (self.rotation/self.accel)
        if dist > 600:
            dist = 600
        elif dist < 300:
            dist = 300
        # check if ship is going to approach border
        if (self.posX < dist or self.posY < dist or 
            self.posX > self.myGalaxy.worldWidth-dist or self.posY > self.myGalaxy.worldHeight-dist):
            rotate = anwp.func.funcs.getTargetRotate(self.posX, self.posY, 5000, 5000, self.facing)
        
        elif self.currentTarget == None:
            rotate = 1
        else:
            # otherwise rotate using state
            targetX = self.currentTarget.posX
            targetY = self.currentTarget.posY
            if self.mode == 'close':
                rotate = anwp.func.funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, self.facing)
            elif self.mode == 'escape':
                rotate = anwp.func.funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, self.facing)
                rotate = -rotate
            elif self.mode == 'engage':
                if len(self.readyWeapons) > 0:
                    myWeapon = self.readyWeapons[0]
                    rotate = anwp.func.funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, myWeapon.getMyFacing())
                elif len(self.activeWeapons) > 0:
                    myWeapon = self.activeWeapons[0]
                    rotate = anwp.func.funcs.getTargetRotate(self.posX, self.posY, targetX, targetY, myWeapon.getMyFacing())
        
        self.dRotation = rotate

    def sacrificeRegiments(self):
        """xShip has taken pod damage which requires some Regiments to perish in battle
        Return list of which regiments died in battle"""
        resultList = []
        resultList.append('%s has taken marine pod damage during battle Following Regiments Destroyed:' % self.name)
        
        for regimentID in self.myRegiments:
            if self.currentTransport > self.maxTransport:
                myRegiment = self.myGalaxy.regiments[regimentID]
                resultList.append('%s Regiment Destroyed in Ship Battle' % myRegiment.name)
                myRegiment = None
                self.myGalaxy.removeRegiment(regimentID)
                self.myRegiments.remove(regimentID)
                self.currentTransport -= 1
            else:
                break
        
        return resultList

    def setAvailSystems(self):
        """xDetermine which systems ship can warp to currently"""
        # check if any Regiments have invaded/reinforced System from this ship
        self.availSystems = []
        for regimentID in self.myRegiments:
            myRegiment = self.myGalaxy.regiments[regimentID]
            if myRegiment.state == 4:
                return # ship cannot move unless regiment is picked up again
        
        if self.toSystem <> self.fromSystem:
            self.availSystems.append(self.fromSystem)
            return # if already moved, ship can only go back to original system
        elif self.toSystem == self.fromSystem:
            # ship has not moved return connected systems
            mySystem = self.myGalaxy.systems[self.fromSystem]
            if mySystem.myEmpireID == self.empireID or anwp.func.globals.diplomacy[self.myGalaxy.empires[mySystem.myEmpireID].diplomacy[self.empireID].diplomacyID]['alliance'] == 1:
                # ship can use systems warp gates since its in alliance or same owner
                self.availSystems = mySystem.getAllConnections()
            else:
                # ship can only go to adjacent systems that it is allowed to go to
                for otherSystemID in mySystem.connectedSystems:
                    otherSystem = self.myGalaxy.systems[otherSystemID]
                    if otherSystem.myEmpireID == self.empireID or anwp.func.globals.diplomacy[self.myGalaxy.empires[otherSystem.myEmpireID].diplomacy[self.empireID].diplomacyID]['move'] == 1:
                        self.availSystems.append(otherSystemID)
    
    def setCurrentTarget(self):
        """xSet Ship Target based on nearest valid target"""
        # first look for closest target of target type
        closestShip = self.getNearestTarget()
        
        if closestShip == None and self.targets <> []:
            # No Targets available, simulation over
            self.myGalaxy.count = self.myGalaxy.maxCount
        else:
            if self.currentTarget <> closestShip:
                # target aquired
                self.currentTarget = closestShip

    def setExperience(self, damage, enemyShip):
        """xAny Ship Captain that hits with a weapon, or gets hit by a weapon gains experience"""
        # experience is based on weapon damage to target hp
        experience = damage/25.0
        if experience > 0:
            self.myCaptain.addExperience(experience)
            enemyShip.myCaptain.addExperience(experience)
    
    def setMyGalaxy(self, galaxyObject):
        """xSet the Galaxy Object Owner of this Ship"""
        self.myGalaxy = galaxyObject
        galaxyObject.ships[self.id] = self
    
    def setMyCaptain(self, captainObject):
        """xAssign the Captain to this ship"""
        self.myCaptain = captainObject
        self.captainID = captainObject.id
        captainObject.setMyShip(self.id)
    
    def setMyDesign(self, designObject):
        """xCopy the Ship Design Attributes, Quads to ship"""
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
        self.maxTransport = designAttrDict['maxTransport']
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
        self.randomizeJunkTrail()

    
    def setFromDict(self, designObject, myShipDict):
        """xsetup this ship according to the design object and ship dictionary info given"""
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
        self.randomizeJunkTrail()
    
    def setMyEntity(self, category, posX, posY, facing):
        """xSetup the Game Entity for this Ship"""
        anwp.sl.entity.Entity.__init__(self, category, None)
        # maintain these attributes (reset by sim init)
        self.posX = posX
        self.posY = posY
        self.facing = facing
    
    def setMyStrength(self):
        """xSet the ships strength from 1 to 100%"""
        ispRatio = float(self.currentISP/self.myShipHull.maxISP)
        myComponents = 0
        designComponents = 0
        for position, myQuad in self.quads.iteritems():
            myComponents += len(myQuad.components)
        for position, myQuad in self.myDesign.quads.iteritems():
            designComponents += len(myQuad.components)
        
        self.strength = (ispRatio * float(myComponents)/float(designComponents))*100.0
        
    def setMyStatus(self):
        """xSet the status of all calculated attributes"""
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
            self.maxTransport += myQuad.maxTransport
            
            if self.spewQuadrant == None and myQuad.components == {}:
                # this must be the first quadrant to be damaged.
                self.spewQuadrant = position
                if self.spewQuadrant == "fore":
                    self.spewQuadrantOffset = 0 + random.randrange(-20, 20, 1)
                    self.spewQuadrantAngle = 0
                elif self.spewQuadrant == "port":
                    self.spewQuadrantOffset = 90 + random.randrange(-35, 35, 1)
                    self.spewQuadrantAngle = 90
                elif self.spewQuadrant == "star":
                    self.spewQuadrantOffset = 270 + random.randrange(-35, 35, 1)
                    self.spewQuadrantAngle = 270
                else:
                    self.spewQuadrantOffset = 180 + random.randrange(-45, 45, 1)
                    self.spewQuadrantAngle = 180

        # scale back attributes if internal structure has been hit
        ratio = self.currentISP/self.myShipHull.maxISP
        self.currentPower = self.currentPower * ratio
        self.thrust = self.thrust * ratio
        self.rotation = self.rotation * ratio
        
        # accel
        self.accel = self.myDesign.getAccel(self.thrust, self.mass)
                
        # rotation
        self.rotation = self.myDesign.getRotation(self.rotation, self.mass)
        
        # set ship strength
        self.setMyStrength()
        
        # set weapons
        self.setWeaponStatus()
        
        # set ships desired range which can change as ship gets damaged
        self.setRange()
    
    def setRepairCost(self):
        """xSet the repair cost of Starship"""
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
    
    def setSystemGrid(self):
        """xTake the ship from and to system to decide its systemGrid Attribute"""
        fromSystem = self.myGalaxy.systems[self.fromSystem]
        toSystem = self.myGalaxy.systems[self.toSystem]
        self.systemGrid = anwp.func.funcs.getMapQuadrant(fromSystem.x, fromSystem.y,
                                                           toSystem.x, toSystem.y)
        
    def setDesiredPosition(self, x, y):
        """xSet the Ships desired position in quadrant"""
        (self.setX, self.setY) = (x , y)
    
    def setPosition(self):
        """xSet the ship posX, posY for battle using setX, setY, and fromSystem, toSystem"""
        # determine posX, posY for battle
        (x1,y1) = anwp.func.globals.battlemapQuadrants[self.systemGrid]
        self.posX = x1+self.setX
        self.posY = y1+self.setY
    
    def setRange(self):
        """xDetermine Ship Range to my Target"""
        # first determine ranges
        if len(self.activeWeapons) > 0:
            myPrimaryWeapon = self.activeWeapons[0]
            self.range = myPrimaryWeapon.myWeaponData.range * 0.9
        else:
            # no weapons left RUN
            self.mode = 'escape'
            self.range = 99999
    
    def setWeaponStatus(self):
        """xGo through all ship weapons and order them from most damaging to least
        ignore ones that are damaged or out of ammo"""
        self.readyWeapons = []
        self.activeWeapons = []
        self.amsWeapons = []
        weaponValues = {}
        for position, myQuad in self.quads.iteritems():
            for id, myWeapon in myQuad.weapons.iteritems():
                if myWeapon.operational == 1:
                    if myWeapon.myWeaponData.AMS == 0:
                        # add weapon to proper spot on activeWeapons List
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
                        # add weapon to amsWeapons List
                        self.amsWeapons.append(myWeapon)
    
    def unloadRegiment(self, regimentID):
        """xAttempt to unload Regiment from Ship"""
        if regimentID in self.myRegiments:
            self.myRegiments.remove(regimentID)
            return 1
        else:
            return 'unable to unload Regiment'
    
    def randomizeJunkTrail(self):
        if self.myShipHull.size == "small":
            self.spewRange = random.randrange(0, 10, 1)
        else:
            self.spewRange = random.randrange(0, 25, 1)

    def update(self, interval, world):
        """xperform all ship commands for an interval of time"""
        self.count += 1
        
        availPower = self.currentBattery + (self.currentPower * interval)
        # for now do the shields first and the remainder goes to weapons
        # regenerate shields
        availPower = self.regenShields(interval, availPower)
        
        # power weapons
        availPower = self.powerWeapons(interval, availPower)
        
        # lock weapons
        self.lockWeapons(interval)

        # place remaining power into batteries
        if self.maxBattery > 0 and availPower > 0:
            #print "charging batteries",availPower
            self.currentBattery += availPower
            if self.currentBattery > self.maxBattery:
                self.currentBattery = self.maxBattery
        
        # fire weapons
        if len(self.readyWeapons) > 0:
            self.fireMyWeapons()
        
        # rotate ship to target
        self.rotateToTarget()
        
        # move ship
        self.move(interval, world)

        # if there is quadrant damage, we should exhaust junk
        self.damageSpew(interval, world)
        
        # calculate the variable delay
        if self.threshold:
            value = max( abs(self.velocityX), abs(self.velocityY), abs(self.turnRate) )
            if value < self.threshold:
                self.uDelay = 1.0 - (value / self.threshold)
            else:
                self.uDelay = 0

        return self.alive
    
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_ship.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()