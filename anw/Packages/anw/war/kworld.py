# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# kworld.py
# Written by Kris Kundert
# ---------------------------------------------------------------------------
# This is the world object used to managed ship simulations
# ---------------------------------------------------------------------------
import time
import random
import math

from anw.func import funcs, globals

class KWorld(object):
    def __init__(self, width, height):
        self.interval = 0
        self.width = width
        self.height = height
        self.ships = []
        self.missiles = []

        self.mode = None

    def addMissile(self, obj):
        self.missiles.append(obj)
        obj.setWorld(self)
    
    def removeMissile(self, obj):
        self.missiles.remove(obj)
    
    def removeShip(self, obj):
        self.ships.remove(obj)
    
    def addShip(self, myShip):
        self.ships.append(myShip)
        myShip.setWorld(self)
        
    def update(self, interval):
        self.interval = interval
        self.checkCollide()
        self.updateShips()
        self.updateMissiles()

    def updateShips(self):
        for myShip in self.ships:
            if myShip.alive == 1:
                myShip.update(self.interval, self)
    
    def updateMissiles(self):
        for myMissile in self.missiles:
            myMissile.update(self.interval, self)

    def checkCollide(self):
        for ship in self.ships:
            for missile in self.missiles:
                if (ship.collidemask & missile.collidemask) and missile.alive == 1:
                    if funcs.doWeCollide(ship.posX, ship.posY, ship.externalRadius, 
                                         missile.posX, missile.posY, missile.radius):
                        ship.hitExternalRadius(missile)
                        if funcs.doWeCollide(ship.posX, ship.posY, ship.radius, 
                                         missile.posX, missile.posY, missile.radius):
                            ship.hitRadius(missile)
            for otherShip in self.ships:
                if (ship.collidemask & ~otherShip.collidemask) and otherShip.alive == 1:
                    if funcs.doWeCollide(ship.posX, ship.posY, globals.alternateTargetRadius, 
                                         otherShip.posX, otherShip.posY, otherShip.radius):
                        ship.hitWeaponRetargetRadius(otherShip)
                        if ((ship.isAssault == 1 or otherShip.isAssault == 1) and 
                            (ship.underAssault == 0 and otherShip.underAssault == 0)):                            
                            if funcs.doWeCollide(ship.posX, ship.posY, ship.radius, 
                                             otherShip.posX, otherShip.posY, otherShip.radius):
                                ship.shallIAssault(otherShip)

    def setMode(self, mode):
        self.mode = mode
