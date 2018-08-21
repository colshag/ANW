# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# war library
# Written by Chris Lewis
# ---------------------------------------------------------------------------
# warsim.py
# extension of sim object for war package
# ---------------------------------------------------------------------------
import random

import anwp.sl.sim
import anwp.sl.entityManager

class WarSim(anwp.sl.sim.SimObject):
    """ For Simple sim objects in war package
    """
    def __init__(self, category, weapon, x, y, facing):
        anwp.sl.sim.SimObject.__init__(self, category, None)
        self.gid = anwp.sl.entityManager.nextGID(self) # unique gid
        self.myWeapon = weapon
        self.myShip = weapon.myQuad.myParent
        self.hp = weapon.myWeaponData.ammoHP
        self.posX = x
        self.posY = y
        self.velocityX = weapon.myQuad.myParent.velocityX
        self.velocityY = weapon.myQuad.myParent.velocityY
        self.shipsTargetingMe = [] # list of ships that have me in their AMSTarget list
        
    def clearEvents(self, action=''):
        self.myShip.myGalaxy.shipEventManager.clearEventsFor(self.gid, action)
    
    def event_retarget(self):
        self.myTarget=None
        self.postEvent('retarget',250)
    
    def event_expire(self):
        """silently destroy missile"""
        self.destroyMe()
    
    def event_takeHit(self, amount):
        """Take damage from weapon"""
        if amount >= self.hp:
            self.destroyMe()
        else:
            self.hp -= amount
    
    def declareToEnemyShip(self):
        """On my creation, declare myself to the enemy ship I'm being launched at"""
        for shipID in self.myShip.targets:
            enemyShip = self.myShip.myGalaxy.ships[shipID]
            if self not in enemyShip.amsTargets:
                enemyShip.addAMSTarget(self)
                
    def explode(self, facing, speed, x, y):
        """Create the small Explosion Sim"""
        if self.myShip.myGalaxy.simMode == 'client':
            import anwp.sims
            myEmpire = self.myShip.myGalaxy.empires[self.myShip.empireID]
            color1 = myEmpire.color1
            color2 = myEmpire.color2
            imageFileName = '%sjunk1_%s_%s.png' % (self.myShip.myGalaxy.game.app.simImagePath, color1, color2)

            # add sim to world
            for iter in range(5):
                explosion = anwp.sl.sim.SimObject(anwp.sims.categories.JunkCategory(imageFileName, 1), None)
                explosion.life = 1
                explosion.turnRate = random.randrange(-360, 360, 1)
                explosion.setState(x, y, facing, speed)
                explosion.facing = facing + random.randrange(0, 360, 1)
                force = 2
                self.myShip.myGalaxy.world.addToWorld(explosion, x, y, explosion.facing, speed, force)
    
    def getMyXY(self):
        """Return posX, posY"""
        return (self.posX, self.posY)
    
    def postEvent(self, action, delay, *args):
        return self.myShip.myGalaxy.shipEventManager.postEvent(self.gid, action, delay ,args)
    