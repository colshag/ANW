# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# missile.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a missile
# ---------------------------------------------------------------------------
import math
import random
import types

from anw.func import funcs, globals
import kobj

class Missile(kobj.KObj):
    """A Missile is fired from a ship at another ship, it moves until 
    it hits something or leaves the world"""
    def __init__(self, weapon, x, y):
        self.name = 'missile'
        self.alive = 1
        self.myWeapon = weapon
        self.x = x
        self.y = y
        self.myTarget = weapon.currentTarget
        self.accel = weapon.myWeaponData.speed * globals.rankMods[self.myWeapon.myQuad.myParent.myCaptain.rank]['missileSpeed']
        self.facing = funcs.getRelativeAngle(x, y, self.myTarget.posX, self.myTarget.posY)
        self.dRotation = 0
        self.trackedSec = 0.0
        if weapon.myWeaponData.missile == 'energy':
            self.isEnergy = 1
        self.rotation = 240.0
        if weapon.myWeaponData.tracking > 0:
            self.tracking = 1
            self.expireGoal = weapon.myWeaponData.tracking * 250
            self.expireCount = 0
        else:
            self.tracking = 0
            self.expireCount = 0
            self.expireGoal  = 400
        self.shipsTargetingMe = []
        self.hp = weapon.myWeaponData.ammoHP
        self.setKObj()

    def setCollidemask(self):
        """The Missiles Collidemask is the invert of the ship that launched it"""
        self.collidemask = ~self.myWeapon.myShip.collidemask

    def setKObj(self):
        kobj.KObj.__init__(self, self.name, self.x, self.y, 0.1, self.facing, self.accel)
        self.setCollidemask()

    def takeHit(self, amount):
        """Take damage from weapon"""
        if amount >= self.hp:
            self.destroyMe()
        else:
            self.hp -= amount

    def destroyMe(self):
        """Destroy Missile"""
        if self.alive == 1:
            self.alive = 0
            self.world.removeMissile(self)        
            self.removeShipsTargetingMe()
            if globals.serverMode == 0:
                self.shipsim.destroy()
                self.shipsim = None
    
    def removeShipsTargetingMe(self):
        """Remove me from ships targetting me"""
        for ship in self.shipsTargetingMe:
            if self in ship.amsTargets:
                ship.amsTargets.remove(self)
    
    def trackTarget(self, interval):
        """Point the missile towards target"""
        self.trackedSec += interval
        if self.myTarget.alive == 1 and self.tracking == 1 and self.trackedSec <= self.myWeapon.myWeaponData.tracking:
            self.dRotation = funcs.getTargetRotate(self.posX, self.posY, self.myTarget.posX, self.myTarget.posY, self.facing)
        else:
            self.dRotation = 0

    def hit(self, other):
        """Called when I hit another object within collision system"""
        if type(other) == types.IntType:
            self.destroyMe()
        elif other.__module__ == 'anw.war.ship':
            if other.alive == 1:
                myEmpire = self.myWeapon.myShip.myGalaxy.empires[self.myWeapon.myShip.empireID]
                myEmpire.stats.incHitsMissile(self.myWeapon.myWeaponData.damage)
                position = funcs.getHitPosition(self.posX, self.posY, other.posX, other.posY, other.facing)
                other.takeHit(self.myWeapon.myWeaponData.damage, self.myWeapon.myWeaponData.missile, position, self.myWeapon.myShip)
                self.destroyMe()
                self.myWeapon.myShip.myGalaxy.playSound('grenade3')
        elif other.__module__ == 'anw.war.drone':
            if other.alive == 1:
                myEmpire = self.myWeapon.myShip.myGalaxy.empires[self.myWeapon.myShip.empireID]
                myEmpire.stats.incHitsMissile(self.myWeapon.myWeaponData.damage)
                position = 'fore'
                other.takeHit(self.myWeapon.myWeaponData.damage*globals.missileHitDroneMultiplier, self.myWeapon.myWeaponData.missile, position, self.myWeapon.myShip)
                self.destroyMe()
                self.myWeapon.myShip.myGalaxy.playSound('grenade3')

    def move(self, interval, world):
        """Perform the Missile's Movement for one interval of time"""
        # fuel runs out same time as tracking unless the target is destroyed before tracking interval is over; in that case the
        # missile still accelerates until out of fuel
        if 0 != self.tracking or self.trackedSec <= self.myWeapon.myWeaponData.tracking:
            self.trackTarget(interval)
        self.dx = math.sin(math.radians(self.facing))
        self.dy = math.cos(math.radians(self.facing))

        if self.dRotation != 0:
            self.facing += (self.dRotation * self.rotation * interval)
        
        self.posX += (self.dx * interval * self.accel)
        self.posY += (self.dy * interval * self.accel)
        self.updatePos(self.posX, self.posY, self.facing)    
            
    def update(self, interval, world):
        """perform all missile commands for an interval of time"""
        self.expire()
        self.move(interval, world)

    def expire(self):
        """Silently destroy missile"""
        if self.expireCount < self.expireGoal:
            self.expireCount += 1
        else:
            self.destroyMe()
        
