# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# drone.py
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# This represents a drone
# ---------------------------------------------------------------------------
import types
import math
import random
import logging

from anw.func import funcs, globals
from anw.war import ship
import component
import weapon
import shield

class Drone(ship.Ship):
    """A Drone is launched from a carrier and is directed towards other 
    drones, missiles and ships"""
    def __init__(self, args):
        ship.Ship.__init__(self, args)
        self.myShip = None
        self.positions = ['fore']
    
    def destroyMe(self):
        """Destroy Drone"""
        if self.alive == 1:
            self.alive = 0
            if globals.serverMode == 0:
                self.shipsim.explode()
                self.shipsim.destroy()
            self.myShip.removeDrone(self)
            self.myGalaxy.resultList.append('DRONE:%s DESTROYED, Count:%d' % (self.name, self.myGalaxy.count))
            self.myGalaxy.playSound('grenade3')
    
    def setMyShip(self, myShip):
        """Set the Ship owner for this drone"""
        self.myShip = myShip
        self.captainID = myShip.captainID
        self.empireID = myShip.empireID
        self.facing = myShip.facing
        self.setMyGalaxy(myShip.myGalaxy)
        self.myCaptain = myShip.myCaptain
        self.componentdata = myShip.componentdata
        self.weapondata = myShip.weapondata
        self.targets = myShip.targets
        self.amsTargets = myShip.amsTargets
        self.alive = 1
        
        # add drone to enemy target lists
        for targetID in self.targets:
            enemyShip = self.myGalaxy.ships[targetID]
            enemyShip.addTargetShip(self.id)
    
    def setMode(self):
        """Set the ships mode"""
        if self.currentTarget != None:
            self.log.debug('COUNT: %s: %s TARGET-> %s' % (self.myGalaxy.count, self.name, self.currentTarget.name))
            ##self.myGalaxy.resultList.append('COUNT: %s: %s TARGET-> %s' % (self.myGalaxy.count, self.name, self.currentTarget.name))
            if 0:##((len(self.activeWeapons) == 0 or (self.currentISP/self.myShipHull.maxISP) < 0.7)) and self.__module__ == 'anw.war.ship':
                self.mode = 'escape'
            else:
                range = funcs.getTargetRange(self.posX, self.posY, self.currentTarget.posX, self.currentTarget.posY)
                if range <= self.range:
                    self.mode = 'engage'
                else:
                    self.mode = 'close'
        if globals.serverMode == 0:
            self.shipsim.updateShipMode()
    
    def setCollidemask(self):
        self.collidemask = self.myShip.collidemask
    
    def getQuadHit(self, position):
        return self.quads['fore']
    
    def setExperience(self, damage, enemyShip):
        """Drones do not give experience to their captains for taking damage, or give experience
        to captains for shooting them down"""
        pass
    
    def setWeaponStatus(self):
        """Go through all ship weapons and order them from most damaging to least
        ignore ones that are damaged or out of ammo"""
        self.readyWeapons = []
        self.activeWeapons = []
        self.amsWeapons = []
        weaponValues = {}
        self.externalRadius = self.radius
        myQuad = self.quads['fore']
        for id, myWeapon in myQuad.weapons.iteritems():
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
                    