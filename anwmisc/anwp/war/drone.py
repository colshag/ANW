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

import anwp.sl.utils
import anwp.sl.sim
import anwp.sl.entity
import anwp.func.root
import anwp.war.ship
import component
import weapon
import shield
import anwp.func.funcs

class Drone(anwp.war.ship.Ship):
    """A Drone is launched from a carrier and is directed towards other 
    drones, missiles and ships"""
    def __init__(self, args):
        anwp.war.ship.Ship.__init__(self, args)
        self.myShip = None
    
    def destroyMe(self):
        """Destroy Ship"""
        if self.alive == 1:
            self.alive = 0
            
            # set an explosion sim
            self.explode(random.randrange(15,25,1), 30, True)
            
            # tell simulator to remove selector if its on me
            if self.myGalaxy.shipInfo <> None:
                if self.myGalaxy.shipInfo.ship == self:
                    self.myGalaxy.onSelectNoSim()
            
            # log
            self.myGalaxy.resultList.append('DRONE:%s DESTROYED, Count:%d' % (self.name, self.myGalaxy.count))
            self.myGalaxy.game.app.playSound('bomb7')
    
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
    
    def event_takeHit(self, amount, type, position, enemyShip):
        """Take damage from incoming weapon, direct damage to appropriate quadrant"""
        self.log.debug('COUNT: %s: %s TAKE HIT, Amount:%d, enemy:%s' % (self.myGalaxy.count, self.name, amount, enemyShip.name))
        myQuad = self.quads['fore']
        
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
    
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_drone.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        