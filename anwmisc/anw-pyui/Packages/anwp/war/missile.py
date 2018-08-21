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

import anwp.war.warsim
import anwp.sl.utils
import anwp.func.funcs
import anwp.func.globals

class Missile(anwp.war.warsim.WarSim):
    """A Missile is fired from a ship at another ship, it moves until 
    it hits something or leaves the world"""
    def __init__(self, category, weapon, x, y, facing):
        anwp.war.warsim.WarSim.__init__(self, category, weapon, x, y, facing)
        self.myTarget = weapon.currentTarget
        self.accel = weapon.myWeaponData.speed * anwp.func.globals.rankMods[self.myWeapon.myQuad.myParent.myCaptain.rank]['missileSpeed']
        self.dx = math.cos(anwp.sl.utils.toRadians(facing))
        self.dy = math.sin(anwp.sl.utils.toRadians(facing))
        # number of seconds missile has been tracking
        self.trackedSec = 0.0
        
        self.smokeRatio = 0.04
        self.timeSinceLastSmoke = 0
        if self.myWeapon.myWeaponData.missile == 'energy':
            self.rotation = 4000.0
            self.gas = 0
        else:
            self.rotation = 0.0
            self.gas = 1
        if self.myWeapon.myWeaponData.tracking > 0:
            self.tracking = 1
            self.postEvent('expire', self.myWeapon.myWeaponData.tracking * 250)
        else:
            self.tracking = 0
        # add missile to ship so it can be tracked easier
        self.myShip.addMissile(self)
        self.declareToEnemyShip()

    def destroyMe(self):
        """Destroy Missile"""
        self.alive = 0
        self.clearEvents()
        # remove me from ships targetting me
        for ship in self.shipsTargetingMe:
            if self in ship.amsTargets:
                ship.amsTargets.remove(self)
        # create explosion
        self.explode(self.facing, 100, self.posX-4, self.posY-4)
   
        self.myShip.removeMissile(self.gid)
    
    def trackTarget(self, interval):
        """set the dx,dy direction tracking towards target"""
        self.trackedSec += interval
        if self.myTarget.alive == 1 and self.tracking == 1 and self.trackedSec <= self.myWeapon.myWeaponData.tracking:
            # get relative angle between missile and target
            angle = anwp.func.funcs.getRelativeAngle(self.posX, self.posY, self.myTarget.posX, self.myTarget.posY)
            # set the new tracking direction
            self.dx = math.cos(anwp.sl.utils.toRadians(angle))
            self.dy = math.sin(anwp.sl.utils.toRadians(angle))
            # set the missile facing
            if self.rotation == 0:
                self.facing = angle
        else:
            self.tracking = 0

    def hit(self, other, newPosX, newPosY, newFacing):
        """Called when I hit another object within collision system"""
        if type(other) == types.IntType:
            # collision with world walls destroys missile instantly
            self.destroyMe()
            return 1
        elif other.__module__ in ('anwp.war.ship', 'anwp.war.drone'):
            if other.id in self.myShip.targets and other.alive == 1:
                # missile has hit enemy ship
                # determine position of hit
                position = anwp.func.funcs.getHitPosition(self.posX, self.posY, other.posX, other.posY, other.facing)
                other.postEvent('takeHit', 1, self.myWeapon.myWeaponData.damage, self.myWeapon.myWeaponData.missile, position, self.myShip)
                self.destroyMe()
                self.myShip.myGalaxy.game.app.playSound('grenade3')
                return 1

    def move(self, interval, world):
        """Perform the Missile's Movement for one interval of time"""
      
        # fuel runs out same time as tracking unless the target is destroyed before tracking interval is over; in that case the
        # missile still accelerates until out of fuel
        if 0 != self.tracking or self.trackedSec <= self.myWeapon.myWeaponData.tracking:
            # track target
            self.trackTarget(interval)
            # split accel into x and y directions based on desires of ship ai
            xAccel = self.dx*self.accel
            yAccel = self.dy*self.accel
            
            # velocity = accel * time
            self.velocityX = xAccel * interval
            self.velocityY = yAccel * interval

            if self.gas and self.timeSinceLastSmoke > self.smokeRatio:
                # create smoke
                imageFileName = '%ssmoke.png' % self.myShip.myGalaxy.game.app.genImagePath     
                smoke = anwp.sl.sim.SimObject(anwp.sims.categories.JunkCategory(imageFileName, 1), None)
                smoke.life = 1
                smoke.turnRate = random.randrange(-360, 360, 1)
                smoke.facing = self.facing - 180 + random.randrange(-45, 45, 1)
                force = 2
                accel = 15
                smoke.setState(self.posX, self.posY, smoke.facing, accel)
                world.addToWorld(smoke, self.posX, self.posY, smoke.facing, accel, force)
                self.timeSinceLastSmoke = 0
            else:
                self.timeSinceLastSmoke += interval
        
        # move position (distance = velocity * time)
        newPosX = self.posX + (self.velocityX * interval)
        newPosY = self.posY + (self.velocityY * interval)

        # rotate missile if its energy based
        if self.rotation > 0:
            newFacing = self.facing + (self.rotation * interval)
        else:
            newFacing = self.facing

        if world.canMove(self, newPosX, newPosY, newFacing):
            self.posX = newPosX
            self.posY = newPosY
            self.facing = newFacing
            world.move(self, newPosX, newPosY, newFacing)
            self.graphicsObject.setState(newPosX, newPosY, newFacing)
    
    def update(self, interval, world):
        """perform all missile commands for an interval of time"""
        # move
        self.move(interval, world)

        if self.life:
            self.life -= interval
            if self.life <= 0:
                self.alive = 0

        return self.alive
    
def main():
    import doctest,unittest
    suite = doctest.DocFileSuite('unittests/test_missile.txt')
    unittest.TextTestRunner(verbosity=2).run(suite)
  
if __name__ == "__main__":
    main()
        
