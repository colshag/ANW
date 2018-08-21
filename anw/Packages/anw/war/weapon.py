# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# weapon.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a basic ship weapon
# ---------------------------------------------------------------------------
import string
import types
import copy

from anw.func import root, globals, funcs
import direct

class Weapon(root.Root):
    """A Ship Weapon contains the basic attributes of any ship weapon"""
    def __init__(self, args):
        # Attributes
        self.id = str() # Unique Game Object ID
        self.type = str() # Given Weapon Type (id)
        self.facing = float() # default weapon facing in degrees(0, 90, 180, 270)
        self.currentLock = float() # number of seconds spent aquiring a lock
        self.maxLock = float() # modified max lock based on targetting computers
        self.currentAmmo = int() # current ammo state
        self.currentPower = float() # current power level of weapon
        self.currentHP = int() # current HP of weapon
        self.maxHP = int() # max HP of weapon
        self.operational = int() # 1=operational
        self.droneID = str() # drone ID if weapon is drone launcher
        self.defaultAttributes = ('id', 'type', 'facing', 'currentLock', 'maxLock', 'currentAmmo',
                                   'currentPower', 'currentHP', 'maxHP', 'operational','droneID')
        self.setAttributes(args)
        
        self.myQuad = None # Actual Quadrant object containing weapon
        self.myWeaponData = None # Referenced
        self.currentTarget = None # current ship target ship (ref obj)
        self.myShip = None
        self.availAmmo = 0 # available ammo to this weapon at any given time
        self.direction = 0 # direction of weapon in degrees
        self.distance = 0 # distance of weapon in pixels

    def aquireTarget(self):
        """Aquire a target for weapon"""
        if self.myWeaponData.AMS == 0:
            self.aquireShipTarget()
        else:
            self.aquireMissileTarget()

    def aquireShipTarget(self):
        """Aquire the best Ship Target based on range"""
        newRange = 99999
        newTarget = None
        for target in self.myShip.alternateTargets:
            if target.alive == 1 and self.checkIfTargetBeingAssaulted(target) == 0:
                range = self.targetInRangeArc(target)
                if range <= self.myWeaponData.range and range != 0 and target == self.myShip.currentTarget:
                    self.currentTarget = target
                    return
                if range < newRange and range != 0 and range <= self.myWeaponData.range:
                    newTarget = target
                    newRange = range
        if newTarget !=  None:
            self.currentTarget = newTarget
        elif self.checkIfTargetBeingAssaulted(self.myShip.currentTarget) == 0:
            self.currentTarget = self.myShip.currentTarget
    
    def checkIfTargetBeingAssaulted(self, ship):
        """If a target is under assault do not fire on it"""
        if ship == None:
            return 0
        if ship.underAssault == 1 and ship.isAssault == 0:
            return 1
        else:
            return 0
            
    def aquireMissileTarget(self):
        """Aquire the best Missile Target from list of Missiles detected in range"""
        newRange = 99999
        newTarget = None
        for target in self.myShip.amsTargets:
            if target.alive == 1:
                range = self.targetInRangeArc(target)
                if range < newRange and range != 0:
                    newTarget = target
                    newRange = range
        if newTarget !=  None:
            self.currentTarget = newTarget

    def clearMyStatus(self):
        """Clear weapon Attributes"""
        self.currentHP = 0
        self.operational = 0
        self.availAmmo = 0
        self.currentAmmo = 0

    def fire(self):
        """Fire Weapon at target ship"""
        ##self.stats.inc
        # remove ammo if weapon uses ammo
        if self.currentAmmo == 1:
            self.currentAmmo = 0
            
        # remove power
        self.currentPower = 0
        self.myQuad.myParent.allWeaponsPowered = 0
        
        # fire specific weapon
        if self.droneID != '':
            self.fireDrone()
        elif self.myWeaponData.direct != '':
            if self.myWeaponData.AMS == 1:
                self.fireAMS()
            else:
                self.fireDirect()
        elif self.myWeaponData.missile != '':
            self.fireMissile()
        else:
            print 'Nothing to fire'
        self.currentLock=0;

    def fireAMS(self):
        """Fire an Anti-Missile weapon"""
        D100 = self.myShip.myGalaxy.getNextD100()
        if D100 <= globals.rankMods[self.myShip.myCaptain.rank]['toHit']:
            self.createLaserLine(D100, globals.rankMods[self.myShip.myCaptain.rank]['toHit'], 0.02, 'laser1',4)
            self.currentTarget.takeHit(self.myWeaponData.damage)
        else:
            self.createLaserLine(D100, globals.rankMods[self.myShip.myCaptain.rank]['toHit'], 0.02, 'laser1',5)
            
    def fireDirect(self):
        """Fire a direct based weapon"""
        myEmpire = self.myShip.myGalaxy.empires[self.myShip.empireID]
        myEmpire.stats.incShotsDirect(0)
        D100 = self.myShip.myGalaxy.getNextD100()
        rollNeeded = globals.rankMods[self.myShip.myCaptain.rank]['toHit']
        if D100 <= rollNeeded:
            if self.currentTarget.positions == ['fore'] and self.myShip.positions != ['fore']:
                D100 = self.myShip.myGalaxy.getNextD100()
                if D100 <= globals.rankMods[self.myShip.myCaptain.rank]['droneDodge']:
                    self.createLaserLine(D100, globals.rankMods[self.myShip.myCaptain.rank]['droneDodge'], 0.10, 'laser2',4)
                    return
            self.createLaserLine(D100, rollNeeded, 0.10, 'laser2',6)
            position = funcs.getHitPosition(self.myShip.posX, self.myShip.posY, 
                                            self.currentTarget.posX, self.currentTarget.posY, 
                                            self.currentTarget.facing)
            myEmpire.stats.incShotsDirect(self.myWeaponData.damage)
            self.currentTarget.takeHit(self.myWeaponData.damage, self.myWeaponData.direct, position, self.myShip)
        else:
            self.createLaserLine(D100, rollNeeded, 0.10, 'laser2',4)
            

    def createLaserLine(self, rollGot, rollNeeded, lineWidth, sound, fade):
        """Fire a laser (direct or AMS), move its position based on if its hit chance"""
        if globals.serverMode == 0:
            from anw.gui import line
            if rollGot < rollNeeded:
                offSet = 0
                hit = 1
            else:
                offSet = self.currentTarget.radius * 2
                hit = 0
                
            (x,y) = self.getMyXY()
            xTar = self.currentTarget.posX+offSet
            yTar = self.currentTarget.posY+offSet
            myLine = line.Line(self.myShip.myGalaxy.guiMediaPath, (x,y), (xTar, yTar), texture='square_grey',width=lineWidth,hit=hit)
            myLine.setColor(globals.colors[self.myShip.myGalaxy.empires[self.myShip.empireID].color1])
            myLine.startFade(fade, self, self.currentTarget)
            self.myShip.myGalaxy.playSound(sound)
            
    def fireDrone(self):
        """Fire a drone based weapon"""
        if globals.serverMode == 0:
            from anw.gui import shipsim
        from anw.war import drone
        self.operational = 0
        myGalaxy = self.myShip.myGalaxy
        myEmpire = myGalaxy.empires[self.myShip.empireID]
        myDroneDesign = myEmpire.droneDesigns[self.droneID]
        shipID = myGalaxy.getNextID(myGalaxy.ships)
        myDrone = drone.Drone({'id':shipID, 'empireID':myEmpire.id})
        myDrone.setMyShip(self.myShip)
        myDrone.setMyDesign(myDroneDesign)
        myDrone.setMyStatus()
        (myDrone.posX,myDrone.posY) = self.getMyXY()
        myDrone.setKObj()
        myDrone.setCollidemask()
        
        if globals.serverMode == 0:
            myDrone.sim = shipsim.ShipSim(myGalaxy.guiMediaPath, myGalaxy, myDrone)
            myDrone.setShipsim(myDrone.sim)

        myGalaxy.kworld.addShip(myDrone)
        
        if globals.serverMode == 0:
            myGalaxy.setPlanePickable(myDrone, 'ships')
            myGalaxy.sims.append(myDrone.sim)
            myGalaxy.addMiniMapTarget(myDrone)
        self.myShip.addDrone(myDrone)
        myDrone.begin()
    
    def fireMissile(self):
        """Fire a missile based weapon"""
        if globals.serverMode == 0:
            from anw.gui import warsim
        from anw.war import missile
        myEmpire = self.myShip.myGalaxy.empires[self.myShip.empireID]
        myEmpire.stats.incShotsMissile()
        (x,y) = self.getMyXY()
        myMissile = missile.Missile(self, x, y)
        myGalaxy = self.myShip.myGalaxy
        if globals.serverMode == 0:
            myMissile.sim = warsim.WarSim(myGalaxy.guiMediaPath, myGalaxy, self.myShip, 'missile1')
        
        if globals.serverMode == 0:
            myMissile.setShipsim(myMissile.sim)
            myGalaxy.playSound('cannon6')
        
        myGalaxy.kworld.addMissile(myMissile)

    def getMyFacing(self):
        """Get weapons relative facing"""
        weapFacing = self.facing
        shipFacing = self.myShip.facing
        newFacing = (self.myShip.facing + self.facing) % 360
        return newFacing

    def getMyXY(self):
        """Return the current (x,y) of this weapon in simulation"""
        direction = (self.myQuad.myParent.facing + self.direction) % 360
        (x,y) = funcs.findOffset(self.myShip.posX, self.myShip.posY, direction, self.distance)
        return (x,y)

    def getMyValue(self):
        """Return the weapons value in comparison to all other weapons"""
        if type(self.myWeaponData) == types.StringType:
            return 0
        if self.myWeaponData.AMS == 1:
            return 0
        else:
            return self.myWeaponData.range

    def loadAmmo(self):
        """Load Ammunition into weapon chamber, only grab proper ammo from same quadrant"""
        if type(self.myWeaponData) == types.StringType:
            return 1
        if self.currentAmmo == 1:
            return 1
        else:
            # go through all components in ship, look for ammo components that match weapon ABR
            self.availAmmo = 0
            for position in self.myQuad.myParent.positions:
                myQuad = self.myQuad.myParent.quads[position]
                componentIDList = funcs.sortStringList(myQuad.components.keys())
                for componentID in componentIDList:
                    myComponent = myQuad.components[componentID]
                    if (myComponent.myComponentData.abr == (self.myWeaponData.abr+'A') and
                        myComponent.currentAmount > 0):
                        self.availAmmo += myComponent.currentAmount
                        if self.currentAmmo == 0:
                            myComponent.currentAmount -= 1
                            self.currentAmmo += 1
                            self.availAmmo -= 1
        
        if self.availAmmo == 0 and self.currentAmmo == 0:
            self.operational = 0

        return self.currentAmmo
    
    def setTotalAmmo(self):
        if self.myWeaponData.missile != '' or self.myWeaponData.direct != '' and self.myWeaponData.ammo == 1:
            self.loadAmmo()
    
    def lockTarget(self, interval):
        """Increment Target lock if enemy ship is still alive"""
        if self.operational == 0 or self.currentTarget == None or self.currentTarget.alive == 0:
            self.currentLock = 0
            return
        
        if self.currentLock < self.maxLock: 
            self.currentLock += interval
            if self.currentLock > self.maxLock:
                self.currentLock = self.maxLock

    def preFireCheck(self):
        """Perform Pre-Fire Checks on weapon, can weapon fire? return 1=yes, 0=no"""
        # is weapon operational?
        if self.operational == 0:
            return 0
        
        # deal with drone possibility
        if type(self.myWeaponData) == types.StringType:
            droneType = self.myShip.myGalaxy.dronehulldata[self.myWeaponData]
            powerReq = droneType.mass*5.0
            ammoReq = 0
        else:
            powerReq = self.myWeaponData.maxPower
            ammoReq = self.myWeaponData.ammo
        
        # is weapon at full energy to fire?
        if self.currentPower < powerReq:
            return 0
        
        # does the weapon require ammo?
        if ammoReq == 1 and self.currentAmmo == 0:
            # attempt to load ammo into weapon
            if self.loadAmmo() == 0:
                return 0
            
        # does the weapon have a valid target (target in range/arc)
        if (self.currentTarget == None or 
            self.currentTarget.alive == 0 or 
            (self.currentTarget != self.myShip.currentTarget and self.myWeaponData.AMS == 0) or
            self.myShip.alternateTargets != []):
            self.aquireTarget()
        if self.currentTarget == None:
            return 0
        elif self.targetInRangeArc(self.currentTarget) == 0:
            return 0
        elif self.currentLock < self.maxLock:
            return 0
        else:
            return 1
    
    def setMyQuad(self, quadObject):
        """Set the Quad Owner of this weapon"""
        self.myQuad = quadObject
        quadObject.weapons[self.id] = self
        self.myWeaponData = self.myQuad.weapondata[self.type]
        self.myShip = self.myQuad.myParent
        self.setMyStatus()
    
    def setMyStatus(self):
        """Set the status of all calculated attributes"""
        if self.type != '' and self.myQuad != None:
            self.clearMyStatus()
            self.maxHP = self.myWeaponData.maxCompHP * self.myWeaponData.numComps
            # set weapon HP based on total component HP
            for compID, myComponent in self.myQuad.components.iteritems():
                if myComponent.weaponID == self.id:
                    self.currentHP += myComponent.currentHP
            # determine if weapon is operational
            try:
                if self.myWeaponData.abr[-1:] == 'L' and self.myQuad.myParent.myGalaxy.count > 10:
                    return # drone launchers can only fire once
            except:
                pass
            if self.currentHP == self.maxHP:
                self.operational = 1
                # set the weapons lock time based on targetting computers and captain experience
                mod = self.myQuad.target
                if self.myQuad.myParent.__module__ == 'anw.war.ship':
                    mod += globals.rankMods[self.myQuad.myParent.myCaptain.rank]['targetLock']
                if mod > 70.0:
                    mod = 70.0 # max with all modifiers is 70% of lock time
                self.maxLock = self.myWeaponData.maxLock * (100.0 - mod) / 100.0
            # set the direction and distance attributes of the weapon
            if self.myShip.myShipHull != None:
                # this is a regular ship hull, place according to ship Hull hardpoints
                [self.direction, self.distance] = self.myShip.myShipHull.hardPoints['%s-%s' % (self.myQuad.position, self.id)]
                self.distance = self.distance/100.0
    
    def targetInRangeArc(self, enemyShip):
        """Check if weapon is in range and arc of weapon"""
        if enemyShip.alive == 0:
            return 0
        else:
            (xMe, yMe) = self.getMyXY()
            facing = self.getMyFacing()
            xTar = enemyShip.posX
            yTar = enemyShip.posY
            weapRange = self.myWeaponData.range
            weapArc = self.myWeaponData.arc
            result = funcs.targetInRangeArc(facing, xMe, yMe, xTar, yTar, weapRange, weapArc)
            return result
