# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# weapon.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a basic ship weapon
# ---------------------------------------------------------------------------
import string
import types

import anwp.func.root
import anwp.func.funcs
import anwp.func.globals
import direct
import missile
import drone

class Weapon(anwp.func.root.Root):
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
        """aquire a target for weapon"""
        if self.myWeaponData.AMS == 0:
            range = 99999
            newTarget = None
            for shipID in self.myShip.targets:
                enemyShip = self.myShip.myGalaxy.ships[shipID]
                if enemyShip.alive == 1:
                    newRange = self.targetInRangeArc(enemyShip)
                    if newRange < range and newRange <> 0:
                        newTarget = enemyShip
                        range = newRange
        
            if newTarget <> None:
                self.currentTarget = newTarget
        else:
            # this is an anti-missile weapon, look for missiles
            nearestTarget = None
            nearestRange = 99999
            for target in self.myShip.amsTargets:
                range = self.targetInRangeArc(target)
                if range < nearestRange and range <> 0:
                    nearestTarget = target
                    nearestRange = range
            
            if nearestTarget <> None:
                self.currentTarget = nearestTarget

    def clearMyStatus(self):
        """Clear weapon Attributes"""
        self.currentHP = 0
        self.operational = 0
        self.availAmmo = 0

    def fire(self):
        """Fire Weapon at target ship"""
        #self.stats.inc
        # remove ammo if weapon uses ammo
        if self.currentAmmo == 1:
            self.currentAmmo = 0
            
        # remove power
        self.currentPower = 0
        self.myQuad.myParent.allWeaponsPowered = 0
        
        # fire specific weapon
        if self.droneID <> '':
            self.fireDrone()
        if self.myWeaponData.direct <> '':
            if self.myWeaponData.AMS == 1:
                self.fireAMS()
            else:
                self.fireDirect()
        elif self.myWeaponData.missile <> '':
            self.fireMissile()
        else:
            print 'Nothing to fire'
        self.currentLock=0;

    def fireAMS(self):
        """Fire an Anti-Missile weapon"""
        # display line
        self.myShip.myGalaxy.lines.append([self, self.currentTarget, 2])
        # add sound
        self.myShip.myGalaxy.game.app.playSound('laser1')
        # check if weapon hits
        D100 = self.myShip.myGalaxy.getNextD100()
        if D100 <= anwp.func.globals.rankMods[self.myShip.myCaptain.rank]['toHit']:
            # hit target
            self.currentTarget.postEvent('takeHit', 1, self.myWeaponData.damage)
            ##self.myShip.stats.incShotsAMS(self.myWeaponData.damage)
        ##else:
            ##self.myShip.stats.incShotsAMS(0)
            
    def fireDirect(self):
        """Fire a direct based weapon"""
        # create directfire image
        import anwp.sims
        myGalaxy = self.myShip.myGalaxy
        myEmpire = myGalaxy.empires[self.myShip.empireID]
        name = 'zdirect1_%s_%s' % (myEmpire.color1, myEmpire.color2)
        imageFileName = '%s%s.png' % (myGalaxy.game.app.simImagePath, name)
        speed = 0
        force = 1
        (wX, wY) = self.getMyXY()
        tX = self.currentTarget.posX
        tY = self.currentTarget.posY
        centerX = (wX+tX)/2
        centerY = (wY+tY)/2
        angle = anwp.func.funcs.getRelativeAngle(wX, wY, tX, tY)
        category = anwp.sims.categories.DirectFireCategory(imageFileName, string.lower(self.myWeaponData.abr[0]))
        sim = direct.Direct(category, self, centerX, centerY, angle, self.currentTarget)
        myGalaxy.world.addToWorld(sim, centerX, centerY, angle, speed, force)
        # add sound
        self.myShip.myGalaxy.game.app.playSound('laser2')
        # check if weapon hits
        D100 = self.myShip.myGalaxy.getNextD100()
        if D100 <= anwp.func.globals.rankMods[self.myShip.myCaptain.rank]['toHit']:
            # determine position of hit
            position = anwp.func.funcs.getHitPosition(self.myShip.posX, self.myShip.posY, self.currentTarget.posX, self.currentTarget.posY, self.currentTarget.facing)
            # hit target
            self.currentTarget.postEvent('takeHit', 1, self.myWeaponData.damage, self.myWeaponData.direct, position, self.myShip)
            ##self.myShip.stats.incShotsDirect(self.myWeaponData.damage)
        ##else:
            ##self.myShip.stats.incShotsDirect(0)
            
    def fireDrone(self):
        """Fire a drone based weapon"""
        import anwp.sims
        # once a drone is launched weapon is no longer valid
        self.operational = 0
        myGalaxy = self.myShip.myGalaxy
        myEmpire = myGalaxy.empires[self.myShip.empireID]
        
        # create drone object
        myDroneDesign = myEmpire.droneDesigns[self.droneID]
        shipID = myGalaxy.getNextID(myGalaxy.ships)
        myDrone = drone.Drone({'id':shipID, 'empireID':myEmpire.id})
        myDrone.setMyShip(self.myShip)
        myDrone.setMyDesign(myDroneDesign)
        myDrone.setMyStatus()
        (myDrone.posX,myDrone.posY) = self.getMyXY()
        
        # create drone sim object
        imageFileName = '%s%s.png' % (myGalaxy.game.app.simImagePath, myDrone.myDesign.getImageFileName())
        # create sim
        myDrone.setMyEntity(anwp.sims.categories.ShipCategory(imageFileName, string.lower(myDrone.myShipHull.abr)), myDrone.posX, myDrone.posY, myDrone.facing)
                        
        # add sim to world
        speed = 0
        force = 1
        myGalaxy.world.addToWorld(myDrone, myDrone.posX, myDrone.posY, myDrone.facing, speed, force)
        myDrone.begin()
    
    def fireMissile(self):
        """Fire a missile based weapon"""
        import anwp.sims
        myGalaxy = self.myShip.myGalaxy
        myEmpire = myGalaxy.empires[self.myShip.empireID]
        # determine missile image to use
        if self.myWeaponData.missile == 'impact':
            # add sound
##            myGalaxy.game.app.playSound('missile1')
            #cannon sounds way cooler. :)
            myGalaxy.game.app.playSound('cannon6')
            num = 1
        else:
            # add sound
            myGalaxy.game.app.playSound('photon1')
            num = 2
        name = 'missile%d_%s_%s' % (num, myEmpire.color1, myEmpire.color2)
        imageFileName = '%s%s.png' % (myGalaxy.game.app.simImagePath, name)
        speed = 0
        force = 1
        (x,y) = self.getMyXY()
        # get relative angle between missile and target
        angle = anwp.func.funcs.getRelativeAngle(x, y, self.currentTarget.posX, self.currentTarget.posY)
        # determine proper Missile category
        category = anwp.sims.categories.MissileCategory(imageFileName, string.lower(self.myWeaponData.abr[0]), num)
        sim = missile.Missile(category, self, x, y, angle)
        myGalaxy.world.addToWorld(sim, x, y, angle, speed, force)
        sim.velocityX = self.myShip.velocityX
        sim.velocityY = self.myShip.velocityY
        ##self.myShip.stats.incShotsMissile()

    def getMyFacing(self):
        """Get weapons relative facing"""
        weapFacing = self.facing
        shipFacing = self.myShip.facing
        newFacing = (self.myShip.facing + self.facing) % 360
        return newFacing

    def getMyXY(self):
        """Return the current (x,y) of this weapon in simulation"""
        direction = (self.myQuad.myParent.facing + self.direction) % 360
        (x,y) = self.myQuad.myParent.findOffset(direction, self.distance)
        return (x,y)

    def getMyValue(self):
        """Return the weapons value in comparison to all other weapons"""
        if type(self.myWeaponData) == types.StringType:
            return 0
        if self.myWeaponData.AMS == 1:
            return 0
        else:
            return self.myWeaponData.range + self.myWeaponData.damage

    def loadAmmo(self):
        """Load Ammunition into weapon chamber, only grab proper ammo from same quadrant"""
        if type(self.myWeaponData) == types.StringType:
            return 1
        if self.currentAmmo == 1:
            return 1
        else:
            # go through all components in ship, look for ammo components that match weapon ABR
            self.availAmmo = 0
            for position in ['fore','aft','port','star']:
                myQuad = self.myQuad.myParent.quads[position]
                componentIDList = anwp.func.funcs.sortStringList(myQuad.components.keys())
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
        if self.type <> '' and self.myQuad <> None:
            self.clearMyStatus()
            self.maxHP = self.myWeaponData.maxCompHP * self.myWeaponData.numComps
            # set weapon HP based on total component HP
            for compID, myComponent in self.myQuad.components.iteritems():
                if myComponent.weaponID == self.id:
                    self.currentHP += myComponent.currentHP
            # determine if weapon is operational
            if self.currentHP == self.maxHP:
                self.operational = 1
                # set the weapons lock time based on targetting computers and captain experience
                mod = self.myQuad.target
                if self.myQuad.myParent.__module__ == 'anwp.war.ship':
                    mod += anwp.func.globals.rankMods[self.myQuad.myParent.myCaptain.rank]['targetLock']
                if mod > 70.0:
                    mod = 70.0 # max with all modifiers is 70% of lock time
                self.maxLock = self.myWeaponData.maxLock * (100.0 - mod) / 100.0
            # set the direction and distance attributes of the weapon
            if self.myShip.myShipHull <> None:
                # this is a regular ship hull, place according to ship Hull hardpoints
                [self.direction, self.distance] = self.myShip.myShipHull.hardPoints['%s-%s' % (self.myQuad.position, self.id)]
    
    def targetInRangeArc(self, enemyShip):
        """Check if weapon is in range and arc of weapon"""
        if enemyShip.alive == 0:
            return 0
        else:
            ##xMe = self.myShip.posX
            ##yMe = self.myShip.posY
            (xMe, yMe) = self.getMyXY()
            facing = self.getMyFacing()
            xTar = enemyShip.posX
            yTar = enemyShip.posY
            weapRange = self.myWeaponData.range
            weapArc = self.myWeaponData.arc
            result = anwp.func.funcs.targetInRangeArc(facing, xMe, yMe, xTar, yTar, weapRange, weapArc)
            return result
        
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_weapon.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        
