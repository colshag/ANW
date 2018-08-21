# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# statistics.py
# Written by
# ---------------------------------------------------------------------------
# Battle statistics tracking.
# ---------------------------------------------------------------------------

class Statistics:
    """ Speedy statistics tracking. """
    def __init__(self):
        # Attributes
        self.shotsAMS = int(0)
        self.hitsAMS = int(0)
        self.damageAMS = int(0)
        
        self.shotsDirect = int(0)
        self.hitsDirect = int(0)
        self.damageDirect = int(0)
        
        self.shotsMissile = int(0)
        self.hitsMissile = int(0)
        self.damageMissile = int(0)
        
        self.shotsDroneAMS = int(0)
        self.hitsDroneAMS = int(0)
        self.damageDroneAMS = int(0)
        
        self.shotsDroneDirect = int(0)
        self.hitsDroneDirect = int(0)
        self.damageDroneDirect = int(0)
        
    def incShotsAMS(self, damage):
        self.shotsAMS+=1
        if damage != 0:
                self.hitsAMS+=1
                self.damageAMS+=damage
        
    def incShotsDirect(self, damage):
        self.shotsDirect+=1
        if damage != 0:
                self.hitsDirect+=1
                self.damageDirect+=damage
    
    def incShotsMissile(self):
        self.shotsMissile+=1
    
    def incHitsMissile(self, damage):
        self.hitsMissile+=1
        self.damageMissile+=damage
        
    def incShotsDroneAMS(self, damage):
        self.shotsDroneAMS+=1
        if damage != 0:
                self.hitsDroneAMS+=1
                self.damageDroneAMS+=damage
            
    def incShotsDroneDirect(self, damage):
        self.shotsDroneDirect+=1
        if damage != 0:
                self.hitsDroneDirect+=1
                self.damageDroneDirect+=damage
            
    def getShotsAMS(self):
        return self.shotsAMS
    
    def getHitsAMS(self):
        return self.hitsAMS
    
    def getDamageAMS(self):
        return self.damageAMS
    
    def getShotsDirect(self):
        return self.shotsDirect
    
    def getHitsDirect(self):
        return self.hitsDirect
    
    def getDamageDirect(self):
        return self.damageDirect
    
    def getShotsMissile(self):
        return self.shotsMissile
    
    def getHitsMissile(self):
        return self.hitsMissile
    
    def getDamageMissile(self):
        return self.damageMissile
    
    def getAccuracyAMS(self):
        acc=0.0
        if self.shotsAMS != 0:
            if self.hitsAMS != 0:
                acc=(float(self.hitsAMS) / float(self.shotsAMS)) * 100.0
            else:
                acc=0.0
        return acc
    
    def getAccuracyDirect(self):
        acc=0.0
        if self.shotsDirect != 0:
            if self.hitsDirect != 0:
                acc=(float(self.hitsDirect) / float(self.shotsDirect)) * 100.0
            else:
                acc=0.0
        return acc
    
    def getAccuracyMissile(self):
        acc=0.0
        if self.shotsMissile != 0:
            if self.hitsMissile != 0:
                acc=(float(self.hitsMissile) / float(self.shotsMissile)) * 100.0
            else:
                acc=0.0
        return acc
    
    def getAccuracyDroneAMS(self):
        acc=0.0
        if self.shotsDroneAMS != 0:
            if self.hitsDroneAMS != 0:
                acc=(float(self.hitsDroneAMS) / float(self.shotsDroneAMS)) * 100.0
            else:
                acc=0.0
        return acc
    
    def getAccuracyDroneDirect(self):
        acc=0.0
        if self.shotsDroneDirect != 0:
            if self.hitsDroneDirect != 0:
                acc=(float(self.hitsDroneDirect) / float(self.shotsDroneDirect)) * 100.0
            else:
                acc=0.0
        return acc
    
    def getSummary(self):
        ##s= 'AMS acc:          %.2f%%\n' % self.getAccuracyAMS()
        ##s+='shotsAMS:         %04d\n' % self.shotsAMS
        ##s+='hitsAMS:          %04d\n' % self.hitsAMS
        ##s+='damageAMS:        %04d\n' % self.damageAMS
        
        ##s+='Direct acc:       %.2f%%\n' % self.getAccuracyDirect()
        ##s+='shotsDirect:      %04d\n' % self.shotsDirect
        ##s+='hitsDirect:       %04d\n' % self.hitsDirect
        ##s+='damageDirect:     %04d\n' % self.damageDirect
        
        ##s+='Missile acc:      %.2f%%\n' % self.getAccuracyMissile()
        ##s+='shotsMissile:     %04d\n' % self.shotsMissile
        ##s+='hitsMissile:      %04d\n' % self.hitsMissile
        ##s+='damageMissile:    %04d\n' % self.damageMissile
        
        ##s+='DroneAMS acc:     %.2f%%\n' % self.getAccuracyDroneAMS()
        ##s+='shotsDroneAMS:    %04d\n' % self.shotsDroneAMS
        ##s+='hitsDroneAMS:     %04d\n' % self.hitsDroneAMS
        ##s+='damageDroneAMS:   %04d\n' % self.damageDroneAMS
        
        ##s+='DroneDirect acc:  %.2f%%\n' % self.getAccuracyDroneDirect()
        ##s+='shotsDroneDirect: %04d\n' % self.shotsDroneDirect
        ##s+='hitsDroneDirect:  %04d\n' % self.hitsDroneDirect
        ##s+='damageDroneDirect:%04d' % self.damageDroneDirect
        
        s ='Direct Accuracy:       %.2f%%\n' % self.getAccuracyDirect()
        s+='        Direct Damage:     %04d\n' % self.damageDirect
        s+='        Missile Accuracy:      %.2f%%\n' % self.getAccuracyMissile()
        s+='        Missile Damage:    %04d\n' % self.damageMissile
        #s+='   Drone Damage:%04d' % self.damageDroneDirect
        return s

def main():
    pass
  
if __name__ == "__main__":
    main()